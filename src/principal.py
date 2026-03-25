from factoria import Factoria

def main() -> None:
    # 0. Definimos las rutas a los ficheros (ajusta los nombres a los tuyos)
    # Suponemos que has guardado los Excel como archivos CSV separados por comas
   # 0. Definimos las rutas a los ficheros
    ruta_a1 = 'Anexo I.xlsx'
    ruta_a2 = 'Anexo II.xlsx'
    ruta_a3 = 'Anexo III.xlsx'
    ruta_a4 = 'Anexo IV.xlsx'

    print("Cargando datos desde los ficheros... paciencia, que son muchos.\n")
    
    # Arrancamos la factoría
    gestor_todos, gestor_concedidos, gestor_contratos = Factoria.leer_datos(
        ruta_a1, ruta_a2, ruta_a3, ruta_a4
    )

    # -------------------------------------------------------------------------
    # 1) Mostrar el total de registros almacenados en cada clase Gestor
    # -------------------------------------------------------------------------
    print("--- 1. TOTAL DE REGISTROS ALMACENADOS ---")
    print(f"Total de proyectos (Gestor_Proyecto): {len(gestor_todos.proyectos)}")
    print(f"Proyectos concedidos (Gestor_ProyectoConcedido): {len(gestor_concedidos.proyectos)}")
    print(f"Proyectos con contrato (Gestor_ProyectoContrato): {len(gestor_contratos.proyectos)}")
    print("-" * 40 + "\n")

    # -------------------------------------------------------------------------
    # 2) Estadísticas: Tasa de proyectos concedidos sobre solicitados por CCAA
    # -------------------------------------------------------------------------
    print("--- 2. TASA DE ÉXITO POR COMUNIDAD AUTÓNOMA ---")
    # Diccionario para ir contando: {'ANDALUCIA': {'solicitados': X, 'concedidos': Y}, ...}
    stats_ccaa: dict[str, dict[str, int]] = {}
    
    for p in gestor_todos.proyectos:
        ccaa = p.comunidad_autonoma
        if ccaa not in stats_ccaa:
            stats_ccaa[ccaa] = {'solicitados': 0, 'concedidos': 0}
            
        stats_ccaa[ccaa]['solicitados'] += 1
        if p.concedido:
            stats_ccaa[ccaa]['concedidos'] += 1

    # Mostramos los resultados ordenados alfabéticamente
    for ccaa in sorted(stats_ccaa.keys()):
        datos = stats_ccaa[ccaa]
        solicitados = datos['solicitados']
        concedidos = datos['concedidos']
        
        # Evitamos división por cero por si acaso
        tasa = (concedidos / solicitados * 100) if solicitados > 0 else 0.0
        print(f"{ccaa}: {tasa:.2f}% (Concedidos: {concedidos} / Solicitados: {solicitados})")
    
    print("-" * 40 + "\n")

    # -------------------------------------------------------------------------
    # 3) Total de importes global y por comunidad autónoma
    # -------------------------------------------------------------------------
    print("--- 3. IMPORTES CONCEDIDOS (PRESUPUESTOS) ---")
    importe_global: float = 0.0
    importes_ccaa: dict[str, float] = {}
    
    # Recorremos solo los concedidos, que son los que tienen la propiedad "presupuesto"
    for p in gestor_concedidos.proyectos:
        ccaa = p.comunidad_autonoma
        presupuesto = p.presupuesto
        
        importe_global += presupuesto
        importes_ccaa[ccaa] = importes_ccaa.get(ccaa, 0.0) + presupuesto

    # Función auxiliar para imprimir bonito en euros (ej. 1.234.567,89 €)
    def formato_euros(valor: float) -> str:
        return f"{valor:,.2f} €".replace(',', 'X').replace('.', ',').replace('X', '.')

    print(f"**IMPORTE GLOBAL CONCEDIDO**: {formato_euros(importe_global)}")
    print("\nDesglose por Comunidad Autónoma (ordenado de mayor a menor):")
    
    # Ordenamos el diccionario por importe (de mayor a menor)
    importes_ordenados = sorted(importes_ccaa.items(), key=lambda item: item[1], reverse=True)
    
    for ccaa, importe in importes_ordenados:
        print(f"  - {ccaa}: {formato_euros(importe)}")


if __name__ == '__main__':
    main()