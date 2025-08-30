from agents import Agent, function_tool

@function_tool
def EcuadorAPI_Tool(year: int = None,
                    search: str = None,
                    page: int = 1,
                    buyer: str = None,
                    supplier: str = None,
                    all: bool = False,
                    append: bool = True):
    from utils.apis.ecuador import api_ecuador
    response = api_ecuador(
        year=year,
        search=search,
        page=page,
        buyer=buyer,
        supplier=supplier,
        append=append,
        all=all,
        reset=True
    )
    return response

ecuador_agent = Agent(
    name="Ecuador Downloader",
    instructions=(
        "Eres un agente encargado de descargar datos de procesos de Ecuador."
        "Recibes instrucciones en lenguaje natural y conviertes esas instrucciones en los parámetros de la función EcuadorAPI_Tool."
        "Tu objetivo es descargar los datos correctamente según los parámetros indicados."
    ),
    model="o3-mini",
    tools=[EcuadorAPI_Tool],
)
