import time
from sentence_transformers import SentenceTransformer, util

# Cache stores entries with user_role
SEMANTIC_CACHE = []
SIMILARITY_THRESHOLD = 0.85

def check_semantic_cache(query_text: str, user_role: str):
    if not SEMANTIC_CACHE:
        return None
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_vector = model.encode(query_text)

    for item in SEMANTIC_CACHE:
        # ONLY match if the user role matches the cached response's role
        if item["user_role"] == user_role:
            similarity = util.cos_sim(query_vector, item["vector"])[0][0].item()
            if similarity >= SIMILARITY_THRESHOLD:
                print(f"[Cache HIT] Found cached query for role '{user_role}' ({similarity:.2f} similarity).")
                return item["answer"]
            
    print(f"[Cache MISS] Querying LLM pipeline for role '{user_role}'...")
    return None

def save_to_semantic_cache(query_text: str, user_role: str, answer: str):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_vector = model.encode(query_text)
    SEMANTIC_CACHE.append({
        "vector": query_vector,
        "user_role": user_role,
        "answer": answer,
        "timestamp": time.time()
    })

def cost_aware_model_router(query_text: str):
    word_count = len(query_text.split())
    if word_count < 6 or "menu" in query_text.lower() or "how to" in query_text.lower():
        selected_model = "Llama-3-8B (Cheap & Fast Local Model)"
        tier = "Low Cost"
    else:
        selected_model = "GPT-4 / Claude-3.5 (Advanced Enterprise Model)"
        tier = "High Cost"
        
    print(f"[Model Router] Query length: {word_count} words -> Routed to: {selected_model}")
    return selected_model, tier