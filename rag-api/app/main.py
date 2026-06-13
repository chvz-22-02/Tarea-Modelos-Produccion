"""
app/main.py — FastAPI demo para el curso GenAI Multimodal
Instructor: Rodrigo López Vera | Revolut Perú

Endpoints:
  GET  /           — health check (modelos activos + doc counts)
  POST /ingest     — recibe documento (texto o imagen), lo indexa en ChromaDB
  POST /query      — pregunta + imagen opcional → RAGResponse (multipart)
  POST /query/json — pregunta en JSON puro → RAGResponse (sin imagen)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CÓMO PROBAR — GUÍA 
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PASO 1 — Levanta la API
  export GOOGLE_API_KEY="AIza..."
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

PASO 2 — Ingesta documentos (necesario antes del primer query)
-- Referir a taller pasado o:

  # Texto: circular SBS
  curl -X POST http://localhost:8000/ingest \\
       -F "file=@data/circulares_sbs/circular_B_2244_2024.md" \\
       -F "source_id=circular_B_2244_2024" \\
       -F "date=2024-03" \\
       -F "doc_type=text"

  # Imagen: voucher de pago
  curl -X POST http://localhost:8000/ingest \\
       -F "file=@data/images/voucher_yape_001.png" \\
       -F "source_id=voucher_yape_001" \\
       -F "date=2024-06" \\
       -F "doc_type=image"

PASO 3 — Consultas

  # Query simple (JSON)
  curl -X POST http://localhost:8000/query/json \\
       -H "Content-Type: application/json" \\
       -d '{"question": "¿Qué es una operación sospechosa?"}'

  # Query con filtro de fecha
  curl -X POST http://localhost:8000/query/json \\
       -H "Content-Type: application/json" \\
       -d '{"question": "Obligaciones del oficial de cumplimiento", "date_filter": "2024-01", "n_results": 5}'

  # Query multimodal (pregunta + voucher)
  curl -X POST http://localhost:8000/query \\
       -F "question=¿Esta transferencia requiere reporte a la UIF?" \\
       -F "image=@data/images/voucher_bbva_internacional_003.png"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CÓMO PROBAR DESDE PYTHON / GOOGLE COLAB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  import httpx

  BASE = "http://localhost:8000"   

  # 1. Health check
  print(httpx.get(f"{BASE}/").json())

  # 2. Ingestar circular SBS
  with open("data/circulares_sbs/circular_B_2244_2024.md", "rb") as f:
      r = httpx.post(f"{BASE}/ingest",
                     files={"file": f},
                     data={"source_id": "circular_B_2244_2024",
                           "date": "2024-03", "doc_type": "text"})
  print(r.json())  # {"status": "ok", "chunks_indexed": N, "collection": "circulares_sbs"}

  # 3. Ingestar voucher
  with open("data/images/voucher_yape_001.png", "rb") as f:
      r = httpx.post(f"{BASE}/ingest",
                     files={"file": f},
                     data={"source_id": "voucher_yape_001",
                           "date": "2024-06", "doc_type": "image"})
  print(r.json())  # {"status": "ok", "chunks_indexed": 1, "collection": "vouchers_financieros"}

  # 4. Query solo texto
  r = httpx.post(f"{BASE}/query/json",
                 json={"question": "¿Cuál es el umbral para reportar operaciones sospechosas?"})
  print(r.json())

  # 5. Query multimodal
  with open("data/images/voucher_bbva_internacional_003.png", "rb") as f:
      r = httpx.post(f"{BASE}/query",
                     data={"question": "¿Esta operación requiere reporte a la UIF?"},
                     files={"image": f}, timeout=30)
  print(r.json())

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SWAGGER UI — documentación interactiva en el navegador
  http://localhost:8000/docs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import io
import json
import os
import re
from contextlib import asynccontextmanager
from typing import Optional

import chromadb
import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from google import genai
from google.genai import types
from PIL import Image
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
MODEL = "gemini-3.1-flash-lite-preview"
EMBED_MODEL = "gemini-embedding-2"
CHROMA_PATH = "./chroma_db"
CHROMA_HOST = os.environ.get("CHROMA_HOST")          # set by docker-compose
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", 8000))

# Estos se inicializan en el lifespan para no bloquear el import
gemini_client: genai.Client = None
chroma_client = None  # chromadb.HttpClient o PersistentClient según entorno
text_collection = None
image_collection = None


# ---------------------------------------------------------------------------
# Lifespan: inicialización al arrancar la app
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa clientes al arrancar. Se ejecuta una sola vez."""
    global gemini_client, chroma_client, text_collection, image_collection

    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY no encontrada en variables de entorno.")

    # Inicializar Gemini
    gemini_client = genai.Client(api_key=GOOGLE_API_KEY)
    print("[startup] Gemini client inicializado.")

    # Inicializar ChromaDB
    # Si CHROMA_HOST está definido (ej: docker-compose), usar el servidor HTTP externo.
    # Si no, usar PersistentClient local (desarrollo fuera de Docker).
    if CHROMA_HOST:
        chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        print(f"[startup] ChromaDB: conectado a http://{CHROMA_HOST}:{CHROMA_PORT}")
    else:
        chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        print(f"[startup] ChromaDB: PersistentClient en {CHROMA_PATH}")
    text_collection = chroma_client.get_or_create_collection("ddls", embedding_function=None)
    # image_collection = chroma_client.get_or_create_collection("vouchers_financieros")
    print(f"[startup] ChromaDB: {text_collection.count()} esquemas registrados.")
    # print(f"[startup] ChromaDB: {image_collection.count()} docs en vouchers_financieros.")

    yield  # La app corre entre yield y el bloque de cleanup

    # Cleanup (opcional aquí, ChromaDB persiste solo)
    print("[shutdown] Cerrando app.")


app = FastAPI(
    title="GenAI Compliance API",
    description="API de consulta normativa SBS con RAG multimodal",
    version="1.0.0",
    lifespan=lifespan
)


# ---------------------------------------------------------------------------
# Schemas de request / response
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    question: str
    date_filter: Optional[str] = None   # ej: "2024-01" para solo normas >= esa fecha
    n_results: int = 3


class RAGResponse(BaseModel):
    answer: str
    sources: str
    confidence_note: str


class IngestResponse(BaseModel):
    status: str
    chunks_indexed: int
    collection: str
    chunks: list


# ---------------------------------------------------------------------------
# Utilidades internas (mismas funciones que en el notebook)
# ---------------------------------------------------------------------------

def embed_texts(texts: list[str]) -> list[list[float]]:
    """Genera embeddings con gemini-embedding-2 (una llamada por texto).

    Nota: embed_content con una lista de strings devuelve un único embedding
    (los concatena). Se llama una vez por texto y se agregan los resultados.
    """
    embeddings = []
    for text in texts:
        result = gemini_client.models.embed_content(
            model=EMBED_MODEL,
            contents=text
        )
        embeddings.append(result.embeddings[0].values)
    return embeddings


def parse_md_to_articles(md_text: str, source_id: str, date: str) -> list[dict]:
    """Divide un MD de SPIJ por artículo. Un artículo = un chunk."""
    chunks = []
    pattern = re.compile(r'^#{1,3}\s*Art[ií]culo\s+[\w]+', re.MULTILINE | re.IGNORECASE)
    matches = list(pattern.finditer(md_text))

    if not matches:
        return [{"text": md_text.strip(), "source": source_id, "article": "completo", "date": date}]

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md_text)
        chunk_text = md_text[start:end].strip()
        article_num = match.group(0).strip().split()[-1]
        chunks.append({"text": chunk_text, "source": source_id, "article": article_num, "date": date})

    return chunks

def cargar_tablas(tablas: list) -> list[dict]:
    """
    Recibe la lista ya parseada del JSON y retorna una lista de diccionarios
    con la estructura: {"id": ..., "nombre": ..., "descripcion": ..., "ddl": ...}
    """
    return [
        {
            "id":          tabla["id"],
            "nombre":      tabla["nombre"],
            "descripcion": tabla["descripcion"],
            "ddl":         tabla["ddl"],
        }
        for tabla in tablas
    ]

def retrieve_chunks(
    query: str,
    collection,
    n_results: int = 3,
    where: Optional[dict] = None
) -> list[dict]:
    """Retrieval semántico contra una colección ChromaDB."""
    total = collection.count()
    if total == 0:
        return []

    query_emb = embed_texts([query])[0]

    kwargs = {
        "query_embeddings": [query_emb],
        "n_results": min(n_results, total),  # nunca pedir más de lo que hay
        "include": ["documents", "metadatas", "distances"]
    }
    if where:
        kwargs["where"] = where

    results = collection.query(**kwargs)

    return [
        {"text": doc, "metadata": meta, "distance": dist}
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        )
    ]


def build_rag_response(question: str, ddl: str) -> RAGResponse:
    """
    Construye el prompt de augmentation y llama a Gemini.
    Retorna RAGResponse estructurado.
    """

    augmented_prompt = f"""
### Task
Generate a SQL query to answer [QUESTION]{question}[/QUESTION]

### Instructions
- If you cannot answer the question with the available database schema, return 'I do not know'

### Database Schema
The query will run on a database with the following schema:
{ddl}

### Answer
Given the database schema, here is the SQL query that answers [QUESTION]{question}[/QUESTION]
[SQL]
"""

    # Contenido: imagen (si hay) + prompt
    contents = [augmented_prompt]

    response = gemini_client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=0.0,
            max_output_tokens=600,
            response_mime_type="application/json",
            response_schema=RAGResponse
        )
    )

    parsed = json.loads(response.text)
    if "i do not know" in parsed.get("answer", "").lower():
        parsed["sources"] = ""

    return RAGResponse(**parsed)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    """Health check."""
    return {
        "status": "ok",
        "model": MODEL,
        "embed_model": EMBED_MODEL,
        "text_docs": text_collection.count()
    }


@app.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    file: Optional[UploadFile] = File(default=None)
):
    """
    Indexa un documento en ChromaDB.

    Acepta:
    - Archivo MD/TXT + metadata (source_id, date)
    - Texto directo como form field
    - Imagen (PNG/JPG) → Gemini la describe → embed la descripción

    Ejemplo con httpx:
        files = {"file": open("circular.md", "rb")}
        data = {"source_id": "circular_SBS_B_2244_2024", "date": "2024-03"}
        r = httpx.post("/ingest", files=files, data=data)
    """
    # -- Indexación de texto (MD/TXT) --
    global text_collection

    raw = await file.read()
    content = json.loads(raw.decode("utf-8"))
    chunks = cargar_tablas(content)

    if not chunks:
        raise HTTPException(400, "No se encontraron tablas en el documento.")

    # Recrear la colección limpia con embedding_function=None
    chroma_client.delete_collection("ddls")
    text_collection = chroma_client.get_or_create_collection(
        name="ddls",
        embedding_function=None
    )

    # Embed e indexar
    batch_size = 50
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        embeddings = embed_texts([chunk["descripcion"] for chunk in batch])

        text_collection.upsert(
            ids        = [chunk["id"]          for chunk in batch],
            documents  = [chunk["descripcion"] for chunk in batch],
            embeddings = embeddings,
            metadatas  = [{"nombre": chunk["nombre"], "ddl": chunk["ddl"]} for chunk in batch],
        )

    return IngestResponse(status="ok", chunks_indexed=len(chunks), collection="ddls", chunks=chunks)


@app.post("/query", response_model=RAGResponse)
async def query_endpoint(
    # Soportar tanto JSON puro como multipart con imagen
    question: str = Form(...),
    date_filter: Optional[str] = Form(default=None),
    n_results: int = Form(default=3),
    image: Optional[UploadFile] = File(default=None)
):
    """
    Consulta el pipeline RAG multimodal.

    Parámetros:
        question    : pregunta del analista
        date_filter : ej '2024-01' para solo normas posteriores
        n_results   : cuántos chunks recuperar (default: 3)
        image       : voucher/imagen opcional (multipart)

    Ejemplo con httpx (solo texto):
        r = httpx.post("/query", data={"question": "¿Cuál es el umbral de reporte?"})

    Ejemplo con imagen:
        files = {"image": open("voucher.png", "rb")}
        data = {"question": "¿Requiere reporte esta operación?"}
        r = httpx.post("/query", files=files, data=data)
    """

    if text_collection.count() == 0:
        raise HTTPException(
            503,
            "La colección está vacía. Ingesta documentos primero con POST /ingest."
        )

    # Retrieval de texto normativo
    where = {"date": {"$gte": date_filter}} if date_filter else None
    chunks = retrieve_chunks(question, text_collection, n_results=n_results, where=where)

    if not chunks:
        raise HTTPException(404, "No se encontraron fragmentos relevantes para la query.")

    # Procesar imagen si se incluyó
    pil_image = None
    if image is not None:
        raw = await image.read()
        pil_image = Image.open(io.BytesIO(raw))

    # Construir respuesta RAG
    result = build_rag_response(question, chunks, image=pil_image)
    return result


@app.post("/query/json")
async def query_json(request: QueryRequest):
    """
    Dado una pregunta en lenguaje natural, devuelve la tabla más relevante
    según similitud semántica con su descripción.

    Ejemplo:
        r = httpx.post("/query/json", json={"question": "¿Qué productos hay disponibles?"})
        # → {"id": "tabla_1", "nombre": "productos", "ddl": "CREATE TABLE ..."}
    """
    if text_collection.count() == 0:
        raise HTTPException(503, "Colección vacía. Ingesta documentos primero.")

    chunks = retrieve_chunks(request.question, text_collection, n_results=1)

    if not chunks:
        raise HTTPException(404, "No se encontró ninguna tabla relevante.")

    best = chunks[0]

    return build_rag_response(question = request.question, ddl = best["metadata"]["ddl"])
#    return {
#        "id":       best["metadata"]["nombre"],  
#        "nombre":   best["metadata"]["nombre"],
#        "ddl":      best["metadata"]["ddl"],
#        "distance": best["distance"],
#    }
