import openai
from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from config import SELECTED_MODEL, IMAGE_SIZE, ZAPIER_NLA_API_KEY, BOT_NAME
from models import initialize_language_model
from templates import get_template
from langchain.agents.agent_toolkits import ZapierToolkit
from langchain.utilities.zapier import ZapierNLAWrapper
from langchain.agents import initialize_agent

# Si se proporciona una clave API de Zapier NLA, inicializa el agente para manejar las interacciones con Zapier
if ZAPIER_NLA_API_KEY:
  llm = OpenAI(temperature=0)
  zapier = ZapierNLAWrapper()
  toolkit = ZapierToolkit.from_zapier_nla_wrapper(zapier)
  agent = initialize_agent(toolkit.get_tools(),
                           llm,
                           agent="zero-shot-react-description",
                           verbose=True)
else:
  zapier = None
  toolkit = None
  agent = None


async def get_topic(text: str, history_string: str) -> str:
  """
      Obtiene el tema del texto dado basado en el historial de la conversación.
 
    Args:
        texto (str): Mensaje de texto de entrada.
        history_string (str): Cadena de historial de conversación formateada.

    Returns:
        str: El tema detectado.
    """
  prompt_template = get_template("topic")
  prompt = PromptTemplate(input_variables=["history", "human_input"],
                          template=prompt_template)

  chatgpt_chain = LLMChain(
    llm=initialize_language_model(SELECTED_MODEL),
    prompt=prompt,
    verbose=False,
    memory=ConversationBufferMemory(),
  )

  topic = chatgpt_chain.predict(history=history_string, human_input=text)

  return topic


def process_chat(text: str, history_string: str) -> str:
  """
    Procesa un mensaje de chat y genera una respuesta.

    Args:
        text (str): Mensaje de texto de entrada.
        history_string (str): Cadena de historial de conversación formateada.

    Returns:
        str: El tema detectado.
    """
  prompt_template = get_template("chat")
  prompt = PromptTemplate(input_variables=["history", "human_input"],
                          template=prompt_template)

  chatgpt_chain = LLMChain(
    llm=initialize_language_model(SELECTED_MODEL),
    prompt=prompt,
    verbose=False,
    memory=ConversationBufferMemory(),
  )

  output = chatgpt_chain.predict(history=history_string, human_input=text)

  return output


async def process_image(text: str, history_string: str) -> str:
  """
    Procesa una solicitud de imagen y genera una respuesta.

    Args:
        text (str): Mensaje de texto de entrada.
        history_string (str): Cadena de historial de conversación formateada.

    Returns:
        str: El tema detectado.
    """
  prompt_template = get_template("image")
  prompt = PromptTemplate(input_variables=["history", "human_input"],
                          template=prompt_template)

  chatgpt_chain = LLMChain(
    llm=initialize_language_model(SELECTED_MODEL),
    prompt=prompt,
    verbose=False,
    memory=ConversationBufferMemory(),
  )

  prompt_text = chatgpt_chain.predict(history=history_string, human_input=text)

  if prompt_text == "false":
    output = "Por favor, proporciona más detalles sobre la imagen que estás buscando."
  else:
    try:
      response = openai.Image.create(prompt=prompt_text, n=1, size=IMAGE_SIZE)
      deissue = False
      image = response["data"][0]["url"]
    except:
      deissue = True

    if deissue:
      output = "Tu solicitud fue rechazada debido a nuestro sistema de seguridad. Tu solicitud puede contener texto que no está permitido por nuestro sistema de seguridad."
    else:
      output = ("image of " + prompt_text, image)

  return output


def process_calendar(text: str, history_string: str) -> str:
  """
    Procesa una solicitud de evento de calendario y genera una respuesta.

    Args:
        text (str): Mensaje de texto de entrada.
        history_string (str): Cadena de historial de conversación formateada.

    Returns:
        str:El tema detectado.
    """
  if agent is None:
    return f"{BOT_NAME}:Lo siento, pero no puedo acceder a tu calendario sin una configuración adecuada. Por favor, configura la clave API de Zapier para habilitar la integración del calendario."

  prompt_template = get_template("calendar")
  prompt = PromptTemplate(input_variables=["history", "human_input"],
                          template=prompt_template)

  chatgpt_chain = LLMChain(
    llm=initialize_language_model(SELECTED_MODEL),
    prompt=prompt,
    verbose=False,
    memory=ConversationBufferMemory(),
  )

  prompt_calendar = chatgpt_chain.predict(history=history_string,
                                          human_input=text)
  output = agent.run(prompt_calendar)

  return output
