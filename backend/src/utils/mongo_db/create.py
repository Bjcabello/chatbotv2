import uuid
from pymongo.errors import OperationFailure
from conexion_mongo import *      

def create_users_collection():
    try:
        db = connect_to_mongodb()

        # Definir el esquema de validación
        validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["user_name", "password", "email"],  # Campos obligatorios
                "properties": {
                    "_id": {
                        "bsonType": "binData",  # Para UUID
                        "description": "Debe ser un UUID"
                    },
                    "user_name": {
                        "bsonType": "string",
                        "description": "Debe ser una cadena y es obligatorio"
                    },
                    "password": {
                        "bsonType": "string",
                        "description": "Debe ser una cadena y es obligatorio"
                    },
                    "email": {
                        "bsonType": "string",
                        "description": "Debe ser una cadena y es obligatorio"
                    }
                }
            }
        }

        # Crear o actualizar la colección con el validador
        db.command("collMod", "users", validator=validator)
        print("Esquema de validación aplicado a la colección 'users'")

    except OperationFailure as e:
        raise Exception(f"Error al configurar la colección: {e}")
    except Exception as e:
        raise Exception(f"Error inesperado: {e}")

def insert_user(user_name, password, email):
    try:
        _, _, collection = connect_to_mongodb()
        
        # Generar un UUID para el _id
        user_id = uuid.uuid4()
        
        # Crear el documento del usuario
        user_document = {
            "_id": user_id.bytes,  # Convertir UUID a formato binario para MongoDB
            "user_name": user_name,
            "password": password,  # Nota: ¡Debes hashear la contraseña en producción!
            "email": email
        }
        
        result = collection.insert_one(user_document)
        print(f"Usuario insertado con ID: {user_id}")
        return result

    except Exception as e:
        raise Exception(f"Error al insertar usuario: {e}")