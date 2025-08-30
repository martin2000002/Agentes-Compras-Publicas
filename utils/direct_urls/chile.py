import requests
import os
import gzip
from tqdm import tqdm

def url_chile(
    year: int,
    search: list[str] = None,
    save_dir: str = "data/raw",
    filename: str = None,
    skip_download: bool = False,
    skip_extract: bool = False
):
    """
    Descarga, extrae y filtra el JSON de Chile de la plataforma Open Contracting para un año específico.
    Retorna un dict con status, message, filepath y total.
    """
    try:
        os.makedirs(save_dir, exist_ok=True)

        if filename is None:
            filename = f"chile.jsonl"

        gz_filename = f"chile_sin_filtrar.jsonl.gz"
        gz_path = os.path.join(save_dir, gz_filename)
        jsonl_filename = gz_filename.replace(".gz", "")
        jsonl_path = os.path.join(save_dir, jsonl_filename)

        # DESCARGA
        if not skip_download:
            url = f"https://data.open-contracting.org/es/publication/144/download?name={year}.jsonl.gz"
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            chunk_size = 8192
            
            with open(gz_path, "wb") as f, tqdm(
                total=total_size, unit='B', unit_scale=True, desc=f"Descargando {gz_filename}"
            ) as pbar:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    pbar.update(len(chunk))
            print(f"✅ Archivo descargado en {gz_path}")
        else:
            if not os.path.exists(gz_path):
                return {
                    "status": "error",
                    "message": f"❌ skip_download=True pero no se encontró el archivo {gz_path}"
                }
            print(f"⚡ Saltando descarga, usando {gz_path}")

        # EXTRACCIÓN
        if not skip_extract:
            gz_size = os.path.getsize(gz_path)
            chunk_size = 8192
            aprox_jsonl_size = gz_size * 9.88

            with gzip.open(gz_path, 'rb') as f_in, open(jsonl_path, 'wb') as f_out, tqdm(
                total=aprox_jsonl_size, unit='B', unit_scale=True, desc=f"Extrayendo {jsonl_filename}"
            ) as pbar:
                while True:
                    chunk = f_in.read(chunk_size)
                    if not chunk:
                        break
                    f_out.write(chunk)
                    pbar.update(len(chunk))
            print(f"✅ Archivo extraído en {jsonl_path}")
        else:
            if not os.path.exists(jsonl_path):
                return {
                    "status": "error",
                    "message": f"❌ skip_extract=True pero no se encontró el archivo {jsonl_path}"
                }
            print(f"⚡ Saltando extracción, usando {jsonl_path}")

        # FILTRADO
        if search:
            search_lower = [s.lower() for s in search]
            filtered_path = os.path.join(save_dir, filename)
            total_lines = sum(1 for _ in open(jsonl_path, 'r', encoding='utf-8'))
            matches = 0
            with open(jsonl_path, 'r', encoding='utf-8') as fin, open(filtered_path, 'w', encoding='utf-8') as fout, tqdm(
                total=total_lines, desc=f"Filtrando registros por keywords"
            ) as pbar:
                for line in fin:
                    try:
                        line_lower = line.lower()
                        if any(keyword in line_lower for keyword in search_lower):
                            fout.write(line)
                            matches += 1
                    except:
                        pass
                    pbar.update(1)
            print(f"✅ Archivo filtrado guardado en {filtered_path}")
            return {
                "status": "ok",
                "message": f"✅ Descarga y filtrado completo: {matches} registros en {filtered_path}",
                "filepath": filtered_path,
                "total": matches
            }

        # GUARDADO
        total_lines = sum(1 for _ in open(jsonl_path, 'r', encoding='utf-8'))
        print(f"✅ Archivo final listo en {jsonl_path} con {total_lines} registros")
        return {
            "status": "ok",
            "message": f"✅ Descarga completa: {total_lines} registros en {jsonl_path}",
            "filepath": jsonl_path,
            "total": total_lines
        }

    except Exception as e:
        print(f"❌ Excepción: {str(e)}")
        return {"status": "error", "message": f"❌ Excepción: {str(e)}"}
