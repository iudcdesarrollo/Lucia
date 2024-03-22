import asyncio
from fastapi import APIRouter, Form, Response, Request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from chat_handler import process_chat_message
from voice_handler import process_voice_message
from config import BABYAGI, ACCOUNT_SID, AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER, FACEBOOK_PAGE_ID
from babyagi import process_task

twilio_api_reply = APIRouter()


# Procesa un mensaje de chat o voz entrante y envía una respuesta utilizando Twilio.
async def send_twilio_response(chat_id: str,
                               message: str,
                               platform: str = "whatsapp",
                               is_voice: bool = False):
  """
    Processa un mensaje de chat o voz entrante y envía una respuesta utilizando Twilio.
    Args:
        chat_id (str): Identificador único para el chat.
        message (str):  Mensaje de entrada, ya sea texto o una URL de un mensaje de voz.
        platform (str): Plataforma de mensajería, ya sea "whatsapp" o "messenger". El valor predeterminado es "whatsapp".
        is_voice (bool): Si el mensaje de entrada es un mensaje de voz (True) o un mensaje de texto (False). El valor predeterminado es False.
    """

  if platform not in ("whatsapp", "messenger"):
    raise ValueError(
      "Plataforma no válida especificada. Las plataformas válidas son 'whatsapp' y 'messenger'."
    )

  if platform == "whatsapp" and not TWILIO_WHATSAPP_NUMBER:
    print(
      "Número de WhatsApp de Twilio no configurado. Por favor, establezca la variable de entorno TWILIO_WHATSAPP_NUMBER."
    )
    return
  elif platform == "messenger" and not FACEBOOK_PAGE_ID:
    print(
      "ID de página de Facebook no configurado. Por favor, establezca la variable de entorno FACEBOOK_PAGE_ID."
    )
    return

  if platform == "messenger":
    twilio_phone_number = f'messenger:{FACEBOOK_PAGE_ID}'
  else:
    twilio_phone_number = f'whatsapp:{TWILIO_WHATSAPP_NUMBER}'

  # Rest of the function remains unchanged
  if is_voice:
    # Procesa mensajes de voz
    output = await process_voice_message(message, chat_id)
  elif BABYAGI and message.startswith("/task"):
    if BABYAGI:
      # Procesa mensajes de texto
      task = message[5:]
      await process_task(task,
                         chat_id=chat_id,
                         platform='twilio',
                         client=None,
                         base_url=None)
      output = task
  else:
    output = await process_chat_message(message, chat_id)

  # Inicializa la respuesta de Twilio
  resp = MessagingResponse()

  # Envía el resultado como un mensaje de texto o una foto con una leyenda, dependiendo del tipo de resultado
  if isinstance(output, tuple):
    summary, image = output
    response_msg = resp.message(summary)
    response_msg.media(image)
  else:
    response_msg = resp.message(output)

  # Envía el mensaje utilizando el cliente de Twilio
  from twilio.rest import Client
  account_sid = ACCOUNT_SID
  auth_token = AUTH_TOKEN
  client = Client(account_sid, auth_token)

  if is_voice:
    if isinstance(output, tuple):
      summary, image = output
      client.messages.create(body=summary,
                             media_url=image,
                             from_=twilio_phone_number,
                             to=chat_id)
    else:
      client.messages.create(body=output,
                             from_=twilio_phone_number,
                             to=chat_id)
  else:
    if isinstance(output, tuple):
      summary, image = output
      client.messages.create(body=summary,
                             media_url=image,
                             from_=twilio_phone_number,
                             to=chat_id)
    else:
      client.messages.create(body=output,
                             from_=twilio_phone_number,
                             to=chat_id)


# Maneja la respuesta de la API de Twilio
@twilio_api_reply.post("/api")
async def handle_twilio_api_reply(request: Request,
                                  Body: str = Form(""),
                                  MediaUrl0: str = Form("")):
  form_data = await request.form()
  chat_id = form_data.get("From")
  platform = form_data.get("To")

  if platform.startswith("whatsapp"):
    platform = "whatsapp"
  elif platform.startswith("messenger"):
    platform = "messenger"
  else:
    return Response(content="Invalid platform",
                    media_type="text/plain",
                    status_code=400)

# Solo procesa los mensajes de Twilio si el número de WhatsApp de Twilio o el ID de la página de Facebook están configurados
  if (platform == "whatsapp"
      and TWILIO_WHATSAPP_NUMBER) or (platform == "messenger"
                                      and FACEBOOK_PAGE_ID):
    if MediaUrl0:
      asyncio.create_task(
        send_twilio_response(chat_id,
                             MediaUrl0,
                             platform=platform,
                             is_voice=True))
    else:
      asyncio.create_task(
        send_twilio_response(chat_id, Body.strip(), platform=platform))

# Devuelve una respuesta vacía a Twilio
  resp = MessagingResponse()
  return Response(content=str(resp), media_type="application/xml")
