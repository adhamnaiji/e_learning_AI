from qdrant_client import QdrantClient

def reset_collection():
    """Delete Qdrant collection to start fresh"""
    try:
        client = QdrantClient(url="http://localhost:6333")
        
        # Check and delete collection
        collections = client.get_collections().collections
        if any(col.name == "elearning_courses" for col in collections):
            client.delete_collection("elearning_courses")
            print("✅ Deleted collection 'elearning_courses'")
        else:
            print("ℹ️ Collection doesn't exist yet")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    reset_collection()
