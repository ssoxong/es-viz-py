from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from elasticsearch import Elasticsearch
import json
import uvicorn
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Elasticsearch client
es = Elasticsearch("http://localhost:9200")

class IndexCreateRequest(BaseModel):
    indexName: str
    shards: int = 1
    replicas: int = 1

class DocumentCreateRequest(BaseModel):
    id: Optional[str] = None
    body: str

@app.get("/indices")
async def get_indices():
    try:
        # Get all non-system indices
        indices = es.cat.indices(h=["index", "status", "docs.count", "store.size"], format="json")
        return [index for index in indices if not index['index'].startswith('.')]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/index")
async def create_index(request: IndexCreateRequest):
    try:
        response = es.indices.create(
            index=request.indexName,
            body={
                "settings": {
                    "number_of_shards": request.shards,
                    "number_of_replicas": request.replicas
                }
            }
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/index/{index_name}/document")
async def create_document(index_name: str, request: DocumentCreateRequest):
    try:
        body = json.loads(request.body)
        if request.id:
            response = es.index(index=index_name, id=request.id, body=body)
        else:
            response = es.index(index=index_name, body=body)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/index/{index_name}/search")
async def search_index(index_name: str, query: Dict[str, Any] = None):
    try:
        response = es.search(index=index_name, body=query or {})
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/index/{index_name}")
async def delete_index(index_name: str):
    try:
        response = es.indices.delete(index=index_name)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/index/{index_name}/delete")
async def delete_documents(index_name: str, ids: List[str]):
    try:
        query = {
            "query": {
                "terms": {
                    "_id": ids
                }
            }
        }
        response = es.delete_by_query(index=index_name, body=query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/index/{index_name}/update/{doc_id}")
async def update_document(index_name: str, doc_id: str, doc: Dict[str, Any]):
    try:
        response = es.update(index=index_name, id=doc_id, body={"doc": doc})
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @app.post("/index/{index_name}/multi-search")
# async def multi_search_index(index_name: str, query: str):
#     try:
#         search_query = {
#             "query": {
#                 "multi_match": {
#                     "query": query,
#                     "fields": ["*"]
#                 }
#             }
#         }
#         response = es.search(index=index_name, body=search_query)
#         return response
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
# # 애플리케이션 실행

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
