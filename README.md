# entrar al backend crear un venv
python -m venv venv

# correr el venv
venv\Scripts\activate

# instalar requirements
pip install -r requirements.txt

# correr el proyecto(backend)
uvicorn src.main:app --reload

# correr frontend 
En el Frontend acceder y cd frontend y correr
npm install
npm run dev