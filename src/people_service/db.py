import os
from pymongo import MongoClient

client = MongoClient(os.getenv("MONGO_URI", "mongodb://mongo:27017"))
db = client[os.getenv("DB_NAME", "simple_db")]
