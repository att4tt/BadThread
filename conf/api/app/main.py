from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from strawberry.fastapi import GraphQLRouter
import strawberry
import json
from schema import Query, Mutation
from starlette.middleware.base import BaseHTTPMiddleware
from time import time
from collections import defaultdict
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

request_tracker = defaultdict(list)
penalty_tracker = defaultdict(lambda: {'start': 0, 'count': 0})

RATE_LIMIT = 30
MAX_REQUESTS = 30
BASE_PENALTY_TIME = 30
PENALTY_INCREMENT = 30

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time()

        penalty_info = penalty_tracker[client_ip]
        penalty_start = penalty_info['start']
        if current_time < penalty_start:
            penalty_remaining = int(penalty_start - current_time)
            return JSONResponse(
                content={"detail": f"Rate limit exceeded. Try again after {penalty_remaining} seconds."},
                status_code=422
            )

        timestamps = request_tracker[client_ip]

        timestamps = [t for t in timestamps if current_time - t < RATE_LIMIT]
        request_tracker[client_ip] = timestamps

        timestamps.append(current_time)
        
        if len(timestamps) > MAX_REQUESTS:
            penalty_info['count'] += 1
            penalty_time = BASE_PENALTY_TIME + (penalty_info['count'] - 1) * PENALTY_INCREMENT
            penalty_info['start'] = current_time + penalty_time
            return JSONResponse(
                content={"detail": f"Rate limit exceeded. Try again after {penalty_time} seconds."},
                status_code=422
            )

        response = await call_next(request)
        return response

app.add_middleware(RateLimitMiddleware)


class CustomJSONResponse(JSONResponse):
    def render(self, content: dict) -> bytes:
        return json.dumps(content, ensure_ascii=False).encode('utf-8')

@app.middleware("http")
async def custom_json_response_middleware(request: Request, call_next):
    response = await call_next(request)
    content_type = response.headers.get('Content-Type', '')
    
    if request.url.path.startswith("/graphql") and content_type.startswith('application/json'):
        body = b"".join([chunk async for chunk in response.body_iterator])
        content = json.loads(body.decode('utf-8'))            
        response = CustomJSONResponse(content=content, status_code=response.status_code)
    
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1"],
    allow_methods=["POST"], 
    allow_headers=["*"], 
)

schema = strawberry.Schema(Query, Mutation)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")