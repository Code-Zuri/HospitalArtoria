import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
print(f"URI: {MONGO_URI}")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
    client.admin.command('ping')
    print("✅ Conexión exitosa a MongoDB Atlas.")
    # Lista las bases de datos disponibles
    print("Bases de datos:", client.list_database_names())
except Exception as e:
    print(f"❌ Error de conexión: {e}")