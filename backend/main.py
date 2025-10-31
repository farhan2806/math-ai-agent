from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import Optional
import uvicorn
import os
from dotenv import load_dotenv
from agents.math_agent import MathRoutingAgent
from knowledge_base.kb_manager import KnowledgeBaseManager

# Load environment variables from .env file
load_dotenv()

# Print for debugging (remove in production)
print(f"🔍 Debug - GROQ_API_KEY exists: {bool(os.getenv('GROQ_API_KEY'))}")
print(f"🔍 Debug - TAVILY_API_KEY exists: {bool(os.getenv('TAVILY_API_KEY'))}")


# Store feedback
feedback_store = []

# Initialize managers
kb_manager = KnowledgeBaseManager()
math_agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    global math_agent
    print("🚀 Starting Math Agent API...")
    kb_manager.load_and_index()
    math_agent = MathRoutingAgent()
    print("✅ Math Agent API Ready!")
    yield
    # Shutdown
    print("👋 Shutting down Math Agent API...")

app = FastAPI(
    title="Math Routing Agent API",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

class FeedbackRequest(BaseModel):
    question: str
    solution: str
    rating: int  # 1-5
    comments: Optional[str] = None

@app.post("/api/solve")
async def solve_math_problem(request: QueryRequest):
    """Main endpoint to solve math problems"""
    try:
        result = math_agent.route_query(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Human-in-the-loop feedback"""
    feedback_store.append(feedback.dict())
    
    if feedback.rating < 3:
        print(f"⚠️ Low rating for: {feedback.question}")
    
    return {"message": "Feedback received", "total_feedback": len(feedback_store)}

@app.get("/api/feedback/stats")
async def get_feedback_stats():
    """Get feedback statistics"""
    if not feedback_store:
        return {"average_rating": 0, "total_feedback": 0}
    
    avg_rating = sum(f['rating'] for f in feedback_store) / len(feedback_store)
    return {
        "average_rating": round(avg_rating, 2),
        "total_feedback": len(feedback_store),
        "feedback_breakdown": {
            "5_star": len([f for f in feedback_store if f['rating'] == 5]),
            "4_star": len([f for f in feedback_store if f['rating'] == 4]),
            "3_star": len([f for f in feedback_store if f['rating'] == 3]),
            "2_star": len([f for f in feedback_store if f['rating'] == 2]),
            "1_star": len([f for f in feedback_store if f['rating'] == 1]),
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "ready",
        "knowledge_base_size": kb_manager.collection.count(),
        "groq_configured": bool(os.getenv("GROQ_API_KEY")),
        "tavily_configured": bool(os.getenv("TAVILY_API_KEY"))
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Math Routing Agent API",
        "version": "1.0.0",
        "endpoints": {
            "solve": "/api/solve",
            "feedback": "/api/feedback",
            "stats": "/api/feedback/stats",
            "health": "/api/health"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)