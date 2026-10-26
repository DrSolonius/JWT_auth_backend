import os

from dotenv import load_dotenv


# Lee el archivo .env (busca en esta carpeta y en las superiores).
load_dotenv()

# Sin valor por defecto: si falta, la API no arranca (KeyError), igual que DB_USER.
JWT_SECRET = os.environ["JWT_SECRET"]

# El algoritmo se fija en el código, no en el .env.
JWT_ALGORITMO = "HS256"

ACCESS_TOKEN_MINUTOS = int(os.environ.get("ACCESS_TOKEN_MINUTOS", 15))
REFRESH_TOKEN_DIAS = int(os.environ.get("REFRESH_TOKEN_DIAS", 7))

# true salvo que el .env diga lo contrario (en desarrollo con http: false).
COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "true").lower() == "true"
