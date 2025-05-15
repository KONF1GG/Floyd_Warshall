from fastapi import FastAPI, Query
from floyd_warshall import main_response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from schemas import Locality, Ural

app = FastAPI(
    title="floyd_warshall API",
    version="1.0.0",
)

origins = [
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

@app.get("/shortest_paths", response_model=list[Locality])
def get_shortest_paths_floyd_warshall(ural: int = Query(..., gt=0, lt=3)):
    shortest_paths = main_response(Ural(ural=ural))
    return shortest_paths

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True, host='0.0.0.0', port=8080)