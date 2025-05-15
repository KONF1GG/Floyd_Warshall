from fastapi import FastAPI
from floyd_warshall import main_response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

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

@app.get("/shortest_paths")
def get_shortest_paths_floyd_warshall():
    shortest_paths = main_response()
    return shortest_paths

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True, host='0.0.0.0', port=8080)