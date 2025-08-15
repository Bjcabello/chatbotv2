from pymongo import MongoClient
# from pymongo.errors import ConnectionFailure

def connect_to_mongodb():
    try:
        uri = "mongodb://localhost:27017"
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)  # Timeout para evitar bloqueos
        # Verificar la conexión
        client.admin.command({'ping': 1})  # Prueba si el servidor está vivo
        print("Conexión a MongoDB exitosa")
        
        database = client["Login_User"]  # Nombre de la base de datos
        collection = database["users"]  # Nombre de la colección
        return collection
    
    except Exception as e:
        raise Exception(
            "The following error occurred: ", e)

    # except ConnectionFailure as e:
    #     raise Exception(f"No se pudo conectar a MongoDB: {e}")
    # except Exception as e:
    #     raise Exception(f"Error inesperado: {e}")

# Ejemplo de uso (puedes descomentar para probar)
# client, db, collection = connect_to_mongodb()
# client.close()  # Cierra la conexión cuando termines