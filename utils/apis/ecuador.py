import time
import requests
import json
import os
import sys

def api_ecuador(
    year: int,
    search: str = None,
    page: int = 1,
    buyer: str = None,
    supplier: str = None,
    save_dir: str = "data/raw",
    filename: str = None,
    append: bool = True,
    all: bool = False,
    reset: bool = False 
):
    """
    Descarga procesos de Ecuador usando la API y guarda en formato JSON Lines.
    Incluye barra de progreso si all=True.
    Si reset=True, borra el contenido del archivo antes de descargar.
    Retorna un dict con status, message, filepath y total.
    """

    try:
        if search and len(search) < 3:
            return {"status": "error", "message": "❌ El parámetro 'search' debe tener al menos 3 caracteres"}
        if buyer and len(buyer) < 3:
            return {"status": "error", "message": "❌ El parámetro 'buyer' debe tener al menos 3 caracteres"}
        if supplier and len(supplier) < 3:
            return {"status": "error", "message": "❌ El parámetro 'supplier' debe tener al menos 3 caracteres"}
        
        os.makedirs(save_dir, exist_ok=True)
        if filename is None:
            filename = f"ecuador.jsonl"
        filepath = os.path.join(save_dir, filename)

        if reset and os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                pass
        
        if filename is None:
            filename = f"ecuador.jsonl"
        
        filepath = os.path.join(save_dir, filename)

        base_url = "https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/api/search_ocds"
        
        total_registros = 0
        
        if all:
            init_params = {"year": year, "page": 1}
            if buyer:
                init_params["buyer"] = buyer
            if supplier:
                init_params["supplier"] = supplier
            if search:
                init_params["search"] = search

            init_resp = requests.get(base_url, params=init_params)
            init_resp.raise_for_status()
            meta = init_resp.json()
            total_pages = meta.get("pages", 1)

            print(f"📥 Descargando {total_pages} páginas de datos del año {year}...\n")

            current_page = 1
            while current_page <= total_pages:
                params = {"year": year, "page": current_page}
                if buyer:
                    params["buyer"] = buyer
                if supplier:
                    params["supplier"] = supplier
                if search:
                    params["search"] = search
                
                response = requests.get(base_url, params=params)

                if response.status_code == 429:  
                    print("⚠️ Límite alcanzado, esperando 30 segundos...")
                    time.sleep(30)
                    continue
                response.raise_for_status()

                data = response.json().get("data", [])
                if not data:
                    break
                
                mode = "a" if (append or current_page > 1) else "w"
                with open(filepath, mode, encoding="utf-8") as f:
                    for registro in data:
                        f.write(json.dumps(registro, ensure_ascii=False) + "\n")
                
                total_registros += len(data)

                progress = int((current_page / total_pages) * 20)
                bar = "█" * progress + "-" * (20 - progress)
                sys.stdout.write(
                    f"\rPág. {current_page}/{total_pages}, "
                    f"Num. Registros {len(data)}, "
                    f"[{bar}] {int((current_page/total_pages)*100)}%"
                )
                sys.stdout.flush()

                current_page += 1
            
            print()
        
        else:
            params = {"year": year, "page": page}
            if buyer:
                params["buyer"] = buyer
            if supplier:
                params["supplier"] = supplier
            if search:
                params["search"] = search
            
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            
            data = response.json().get("data", [])
            mode = "a" if append else "w"
            with open(filepath, mode, encoding="utf-8") as f:
                for registro in data:
                    f.write(json.dumps(registro, ensure_ascii=False) + "\n")
            
            print(f"Guardados {len(data)} registros en {filepath} (append={append})")
            total_registros = len(data)
        
        print(f"\n✅ Descarga completa: {total_registros} registros en {filepath}")
        return {
            "status": "ok",
            "message": f"✅ Descarga completa: {total_registros} registros en {filepath}",
            "filepath": filepath,
            "total": total_registros
        }
    
    except Exception as e:
        print(f"❌ Excepción: {str(e)}")
        return {"status": "error", "message": f"❌ Excepción: {str(e)}"}
