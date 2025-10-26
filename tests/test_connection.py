import sys
sys.path.append('..')

from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os

load_dotenv()

def test_qdrant_connection():
    """Test connection to Qdrant Cloud"""
    print("🔍 Testing Qdrant connection...")
    
    try:
        client = QdrantClient(
            url=os.getenv('QDRANT_URL'),
            api_key=os.getenv('QDRANT_API_KEY')
        )
        
        collections = client.get_collections()
        print("✅ Successfully connected to Qdrant!")
        print(f"📦 Existing collections: {collections}")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to Qdrant: {str(e)}")
        return False

if __name__ == "__main__":
    test_qdrant_connection()
