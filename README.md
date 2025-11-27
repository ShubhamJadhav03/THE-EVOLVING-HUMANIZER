# 🧬 The Evolving Humanizer

![Project Status](https://img.shields.io/badge/Status-Live-success)  ![AWS](https://img.shields.io/badge/Cloud-AWS%20Serverless-orange)  ![AI](https://img.shields.io/badge/AI-LangGraph%20%2B%20OpenAI-blue)  ![MLOps](https://img.shields.io/badge/MLOps-DVC%20%2B%20GitHub%20Actions-purple)

**A Self-Improving AI System that rewrites robotic text into natural human speech.**

Unlike standard wrappers, this system features a **Feedback Loop**.  
It learns from user preferences over time by capturing interaction data and automatically fine-tuning the underlying model to adapt to a user’s unique writing style.

---

## 🏛️ **Architecture**

This project implements an **Event-Driven, Asynchronous Architecture** to handle complex LLM workflows without hitting API Gateway timeouts.

### **High-Level Data Flow**

![system arch evolving humanizer](https://github.com/user-attachments/assets/7864cd18-d411-4a01-93f4-bbd027b750df)

1. **Frontend (React/Vite):** User submits text.  
2. **API Gateway + Lambda (Receptionist):** Accepts the request and issues a `job_id`.  
3. **DynamoDB (Job Queue):** Stores the job status (`QUEUED → PROCESSING → COMPLETED`).  
4. **Worker Lambda (The Brain):**  
   - Triggered asynchronously  
   - Runs a **LangGraph Multi-Agent workflow** (Draft → Critique → Refine)  
   - Updates DynamoDB with the rewritten output  
5. **MLOps Pipeline (The Teacher):**  
   - User clicks 👍 / 👎  
   - Feedback is stored in DynamoDB  
   - GitHub Actions triggers a DVC extraction pipeline  
   - The model is fine-tuned on OpenAI to improve future performance  

---

## 🛠️ **Tech Stack**

| Domain | Tools Used |
|--------|------------|
| **Frontend** | React, TypeScript, Tailwind CSS, Vite, Vercel |
| **Backend** | Python (FastAPI), AWS Lambda, Mangum |
| **AI / Agents** | LangGraph, OpenAI (GPT-4o-mini), Prompt Engineering |
| **Database** | Amazon DynamoDB (NoSQL) |
| **Infrastructure** | AWS SAM (Infrastructure-as-Code) |
| **MLOps** | DVC, GitHub Actions (CI/CD) |

---

## 🤖 **The Agentic Workflow**

The core logic is not a single prompt — it’s a **State Machine** orchestrated using LangGraph:

1. **✍️ Drafter Agent**  
   Creates the first version and removes “AI-isms” (e.g., *delve, tapestry, crucial*).  
2. **🧐 Critic Agent**  
   Evaluates the draft using strict stylistic rules and gives targeted feedback.  
3. **🔧 Refiner Agent**  
   Implements the feedback and rewrites the text.  
4. **🔁 Loop**  
   Repeats until the Critic is satisfied or a safety limit is reached.

---

## 🚀 **Getting Started (Local Development)**

### **Prerequisites**
- Node.js v20+  
- Python 3.10+  
- AWS CLI (configured)  
- AWS SAM CLI  

---

### **1. Backend Setup**

```bash
# Install Python dependencies
pip install -r requirements.txt

# Build and run the API locally
sam build
sam local start-api
```

---

### **2. Frontend Setup**

```bash
cd phase3
npm install
npm run dev
```

---

## 🔄 **MLOps Pipeline (Automated Training)**

This project treats **data as a first-class citizen**.

- **Feedback Collection:** Every 👍 in the UI is stored in the `HumanizerFeedback` table.  
- **Extraction:** A Python script pulls high-quality examples (`score = 1`).  
- **Versioning:** DVC tracks changes in `training.jsonl`.  
- **Automation:**  
  - GitHub Action (`data_pipeline.yml`) runs extraction  
  - Commits a new data snapshot automatically  
- **Training:**  
  - `train_model.py` triggers an OpenAI fine-tuning job  
  - Produces a custom model aligned with real user preferences  

---

## 🔮 **Future Roadmap**

- [ ] **Vector Search (RAG):** Retrieve past rewrites for style consistency  
- [ ] **User Accounts:** Personalize fine-tuned models per user  
- [ ] **A/B Testing:** Serve new models to 50% users to measure improvement  

---

## 👨‍💻 **Author**

**Shubham Jadhav**  
Connecting AI Agents with Real-World Engineering.
