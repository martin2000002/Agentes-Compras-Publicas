import requests
import json
import os

def api_colombia(
    fecha_inicio: str,
    fecha_fin: str,
    modalidad: str,
    save_dir: str = "data/raw",
    filename: str = None,
    append: bool = True
):
    """
    Descarga datos de procesos de contratación de Colombia SECOP II utilizando la API de datos.gov.co.
    Siempre retorna un dict con 'status' y 'message' para que el agente lo entienda.
    """
    try:
        if not fecha_inicio or not fecha_fin:
            return {"status": "error", "message": "❌ Debes proporcionar fecha_inicio y fecha_fin en formato 'YYYY-MM-DD'."}
        if not modalidad:
            return {"status": "error", "message": "❌ Debes proporcionar la modalidad del procedimiento a buscar."}
        os.makedirs(save_dir, exist_ok=True)
        
        if filename is None:
            filename = f"colombia.jsonl"
        
        filepath = os.path.join(save_dir, filename)
        
        url = "https://www.datos.gov.co/resource/p6dx-8zbt.json"
        
        params = {
            "$where": f"fecha_de_publicacion_del between '{fecha_inicio}' and '{fecha_fin}' AND modalidad_de_contratacion like '%{modalidad}%'",
            "$limit": 100000
        }

        print(f"📥 Descargando datos...\n")
        
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return {"status": "error", "message": f"❌ Error en la API: {response.status_code} - {response.text}"}
        
        data = response.json()
        mode = "a" if append else "w"
        with open(filepath, mode, encoding="utf-8") as f:
            for registro in data:
                f.write(json.dumps(registro, ensure_ascii=False) + "\n")
        print(f"\n✅ Descarga completa: {len(data)} registros en {filepath}")
        return {
            "status": "ok",
            "message": f"✅ Descarga completa: {len(data)} registros en {filepath}",
            "filepath": filepath,
            "total": len(data)
        }
    
    except Exception as e:
        return {"status": "error", "message": f"❌ Excepción: {str(e)}"}
