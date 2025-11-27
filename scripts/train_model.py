import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables (API Key)
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def start_finetuning():
    print(" Preparing to fine-tune...")

    # Step 1: Check if file exists
    if not os.path.exists("data/training.jsonl"):
        print(" Error: data/training.jsonl not found.")
        print(" Run 'python scripts/extract_data.py' first!")
        return

    # Step 2: Upload the Training File
    print(" Uploading training data to OpenAI...")
    try:
        file_response = client.files.create(
            file=open("data/training.jsonl", "rb"),
            purpose="fine-tune"
        )
        file_id = file_response.id
        print(f" File uploaded! File ID: {file_id}")
    except Exception as e:
        print(f" Upload failed: {e}")
        return

    # Step 3: Start the Training Job
    print(" Starting Fine-Tuning Job on gpt-4o-mini...")
    print("(This might cost ~₹10-50 depending on data size)")
    
    try:
        job_response = client.fine_tuning.jobs.create(
            training_file=file_id,
            model="gpt-4o-mini-2024-07-18", # Explicit version is safer
            hyperparameters={
                "n_epochs": 3 # Standard for small datasets
            }
        )
        job_id = job_response.id
        
        print("\n" + "="*50)
        print(f" SUCCESS! Job started.")
        print(f" Job ID: {job_id}")
        print(f" Track it here: https://platform.openai.com/finetune/{job_id}")
        print("="*50 + "\n")
        print(" When it finishes, OpenAI will email you the 'New Model Name'.")
        print(" You will use that name in Phase 5 to update your Lambda.")
        
    except Exception as e:
        print(f" Failed to start training: {e}")

if __name__ == "__main__":
    start_finetuning()