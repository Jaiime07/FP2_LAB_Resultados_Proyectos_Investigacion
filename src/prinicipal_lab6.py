from factoria import Factoria
import os

def main():
    # 0. Definimos las rutas a todos los ficheros necesarios
    ruta_a1 = 'Anexo I.xlsx'
    ruta_a2 = 'Anexo II.xlsx'
    ruta_a3 = 'Anexo III.xlsx'
    ruta_a4 = 'Anexo IV.xlsx'
    
    # Nuevos archivos del Lab 6
    ruta_pob = 'poblacion_ccaa.xlsx'
    ruta_json = 'diccionario_areas.json'
    ruta_salida_financiacion = 'resultado_financiacion.xlsx'

    print("Cargando miles de datos desde los Excel... un poco de paciencia.\n")
    gestor_todos, gestor_concedidos, gestor_contratos = Factoria.leer_datos(
        ruta_a1, ruta_a2, ruta_a3, ruta_a4
    )
    print("¡Datos cargados correctamente!\n")
    print("=" * 60)

    # --- REQUISITO 1: Tasas de éxito por CCAA ---
    print("\n--- 1. TASAS DE ÉXITO POR COMUNIDAD AUTÓNOMA ---")
    tasas_ccaa = gestor_todos.tasa_exito_ccaa()
    # Ordenamos alfabéticamente por el nombre de la CCAA para que quede limpio
    for ccaa, datos in sorted(tasas_ccaa.items()):
        print(f"📍 {ccaa}:")
        print(f"    Solicitados: {datos['solicitados']} proyectos")
        print(f"    Tasa Concedidos: {datos['tasa_concedidos']:.2f}%")
        print(f"    Tasa Contratados: {datos['tasa_contratos']:.2f}%")

    # --- REQUISITO 2: Financiación por habitante ---
    print("\n--- 2. FINANCIACIÓN POR HABITANTE ---")
    # Comprobamos que el excel de población existe antes de intentar cruzar datos
    if os.path.exists(ruta_pob):
        gestor_todos.financiacion_por_habitante(ruta_pob, ruta_salida_financiacion)
        print(f"✅ Excel generado con éxito: '{ruta_salida_financiacion}'. ¡Ábrelo para ver los datos cruzados!")
    else:
        print(f"⚠️ Error: No se encontró '{ruta_pob}'. ¿Ejecutaste generador_datos.py?")

    # --- REQUISITO 3: Top N Entidades ---
    N = 5  # Puedes cambiar este número para ver el Top 10 o Top 3
    print(f"\n--- 3. TOP {N} ENTIDADES CON MAYOR TASA DE ÉXITO ---")
    top_entidades = gestor_todos.top_n_entidades(N)
    for i, (entidad, t_conc, t_cont) in enumerate(top_entidades, 1):
        print(f"{i}. {entidad}")
        print(f"   ↳ Concedidos: {t_conc:.2f}% | Contratados: {t_cont:.2f}%")

    # --- REQUISITO 4: Tasas por Macro Área ---
    print("\n--- 4. TASAS DE ÉXITO POR MACRO ÁREA ---")
    if os.path.exists(ruta_json):
        # Llamamos a nuestra función pasándole que queremos agrupar por 'macro_area'
        tasas_macro = gestor_todos.tasas_exito_por_clasificacion(ruta_json, 'macro_area')
        for macro, datos in tasas_macro.items():
            print(f"📚 {macro}:")
            print(f"    Solicitados: {datos['solicitados']}")
            print(f"    Tasa Concedidos: {datos['tasa_concedidos']:.2f}%")
            print(f"    Tasa Contratados: {datos['tasa_contratos']:.2f}%")
    else:
        print(f"⚠️ Error: No se encontró el diccionario '{ruta_json}'.")

    print("\n" + "=" * 60)
    print("¡Análisis del Laboratorio 6 completado con éxito!")

if __name__ == '__main__':
    main()