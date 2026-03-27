import os
from pymongo import MongoClient
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from redis import Redis

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "escola")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")

client = MongoClient(MONGODB_URL)
# client = AsyncIOMotorClient(MONGO_URL) DÚVIDA
db = client[DATABASE_NAME]

def get_db():
    return db

redis_client = Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)