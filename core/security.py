from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer

def secure_retrieve(query_text: str, user_role: str, top_k: int = 2):
    print(f"\n[Security Check] User Role: '{user_role}' querying: '{query_text}'")
    
    # Load embedding model and client
    model = SentenceTransformer('all-MiniLM-L6-v2')
    client = QdrantClient(path="./qdrant_storage")
    collection_name = "enterprise_docs"

    # Generate query embedding
    query_vector = model.encode(query_text).tolist()

    # CRITICAL: Metadata Pre-Filtering for RBAC
    # This ensures the database ONLY searches among chunks where 'allowed_roles' contains the user_role
    role_filter = Filter(
        must=[
            FieldCondition(
                key="allowed_roles",
                match=MatchValue(value=user_role)
            )
        ]
    )

    # Perform vector search with the security filter applied
    search_results = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        query_filter=role_filter,
        limit=top_k
    ).points

    # Extract text from results
    retrieved_chunks = [hit.payload["text"] for hit in search_results]
    print(f"[Retrieval Success] Found {len(retrieved_chunks)} permitted chunks.")
    return retrieved_chunks

# Quick test script if you run this file directly
if __name__ == "__main__":
    # Test 1: Intern tries to access executive info (Should return 0 results or cafeteria/onboarding)
    secure_retrieve("What are the executive compensation targets?", user_role="intern")
    
    # Test 2: Manager tries to access executive info (Should find it)
    secure_retrieve("What are the executive compensation targets?", user_role="manager")