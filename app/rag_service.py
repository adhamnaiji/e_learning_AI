from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

# Optional (recommended) migrations to remove deprecations:
# from langchain_perplexity import ChatPerplexity
# from langchain_qdrant import Qdrant

from langchain_community.chat_models import ChatPerplexity
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import Qdrant
from langchain.prompts import PromptTemplate
from qdrant_client.models import Filter, FieldCondition, MatchValue

import uuid
import logging

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self, settings, embeddings_service):
        self.settings = settings
        self.embeddings_service = embeddings_service

        # Initialize LLM based on provider
        self.llm = self._initialize_llm()

        # Store conversations (memory per conversation id)
        self.conversations = {}

        # Course-grounded prompt - FIXED INDENTATION
        self.prompt_template = """You are a course assistant. Answer the student's question using ONLY the course materials below.

STRICT RULES:
1. Answer the exact question asked - nothing more
2. Do NOT include course metadata (instructor, duration, level) unless specifically asked
3. Be concise - maximum 100 words unless listing items
4. If listing lessons/topics, use bullet points with NO extra description
5. If you cannot answer from the context, say: "That information isn't in the course materials."

Course Materials:
{context}

Chat History: {chat_history}

Question: {question}

Answer:"""

    def _initialize_llm(self):
        """Initialize LLM based on provider setting"""
        provider = self.settings.llm_provider.lower()

        if provider == "perplexity":
            logger.info(f"Initializing Perplexity LLM: {self.settings.llm_model}")
            return ChatPerplexity(
                model=self.settings.llm_model,
                temperature=0.0,  # Changed from 0.2
                pplx_api_key=self.settings.perplexity_api_key,
                max_tokens=150,  # Reduced from 512 for conciseness
            )
        elif provider == "groq":
            logger.info(f"Initializing Groq LLM: {self.settings.llm_model}")
            return ChatGroq(
                model=self.settings.llm_model,
                groq_api_key=self.settings.groq_api_key,
                temperature=0.0,  # Changed from 0.7
            )
        else:  # default to openai
            logger.info(f"Initializing OpenAI LLM: {self.settings.llm_model}")
            return ChatOpenAI(
                model=self.settings.llm_model,
                openai_api_key=self.settings.openai_api_key,
                temperature=0.0,  # Changed from 0.7
            )

    def get_or_create_conversation(self, conversation_id: str = None):
        """Get existing conversation or create new one"""
        if not conversation_id:
            conversation_id = str(uuid.uuid4())

        if conversation_id not in self.conversations:
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer",
            )
            self.conversations[conversation_id] = memory

        return conversation_id, self.conversations[conversation_id]

    async def chat(
        self,
        message: str,
        course_id: int = None,
        conversation_id: str = None,
    ):
        """Chat with RAG system"""
        logger.info(
            f"Chat request - message: '{message}', course_id: {course_id}"
        )

        # Get or create conversation memory
        conversation_id, memory = self.get_or_create_conversation(conversation_id)

        # Vector store
        vector_store = Qdrant(
            client=self.embeddings_service.client,
            collection_name=self.settings.collection_name,
            embeddings=self.embeddings_service.embeddings,
        )

        # Build retriever and filter
        search_kwargs = {"k": self.settings.top_k_results}

        if course_id:
            # use nested metadata path
            filter_key = "metadata.course_id"
            search_kwargs["filter"] = Filter(
                must=[
                    FieldCondition(
                        key=filter_key,
                        match=MatchValue(value=course_id),
                    )
                ]
            )
            logger.info(f"Applying filter for course_id: {course_id} on key '{filter_key}'")

        retriever = vector_store.as_retriever(search_kwargs=search_kwargs)

        # DEBUG: test retrieval before running the chain
        try:
            test_docs = retriever.invoke(message)
            logger.info(f"Retriever found {len(test_docs)} documents")
            if test_docs:
                logger.info(f"Sample doc metadata: {test_docs[0].metadata}")
            else:
                logger.warning("No documents found by retriever")
                logger.warning(f"Filter used: {search_kwargs.get('filter')}")
        except Exception as e:
            logger.error(f"Retriever test failed: {e}")

        # Custom prompt
        QA_PROMPT = PromptTemplate(
            template=self.prompt_template,
            input_variables=["context", "chat_history", "question"],
        )

        # Chain with custom prompt
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            verbose=True,
            combine_docs_chain_kwargs={"prompt": QA_PROMPT},
        )

        # Use invoke (removes deprecation warning)
        result = qa_chain.invoke({"question": message})

        # Extract sources
        sources = []
        source_docs = result.get("source_documents", [])
        logger.info(f"QA chain returned {len(source_docs)} source documents")

        for doc in source_docs:
            sources.append(
                {
                    "course_id": doc.metadata.get("course_id"),
                    "title": doc.metadata.get("title"),
                    "content": (doc.page_content[:200] + "...")
                    if doc.page_content
                    else "",
                }
            )

        return {
            "response": result["answer"],
            "sources": sources,
            "conversation_id": conversation_id,
        }

    def clear_conversation(self, conversation_id: str):
        """Clear conversation history"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Cleared conversation: {conversation_id}")
