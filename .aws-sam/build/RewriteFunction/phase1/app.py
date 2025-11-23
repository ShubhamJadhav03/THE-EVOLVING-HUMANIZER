import boto3
import uuid
import time
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import BaseModel
from phase1.graph.workflow import rewrite

app = FastAPI()

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DynamoDB Setup (The Memory)
# We initialize this outside the handler to reuse connections if possible
dynamodb = boto3.resource("dynamodb")
TABLE_NAME = "HumanizerFeedback" 
table = dynamodb.Table(TABLE_NAME)

# Input Models
class RewriteRequest(BaseModel):
    text: str

class FeedbackRequest(BaseModel):
    original_text: str
    rewritten_text: str
    score: int  # 1 for Like, -1 for Dislike
    timestamp: int = int(time.time())

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "The Evolving Humanizer"}

@app.post("/rewrite")
def rewrite_api(payload: RewriteRequest):
    try:
        result = rewrite(payload.text)
        return {"rewritten_text": result}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
def save_feedback(payload: FeedbackRequest):
    try:
        feedback_id = str(uuid.uuid4())
        
        # Construct item ensuring all types are compatible with DynamoDB
        item = {
            "feedback_id": feedback_id,
            "original_text": payload.original_text,
            "rewritten_text": payload.rewritten_text,
            "score": payload.score,
            "timestamp": int(time.time())
        }
        
        # Save to DynamoDB
        table.put_item(Item=item)
        
        return {"status": "success", "id": feedback_id}
    except Exception as e:
        print(f"DB Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

handler = Mangum(app)