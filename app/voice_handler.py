import urllib.request
import librosa
import soundfile as sf
import os
import openai
from chat_handler import process_chat_message


def transcribe_audio(audio_filepath: str) -> str:
  """
    Transcribe un archivo de audio utilizando la API de ASR Whisper de OpenAI.

    Args:
        audio_filepath (str): Ruta al archivo de audio.

    Returns:
        str: Texto transcrito.
    """
  with open(audio_filepath, "rb") as audio:
    transcript = openai.Audio.transcribe("whisper-1", audio)
    return transcript["text"]


async def handle_voice_message(audio_filepath: str, chat_id: int) -> str:
  """
    Maneja un mensaje de voz entrante y genera una respuesta apropiada.

    Args:
        audio_filepath (str): Ruta al archivo de audio.
        chat_id (int): Identificador único para el chat.

    Returns:
        str: La respuesta generada.
    """
  # Transcribe el archivo de audio
  transcribed_text = transcribe_audio(audio_filepath)
  print("transcribed text: " + transcribed_text)
  output = await process_chat_message(transcribed_text, chat_id)
  return output


async def process_voice_message(voice_url: str, chat_id: int) -> str:
  """
    Procesa un mensaje de voz entrante y genera una respuesta apropiada.

    Args:
        voice_url (str): URL del mensaje de voz.
        chat_id (int): Identificador único para el chat.

    Returns:
        str: La respuesta generada.
    """
  # Descarga el archivo de voz desde la URL
  voice_file = "voice_message.ogg"

  # Crea un agente de usuario personalizado para evitar cualquier restricción
  user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
  headers = {"User-Agent": user_agent}
  request = urllib.request.Request(voice_url, headers=headers)

  # Descarga el archivo utilizando el agente de usuario personalizado
  with urllib.request.urlopen(request) as response:
    with open(voice_file, 'wb') as out_file:
      out_file.write(response.read())

  # Convierte el archivo de audio OGG/Opus a un formato compatible (por ejemplo, 'wav')
  y, sr = librosa.load(voice_file, sr=None)
  converted_voice_file = "converted_audio.wav"
  sf.write(converted_voice_file, y, sr, format='wav', subtype='PCM_24')

  # Procesa el archivo de voz (transcribe, analiza, responde, etc.)
  output = await handle_voice_message(converted_voice_file, chat_id)

  # Limpia los archivos de voz
  os.remove(voice_file)
  os.remove(converted_voice_file)

  # Devuelve la salida (texto, imagen, etc.)
  return output
