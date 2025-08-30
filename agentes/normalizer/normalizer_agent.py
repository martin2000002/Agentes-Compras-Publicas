import json
from pathlib import Path
from typing import TypedDict
from agents import Agent, function_tool
import re
from tqdm import tqdm

class MappingDictStr(TypedDict):
    id: str
    entidad: str
    objeto: str
    presupuesto: str
    moneda: str
    lugar: str
    fecha_conv: str
    fecha_adj: str
    oferentes: str
    proveedor: str
    valor_adj: str
    justificacion: str

class MappingDict(TypedDict):
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

def mappingdict_to_schema(cls):
    """
    Devuelve solo los nombres de los atributos de la clase TypedDict.
    """
    return "\n".join([f"    {k}" for k in cls.__annotations__.keys()])

def resolve_path(record, path):
    """
    Extrae el valor de un registro usando una ruta tipo 'awards[0].value.amount'.
    Si la ruta no existe, retorna None.
    """
    # Soporte para len(...)
    len_match = re.match(r"len\((.+)\)", path)
    if len_match:
        inner_path = len_match.group(1)
        value = resolve_path(record, inner_path)
        if isinstance(value, list):
            return len(value)
        else:
            return 0
        
    parts = re.split(r'\.|\[|\]', path)
    parts = [p for p in parts if p != '']
    value = record
    try:
        for part in parts:
            if part.isdigit():
                value = value[int(part)]
            else:
                value = value.get(part)
        return value
    except Exception:
        return None

def is_quemar(value: str):
    """
    Detecta si el valor tiene la sintaxis QUEMAR(valor) y retorna el valor quemado.
    """
    match = re.match(r"QUEMAR\((.*?)\)", value)
    if match:
        return match.group(1)
    return None

@function_tool
def normalize_dataset(country: str, mapping: MappingDictStr):
    """
    Normaliza el dataset raw del país usando el mapping y muestra una barra de progreso.
    Permite valores quemados en el mapping con la sintaxis QUEMAR(valor).
    Guarda el resultado en normalized.
    """
    try:
        country = country.lower()
        raw_path = f"data/raw/{country}.jsonl"
        normalized_dir = "data/normalized"
        normalized_path = f"{normalized_dir}/{country}.json"
        normalized = []

        Path(normalized_dir).mkdir(parents=True, exist_ok=True)

        with open(raw_path, "r", encoding="utf-8") as f:
            total = sum(1 for _ in f)

        with open(raw_path, "r", encoding="utf-8") as f:
            for line in tqdm(f, total=total, desc=f"Normalizando {country}"):
                record = json.loads(line)
                norm_record = {}
                for target, source in mapping.items():
                    tipo = MappingDict.__annotations__[target]
                    valor = None
                    if isinstance(source, str):
                        quemado = is_quemar(source)
                        if quemado is not None:
                            valor = quemado
                        else:
                            valor = resolve_path(record, source)
                    else:
                        valor = source

                    if valor is not None:
                        try:
                            if tipo == int:
                                valor = int(valor)
                            elif tipo == float:
                                valor = float(valor)
                            elif tipo == str:
                                valor = str(valor)
                        except Exception:
                            pass

                    norm_record[target] = valor
                normalized.append(norm_record)

        with open(normalized_path, "w", encoding="utf-8") as f:
            json.dump(normalized, f, ensure_ascii=False, indent=2)
        return f"Guardado en {normalized_path}"
    except Exception as e:
        return print(f"Error al normalizar!!: {str(e)}")
    
@function_tool
def get_sample_records(country: str):
    """
    Lee los primeros 25 registros del archivo raw de un país.
    """
    country = country.lower()
    raw_path = f"data/raw/{country}.jsonl"
    records = []
    with open(raw_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= 25:
                break
            records.append(json.loads(line))
    return records

TARGET_SCHEMA = mappingdict_to_schema(MappingDictStr)

normalizer_agent = Agent(
    name="NormalizerAgent",
    instructions=f"""
    Eres un agente encargado de normalizar datasets de compras públicas.
    Cuando te indiquen el país, usa la tool 'get_sample_records' para obtener los primeros 25 registros del dataset raw.
    Analiza esos registros y genera un mapping para transformar los campos al siguiente esquema: {TARGET_SCHEMA}.
    El mapping debe ser un diccionario donde cada clave es el campo destino y cada valor es:
    - La ruta exacta del campo en el registro (por ejemplo: 'awards[0].value.amount', 'buyer.name', 'len(tender.tenderers)').
    - Si notas que no hay un campo que indique la moneda, quema su valor con la moneda local del país. Para hacerlo usa la sintaxis QUEMAR(valor), por ejemplo: 'moneda': 'QUEMAR(COP)'.
    - Los oferentes debe ser la cantidad de oferentes, mas qué oferentes.
    No incluyas comentarios ni condiciones en los valores del mapping, solo la ruta. Para el unico campo en el que puedes no poner la ruta es moneda, que puedes quemar su valor.
    Luego llama a la tool 'normalize_dataset' con el país y el mapping generado para normalizar todo el dataset.
    Guarda el resultado en data/normalized/.
    """,
    tools=[get_sample_records, normalize_dataset],
    model="gpt-4o"
)  