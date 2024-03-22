from langchain.chat_models import ChatOpenAI
from config import TEMPERATURE_VALUE
from langchain import OpenAI


def initialize_language_model(selected_model):
  if selected_model == 'gpt-3':
    # Inicializa el modelo GPT-3 aquí
    return OpenAI(temperature=TEMPERATURE_VALUE)
  elif selected_model == 'gpt-3.5-turbo':
    # Inicializa el modelo GPT-3.5 aquí
    return ChatOpenAI(model_name="gpt-3.5-turbo",
                      temperature=TEMPERATURE_VALUE)
  elif selected_model == 'gpt-4':
    # Inicializa el modelo GPT-4 aquí
    return ChatOpenAI(model_name="gpt-4", temperature=TEMPERATURE_VALUE)
  else:
    raise ValueError(f"Invalid model selected: {selected_model}")
