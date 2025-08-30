import json
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from agents import Agent, function_tool
import os

@function_tool
def generar_reporte():
    try:
        dist_dir = "dist"
        os.makedirs(dist_dir, exist_ok=True)

        with open("data/analiced/analisis.json", "r", encoding="utf-8") as f:
            analysis = json.load(f)

        df = pd.DataFrame(analysis).T
        df = df[["salud", "educación", "infraestructura"]]

        png_path = os.path.join(dist_dir, "comparativo.png")
        plt.figure(figsize=(8, 5))
        df.plot(kind="bar")
        plt.title("Comparativo de presupuesto", fontweight="semibold")
        plt.ylabel("Presupuesto en USD")
        plt.tight_layout()
        plt.savefig(png_path)
        plt.close()

        pdf_path = os.path.join(dist_dir, "informe_presupuesto.pdf")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 12, "Informe de Presupuesto por País y Categoría", ln=True, align="C")

        pdf.set_font("Arial", size=12)
        pdf.ln(10)

        col_width = 40
        num_cols = len(df.columns) + 1
        table_width = col_width * num_cols
        page_width = pdf.w - 2 * pdf.l_margin
        x_start = (page_width - table_width) / 2 + pdf.l_margin

        pdf.set_x(x_start)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(col_width, 10, "", border=1)
        for col in df.columns:
            pdf.cell(col_width, 10, col.capitalize(), border=1)
        pdf.ln()

        for idx, row in df.iterrows():
            pdf.set_x(x_start)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(col_width, 10, idx.capitalize(), border=1)
            pdf.set_font("Arial", size=12)
            for val in row:
                pdf.cell(col_width, 10, f"${val:,.2f}", border=1)
            pdf.ln()

        pdf.ln(10)
        pdf.image(png_path, x=10, w=180)

        pdf.output(pdf_path)

        if os.path.exists(png_path):
            os.remove(png_path)

        return f"Reporte PDF generado exitosamente en {pdf_path}."
    except Exception as e:
        print(f"[generar_reporte] Error: {e}")
        return f"Error al generar el reporte: {e}"

reporter_agent = Agent(
    name="ReporterAgent",
    instructions="""
    Cuando te pidan crear el reporte de presupuesto comparativo, ejecuta la función generar_reporte.
    Si no te lo piden explícitamente, no hagas nada.
    """,
    tools=[generar_reporte],
    model="gpt-4o"
)