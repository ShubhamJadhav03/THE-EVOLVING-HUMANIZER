import boto3
import json
import os
import time
from phase1.graph.workflow import rewrite

# Connect to DynamoDB
dynamodb = boto3.resource("dynamodb")
# Ensure this matches your template.yaml table name
jobs_table = dynamodb.Table("HumanizerJobs")

def process_job(job_id, text):
    print(f" Worker started on Job {job_id}...")
    
    try:
        # 1. Update Status to PROCESSING
        jobs_table.update_item(
            Key={'job_id': job_id},
            UpdateExpression="set #s = :s",
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={':s': 'PROCESSING'}
        )
        
        # 2. Do the Heavy Lifting (The Slow Part)
        print(" Running LangGraph logic...")
        rewritten_text = rewrite(text)
        
        # 3. Save the Result
        # 👇 FIX: We alias 'result' to '#r' because 'result' is a reserved word
        jobs_table.update_item(
            Key={'job_id': job_id},
            UpdateExpression="set #s = :s, #r = :r",
            ExpressionAttributeNames={
                '#s': 'status',
                '#r': 'result'  # <--- The Fix
            },
            ExpressionAttributeValues={
                ':s': 'COMPLETED',
                ':r': rewritten_text
            }
        )
        print(f" Job {job_id} Completed!")
        
    except Exception as e:
        print(f" Job {job_id} Failed: {e}")
        jobs_table.update_item(
            Key={'job_id': job_id},
            UpdateExpression="set #s = :s, #e = :e",
            ExpressionAttributeNames={
                '#s': 'status',
                '#e': 'error_msg'
            },
            ExpressionAttributeValues={
                ':s': 'FAILED',
                ':e': str(e)
            }
        )

# Handler for Lambda
def handler(event, context):
    job_id = event.get('job_id')
    text = event.get('text')
    
    if job_id and text:
        process_job(job_id, text)
        return {"status": "success"}
    else:
        print("Invalid input event")
        return {"status": "error", "message": "Missing job_id or text"}