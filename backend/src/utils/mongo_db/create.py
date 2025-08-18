#backend/src/utils/mongo_db/create.py
import uuid
from pymongo.errors import OperationFailure
from src.utils.mongo_db.conexion_mongo import connect_to_mongodb
from src.models.users_models import User
from pydantic import ValidationError

def validation_users():
    try:
        db = connect_to_mongodb()

        # Definir el esquema de validación
        validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["user_name", "password", "email", "createdAt"],  # Campos obligatorios
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
    


def ensure_indexes(ttl_seconds: int | None = None):
    """
    Crea índices necesarios:
    - email único
    - TTL sobre createdAt (si ttl_seconds no es None)
    """
    db, collection = connect_to_mongodb()

    # Único por email
    collection.create_index("email", unique=True)

    # TTL (si quieres que caduque)
    if ttl_seconds is not None:
        # Nota: TTL funciona sobre un campo DATE.
        collection.create_index("createdAt", expireAfterSeconds=int(ttl_seconds))

    print("Índices garantizados (email único, TTL opcional).")
