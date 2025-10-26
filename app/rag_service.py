from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
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
        
        # Custom prompt template
        self.prompt_template = """You are an AI learning assistant for an e-learning platform.
        Your role is to help students understand course content and answer their questions.
        Use the following context from our courses to answer the question.
        If you don't know the answer based on the context, say so honestly.
        Always be encouraging and supportive in your responses.
        
        Context: {context}
        
        Chat History: {chat_history}
        
        Student Question: {question}
        
        Helpful Answer:"""
    
    def _initialize_llm(self):
        """Initialize LLM based on provider setting"""
        provider = self.settings.llm_provider.lower()
        
        if provider == "perplexity":
            logger.info("Initializing Perplexity LLM")
            return ChatPerplexity(
                model=self.settings.llm_model,
                temperature=0.2,
                pplx_api_key=self.settings.perplexity_api_key,
                max_tokens=1024
            )
        elif provider == "groq":
            logger.info("Initializing Groq LLM")
            return ChatGroq(
                model=self.settings.llm_model,
                groq_api_key=self.settings.groq_api_key,
                temperature=0.7
            )
        else:  # default to openai
            logger.info("Initializing OpenAI LLM")
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
        # Get or create conversation
        conversation_id, memory = self.get_or_create_conversation(conversation_id)
        
        # Get vector store
        vector_store = Qdrant(
            client=self.embeddings_service.client,
            collection_name=self.settings.collection_name,
            embeddings=self.embeddings_service.embeddings
        )
        
        # Create retriever with optional course filter
        search_kwargs = {"k": self.settings.top_k_results}
        if course_id:
            # Use proper Qdrant filter format
            search_kwargs["filter"] = Filter(
                must=[
                    FieldCondition(
                        key="course_id",
                        match=MatchValue(value=course_id)
                    )
                ]
            )
        
        retriever = vector_store.as_retriever(
            search_kwargs=search_kwargs
        )
        
        # Create QA chain
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            verbose=True
        )
        
        # Get response
        result = qa_chain({"question": message})
        
        # Extract sources
        sources = []
        for doc in result.get('source_documents', []):
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
