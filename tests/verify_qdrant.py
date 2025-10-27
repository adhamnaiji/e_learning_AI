# test_qdrant_data.py
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os

load_dotenv()

client = QdrantClient(
    url=os.getenv('QDRANT_URL'),
    api_key=os.getenv('QDRANT_API_KEY')
)

# Get some points from the collection
result = client.scroll(
    collection_name="elearning_courses",
    limit=5,
    with_payload=True,
    with_vectors=False
)

print("📊 Sample documents from Qdrant:\n")
for point in result[0]:
    print(f"ID: {point.id}")
    print(f"Payload: {point.payload}")
    print("-" * 80)
