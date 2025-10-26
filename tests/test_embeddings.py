import sys
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
import os

sys.path.append('..')

load_dotenv()


def test_embeddings():
    """Test HuggingFace embeddings"""
    print("🔍 Testing HuggingFace embeddings...")
    
    try:
        # HuggingFace embeddings run locally - no API key needed
        embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5"
        )
        
        # Test embedding
        test_text = "This is a test course about Python programming"
        embedding = embeddings.embed_query(test_text)
        
        print(f"✅ Successfully created embedding!")
        print(f"📊 Embedding dimension: {len(embedding)}")
        print(f"🔢 First 5 values: {embedding[:5]}")
        return True
    except Exception as e:
        print(f"❌ Failed to create embedding: {str(e)}")
        return False


if __name__ == "__main__":
    test_embeddings()
