from fastapi import FastAPI, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.models import SessionLocal, AuditLog, User, init_db
from core.security import secure_retrieve
from core.router_cache import check_semantic_cache, save_to_semantic_cache, cost_aware_model_router

app = FastAPI(
    title="Enterprise-Grade Secure RAG Engine",
    description="Multi-tenant RBAC RAG with Semantic Caching and Cost-Aware Model Routing",
    version="1.0.0"
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class QueryRequest(BaseModel):
    query: str

@app.on_event("startup")
def startup_event():
    init_db()
    print("FastAPI server started & database verified.")

@app.post("/chat")
def enterprise_rag_endpoint(
    request: QueryRequest, 
    x_user_role: str = Header(default="intern"), # Simulated user role header for testing
    db: Session = Depends(get_db)
):
    query_text = request.query
    user_id = 1  # Simulated user ID for logging

    print(f"\n--- Incoming Request ---")
    print(f"Query: '{query_text}' | Role: '{x_user_role}'")

    # Step 1: Check Semantic Cache (Role-Aware)
    cached_answer = check_semantic_cache(query_text, user_role=x_user_role)
    if cached_answer:
        # Log successful cache hit to audit trail
        audit = AuditLog(user_id=user_id, user_role=x_user_role, query_text=query_text, status="SUCCESS (CACHE HIT)")
        db.add(audit)
        db.commit()
        return {
            "source": "Semantic Cache",
            "cost_tier": "Free (0 tokens)",
            "answer": cached_answer
        }

    # Step 2: Secure Retrieval using RBAC Metadata Pre-Filtering
    retrieved_chunks = secure_retrieve(query_text, user_role=x_user_role)
    
    if not retrieved_chunks:
        # Log blocked/empty access
        audit = AuditLog(user_id=user_id, user_role=x_user_role, query_text=query_text, status="BLOCKED / NO PERMITTED DATA")
        db.add(audit)
        db.commit()
        raise HTTPException(
            status_code=403, 
            detail="Access Denied: You do not have the required security clearance to view information for this query."
        )

    # Step 3: Cost-Aware Model Routing
    model_name, cost_tier = cost_aware_model_router(query_text)

    # Step 4: Synthesize Final Answer (Simulated generation using retrieved context)
    context_str = "\n".join(retrieved_chunks)
    final_answer = f"Based on authorized internal documents for role '{x_user_role}': {context_str}"

    # Save to semantic cache for future requests (Role-Aware)
    save_to_semantic_cache(query_text, x_user_role, final_answer)

    # Step 5: Immutable Audit Logging
    audit = AuditLog(user_id=user_id, user_role=x_user_role, query_text=query_text, status="SUCCESS")
    db.add(audit)
    db.commit()

    return {
        "source": "Vector DB + LLM Pipeline",
        "routed_model": model_name,
        "cost_tier": cost_tier,
        "retrieved_context": retrieved_chunks,
        "answer": final_answer
    }