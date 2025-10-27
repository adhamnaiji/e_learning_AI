import sys
from pathlib import Path

# Ensure the project root (parent of the tests folder) is on sys.path so
# imports like `from app.config import ...` work regardless of current CWD.
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.config import get_settings
from app.embeddings_service import EmbeddingsService
from app.rag_service import RAGService
import asyncio

async def test_full_system():
    """Test the complete RAG system"""
    print("=" * 60)
    print("🚀 TESTING COMPLETE RAG SYSTEM")
    print("=" * 60)
    
    settings = get_settings()
    
    # Initialize services
    print("\n📦 Initializing services...")
    embeddings_service = EmbeddingsService(settings)
    rag_service = RAGService(settings, embeddings_service)
    print("✅ Services initialized!")
    
    # Test course data
    test_course = {
        'id': 999,
        'title': 'Test Python Course',
        'description': 'Learn Python programming from scratch',
        'instructor': 'John Doe',
        'category': 'Programming',
        'level': 'Beginner',
        'whatYouLearn': [
            'Python basics and syntax',
            'Data structures and algorithms',
            'Object-oriented programming'
        ],
        'requirements': [
            'No prior programming experience needed',
            'A computer with internet connection'
        ],
        'lessons': [
            {
                'title': 'Introduction to Python',
                'description': 'Learn Python basics and setup'
            },
            {
                'title': 'Variables and Data Types',
                'description': 'Understanding Python data types'
            }
        ]
    }
    
    # Test 1: Index a course
    print("\n" + "=" * 60)
    print("TEST 1: Indexing Course")
    print("=" * 60)
    
    try:
        embeddings_service.index_course(test_course)
        print("✅ Course indexed successfully!")
    except Exception as e:
        print(f"❌ Indexing failed: {str(e)}")
        return
    
    # Wait a moment for indexing to complete
    await asyncio.sleep(2)
    
    # Test 2: Search for similar courses
    print("\n" + "=" * 60)
    print("TEST 2: Semantic Search")
    print("=" * 60)
    
    try:
        search_query = "I want to learn programming for beginners"
        print(f"🔍 Query: {search_query}")
        
        results = embeddings_service.search_similar(search_query, top_k=3)
        print(f"\n📊 Found {len(results)} results:")
        
        for i, (doc, score) in enumerate(results, 1):
            print(f"\n{i}. Score: {score:.4f}")
            print(f"   Title: {doc.metadata.get('title')}")
            print(f"   Content: {doc.page_content[:100]}...")
        
        print("\n✅ Search completed successfully!")
    except Exception as e:
        print(f"❌ Search failed: {str(e)}")
    
    # Test 3: Chat with RAG
    print("\n" + "=" * 60)
    print("TEST 3: RAG Chat")
    print("=" * 60)
    
    try:
        question = "What will I learn in the Python course?"
        print(f"💬 Question: {question}")
        
        result = await rag_service.chat(
            message=question,
            course_id=999
        )
        
        print(f"\n🤖 Answer: {result['response']}")
        print(f"\n📚 Sources used: {len(result['sources'])}")
        for i, source in enumerate(result['sources'], 1):
            print(f"   {i}. {source['title']}")
        
        print("\n✅ Chat completed successfully!")
    except Exception as e:
        print(f"❌ Chat failed: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_full_system())
