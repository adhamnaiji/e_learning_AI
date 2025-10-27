from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
# Recommended migration (deprecation fix):
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
        
        # Store conversations
        self.conversations = {}
        
        # Custom prompt template for course-specific answers
        self.prompt_template = """You are an AI learning assistant helping students with a SPECIFIC course.

IMPORTANT INSTRUCTIONS:
1. Answer ONLY based on the course content provided in the context
2. DO NOT provide general information - be specific to THIS course
3. If the context contains course information, describe THAT SPECIFIC course
4. If asked about videos/lessons, list the actual lessons from THIS course
5. If you don't find the answer in the context, say: "I don't have that specific information about this course."

Course Context:
{context}

Chat History: {chat_history}

Student Question: {question}

Helpful Answer (specific to this course):"""

    def _initialize_llm(self):
        """Initialize LLM based on provider setting"""
        provider = self.settings.llm_provider.lower()
        
        if provider == "perplexity":
            logger.info(f"Initializing Perplexity LLM: {self.settings.llm_model}")
            return ChatPerplexity(
                model=self.settings.llm_model,
                temperature=0.2,
                pplx_api_key=self.settings.perplexity_api_key,
                max_tokens=1024
            )
        elif provider == "groq":
            logger.info(f"Initializing Groq LLM: {self.settings.llm_model}")
            return ChatGroq(
                model=self.settings.llm_model,
                groq_api_key=self.settings.groq_api_key,
                temperature=0.7
            )
        else:  # default to openai
            logger.info(f"Initializing OpenAI LLM: {self.settings.llm_model}")
            return ChatOpenAI(
                model=self.settings.llm_model,
                openai_api_key=self.settings.openai_api_key,
                temperature=0.7
            )

    def get_or_create_conversation(self, conversation_id: str = None):
        """Get existing conversation or create new one"""
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        if conversation_id not in self.conversations:
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
            self.conversations[conversation_id] = memory
        
        return conversation_id, self.conversations[conversation_id]

    async def chat(self, message: str, course_id: int = None,
                   conversation_id: str = None):
        """Chat with RAG system"""
        logger.info(f"Chat request - message: '{message}', course_id: {course_id}")
        
        # Get or create conversation
        conversation_id, memory = self.get_or_create_conversation(conversation_id)
        
        # Get vector store
        vector_store = Qdrant(
            client=self.embeddings_service.client,
            collection_name=self.settings.collection_name,
            embeddings=self.embeddings_service.embeddings
            # If you migrate to langchain_qdrant and store metadata under "metadata":
            # metadata_payload_key="metadata",
        )
        
        # Create retriever with course filter
        search_kwargs = {"k": self.settings.top_k_results}
        
        # Apply course filter if provided
        if course_id:
            # If your payload has course_id at root (default langchain_community behavior):
            filter_key = "course_id"
            # If your payload is nested under "metadata", switch to:
            # filter_key = "metadata.course_id"
            search_kwargs["filter"] = Filter(
                must=[
                    FieldCondition(
                        key=filter_key,
                        match=MatchValue(value=course_id)
                    )
                ]
            )
            logger.info(f"Applying filter for course_id: {course_id}")
        
        retriever = vector_store.as_retriever(
            search_kwargs=search_kwargs
        )
        
        # Test retrieval (optional - for debugging)
        try:
            test_docs = retriever.invoke(message)  # modern API
            logger.info(f"Retriever found {len(test_docs)} documents")
            if test_docs:
                logger.info(f"Sample doc metadata: {test_docs[0].metadata}")
                # logger.info(f"Sample content: {test_docs[0].page_content[:200]}")
            else:
                logger.warning("No documents found by retriever")
                logger.warning(f"Filter used: {search_kwargs.get('filter')}")
        except Exception as e:
            logger.error(f"Retriever test failed: {e}")
        
        # Create custom prompt
        QA_PROMPT = PromptTemplate(
            template=self.prompt_template,
            input_variables=["context", "chat_history", "question"]
        )
        
        # Create QA chain with custom prompt
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            verbose=True,
            combine_docs_chain_kwargs={"prompt": QA_PROMPT}
        )
        
        # Get response (migrate to invoke to remove deprecation warning)
        # result = qa_chain({"question": message})
        result = qa_chain.invoke({"question": message})
        
        # Extract sources
        sources = []
        source_docs = result.get('source_documents', [])
        logger.info(f"QA chain returned {len(source_docs)} source documents")
        
        for doc in source_docs:
            sources.append({
                'course_id': doc.metadata.get('course_id'),
                'title': doc.metadata.get('title'),
                'content': doc.page_content[:200] + '...'
            })
        
        return {
            'response': result['answer'],
            'sources': sources,
            'conversation_id': conversation_id
        }

    def clear_conversation(self, conversation_id: str):
        """Clear conversation history"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Cleared conversation: {conversation_id}")
