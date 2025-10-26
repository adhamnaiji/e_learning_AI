from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType
from typing import List
import logging

logger = logging.getLogger(__name__)

class EmbeddingsService:
    def __init__(self, settings):
        self.settings = settings
        # Use HuggingFace embeddings instead of OpenAI
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={'device': 'cpu'},  # Use 'cuda' if you have GPU
            encode_kwargs={'normalize_embeddings': True}
        )
        
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key if settings.qdrant_api_key else None
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Create collection if it doesn't exist"""
        collections = self.client.get_collections().collections
        collection_names = [col.name for col in collections]
        
        if self.settings.collection_name not in collection_names:
            # Get embedding dimension
            sample_embedding = self.embeddings.embed_query("test")
            dimension = len(sample_embedding)
            
            self.client.create_collection(
                collection_name=self.settings.collection_name,
                vectors_config=VectorParams(
                    size=dimension,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {self.settings.collection_name}")
        
        # ALWAYS create payload indexes (moved outside the if block)
        try:
            # Index for course_id (integer)
            self.client.create_payload_index(
                collection_name=self.settings.collection_name,
                field_name="course_id",
                field_schema=PayloadSchemaType.INTEGER
            )
            logger.info("Created index for course_id")
        except Exception as e:
            # Index might already exist - that's fine
            logger.debug(f"Index creation skipped (may already exist): {e}")
    
    def index_course(self, course_data: dict):
        """Index a course into the vector database"""
        # Combine course information
        content = f"""
        Title: {course_data['title']}
        Instructor: {course_data['instructor']}
        Category: {course_data['category']}
        Level: {course_data['level']}
        Description: {course_data['description']}
        
        What You'll Learn:
        {' '.join(course_data.get('whatYouLearn', []))}
        
        Requirements:
        {' '.join(course_data.get('requirements', []))}
        
        Lessons:
        {' '.join([f"{lesson['title']}: {lesson['description']}" 
                   for lesson in course_data.get('lessons', [])])}
        """
        
        # Split into chunks
        chunks = self.text_splitter.split_text(content)
        
        # Create vector store
        vector_store = Qdrant(
            client=self.client,
            collection_name=self.settings.collection_name,
            embeddings=self.embeddings
        )
        
        # Add documents with metadata
        metadatas = [{
            'course_id': course_data['id'],
            'title': course_data['title'],
            'category': course_data['category'],
            'level': course_data['level'],
            'instructor': course_data['instructor'],
            'chunk_index': i
        } for i in range(len(chunks))]
        
        vector_store.add_texts(
            texts=chunks,
            metadatas=metadatas
        )
        
        logger.info(f"Indexed course: {course_data['title']} with {len(chunks)} chunks")
    
    def search_similar(self, query: str, top_k: int = 5, filter_category: str = None):
        """Search for similar courses"""
        vector_store = Qdrant(
            client=self.client,
            collection_name=self.settings.collection_name,
            embeddings=self.embeddings
        )
        
        # Build filter if category specified
        search_kwargs = {"k": top_k}
        if filter_category:
            search_kwargs["filter"] = {"category": filter_category}
        
        results = vector_store.similarity_search_with_score(
            query=query,
            **search_kwargs
        )
        
        return results
