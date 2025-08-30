from agents import Agent, function_tool, Runner
from agentes.downloader.ecuador_downloader import ecuador_agent
from agentes.downloader.colombia_downloader import colombia_agent
from agentes.downloader.chile_downloader import chile_agent
from agentes.normalizer.normalizer_agent import normalizer_agent
from agentes.analyzer.analyzer_agent import analyzer_agent
from agentes.reporter.reporter_agent import reporter_agent

@function_tool
async def download_all_data(countries: list[str], year: int, search: str):
    for country in countries:
        if country.lower() == "ecuador":
            await Runner.run(ecuador_agent, input=f"Descarga todos los datos de Ecuador {year} con proceso {search}")
        elif country.lower() == "colombia":
            await Runner.run(colombia_agent, input=f"Descarga los datos de Colombia {year} con proceso {search}")
        elif country.lower() == "chile":
            await Runner.run(chile_agent, input=f"Descarga los datos de Chile {year} con proceso {search}")
    return "Download completed."

@function_tool
async def normalize_all(countries: list[str]):
    for country in countries:
        await Runner.run(normalizer_agent, input=f"Normaliza {country}")
    return "Normalization completed."

@function_tool
async def analyze_all(countries: list[str]):
    for country in countries:
        await Runner.run(analyzer_agent, input=f"Analiza {country}")
    return "Analysis completed."

@function_tool
async def generate_final_report():
    await Runner.run(reporter_agent, input="Crea el reporte de presupuesto")
    return "Report generated."

orchestrator_agent = Agent(
    name="OrchestratorAgent",
    instructions="""
    Cuando recibas una instrucción para procesar datos de compras públicas, extrae la lista de países, el año y el tipo de proceso (search) del prompt.
    Para cada país, llama a download_all_data con el país, año y tipo de proceso.
    Luego, para cada país, llama a normalize_all.
    Después, para cada país, llama a analyze_all.
    Finalmente, llama a generate_final_report una sola vez.
    Utiliza siempre los parámetros proporcionados en el prompt.
    """,
    tools=[
        download_all_data,
        normalize_all,
        analyze_all,
        generate_final_report
    ],
    model="gpt-4o"
)