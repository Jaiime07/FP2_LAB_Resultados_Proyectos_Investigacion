import pandas as pd
from typing import List, Dict, Tuple, Callable
from proyectos import Proyecto, ProyectoConcedido, ProyectoContrato
import json
import matplotlib.pyplot as plt
from wordcloud import WordCloud


class Gestor_Proyecto:
    """Contenedor para todos los proyectos (concedidos y denegados)."""
    
    def __init__(self):
        self.proyectos: List[Proyecto] = []
        
    def agregar(self, proyecto: Proyecto) -> None:
        self.proyectos.append(proyecto)

    # --- NUEVAS FUNCIONALIDADES (LAB 6) ---

    # --- MOTOR BASE DE CÁLCULO (DRY) ---

    def _agrupar_y_calcular_tasas(self, extractor_clave: Callable[[Proyecto], str]) -> Dict[str, Dict[str, float]]:
        """
        Método privado centralizado que agrupa proyectos y calcula tasas.
        Recibe una función 'extractor_clave' que le dice qué atributo extraer de cada proyecto.
        """
        stats = {}
        for p in self.proyectos:
            # Aquí ocurre la magia: extraemos la clave usando la regla que nos pasen
            clave = extractor_clave(p) 
            
            if clave not in stats:
                stats[clave] = {'solicitados': 0, 'concedidos': 0, 'contratados': 0}
            
            stats[clave]['solicitados'] += 1
            if p.concedido:
                stats[clave]['concedidos'] += 1
            if isinstance(p, ProyectoConcedido) and p.contratado_predoctoral: # verificamos que pertenezca a ProyectoConcedido
                stats[clave]['contratados'] += 1
                
        resultados = {}
        for clave, data in stats.items():   # ojo! data es un diccionario anidado con los contadores de cada clave (dentro de stats)
            solic = data['solicitados']
            tasa_conc = (data['concedidos'] / solic * 100) if solic > 0 else 0.0
            tasa_cont = (data['contratados'] / solic * 100) if solic > 0 else 0.0
            resultados[clave] = {
                'solicitados': solic,
                'tasa_concedidos': tasa_conc, 
                'tasa_contratos': tasa_cont
            }
        return resultados


    def _cargar_mapeo_areas(self, ruta_json: str) -> Dict[str, Dict[str, str]]:
        """Función auxiliar para aplanar el JSON jerárquico y facilitar la búsqueda."""
        with open(ruta_json, 'r', encoding='utf-8') as f:
            jerarquia = json.load(f)
            
        mapeo = {}
        for macro_area, areas in jerarquia.items():
            for area, subareas in areas.items():
                for subarea in subareas:
                    # Relacionamos cada subárea directamente con su área y macro área
                    mapeo[subarea] = {'area': area, 'macro_area': macro_area}
        return mapeo
    
    # --- FUNCIONES PÚBLICAS REFACTORIZADAS ---

    def tasa_exito_ccaa(self) -> Dict[str, Dict[str, float]]:
        """1. Calcula la tasa de éxito por CCAA."""
        # Le pasamos una función lambda que extrae la comunidad autónoma
        return self._agrupar_y_calcular_tasas(lambda p: p.comunidad_autonoma)


    def top_n_entidades(self, n: int) -> List[Tuple[str, float, float]]:
        """3. Devuelve las N entidades con mayor tasa de éxito."""
        # Usamos el motor base agrupando por entidad solicitante
        resultados = self._agrupar_y_calcular_tasas(lambda p: p.entidad_solicitante)
        
        # Convertimos el diccionario a la lista de tuplas que nos piden
        lista_tasas = [
            (ent, datos['tasa_concedidos'], datos['tasa_contratos']) 
            for ent, datos in resultados.items()
        ]
        
        # Ordenamos y devolvemos las N mejores
        lista_tasas.sort(key=lambda x: (x[1], x[2]), reverse=True)
        return lista_tasas[:n]


    def tasas_exito_por_clasificacion(self, ruta_json: str, tipo_clasificacion: str) -> Dict[str, Dict[str, float]]:
        """4. Calcula la tasa de éxito agrupando por 'area' o 'macro_area'."""

        mapeo = self._cargar_mapeo_areas(ruta_json)
        '''
        {
        "AYA": {"area": "FIS", "macro_area": "Ciencias Matemáticas..."},
        "INF": {"area": "TIC", "macro_area": "Ciencias Matemáticas..."},
        "MED": {"area": "MED", "macro_area": "Ciencias de la Vida"}
        }'''
        
        # Le pasamos una función lambda más compleja que busca la subárea en el diccionario
        return self._agrupar_y_calcular_tasas(
            lambda p: mapeo.get(p.area, {}).get(tipo_clasificacion, 'Desconocida')
        )
    

    def financiacion_por_habitante(self, ruta_poblacion: str, ruta_salida: str) -> None:
        """2. Calcula la financiación por habitante y genera un Excel."""
        # 1. Sumamos el presupuesto concedido por cada CCAA
        presupuestos_ccaa = {}
        for p in self.proyectos:
            if isinstance(p, ProyectoConcedido):
                ccaa = p.comunidad_autonoma
                presupuestos_ccaa[ccaa] = presupuestos_ccaa.get(ccaa, 0.0) + p.presupuesto
                
        # 2. Leemos el Excel de población que generamos antes
        df_poblacion = pd.read_excel(ruta_poblacion)
        
        # 3. Cruzamos los datos y calculamos el ratio
        datos_exportar = []
        for _, row in df_poblacion.iterrows():
            ccaa = row['Comunidad Autónoma']
            poblacion = row['Poblacion']
            presupuesto = presupuestos_ccaa.get(ccaa, 0.0)
            
            ratio = (presupuesto / poblacion) if poblacion > 0 else 0.0
            
            datos_exportar.append({
                'Comunidad Autónoma': ccaa,
                'Habitantes': poblacion,
                'Presupuesto Total (€)': presupuesto,
                'Financiación por habitante (€/hab)': round(ratio, 2)
            })
            
        # 4. Guardamos el resultado en un nuevo Excel
        df_resultado = pd.DataFrame(datos_exportar)
        df_resultado.to_excel(ruta_salida, index=False)


    # Requisito 6
    
    def subproyectos_denegados_de_coordinados(self) -> List[str]:
        """6. Devuelve referencias de subproyectos no financiados cuyo coordinador (M=1) sí fue financiado."""
        # Paso 1: Agrupar los proyectos coordinados por su "raíz" compartida
        grupos_coordinados = {}
        for p in self.proyectos:
            partes = p.referencia.split('-')
            # Verificamos si tiene 3 partes y termina en 'C' (Coordinado)
            if len(partes) == 3 and partes[2].startswith('C'):
                # Ejemplo: PID2024-158711OB-C31
                # partes[0] = 'PID2024', partes[1] = '158711OB', partes[2] = 'C31'
                
                # La "raíz" es todo menos el último número (PID2024-158711OB-C3)
                raiz = f"{partes[0]}-{partes[1]}-{partes[2][:-1]}"
                # El índice del subproyecto es el último número (1, 2, 3...)
                sub_id = int(partes[2][-1]) 
                
                if raiz not in grupos_coordinados:
                    grupos_coordinados[raiz] = {}
                grupos_coordinados[raiz][sub_id] = p

        # Paso 2: Analizar cada grupo buscando a los "huérfanos"
        huerfanos = []
        for raiz, subproyectos in grupos_coordinados.items():
            # Verificamos si existe el coordinador (sub_id = 1) y si se lo concedieron
            if 1 in subproyectos and subproyectos[1].concedido:
                # Si el coordinador tiene éxito, miramos a sus "hermanos"
                for sub_id, proyecto in subproyectos.items():
                    if sub_id != 1 and not proyecto.concedido:
                        huerfanos.append(proyecto.referencia)
                        
        return huerfanos


    def analisis_orientada_vs_basica(self) -> Dict[str, Dict]:
        """7. Calcula el reparto de dinero y tasas para Orientados (O) vs No Orientados (N)."""
        def extraer_tipo(p):
            # Ref: PID2024-123456XY-C31 -> partes[1] es '123456XY'. La letra X está en el índice 6.
            try:
                letra_X = p.referencia.split('-')[1][6]
                return "Investigación Orientada (Aplicada)" if letra_X == 'O' else "Investigación No Orientada (Básica)"
            except (IndexError, TypeError):
                return "Desconocida"

        # ¡Usamos nuestro motor base para sacar las tasas mágicamente!
        resultados = self._agrupar_y_calcular_tasas(extraer_tipo)

        # Ahora añadimos manualmente el cálculo del dinero repartido
        for clave in resultados:
            resultados[clave]['dinero_repartido'] = 0.0

        for p in self.proyectos:
            if isinstance(p, ProyectoConcedido):
                tipo = extraer_tipo(p)
                if tipo in resultados:
                    resultados[tipo]['dinero_repartido'] += p.presupuesto
                    
        return resultados


    def analisis_individual_vs_coordinado(self) -> Dict[str, Dict[str, float]]:
        """8. Compara la tasa de éxito entre proyectos Individuales y Coordinados."""
        def extraer_modalidad(p):
            # Ref: PID2024-123456XY-I00 -> la última parte empieza por 'I'
            try:
                sufijo = p.referencia.split('-')[2]
                return "Individual" if sufijo.startswith('I') else "Coordinado"
            except IndexError:
                return "Desconocida"
                
        # Una vez más, el motor base hace todo el trabajo pesado en una sola línea
        return self._agrupar_y_calcular_tasas(extraer_modalidad)
    



  
class Gestor_ProyectoConcedido:
    """Contenedor exclusivo para proyectos concedidos."""
    def __init__(self):
        self.proyectos: List[ProyectoConcedido] = []
        
    def agregar(self, proyecto: ProyectoConcedido) -> None:
        self.proyectos.append(proyecto)




class Gestor_ProyectoContrato:
    """Contenedor exclusivo para proyectos con contrato predoctoral."""
    def __init__(self):
        self.proyectos: List[ProyectoContrato] = []
        
    def agregar(self, proyecto: ProyectoContrato) -> None:
        self.proyectos.append(proyecto)


    def generar_nubes_palabras(self, ruta_json_areas: str) -> None:
        """5. Genera nubes de palabras por macro área eliminando stopwords."""
        # 1. Cargar el diccionario para saber a qué macro área pertenece cada proyecto
        with open(ruta_json_areas, 'r', encoding='utf-8') as f:
            jerarquia = json.load(f)
            
        mapeo_macro = {}
        for macro, areas in jerarquia.items():
            for area, subareas in areas.items():
                for sub in subareas:
                    mapeo_macro[sub] = macro

        # 2. Cajas de texto vacías para ir acumulando los títulos
        textos_macro = {
            "Ciencias Matemáticas, Físicas, Químicas e Ingenierías": "",
            "Ciencias de la Vida": "",
            "Ciencias Sociales y Humanidades": ""
        }

        # 3. Recorremos los proyectos y metemos sus títulos en su caja correspondiente
        for p in self.proyectos:
            titulo = p.titulo_proyecto # Acumulamos el título
            macro = mapeo_macro.get(p.area, "Desconocida")
            
            if macro in textos_macro:
                textos_macro[macro] += titulo + " " # Espacio al final para separar palabras

        # 4. Diccionario de "Stopwords" (palabras vacías que ensucian la gráfica)
        # 4. Diccionario de "Stopwords" (AMPLIADO Y MEJORADO)
        stopwords_es = {
            "el", "la", "los", "las", "un", "una", "unos", "unas", "y", "e", "ni", "o", "u",
            "de", "del", "a", "al", "ante", "bajo", "cabe", "con", "contra", "desde", "en", "entre",
            "hacia", "hasta", "para", "por", "según", "sin", "sobre", "tras", "que", "como",
            "su", "sus", "se", "es", "son", "lo", "no", 
            "estudio", "análisis", "analisis", "desarrollo", "sistema", "sistemas", "uso", 
            "efecto", "efectos", "basado", "basada", "basados", "basadas", "mediante", "impacto", 
            "nuevos", "nuevas", "nuevo", "nueva", "evaluación", "evaluacion", "papel", "rol", 
            "aplicación", "aplicacion", "aplicaciones", "diseño", "proyecto", "proyectos",
            "investigación", "investigacion", "modelo", "modelos", "proceso", "procesos",
            "estrategia", "estrategias", "dinamica", "dinámica", "mecanismo", "mecanismos",
            "avanzada", "avanzado", "avanzadas", "avanzados", "herramienta", "herramientas",
            "traves", "través", "frente", "partir", "durante", "contexto", "perspectiva"
        }

        # 5. Función interna que dibuja la imagen
        def crear_nube(texto: str, macro_nombre: str):
            if not texto.strip(): return # Si no hay texto, no hacemos nada
                
            # Configuramos el "lienzo"
            wordcloud = WordCloud(
                width=800, height=400, 
                background_color='white', 
                stopwords=stopwords_es,
                colormap='viridis', # Un mapa de colores profesional
                max_words=80 # Máximo de palabras a mostrar
            ).generate(texto)
            
            # Dibujamos usando matplotlib
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.title(f"Palabras Clave: {macro_nombre}", fontsize=14, pad=20)
            plt.axis('off') # Quitamos los ejes X e Y
            
            # Limpiamos el nombre para guardarlo como archivo .png
            nombre_archivo = f"nube_{macro_nombre[:10].replace(' ', '_').replace(',', '')}.png"
            plt.savefig(nombre_archivo, bbox_inches='tight')
            print(f"✅ Imagen guardada: {nombre_archivo}")
            plt.close() # Importante: cerrar para no saturar la memoria RAM

        # 6. Ejecutamos la generación para cada macro área
        print("\nGenerando nubes de palabras (esto puede tardar unos segundos)...")
        for macro, texto in textos_macro.items():
            crear_nube(texto, macro)