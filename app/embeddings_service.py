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

        # Use HuggingFace embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        self.client = QdrantClient(
            url=self.settings.qdrant_url,
            api_key=self.settings.qdrant_api_key if self.settings.qdrant_api_key else None
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        collections = self.client.get_collections().collections
        existing_names = [c.name for c in collections]

        if self.settings.collection_name not in existing_names:
            self.client.recreate_collection(
                collection_name=self.settings.collection_name,
                vectors_config=VectorParams(
                    size=384,  # bge-small-en-v1.5 dim
                    distance=Distance.COSINE,
                ),
            )
            logger.info(f"Created collection: {self.settings.collection_name}")

        # Existing index for course_id at root (keep if you also filter on root)
        try:
            self.client.create_payload_index(
                collection_name=self.settings.collection_name,
                field_name="course_id",
                field_schema=PayloadSchemaType.INTEGER,
            )
            logger.info("Created index for course_id")
        except Exception as e:
            logger.debug(f"Index course_id may already exist: {e}")

        # NEW: index for nested metadata.course_id
        try:
            self.client.create_payload_index(
                collection_name=self.settings.collection_name,
                field_name="metadata.course_id",
                field_schema=PayloadSchemaType.INTEGER,
            )
            logger.info("Created index for metadata.course_id")
        except Exception as e:
            logger.debug(f"Index metadata.course_id may already exist: {e}")

    def _split_course_to_docs(self, course: dict) -> List:
        parts = []

        title = course.get("title", "")
        instructor = course.get("instructor", "")
        category = course.get("category", "")
        level = course.get("level", "")
        description = course.get("description", "")

        header = f"Title: {title}\nInstructor: {instructor}\nCategory: {category}\nLevel: {level}\nDescription: {description}\n"
        parts.append(header)

        what = course.get("whatYouLearn", [])
        if what:
            parts.append("What you will learn:\n" + "\n".join(f"- {w}" for w in what))

        reqs = course.get("requirements", [])
        if reqs:
            parts.append("Requirements:\n" + "\n".join(f"- {r}" for r in reqs))

        lessons = course.get("lessons", [])
        if lessons:
            lessons_text = []
            for l in lessons:
                lessons_text.append(f"- {l.get('title', '')}: {l.get('description', '')}")
            parts.append("Lessons:\n" + "\n".join(lessons_text))

        text = "\n\n".join(p for p in parts if p.strip())
        chunks = self.text_splitter.split_text(text)

        from langchain.schema import Document
        docs = []
        for chunk in chunks:
            docs.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "course_id": course.get("id"),
                        "title": course.get("title"),
                        "category": course.get("category"),
                        "level": course.get("level"),
                        "instructor": course.get("instructor"),
                    },
                )
            )
        return docs

    def index_course(self, course: dict):
        docs = self._split_course_to_docs(course)

        vector_store = Qdrant(
            client=self.client,
            collection_name=self.settings.collection_name,
            embeddings=self.embeddings,
        )

        vector_store.add_documents(docs)
        logger.info(f"Indexed course: {course.get('title')} with {len(docs)} chunks")

    def search_similar(self, query: str, top_k: int = 3):
        vector_store = Qdrant(
            client=self.client,
            collection_name=self.settings.collection_name,
            embeddings=self.embeddings,
        )
        docs_and_scores = vector_store.similarity_search_with_score(query, k=top_k)
        return docs_and_scores
