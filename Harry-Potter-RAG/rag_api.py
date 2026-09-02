import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq


# ============================= Setup =============================

load_dotenv()

app = FastAPI(title="Harry Potter RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION")

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "intfloat/multilingual-e5-large",
)

GEMINI_MODEL = os.getenv("GEMINI_MODEL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GROQ_MODEL = os.getenv("GROQ_MODEL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

TOP_K = int(os.getenv("TOP_K", 3))

model = SentenceTransformer(EMBEDDING_MODEL)

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

gemini_llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    api_key=GEMINI_API_KEY,
    temperature=0,
)

groq_llm = ChatGroq(
    model=GROQ_MODEL,
    api_key=GROQ_API_KEY,
    temperature=0,
)


# =========================== Schemas ===========================

class QueryRequest(BaseModel):
    query: str


class Source(BaseModel):
    book_name: str
    page_number: int
    score: float


class QueryResponse(BaseModel):
    query: str
    route: str
    answer: str
    confidence: float
    sources: list[Source]


# =========================== Endpoints ===========================

@app.get("/")
def root():
    return {
        "name": "Harry Potter RAG API",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/query", response_model=QueryResponse)
def query_rag(request: QueryRequest):

    ROUTER_SYSTEM_PROMPT = """
You classify messages for a Harry Potter assistant.

Return exactly one word only:

retrieve - questions about Harry Potter books, characters, spells, locations, creatures, or events.

chitchat - greetings, thanks, introductions, and casual conversation.

off-topic - anything unrelated to Harry Potter books.

Return only:
retrieve
or
chitchat
or
off-topic
"""

    route = (
        groq_llm.invoke(
            [
                SystemMessage(content=ROUTER_SYSTEM_PROMPT),
                HumanMessage(content=request.query),
            ]
        )
        .content.strip()
        .lower()
    )

    if route not in {"retrieve", "chitchat", "off-topic"}:
        route = "off-topic"

    if route == "chitchat":

        CHITCHAT_SYSTEM_PROMPT = """
You are a friendly Harry Potter assistant.

Respond politely and briefly to greetings and casual conversation.

Keep answers short.
"""

        response = groq_llm.invoke(
            [
                SystemMessage(content=CHITCHAT_SYSTEM_PROMPT),
                HumanMessage(content=request.query),
            ]
        )

        return QueryResponse(
            query=request.query,
            route=route,
            answer=response.content,
            confidence=1.0,
            sources=[],
        )

    if route == "off-topic":
        return QueryResponse(
            query=request.query,
            route=route,
            answer="I can only answer questions about the Harry Potter books.",
            confidence=1.0,
            sources=[],
        )

    query_vector = model.encode(
        [f"query: {request.query}"],
        normalize_embeddings=True,
    )[0].tolist()

    results = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=query_vector,
        limit=TOP_K,
        with_payload=True
    ).points

    if not results:
       return QueryResponse(
           query=request.query,
           route=route,
           answer="I do not know.",
           confidence=0.0,
           sources=[]
        )
    
    context = "\n\n".join(
        f"Book: {result.payload['book_name']}\n"
        f"Page: {result.payload['page_number']}\n"
        f"Content: {result.payload['content']}"
        for result in results
    )

    RAG_SYSTEM_PROMPT = """
You are a Harry Potter books assistant.

You MUST answer only from the provided context.

Rules:
- Use only the retrieved pages.
- Never use outside knowledge.
- Never make assumptions.
- Never add facts that do not appear in the context.
- If the context does not contain enough information, reply exactly:
  I do not know.
- Cite the source page using this format:
  [Page X]
- Keep answers concise.
"""

    response = gemini_llm.invoke(
        [
            SystemMessage(content=RAG_SYSTEM_PROMPT),
            HumanMessage(
                content=f"Context:\n{context}\n\nQuestion:\n{request.query}"
            ),
        ]
    )

    answer_text = (
        response.text
        if hasattr(response, "text")
        else str(response.content)
    )

    return QueryResponse(
        query=request.query,
        route=route,
        answer=answer_text,
        confidence=float(results[0].score),
        sources=[
            Source(
                book_name=result.payload["book_name"],
                page_number=result.payload["page_number"],
                score=result.score,
            )
            for result in results
        ],
    )