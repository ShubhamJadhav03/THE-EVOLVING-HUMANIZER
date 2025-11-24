import boto3
import json
import os 

#define DynamoDB

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("HumanizerFeedback")

def extract_training_data():
    print("Scanning DB for Feedback Entries...")
    response = table.scan()
    items = response.get('Items', [])

    print(f"Found Total {len(items)} records.")
    training_data = []

    for item in items:
        if item.get("score") == 1:
            entry = {
                "messages":[
                    {"role": "system","content": "You are a professional ghostwriter. Rewrite the input to sound like a smart, conversational human."},
                    {"role": "user", "content": item.get( "original_text")},
                    {"role": "assistant", "content": item.get( "rewritten_text")},
                ]
            }
            training_data.append(entry)

    print(f"✅ Filtered down to {len(training_data)} high-quality training examples.")

    os.makedirs("data", exist_ok=True)
    with open("data/training.jsonl", "w") as f:
        for entry in training_data:
            f.write(json.dumps(entry) + "\n")

    print("Saved data to data/training.jsonl")

if __name__ == "__main__":
    extract_training_data()