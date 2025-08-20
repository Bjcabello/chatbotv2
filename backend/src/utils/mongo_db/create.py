from pymongo.errors import OperationFailure
from src.utils.mongo_db.conexion_mongo import connect_to_mongodb

def ensure_indexes(ttl_seconds_users: int | None = None):
    """
    Crea índices:
      - users.email único
      - users.createdAt TTL (si se especifica ttl_seconds_users)
      - apikeys.user_email index
      - apikeys.key_hash único
    """
    db, users = connect_to_mongodb()
    apikeys = db["apikeys"]

    # users: email único
    users.create_index("email", unique=True)

    # users: TTL opcional (si quieres que la cuenta caduque y se borre sola)
    if ttl_seconds_users is not None:
        users.create_index("createdAt", expireAfterSeconds=int(ttl_seconds_users))

    # apikeys: índices
    apikeys.create_index("user_email")
    apikeys.create_index("key_hash", unique=True)

    print("Índices garantizados: users(email, TTL opcional) y apikeys(user_email, key_hash único).")
