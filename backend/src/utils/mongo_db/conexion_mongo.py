#backend/src/utlis/mongo_db/conexion.py
from pymongo import MongoClient
# from pymongo.errors import ConnectionFailure

def connect_to_mongodb():
    try:
        uri = "mongodb://localhost:27017"
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)  # Timeout para evitar bloqueos
        # Verificar la conexión
        client.admin.command({'ping': 1})  # Prueba si el servidor está vivo
        print("Conexión a MongoDB exitosa")
        
        database = client["chatvmt_user"]  # Nombre de la base de datos
        collection = database["users"]  # Nombre de la colección
        return database, collection
    
    except Exception as e:
        raise Exception(
            "The following error occurred: ", e)
