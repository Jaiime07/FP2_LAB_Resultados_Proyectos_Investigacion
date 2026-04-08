import pandas as pd
import json

def generar_excel_poblacion():
    datos_poblacion = {
        "Comunidad Autónoma": [
            "ANDALUCIA", "ARAGON", "BALEARES", "C.VALENCIANA", "CANARIAS", 
            "CANTABRIA", "CASTILLA Y LEON", "CASTILLA-LA MANCHA", "CATALUÑA", 
            "CEUTA", "EXTREMADURA", "GALICIA", "LA RIOJA", "MADRID", 
            "MELILLA", "MURCIA", "NAVARRA", "PAIS VASCO", "PDO.ASTURIAS"
        ],
        "Poblacion": [
            8628026, 1349372, 1232014, 5319448, 2238336, 
            591164, 2390452, 2101404, 8021153, 
            83287, 1053458, 2705741, 324009, 7002363, 
            85812, 1569706, 678093, 2227746, 1008874
        ]
    }
    
    df = pd.DataFrame(datos_poblacion)
    # Ruta arreglada (se guardará en el mismo sitio desde donde ejecutes el script)
    ruta_excel = "poblacion_ccaa.xlsx" 
    df.to_excel(ruta_excel, index=False)
    print(f"✅ Excel de población generado con éxito en: {ruta_excel}")


def generar_diccionario_areas():
    # Estructura jerárquica real basada en la clasificación de la AEI
    macro_areas = {
        "Ciencias Matemáticas, Físicas, Químicas e Ingenierías": {
            "FIS": ["AYA", "ESP", "FPN", "FAB", "FCM", "FYA"],
            "MTM": ["MTM"],
            "PIN": ["ICA", "IBI", "IEA", "INA"],
            "TIC": ["INF", "MNF", "TCO"],
            "EYT": ["ENE", "TRA"],
            "CTQ": ["QMC", "IQM"],
            "MAT": ["MAT"]
        },
        "Ciencias de la Vida": {
            "BIO": ["CAN", "ESN", "DPT", "FOS", "IIT", "BME"],
            "BIF": ["BIF", "BCB", "BGG", "BTC"],
            "CTM": ["CTA", "BDV", "MAR", "PLR"],
            "CAA": ["AGR", "ALI", "GYA"],
            "MED": ["MED"]
        },
        "Ciencias Sociales y Humanidades": {
            "CSO": ["COM", "CPO", "FEM", "GEO", "SOC"],
            "DER": ["DER"],
            "ECO": ["ECO"],
            "EDU": ["EDU"],
            "FLA": ["ART", "FIL", "LFL", "LYL"],
            "PHA": ["PSI"],
            "HA":  ["ARQ", "HIS"]
        }
    }
    
    ruta_json = "diccionario_areas.json"
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(macro_areas, f, ensure_ascii=False, indent=4)
    print(f"✅ Diccionario de áreas generado con éxito en: {ruta_json}")

if __name__ == "__main__":
    generar_excel_poblacion()
    generar_diccionario_areas()