import os
import openai
import pinecone
import time
import sys
from collections import deque
from typing import Dict, List
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from config import BABYAGI, ACCOUNT_SID, AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER, FACEBOOK_PAGE_ID

# Verifica si el sistema es BABYAGI (un sistema de IA)
if BABYAGI:
  # Carga las variables de entorno
  load_dotenv()

  # Establece las claves de API y otras variables de entorno
  OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
  PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
  PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east1-gcp")
  YOUR_TABLE_NAME = os.getenv("TABLE_NAME", "")
  YOUR_FIRST_TASK = os.getenv("FIRST_TASK", "")
  USE_GPT4 = os.getenv("USE_GPT4", True)

  # Asegura que las variables requeridas estén configuradas
  if not OPENAI_API_KEY:
    print("OPENAI_API_KEY environment variable is missing from .env")
  if not YOUR_TABLE_NAME:
    print("TABLE_NAME environment variable is missing from .env")
  if not YOUR_FIRST_TASK:
    print("FIRST_TASK environment variable is missing from .env")

  # Configura OpenAI y Pinecone
  openai.api_key = OPENAI_API_KEY
  if PINECONE_API_KEY:
    pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)

  # Crea un índice Pinecone si se establece PINECONE_API_KEY
  if PINECONE_API_KEY and YOUR_TABLE_NAME not in pinecone.list_indexes():
    pinecone.create_index(YOUR_TABLE_NAME,
                          dimension=1536,
                          metric="cosine",
                          pod_type="p1")

  # Conéctate al índice si se establece PINECONE_API_KEY
  if PINECONE_API_KEY:
    index = pinecone.Index(YOUR_TABLE_NAME)

  # Lista de tareas
  task_list = deque([])


# Funciones
def add_task(task: Dict):
  # Agrega una tarea a la lista de tareas
  task_list.append(task)


def get_ada_embedding(text: str) -> List[float]:
  # Obtiene la incrustación de texto de OpenAI utilizando el modelo "text-embedding-ada-002"
  text = text.replace("\n", " ")
  return openai.Embedding.create(
    input=[text], model="text-embedding-ada-002")["data"][0]["embedding"]


def openai_call(prompt: str,
                use_gpt4: bool = False,
                temperature: float = 0.5,
                max_tokens: int = 100):
  # Llama al modelo de chat de OpenAI (ya sea GPT-3 o GPT-4)
  if not use_gpt4:
    # Call GPT-3 DaVinci model
    response = openai.Completion.create(engine='babbage-002',
                                        prompt=prompt,
                                        temperature=temperature,
                                        max_tokens=max_tokens,
                                        top_p=1,
                                        frequency_penalty=0,
                                        presence_penalty=0)
    return response.choices[0].text.strip()
  else:
    # Llama al modelo de chat GPT-4
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
      model="gpt-4",
      messages=messages,
      temperature=temperature,
      max_tokens=max_tokens,
      n=1,
      stop=None,
    )
    return response.choices[0].message.content.strip()


def task_creation_agent(objective: str,
                        result: Dict,
                        task_description: str,
                        task_list: List[str],
                        gpt_version: str = 'gpt-3'):
  # Agente de creación de tareas
  prompt = f"Eres una IA de creación de tareas que utiliza el resultado de un agente de ejecución para crear nuevas tareas con el siguiente objetivo:{objective}, la última tarea completada tiene el resultado: {result}. Este resultado se basó en la descripción de la tarea:{task_description}.Estas son tareas incompletas: {', '.join(task_list)}. Basado en el resultado, crea nuevas tareas que deben ser completadas por el sistema de IA y que no se superpongan con las tareas incompletas. Devuelve las tareas como una matriz."
  response = openai_call(prompt, gpt_version)
  new_tasks = response.split('\n')
  return [{"task_name": task_name} for task_name in new_tasks]


def prioritization_agent(this_task_id: int,
                         objective,
                         gpt_version: str = 'gpt-3'):
  # Agente de priorización de tareas
  global task_list
  task_names = [t["task_name"] for t in task_list]
  next_task_id = int(this_task_id) + 1
  prompt = f"""Eres un IA de priorización de tareas encargado de limpiar el formato y repriorizar las siguientes tareas: {task_names}.Considera el objetivo final de tu equipo: {objective}.No elimines ninguna tarea. Devuelve el resultado como una lista numerada, por ejemplo:
    #. Primera tarea
    #. Segunda tarea
    #. Tercera tarea
    nComienza la lista de tareas con el número {next_task_id}."""
  response = openai_call(prompt, gpt_version)
  new_tasks = response.split('\n')
  task_list = deque()
  for task_string in new_tasks:
    task_parts = task_string.strip().split(".", 1)
    if len(task_parts) == 2:
      task_id = task_parts[0].strip()
      task_name = task_parts[1].strip()
      task_list.append({"task_id": task_id, "task_name": task_name})


def execution_agent(objective: str,
                    task: str,
                    gpt_version: str = 'gpt-3') -> str:
  context = context_agent(index=YOUR_TABLE_NAME, query=objective, n=5)
  prompt = f"You are an AI who performs one task based on the following objective: {objective}.\nTake into account these previously completed tasks: {context}\nYour task: {task}\nResponse:"
  return openai_call(prompt, USE_GPT4, 0.7, 2000)


def context_agent(query: str, index: str, n: int):
  # Agente de contexto
  query_embedding = get_ada_embedding(query)
  index = pinecone.Index(index_name=index)
  results = index.query(query_embedding, top_k=n, include_metadata=True)
  sorted_results = sorted(results.matches, key=lambda x: x.score, reverse=True)
  return [(str(item.metadata['task'])) for item in sorted_results]


async def send_message(chat_id: str,
                       message: str,
                       platform: str,
                       client=None,
                       base_url=None):
  if platform == 'telegram':
    await client.get(f"{base_url}/sendMessage?chat_id={chat_id}&text={message}"
                     )
  elif platform == 'twilio':
    await send_twilio_message(chat_id, message)


async def process_task(objective: str,
                       chat_id: str,
                       platform='telegram',
                       client=None,
                       base_url=None):
  first_task = {"task_id": 1, "task_name": YOUR_FIRST_TASK}

  add_task(first_task)

  task_id_counter = 1
  while True:
    if task_list:
      # Imprime la lista de tareas
      print("\033[95m\033[1m" + "\n*****TASK LIST*****\n" + "\033[0m\033[0m")
      temp = ""
      for t in task_list:
        tsk = str(t['task_id']) + ": " + t['task_name']
        print(tsk)
        temp = temp + tsk + "\n"

      await send_message(chat_id, temp, platform, client, base_url)

      # Paso 1: Extrae la primera tarea
      task = task_list.popleft()
      print("\033[92m\033[1m" + "\n*****NEXT TASK*****\n" + "\033[0m\033[0m")
      next_tsk = str(task['task_id']) + ": " + task['task_name']
      print(next_tsk)

      await send_message(chat_id, next_tsk, platform, client, base_url)

      # Envía la tarea a la función de ejecución para completarla según el contexto
      result = execution_agent(objective, task["task_name"])
      this_task_id = int(task["task_id"])
      print("\033[93m\033[1m" + "\n*****TASK RESULT*****\n" + "\033[0m\033[0m")
      print(result)

      await send_message(chat_id, result, platform, client, base_url)

      # Paso 2: Enriquece el resultado y almacénalo en Pinecone
      # Aquí es donde debes enriquecer el resultado si es necesario
      enriched_result = {'data': result}
      result_id = f"result_{task['task_id']}"
      # Extrae el resultado real del diccionario
      vector = enriched_result['data']
      index.upsert([(result_id, get_ada_embedding(vector), {
        "task": task['task_name'],
        "result": result
      })])

    # Paso 3: Crea nuevas tareas y reprioriza la lista de tareas
    if task_id_counter < 6:
      print(f"tt: {task_id_counter}")
      new_tasks = task_creation_agent(objective, enriched_result,
                                      task["task_name"],
                                      [t["task_name"] for t in task_list])

      for new_task in new_tasks:
        task_id_counter += 1
        new_task.update({"task_id": task_id_counter})
        add_task(new_task)
      prioritization_agent(this_task_id, objective)
    if len(task_list) < 1:
      print("Tareas completadas")
      await send_message(chat_id, "\n\nTareas completadas", platform, client,
                         base_url)
      break


async def send_twilio_message(chat_id: str,
                              message: str,
                              platform: str = "whatsapp"):
  account_sid = ACCOUNT_SID
  auth_token = AUTH_TOKEN
  client = Client(account_sid, auth_token)

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

  try:
    client.messages.create(body=message, from_=twilio_phone_number, to=chat_id)
  except TwilioException as e:
    print(f"Error al enviar el mensaje: {e}")
