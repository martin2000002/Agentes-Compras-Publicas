import os
import json
from agents import Agent, function_tool, Runner
from typing import TypedDict
from tqdm import tqdm
import re
import asyncio

save_lock = asyncio.Lock()

class NormalizedRecord(TypedDict):
    id: str
    entidad: str
    objeto: str
    presupuesto: float
    moneda: str
    lugar: str
    fecha_conv: str
    fecha_adj: str
    oferentes: int
    proveedor: str
    valor_adj: float
    justificacion: str

async def get_usd_rate(moneda: str) -> float:
    result = await Runner.run(currency_agent, input=moneda)
    output = result.output if hasattr(result, "output") else str(result)
    # Primer bloque JSON en la respuesta
    match = re.search(r"\{.*?\}", output, re.DOTALL)
    if match:
        json_str = match.group(0)
    else:
        json_str = output.strip()
    try:
        rate_info = json.loads(json_str)
        return float(rate_info.get("usd_rate", 1.0))
    except Exception as e:
        print(f"[get_usd_rate] Error: {e}\nOutput: {json_str}")
        return 1.0

def save_classification(result, pais: str, mode: str = "a"):
    try:
        pais = pais.lower()
        analiced_dir = "data/analiced"
        clasified_dir = os.path.join(analiced_dir, "clasified")
        os.makedirs(analiced_dir, exist_ok=True)
        os.makedirs(clasified_dir, exist_ok=True)
        output_path = os.path.join(clasified_dir, f"{pais}.jsonl")

        output = result.output if hasattr(result, "output") else str(result)
        match = re.search(r"\[\s*{.*?}\s*\]", output, re.DOTALL)
        if match:
            json_str = match.group(0)
        else:
            json_str = output.strip()
        try:
            items = json.loads(json_str)
            with open(output_path, mode, encoding="utf-8") as f:
                for obj in items:
                    f.write(json.dumps(obj, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[save_classification] Error parsing output: {e}\nOutput: {json_str}")
    except Exception as e:
        print(f"[save_classification] Error: {e}")

@function_tool
async def classify_country(pais: str) -> str:
    try:
        pais = pais.lower()
        input_path = f"data/normalized/{pais}.json"
        if not os.path.exists(input_path):
            return f"No existe el archivo para el país: {pais}"
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        num_registros = len(data)
        batch_size = 50 if num_registros > 10000 else 30
        total_batches = (len(data) + batch_size - 1) // batch_size

        semaphore = asyncio.Semaphore(10)

        pbar = tqdm(total=total_batches, desc=f"Analizando {pais}")

        async def process_batch(idx, batch):
            async with semaphore:
                result = await Runner.run(
                    classifier_agent, input=json.dumps(batch, ensure_ascii=False)
                )
                mode = "w" if idx == 0 else "a"
                async with save_lock:
                    save_classification(result, pais, mode)
                pbar.update(1)

        tasks = []
        for idx, i in enumerate(range(0, len(data), batch_size)):
            batch = data[i:i+batch_size]
            tasks.append(process_batch(idx, batch))

        await asyncio.gather(*tasks)
        pbar.close()
        return f"Análisis de {pais} completado."
    except Exception as e:
        print(f"[classify_country] Error: {e}")
        return f"Error al analizar {pais}: {e}"
    
@function_tool
async def analyze_country(pais: str):
    try:
        pais = pais.lower()
        clasified_path = f"data/analiced/clasified/{pais}.jsonl"
        analysis_path = "data/analiced/analisis.json"
        categorias = ["salud", "educación", "infraestructura"]
        acumulados = {cat: 0.0 for cat in categorias}

        os.makedirs(os.path.dirname(analysis_path), exist_ok=True)

        normalized_path = f"data/normalized/{pais}.json"
        moneda = "USD"
        if os.path.exists(normalized_path):
            with open(normalized_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data and isinstance(data, list):
                    moneda = data[0].get("moneda", "USD")
                                         
        if os.path.exists(clasified_path):
            with open(clasified_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        registro = json.loads(line)
                        categoria = registro.get("categoria", "").lower()
                        presupuesto = registro.get("presupuesto")
                        if categoria in categorias and presupuesto is not None:
                            acumulados[categoria] += float(presupuesto)
                    except Exception as e:
                        print(f"[analyze_country] Error parsing line: {e}\nLine: {line}")
        else:
            print(f"[analyze_country] No existe el archivo clasificado para {pais}")

        usd_rate = await get_usd_rate(moneda)

        acumulados_usd = {cat: acumulados[cat] * usd_rate for cat in categorias}

        if not os.path.exists(analysis_path):
            with open(analysis_path, "w", encoding="utf-8") as f:
                json.dump({}, f)

        with open(analysis_path, "r", encoding="utf-8") as f:
            analysis = json.load(f)

        analysis[pais] = acumulados_usd

        with open(analysis_path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)

        return f"Análisis de {pais} completado. Resultados guardados en {analysis_path}"
    
    except Exception as e:
        print(f"[analyze_country] Error: {e}")

currency_agent = Agent(
    name="CurrencyAgent",
    instructions="""
    Recibe el nombre de una moneda y devuelve el tipo de cambio actual a USD como un número flotante. Obten el valor mas reciente!
    Ejemplo de respuesta: {"moneda": "PEN", "usd_rate": 0.27}
    Independientemente de si puedes obtener el valor mas reciente o no, no me lo digas solo responder en el formato json que te dije con el ultimo usd_rate al que tengas acceso.
    """,
    model="gpt-4o"
)

classifier_agent = Agent(
    name="ClassifierAgent",
    instructions="""
    Recibe un batch de registros de compras públicas en formato JSON.
    Clasifica cada registro en una de las siguientes categorías: Salud, Educación, Infraestructura u Otro.
    Devuelve una lista JSON, donde cada elemento tiene la estructura:
    {
    "categoria": [otra, salud, educación o infraestructura (siempre en minúsculas)],
    "presupuesto": [valor del presupuesto]
    }
    No uses bloques de triple backtick ni texto extra, solo la lista JSON.
    """,
    model="gpt-4o"
)

analyzer_agent = Agent(
    name="analyzerAgent",
    instructions="""
    Recibirás el nombre de un país.
    Con eso primero ejecuta classify_country.
    Luego ejecuta analyze_country.
    """,
    tools=[classify_country, analyze_country],
    model="gpt-4o"
)