import boto3
import uuid
import json
import os
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import BaseModel

# Note: We do NOT import 'rewrite' here anymore. The Worker handles that.

app = FastAPI()

# CORS Setup (Allows React to talk to us)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS Clients (Explicit Region is safer)
REGION = os.environ.get("AWS_REGION", "ap-south-1")
lambda_client = boto3.client('lambda', region_name=REGION)
dynamodb = boto3.resource('dynamodb', region_name=REGION)

# Table Names (Must match what is in template.yaml)
JOBS_TABLE = "HumanizerJobs"
FEEDBACK_TABLE = "HumanizerFeedback"

jobs_table = dynamodb.Table(JOBS_TABLE)
feedback_table = dynamodb.Table(FEEDBACK_TABLE)

# Environment Variables
WORKER_FUNCTION_NAME = os.environ.get('WORKER_FUNCTION_NAME')

# Data Models
class RewriteRequest(BaseModel):
    text: str

class FeedbackRequest(BaseModel):
    original_text: str
    rewritten_text: str
    score: int
    timestamp: int = int(time.time())

# ==================================================================
# 1️. ASYNC REWRITE ENDPOINT (The Order Taker)
# ==================================================================
@app.post("/rewrite")
def start_rewrite_job(payload: RewriteRequest):
    # 🚨 SAFETY CHECK: If Worker Name is missing, crash with a helpful error
    if not WORKER_FUNCTION_NAME:
        print("❌ Error: WORKER_FUNCTION_NAME env var is missing!")
        raise HTTPException(status_code=500, detail="Configuration Error: Worker Name missing")

    job_id = str(uuid.uuid4())
    print(f"🚀 Starting Job {job_id} -> Worker: {WORKER_FUNCTION_NAME}")
    
    try:
        # A. Create the Ticket in DynamoDB
        jobs_table.put_item(Item={
            'job_id': job_id,
            'status': 'QUEUED',
            'original_text': payload.text,
            'created_at': int(time.time())
        })
        
        # B. Dispatch the Worker (Async Fire-and-Forget)
        payload_json = json.dumps({"job_id": job_id, "text": payload.text})
        
        lambda_client.invoke(
            FunctionName=WORKER_FUNCTION_NAME,
            InvocationType='Event', # 'Event' means: "Don't wait for the answer, just go."
            Payload=payload_json
        )
        
        # C. Return Ticket ID immediately (Fast!)
        return {"job_id": job_id, "status": "queued"}
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}") # This will show in CloudWatch
        raise HTTPException(status_code=500, detail=str(e))

# ==================================================================
# 2️. STATUS CHECK ENDPOINT (The Polling Station)
# React will call this every 2 seconds to see if the job is done.
# ==================================================================
@app.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    try:
        response = jobs_table.get_item(Key={'job_id': job_id})
        item = response.get('Item')
        
        if not item:
            raise HTTPException(status_code=404, detail="Job not found")
            
        # Return the full status (queued, processing, completed)
        return {
            "job_id": job_id, 
            "status": item.get('status'), 
            "result": item.get('result'), # This will be None until it's finished
            "error": item.get('error_msg')
        }
    except Exception as e:
        print(f"DB Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================================================================
# 3️. FEEDBACK ENDPOINT (The Memory)
# ==================================================================
@app.post("/feedback")
def save_feedback(payload: FeedbackRequest):
    try:
        feedback_id = str(uuid.uuid4())
        item = {
            "feedback_id": feedback_id,
            "original_text": payload.original_text,
            "rewritten_text": payload.rewritten_text,
            "score": payload.score,
            "timestamp": int(time.time())
        }
        feedback_table.put_item(Item=item)
        return {"status": "success", "id": feedback_id}
    except Exception as e:
        print(f"DB Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Entry point for AWS Lambda
handler = Mangum(app)