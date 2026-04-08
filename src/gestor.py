import pandas as pd
from typing import List, Dict, Tuple, Callable
from proyectos import Proyecto, ProyectoConcedido, ProyectoContrato
import json


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
            if isinstance(p, ProyectoConcedido) and p.contratado_predoctoral:
                stats[clave]['contratados'] += 1
                
        resultados = {}
        for clave, data in stats.items():
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