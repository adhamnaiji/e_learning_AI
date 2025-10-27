from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List
import logging

from .config import get_settings
from .models import ChatMessage, ChatResponse, SearchQuery, SearchResult, CourseDocument
from .embeddings_service import EmbeddingsService
from .rag_service import RAGService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
embeddings_service = None
rag_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global embeddings_service, rag_service
    settings = get_settings()
    
    logger.info("Initializing services...")
    embeddings_service = EmbeddingsService(settings)
    rag_service = RAGService(settings, embeddings_service)
    logger.info("Services initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="E-Learning RAG API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - FIXED for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "http://localhost:8000",
        "*"  # Allow all during development - remove in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "E-Learning RAG API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "API is working"}

@app.post("/api/index-course")
async def index_course(course: CourseDocument):
    """Index a course for RAG retrieval"""
    try:
        embeddings_service.index_course(course.dict())
        return {"message": f"Course '{course.title}' indexed successfully"}
    except Exception as e:
        logger.error(f"Error indexing course: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Chat with the RAG assistant"""
    try:
        logger.info(f"Received chat message: {message.message}")
        result = await rag_service.chat(
            message=message.message,
            course_id=message.course_id,
            conversation_id=message.conversation_id
        )
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search", response_model=List[SearchResult])
async def search_courses(query: SearchQuery):
    """Semantic search for courses"""
    try:
        results = embeddings_service.search_similar(
            query=query.query,
            top_k=query.top_k,
            filter_category=query.category
        )
        
        search_results = []
        seen_courses = set()
        
        for doc, score in results:
            course_id = doc.metadata['course_id']
            if course_id not in seen_courses:
                search_results.append(SearchResult(
                    course_id=course_id,
                    title=doc.metadata['title'],
                    description=doc.page_content[:200],
                    relevance_score=float(score)
                ))
                seen_courses.add(course_id)
        
        return search_results
    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/conversation/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """Clear conversation history"""
    try:
        rag_service.clear_conversation(conversation_id)
        return {"message": "Conversation cleared"}
    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(app, host="0.0.0.0", port=settings.backend_port)
