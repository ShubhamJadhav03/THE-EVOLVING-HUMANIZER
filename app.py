from fastapi import FastAPI
from phase1.graph.workflow import rewrite

app = FastAPI()

@app.post("/rewrite")
def rewrite_api(payload: dict):
    text = payload["text"]
    result = rewrite(text)
    return {"rewritten_text": result}