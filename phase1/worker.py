import boto3
import json
import os
import time
from phase1.graph.workflow import rewrite
from phase1.llm import chat

# Connect to DynamoDB
dynamodb = boto3.resource("dynamodb")
jobs_table = dynamodb.Table("HumanizerJobs")

def process_job(job_id, text):
    print(f"👷 Worker started on Job {job_id}...")
    
    try:
        # 1. Update Status to Processing
        jobs_table.update_item(
            Key={'job_id': job_id},
            UpdateExpression="set #s = :s",
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={':s': 'PROCESSING'}
        )
        
        # 2. Do the Heavy Lifting (The Slow Part)
        # We can now afford to use the SLOW loop (3 iterations) because we are async!
        rewritten_text = rewrite(text)
        
        # 3. Save the Result
        jobs_table.update_item(
            Key={'job_id': job_id},
            UpdateExpression="set #s = :s, result = :r",
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={
                ':s': 'COMPLETED',
                ':r': rewritten_text
            }
        )
        print(f"✅ Job {job_id} Completed!")
        
    except Exception as e:
        print(f"❌ Job {job_id} Failed: {e}")
        jobs_table.update_item(
            Key={'job_id': job_id},
            UpdateExpression="set #s = :s, error_msg = :e",
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={
                ':s': 'FAILED',
                ':e': str(e)
            }
        )

# This handler allows this file to be triggered by AWS Lambda
def handler(event, context):
    
    job_id = event.get('job_id')
    text = event.get('text')
    
    if job_id and text:
        process_job(job_id, text)
        return {"status": "success"}
    else:
        return {"status": "error", "message": "Missing job_id or text"}