from conexion_mongo import * 
from create import * 
from models.users.models import User

def ingresar_dato_prueba(user_model : User):
    
    collection = connect_to_mongodb
    
    user_id = uuid.uuid4()
    
    user_document = {
        "id": user_id.id.bytes,
        "user_name": user_model.user_name,
        "password": user_model.password,
        "email": user_model.email
    }
    
    result = collection.insert_one(user_document)
        print(f"Usuario insertado con ID: {user_id}")
        return result
    

    
    # "_id": user_data.id.bytes,
    #         "user_name": user_data.user_name,
    #         "password": hashed_password,  # Guardar la contraseña hasheada
    #         "email": user_data.email


# collection  = connect_to_mongodb()
# result = collection.insert_one({
#     "user_name": "alexis2004",
#     "password": "alexis12345",    
#     "email": "alexis@gmail.com"
# })
