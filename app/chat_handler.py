from typing import Dict, Union, Tuple
from models import initialize_language_model
from templates import get_template
from config import SELECTED_MODEL
from utils import get_topic, process_chat, process_image, process_calendar

# Inicializa un diccionario para realizar un seguimiento del último mensaje de cada usuario
last_messages: Dict[int, str] = {}


async def process_chat_message(text: str,
                               chat_id: int) -> Union[str, Tuple[str, str]]:
  """
    Procesa un mensaje de chat entrante y genera una respuesta apropiada.
    Args:
        text (str): Mensaje de texto de entrada.
        chat_id (int): Identificador único para el chat.
    Returns:
        Union[str, Tuple[str, str]]: La respuesta generada como una cadena de texto, o una tupla que contiene una cadena de texto y una URL de imagen.
    """
  # Obtener los últimos 3 mensajes para este usuario
  last_3_messages = last_messages.get(chat_id, ["", "", ""])
  history_string = f"""\n{last_3_messages[0]}\n{last_3_messages[1]}\n{last_3_messages[2]}\n"""

  # Determinar el tema
  topic = await get_topic(text, history_string)

  # Procesar el mensaje según el tema
  output = ""
  if topic == "chat":
    output = process_chat(text, history_string)
  elif topic == "image":
    output = await process_image(text, history_string)
  elif topic == "calendar":
    output = process_calendar(text, history_string)

  # Actualizar los últimos mensajes para este usuario
  last_messages[chat_id] = [text] + last_3_messages[:-1]
  print(output)
  return output
