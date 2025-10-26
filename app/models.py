from pydantic import BaseModel
from typing import List, Optional

class CourseDocument(BaseModel):
    course_id: int
    title: str
    description: str
    content: str
    instructor: str
    category: str
    level: str

class ChatMessage(BaseModel):
    message: str
    course_id: Optional[int] = None
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[dict]
    conversation_id: str

class SearchQuery(BaseModel):
    query: str
    top_k: int = 5
    category: Optional[str] = None

class SearchResult(BaseModel):
    course_id: int
    title: str
    description: str
    relevance_score: float
