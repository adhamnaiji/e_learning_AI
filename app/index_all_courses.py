import requests
import json
import time
from typing import Dict, List, Any, Optional


# ============================================================================
# COURSES DATA
# ============================================================================

COURSES = [
    {
        "id": 1,
        "title": "Complete Angular Developer Course",
        "description": "Master Angular from scratch with hands-on projects and real-world applications",
        "instructor": "John Smith",
        "instructorId": 1,
        "category": "Web Development",
        "level": "Intermediate",
        "duration": "40 hours",
        "price": 89.99,
        "originalPrice": 149.99,
        "thumbnail": "assets/Angular.jpg",
        "rating": 4.8,
        "studentsEnrolled": 15420,
        "isFeatured": True,
        "tags": ["Angular", "TypeScript", "Web Development"],
        "whatYouLearn": [
            "Build complete Angular applications from scratch",
            "Master Angular components, directives, and services",
            "Work with RxJS and reactive programming",
            "Implement routing and authentication",
            "Deploy Angular apps to production"
        ],
        "requirements": [
            "Basic HTML, CSS, and JavaScript knowledge",
            "Understanding of programming concepts",
            "A computer with internet connection"
        ],
        "lessons": [
            {
                "id": 1,
                "title": "Introduction to Angular",
                "duration": "15:30",
                "videoUrl": "https://www.youtube.com/embed/3qBXWUpoPHo",
                "description": "Get started with Angular framework",
                "resources": [
                    {"id": 1, "title": "Angular Setup Guide", "type": "pdf", "url": "#"},
                    {"id": 2, "title": "Course Resources", "type": "article", "url": "#"}
                ]
            },
            {
                "id": 2,
                "title": "Components and Templates",
                "duration": "25:45",
                "videoUrl": "https://www.youtube.com/embed/3qBXWUpoPHo",
                "description": "Learn about Angular components",
                "resources": []
            },
            {
                "id": 3,
                "title": "Services and Dependency Injection",
                "duration": "30:20",
                "videoUrl": "https://www.youtube.com/embed/3qBXWUpoPHo",
                "description": "Understanding Angular services",
                "resources": []
            },
            {
                "id": 4,
                "title": "Routing and Navigation",
                "duration": "28:15",
                "videoUrl": "https://www.youtube.com/embed/3qBXWUpoPHo",
                "description": "Implement routing in Angular",
                "resources": []
            }
        ]
    },
    {
        "id": 2,
        "title": "React JS Masterclass",
        "description": "Learn React JS with Redux, Hooks, and modern best practices",
        "instructor": "Sarah Johnson",
        "instructorId": 2,
        "category": "Web Development",
        "level": "Beginner",
        "duration": "35 hours",
        "price": 79.99,
        "originalPrice": 129.99,
        "thumbnail": "assets/Reactjs.jpg",
        "rating": 4.7,
        "studentsEnrolled": 18200,
        "isFeatured": True,
        "tags": ["React", "JavaScript", "Frontend"],
        "whatYouLearn": [
            "Build modern React applications",
            "Master React Hooks and Context API",
            "State management with Redux",
            "Testing React components",
            "Performance optimization"
        ],
        "requirements": [
            "JavaScript fundamentals",
            "Basic understanding of HTML and CSS"
        ],
        "lessons": [
            {
                "id": 1,
                "title": "React Fundamentals",
                "duration": "20:00",
                "videoUrl": "https://www.youtube.com/embed/SqcY0GlETPk",
                "description": "Get started with React and learn the basics",
                "resources": [
                    {"id": 1, "title": "React Setup Guide", "type": "pdf", "url": "#"},
                    {"id": 2, "title": "Course Resources", "type": "article", "url": "#"}
                ]
            },
            {
                "id": 2,
                "title": "React Hooks Deep Dive",
                "duration": "30:00",
                "videoUrl": "https://www.youtube.com/embed/23AeJZg4mIE",
                "description": "Master useState, useEffect, and custom hooks",
                "resources": []
            }
        ]
    },
    {
        "id": 3,
        "title": "Python for Data Science",
        "description": "Master Python programming for data analysis and visualization",
        "instructor": "Michael Chen",
        "instructorId": 3,
        "category": "Data Science",
        "level": "Beginner",
        "duration": "45 hours",
        "price": 94.99,
        "originalPrice": 159.99,
        "thumbnail": "assets/python.jpg",
        "rating": 4.9,
        "studentsEnrolled": 22500,
        "isFeatured": True,
        "tags": ["Python", "Data Science", "Machine Learning"],
        "whatYouLearn": [
            "Python programming fundamentals",
            "Data analysis with Pandas and NumPy",
            "Data visualization with Matplotlib",
            "Machine learning basics with Scikit-learn",
            "Real-world data science projects"
        ],
        "requirements": [
            "No prior programming experience needed",
            "Basic mathematics knowledge"
        ],
        "lessons": [
            {
                "id": 1,
                "title": "Python Basics",
                "duration": "30:00",
                "videoUrl": "https://www.youtube.com/embed/3qBXWUpoPHo",
                "description": "Introduction to Python",
                "resources": []
            }
        ]
    },
    {
        "id": 4,
        "title": "Machine Learning A-Z",
        "description": "Complete hands-on machine learning tutorial with Python",
        "instructor": "Emma Davis",
        "instructorId": 4,
        "category": "Machine Learning",
        "level": "Advanced",
        "duration": "50 hours",
        "price": 99.99,
        "originalPrice": 159.99,
        "thumbnail": "assets/machine_learning.jpg",
        "rating": 4.8,
        "studentsEnrolled": 19800,
        "isFeatured": True,
        "tags": ["Machine Learning", "AI", "Python"],
        "whatYouLearn": [
            "Supervised and unsupervised learning",
            "Neural networks and deep learning",
            "Natural language processing",
            "Computer vision projects",
            "Model deployment"
        ],
        "requirements": [
            "Python programming experience",
            "Statistics and linear algebra basics"
        ],
        "lessons": [
            {
                "id": 1,
                "title": "ML Introduction",
                "duration": "25:00",
                "videoUrl": "https://www.youtube.com/embed/3qBXWUpoPHo",
                "description": "Getting started with ML",
                "resources": []
            }
        ]
    },
    {
        "id": 5,
        "title": "UI/UX Design Fundamentals",
        "description": "Learn professional UI/UX design principles and tools",
        "instructor": "David Wilson",
        "instructorId": 5,
        "category": "Design",
        "level": "Beginner",
        "duration": "30 hours",
        "price": 74.99,
        "originalPrice": 129.99,
        "thumbnail": "assets/UiUx.jpg",
        "rating": 4.6,
        "studentsEnrolled": 12300,
        "isFeatured": True,
        "tags": ["UI", "UX", "Design"],
        "whatYouLearn": [
            "Design thinking process",
            "User research and personas",
            "Wireframing and prototyping",
            "Figma and Adobe XD",
            "Portfolio projects"
        ],
        "requirements": [
            "No design experience needed",
            "Creative mindset"
        ],
        "lessons": [
            {
                "id": 1,
                "title": "Design Principles",
                "duration": "18:00",
                "videoUrl": "https://www.youtube.com/embed/3qBXWUpoPHo",
                "description": "Core design concepts",
                "resources": []
            }
        ]
    },
    {
        "id": 6,
        "title": "Mobile App Development with Flutter",
        "description": "Build beautiful native mobile apps with Flutter",
        "instructor": "Lisa Anderson",
        "instructorId": 6,
        "category": "Mobile Development",
        "level": "Intermediate",
        "duration": "38 hours",
        "price": 84.99,
        "originalPrice": 139.99,
        "thumbnail": "assets/Flutter.jpg",
        "rating": 4.7,
        "studentsEnrolled": 14500,
        "isFeatured": True,
        "tags": ["Flutter", "Dart", "Mobile"],
        "whatYouLearn": [
            "Flutter framework and Dart",
            "Building responsive UI",
            "State management",
            "Firebase integration",
            "Publishing to app stores"
        ],
        "requirements": [
            "Basic programming knowledge",
            "OOP concepts understanding"
        ],
        "lessons": [
            {
                "id": 1,
                "title": "Flutter Basics",
                "duration": "22:00",
                "videoUrl": "https://www.youtube.com/embed/3qBXWUpoPHo",
                "description": "Introduction to Flutter",
                "resources": []
            }
        ]
    }
]


API_URL = "http://localhost:8000/api"


def build_course_content(course: Dict[str, Any]) -> str:
    """Build rich, searchable content for each course"""
    content_parts = [
        "=== COURSE INFORMATION ===",
        f"Course ID: {course['id']}",
        f"Course Title: {course['title']}",
        f"Instructor: {course['instructor']}",
        f"Category: {course['category']}",
        f"Level: {course['level']}",
        f"Duration: {course.get('duration', 'N/A')}",
        "",
        "=== DESCRIPTION ===",
        course['description'],
        "",
        "=== WHAT YOU WILL LEARN ===",
    ]
    
    for i, item in enumerate(course.get('whatYouLearn', []), 1):
        content_parts.append(f"{i}. {item}")
    
    content_parts.extend([
        "",
        "=== REQUIREMENTS ===",
    ])
    
    for i, item in enumerate(course.get('requirements', []), 1):
        content_parts.append(f"{i}. {item}")
    
    content_parts.extend([
        "",
        "=== COURSE CONTENT - VIDEO LESSONS ===",
        f"This course contains {len(course.get('lessons', []))} video lessons:",
        ""
    ])
    
    for i, lesson in enumerate(course.get('lessons', []), 1):
        content_parts.extend([
            f"Lesson {i}: {lesson['title']}",
            f"Duration: {lesson['duration']}",
            f"Description: {lesson['description']}",
            ""
        ])
    
    return "\n".join(content_parts)


def index_course(course: Dict[str, Any]) -> Dict[str, Any]:
    """Index a single course to the RAG system"""
    content = build_course_content(course)
    
    data = {
        "course_id": course["id"],  # This goes to the top level
        "title": course["title"],
        "description": course["description"],
        "content": content,
        "instructor": course["instructor"],
        "category": course["category"],
        "level": course["level"]
    }
    
    try:
        response = requests.post(
            f"{API_URL}/index-course",
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return {"success": True, "course": course}
        else:
            return {"success": False, "course": course, "error": response.text}
    except Exception as e:
        return {"success": False, "course": course, "error": str(e)}


def main() -> None:
    print("=" * 80)
    print(" " * 20 + "🎓 E-LEARNING COURSE INDEXING SYSTEM 🎓")
    print("=" * 80)
    
    # Test backend connection
    print("\n📡 Testing backend connection...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and healthy!\n")
        else:
            print(f"❌ Backend returned unexpected status: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {str(e)}")
        print("\n🔧 Make sure backend is running:")
        print("   cd e_learning_AI")
        print("   uvicorn app.main:app --reload --port 8000")
        return
    
    print(f"📚 Preparing to index {len(COURSES)} courses...\n")
    print("=" * 80)
    
    success_count = 0
    fail_count = 0
    results = []
    
    start_time = time.time()
    
    for i, course in enumerate(COURSES, 1):
        print(f"\n[{i}/{len(COURSES)}] Processing: {course['title']}")
        print(f"    📋 ID: {course['id']}")
        print(f"    👨‍🏫 Instructor: {course['instructor']}")
        print(f"    📂 Category: {course['category']}")
        print(f"    📊 Level: {course['level']}")
        print(f"    🎥 Lessons: {len(course.get('lessons', []))}")
        print(f"    ⏱️  Indexing...", end=" ", flush=True)
        
        result = index_course(course)
        results.append(result)
        
        if result['success']:
            print("✅ SUCCESS")
            success_count += 1
        else:
            print("❌ FAILED")
            print(f"       Error: {result['error']}")
            fail_count += 1
        
        # Small delay between requests
        if i < len(COURSES):
            time.sleep(0.5)
    
    elapsed_time = time.time() - start_time
    
    # Summary
    print("\n" + "=" * 80)
    print(" " * 30 + "📊 INDEXING SUMMARY")
    print("=" * 80)
    print(f"\n✅ Successfully indexed: {success_count}/{len(COURSES)} courses")
    print(f"❌ Failed: {fail_count}/{len(COURSES)} courses")
    print(f"⏱️  Total time: {elapsed_time:.2f} seconds")
    
    if success_count > 0:
        print("\n" + "=" * 80)
        print("✨ SUCCESSFULLY INDEXED COURSES:")
        print("=" * 80)
        
        # Group by category
        categories: Dict[str, List[Dict[str, Any]]] = {}
        for result in results:
            if result['success']:
                cat = result['course']['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(result['course'])
        
        for category, courses in categories.items():
            print(f"\n📂 {category}:")
            for course in courses:
                print(f"   • {course['title']} (ID: {course['id']})")
        
        print("\n" + "=" * 80)
        print("🎉 READY TO USE!")
        print("=" * 80)
        print("\n💬 Your AI chat assistant can now answer questions about:")
        print(f"   • {success_count} different courses")
        print(f"   • {sum(len(r['course'].get('lessons', [])) for r in results if r['success'])} total lessons")
        print("\n🚀 Go to your Angular app and try asking:")
        print("   - 'What is this course about?'")
        print("   - 'What will I learn?'")
        print("   - 'Tell me about the lessons'")
        print("   - 'What are the requirements?'")
        print("   - 'Who is the instructor?'")
    
    if fail_count > 0:
        print("\n" + "=" * 80)
        print("⚠️  FAILED COURSES:")
        print("=" * 80)
        for result in results:
            if not result['success']:
                print(f"\n❌ {result['course']['title']} (ID: {result['course']['id']})")
                print(f"   Error: {result['error']}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
