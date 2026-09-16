from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "CareerOS backend is running"
    }


@app.post("/jobs/analyze")
def analyze_job(data: dict):

    company = data.get("company")
    job_description = data.get("job_description")

    return {
        "message": f"Received job description for {company}"
    }