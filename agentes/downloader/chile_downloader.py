from agents import Agent, function_tool
from utils.direct_urls.chile import url_chile

@function_tool
def ChileDownloader_Tool(
    year: int,
    search: list[str] = None,
):
    """
    Descarga, extrae y filtra los procesos de ChileCompra.
    - year: año de los procesos
    - search: lista de keywords para filtrar (ej: ["subasta", "licitación"])
    """
    
    filepath = url_chile(
        year=year,
        search=search,
    )
    return f"✅ Archivo procesado en {filepath}"

chile_agent = Agent(
    name="Chile Downloader",
    instructions=(
        "Eres un agente encargado de descargar datos de procesos de ChileCompra.\n"
        "Recibes instrucciones en lenguaje natural y conviertes esas instrucciones en los parámetros de la función ChileDownloader_Tool.\n"
        "El usuario puede pedir procesos de un año específico y de un tipo específico (ej: subastas inversas, licitaciones). Si recibes una frase separa a cada palabra de la frase y ponga en un arreglo de strings. (ej: subasta inversa -> ['subasta', 'inversa'])"
        "Debes mapear esas instrucciones al parámetro 'year' y a la lista 'search'.\n"
        "Tu objetivo es devolver el archivo procesado con los datos filtrados."
    ),
    model="o3-mini",
    tools=[ChileDownloader_Tool],
)
