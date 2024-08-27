from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
import os

# API_KEY = os.getenv("API_KEYS")
# print(API_KEY)
load_dotenv()
API_KEY = os.getenv("API_KEYS")
API_KEY_NAME = "api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        print("/////////////////",api_key)
        print(API_KEY)
        print(api_key_header)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return api_key

# print(get_api_key(API_KEY))
