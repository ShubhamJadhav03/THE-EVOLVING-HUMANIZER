from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import BaseModel
from phase1.graph.workflow import rewrite

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequestBody(BaseModel):
    text: str

@app.post("/rewrite")
def rewrite_api(payload: RequestBody):
    try:
        # Call the Agent!
        result = rewrite(payload.text)
        return {"rewritten_text": result}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

handler = Mangum(app)