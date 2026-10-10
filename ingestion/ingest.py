import os
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer

def run_ingestion():
    print("Loading embedding model...")
    # Using a lightweight, high-performing local embedding model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    print("Initializing local Qdrant client...")
    # This creates a local folder named 'qdrant_storage' to save vectors persistently
    client = QdrantClient(path="./qdrant_storage")

    collection_name = "enterprise_docs"

    # Re-create collection if it already exists
    if client.collection_exists(collection_name):
        client.delete_collection(collection_name)
    
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )

    # Sample internal company documents with explicit security metadata tags
    documents = [
        {
            "id": 1,
            "text": "Company cafeteria menu for this week: Monday is pasta, Tuesday is tacos.",
            "allowed_roles": ["intern", "engineer", "manager"]  # Public to everyone
        },
        {
            "id": 2,
            "text": "Standard onboarding guide: How to set up your corporate email and VPN.",
            "allowed_roles": ["intern", "engineer", "manager"]  # Public to everyone
        },
        {
            "id": 3,
            "text": "Q3 Engineering architecture plan for migrating backend microservices to Kubernetes.",
            "allowed_roles": ["engineer", "manager"]  # Restricted to engineers and above
        },
        {
            "id": 4,
            "text": "Executive compensation report and Q4 strategic acquisition targets.",
            "allowed_roles": ["manager"]  # Strictly managers only!
        }
    ]

    print("Generating embeddings and uploading to Qdrant with security tags...")
    points = []
    for doc in documents:
        # Generate vector embedding for the text chunk
        vector = model.encode(doc["text"]).tolist()
        
        # Construct point with payload containing the security metadata filter
        points.append(
            PointStruct(
                id=doc["id"],
                vector=vector,
                payload={
                    "text": doc["text"],
                    "allowed_roles": doc["allowed_roles"]
                }
            )
        )

    client.upsert(
        collection_name=collection_name,
        points=points
    )
    print("Ingestion complete! Documents stored securely with RBAC metadata.")

if __name__ == "__main__":
    run_ingestion()