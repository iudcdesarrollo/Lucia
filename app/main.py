from fastapi import FastAPI
from telegram_handler import telegram_webhook
from twilio_handler import twilio_api_reply

# Crea una instancia de la aplicación FastAPI
app = FastAPI()

# Incluye los enrutadores para el webhook de Telegram y la respuesta API de Twilio
app.include_router(telegram_webhook)
app.include_router(twilio_api_reply)
