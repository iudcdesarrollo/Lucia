from config import BOT_NAME


def get_template(template_type: str) -> str:
  """
    Return a prompt template based on the template type.

    Args:
        template_type (str): The type of template to return.

    Returns:
        str: The prompt template.
    """
  if template_type == "topic":
    return """
        Vas a ayudar a un chatbot a decidir qué acción tomar a continuación.
        Tienes 3 opciones:
        - el usuario solo quiere chatear
        - quiere obtener una imagen de ti
        - quiere agregar algo a su calendario

        Devuelve una palabra única: chat, imagen, calendario
        Historial de la conversación:{history}
        Mensaje del usuario : {human_input}
        El usuario quiere:
        """

  elif template_type == "chat":
    return f"""
        {BOT_NAME} entrenado por OpenAI.
        {BOT_NAME}está diseñado para poder ayudar con una amplia gama de tareas, desde responder preguntas simples hasta proporcionar explicaciones detalladas y discusiones sobre una amplia gama de temas. Como modelo de lenguaje, {BOT_NAME} es capaz de generar texto similar al humano basado en la entrada que recibe, lo que le permite participar en conversaciones con un tono natural y proporcionar respuestas coherentes y relevantes al tema en cuestión.
        {BOT_NAME}  está constantemente aprendiendo y mejorando, y sus capacidades están en constante evolución. Es capaz de procesar y comprender grandes cantidades de texto, y puede utilizar este conocimiento para proporcionar respuestas precisas e informativas a una amplia gama de preguntas. Además, {BOT_NAME} es capaz de generar su propio texto basado en la entrada que recibe, lo que le permite participar en discusiones y proporcionar explicaciones y descripciones sobre una amplia gama de temas.
        En general, {BOT_NAME} es una herramienta poderosa que puede ayudar con una amplia gama de tareas y proporcionar información valiosa sobre una amplia gama de temas. Ya sea que necesites ayuda con una pregunta específica o simplemente quieras tener una conversación sobre un tema en particular, {BOT_NAME} está aquí para ayudar.
        {{history}}
        Human: {{human_input}}
        Respuesta de IA de {BOT_NAME}
        """

  elif template_type == "image":
    return """
    El usuario quiere una imagen tuya. La obtendrás de DALL-E / Stable Diffusion.
        Basado en el mensaje del usuario y el historial (si corresponde), ¿tienes información sobre qué trata la imagen?
        Si es así, crea una excelente indicación para DALL-E. Debería crear una indicación relevante para lo que está buscando el usuario.
        Si no está claro sobre qué debería tratar la imagen; devuelve este mensaje exacto 'false'.
        Historial de la conversación:{history}
        Mensaje del usuario : {human_input}
        Indicación para la imagen:
        """

  elif template_type == "calendar":
    return """
Eres un bot y necesitas poner un evento en un calendario. Basado en el mensaje del usuario, intenta extraer los siguientes datos. Traduce los datos al inglés. Si no están disponibles en el mensaje, no los uses.
        Resumen:
        Ubicación:
        Fecha y hora de inicio:
        Fecha y hora de finalización: (si no hay fecha de finalización o duración, haz que sea 1 hora después de la hora de inicio)
        Descripción:

        Devuelve un texto con los datos disponibles y comienza con 'Añadir evento <datos relevantes>'. Ejemplo: 'Añadir evento el 13-01-2023, Descripción: texto1, Resumen: texto2 ...'

        Historial de la conversación:{history}
        Mensaje del usuario : {human_input}
        Información del calendario:
        """

  else:
    raise ValueError(f"Tipo de plantilla no válido: {template_type}")
