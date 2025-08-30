import os
from agents import Runner, set_default_openai_key
from agentes.orchestrator_agent import orchestrator_agent
from dotenv import load_dotenv
from agentes.analyzer.analyzer_agent import analyzer_agent
from agentes.reporter.reporter_agent import reporter_agent

load_dotenv(dotenv_path="enviroment.env")
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

def main():
    prompt = "Usa todos los datos de compras públicas del 2023 de procesos de subasta inversa de los países Ecuador, Colombia y Chile, y genera un reporte final."

    response = Runner.run_sync(orchestrator_agent, input=prompt)

    print(response)

if __name__ == "__main__":
    main()