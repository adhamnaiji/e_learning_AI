import requests
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os
import time
import sys

load_dotenv()

QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
COLLECTION_NAME = 'elearning_courses'
API_URL = "http://localhost:8000/api"


def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def delete_collection():
    """Delete the old collection"""
    print("🗑️  Deleting old collection...")
    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        client.delete_collection(COLLECTION_NAME)
        print("✅ Old collection deleted\n")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"⚠️  Collection may not exist: {e}\n")
        return False


def recreate_collection():
    """Manually recreate the collection"""
    print("🔧 Recreating collection...")
    try:
        from qdrant_client.models import Distance, VectorParams, PayloadSchemaType
        
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        
        # Create collection
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=384,  # bge-small-en-v1.5 dimension
                distance=Distance.COSINE,
            ),
        )
        print(f"✅ Created collection: {COLLECTION_NAME}")
        
        # Create indexes
        try:
            client.create_payload_index(
                collection_name=COLLECTION_NAME,
                field_name="course_id",
                field_schema=PayloadSchemaType.INTEGER,
            )
            print("✅ Created index for course_id")
        except Exception as e:
            print(f"⚠️  Index course_id: {e}")
        
        try:
            client.create_payload_index(
                collection_name=COLLECTION_NAME,
                field_name="metadata.course_id",
                field_schema=PayloadSchemaType.INTEGER,
            )
            print("✅ Created index for metadata.course_id\n")
        except Exception as e:
            print(f"⚠️  Index metadata.course_id: {e}\n")
        
        return True
    except Exception as e:
        print(f"❌ Failed to recreate collection: {e}\n")
        return False


def reindex_courses():
    """Re-index all courses"""
    print("📚 Re-indexing all courses...\n")
    
    # Import from your indexing script
    try:
        from index_all_courses import COURSES, index_course
    except ImportError:
        print("❌ Cannot import index_all_courses.py")
        print("   Make sure the file exists in the same directory\n")
        return False
    
    success = 0
    failed = 0
    
    for i, course in enumerate(COURSES, 1):
        print(f"[{i}/{len(COURSES)}] {course['title']}...", end=" ", flush=True)
        
        result = index_course(course)
        
        if result['success']:
            print("✅")
            success += 1
        else:
            print(f"❌")
            print(f"   Error: {result['error']}")
            failed += 1
        
        time.sleep(0.5)
    
    print(f"\n✅ Successfully indexed: {success}/{len(COURSES)} courses")
    if failed > 0:
        print(f"❌ Failed: {failed}/{len(COURSES)} courses")
    
    return success > 0


if __name__ == "__main__":
    print("=" * 70)
    print("🔄 RESET AND RE-INDEX SYSTEM")
    print("=" * 70)
    print("\n⚠️  This will DELETE all existing data and re-index from scratch")
    
    try:
        input("Press Enter to continue or Ctrl+C to cancel...\n")
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(0)
    
    # Step 1: Check backend
    print("\n📡 Checking backend status...")
    if not check_backend():
        print("❌ Backend is not running!")
        print("\n🔧 Start the backend first:")
        print("   cd e_learning_AI")
        print("   uvicorn app.main:app --reload --port 8000\n")
        sys.exit(1)
    else:
        print("✅ Backend is running\n")
    
    # Step 2: Delete collection
    delete_collection()
    
    # Step 3: Recreate collection manually
    if not recreate_collection():
        print("❌ Failed to recreate collection")
        print("\n🔧 Try restarting the backend:")
        print("   1. Stop the backend (Ctrl+C)")
        print("   2. Start it again: uvicorn app.main:app --reload --port 8000")
        print("   3. Run this script again\n")
        sys.exit(1)
    
    # Step 4: Re-index
    time.sleep(2)
    if reindex_courses():
        print("\n" + "=" * 70)
        print("✅ RESET COMPLETE!")
        print("=" * 70)
        print("\n🚀 Your system is ready to use!")
        print("   Test with: python scripts/test_all_courses.py")
    else:
        print("\n" + "=" * 70)
        print("⚠️  RESET INCOMPLETE")
        print("=" * 70)
        print("\n❌ Some or all courses failed to index")
        print("   Check the errors above and try again\n")
        sys.exit(1)
