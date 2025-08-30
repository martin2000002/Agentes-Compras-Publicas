from agents import Agent, function_tool

@function_tool
def ColombiaAPI_Tool(
    fecha_inicio: str = None,
    fecha_fin: str = None,
    modalidad: str = None
):
    from utils.apis.colombia import api_colombia
    
    response = api_colombia(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        modalidad=modalidad,
        append=False
    )
    return response

colombia_agent = Agent(
    name="Colombia Downloader",
    instructions=(
        "Eres un agente encargado de descargar datos de procesos de Colombia (SECOP II). "
        "Recibes instrucciones en lenguaje natural y conviertes esas instrucciones en los parámetros fecha_inicio, fecha_fin y modalidad de la función ColombiaAPI_Tool. Las fechas tienen este formato 'YYYY-MM-DD'."
        "Tu objetivo es descargar los datos correctamente según los parámetros indicados."
    ),
    model="o3-mini",
    tools=[ColombiaAPI_Tool],
)
