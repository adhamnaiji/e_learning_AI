import sys
from pathlib import Path

# Ensure the project root (parent of the tests folder) is on sys.path
# so imports like `from app.config import ...` work regardless of CWD
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.config import get_settings
from app.embeddings_service import EmbeddingsService

def check_indexed_courses():
    settings = get_settings()
    embeddings_service = EmbeddingsService(settings)
    
    # Get all documents
    results = embeddings_service.client.scroll(
        collection_name=settings.collection_name,
        limit=100
    )
    
    print("📚 Indexed Courses:")
    print("=" * 50)
    
    courses = {}
    for record in results[0]:
        course_id = record.payload.get('course_id')
        title = record.payload.get('title')
        
        if course_id not in courses:
            courses[course_id] = title
    
    if not courses:
        print("❌ No courses indexed yet!")
        print("\nPlease run: node scripts/index-courses.js")
    else:
        for course_id, title in courses.items():
            print(f"✅ Course {course_id}: {title}")
        print(f"\nTotal: {len(courses)} courses")

if __name__ == "__main__":
    check_indexed_courses()
