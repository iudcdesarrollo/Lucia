import os
from dotenv import load_dotenv

load_dotenv()

# Token de la API de Telegram (por defecto: Ninguno)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', None)

# SID de la cuenta Twilio y token de autenticación (por defecto: Ninguno)
ACCOUNT_SID = os.getenv('ACCOUNT_SID', None)
AUTH_TOKEN = os.getenv('AUTH_TOKEN', None)

# El número Twilio Sandbox o propio de la empresa
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', None)

# El ID de la página de Facebook de tu aplicación de Messenger de Facebook
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID', None)

# Tu clave API personal de Zapier NLA para gestión de calendarios
ZAPIER_NLA_API_KEY = os.getenv('ZAPIER_NLA_API_KEY', None)

# Clave API de OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Elige tu modelo entre gpt-3, gpt-3.5-turbo, gpt-4
SELECTED_MODEL = 'gpt-3.5-turbo'

# Valor de temperatura para el modelo de lenguaje de OpenAI
TEMPERATURE_VALUE = float(0.8)

# Configuración de DALL-E
IMAGE_SIZE = "256x256"

# Nombre del chatbot para generar respuestas
BOT_NAME = 'Luisa'

# ¿Usar BabyAGI o no?
BABYAGI = False