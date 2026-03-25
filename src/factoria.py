import pandas as pd
from typing import Tuple, Dict, Any
from proyectos import Proyecto, ProyectoConcedido, ProyectoContrato
from gestor import Gestor_Proyecto, Gestor_ProyectoConcedido, Gestor_ProyectoContrato

class Factoria:
    """Clase encargada de leer los ficheros Excel y generar los gestores poblados."""

    @staticmethod
    def _parse_float(valor: Any) -> float:
        """Convierte valores (incluso cadenas numéricas con formato español) a float."""
        if pd.isna(valor):  # Manejamos los valores nulos/vacíos de Excel
            return 0.0
        if isinstance(valor, (int, float)):
            return float(valor)
            
        # Si llega como texto, quitamos los puntos de miles y cambiamos la coma decimal
        valor_limpio = str(valor).replace('.', '').replace(',', '.')
        try:
            return float(valor_limpio)
        except ValueError:
            return 0.0

    @classmethod
    def leer_datos(cls, ruta_anexo1: str, ruta_anexo2: str, 
                   ruta_anexo3: str, ruta_anexo4: str) -> Tuple[Gestor_Proyecto, Gestor_ProyectoConcedido, Gestor_ProyectoContrato]:
        
        # 1. Instanciamos los gestores vacíos
        gestor_todos = Gestor_Proyecto()
        gestor_concedidos = Gestor_ProyectoConcedido()
        gestor_contratos = Gestor_ProyectoContrato()
        
        # 2. Leemos Anexo II (Presupuestos) y lo guardamos en un diccionario
        df_anexo2 = pd.read_excel(ruta_anexo2)
        presupuestos: Dict[str, Dict[str, Any]] = {}
        for row in df_anexo2.to_dict('records'):
            ref = str(row['REFERENCIA'])
            anualidades = [
                cls._parse_float(row.get('SUBVENCION_2025_TOTAL', 0)),
                cls._parse_float(row.get('SUBVENCION_2026', 0)),
                cls._parse_float(row.get('SUBVENCION_2027', 0)),
                cls._parse_float(row.get('SUBVENCION_2028', 0))
            ]
            presupuestos[ref] = {
                'cd': cls._parse_float(row.get('CD_COSTES_DIRECTOS', 0)),
                'ci': cls._parse_float(row.get('CI_COSTES_INDIRECTOS', 0)),
                'anticipo': cls._parse_float(row.get('ANTICIPO_REEMBOLSABLE', 0)),
                'subvencion': cls._parse_float(row.get('SUBVENCION', 0)),
                'anualidades': anualidades,
                'num_contratos': int(row.get('NUM_CONTRATOS_PREDOC', 0) if pd.notna(row.get('NUM_CONTRATOS_PREDOC')) else 0)
            }
                
        # 3. Leemos Anexo IV (Contratos) y guardamos los títulos
        df_anexo4 = pd.read_excel(ruta_anexo4)
        titulos_contratos: Dict[str, str] = {}
        for row in df_anexo4.to_dict('records'):
            titulos_contratos[str(row['REFERENCIA'])] = str(row['TITULO DEL PROYECTO'])
                
        # 4. Leemos Anexo I (Proyectos Concedidos)
        df_anexo1 = pd.read_excel(ruta_anexo1)
        for row in df_anexo1.to_dict('records'):
            ref = str(row['REFERENCIA'])
            presup = presupuestos.get(ref, {})
            
            # Si la referencia está en el dict de contratos, instanciamos ProyectoContrato
            if ref in titulos_contratos:
                proyecto_contrato = ProyectoContrato(
                    referencia=ref,
                    area=str(row.get('AREA', '')),
                    entidad_solicitante=str(row.get('ENTIDAD SOLICITANTE', '')),
                    comunidad_autonoma=str(row.get('CCAA Entidad Solicitante', '')),
                    costes_directos=presup.get('cd', 0.0),
                    costes_indirectos=presup.get('ci', 0.0),
                    anticipo=presup.get('anticipo', 0.0),
                    subvencion=presup.get('subvencion', 0.0),
                    anualidades=presup.get('anualidades', []),
                    num_contratos=presup.get('num_contratos', 1),
                    titulo_proyecto=titulos_contratos[ref]
                )
                gestor_contratos.agregar(proyecto_contrato)
                gestor_concedidos.agregar(proyecto_contrato)
                gestor_todos.agregar(proyecto_contrato)
                
            # Si no, es un ProyectoConcedido normal
            else:
                proyecto_concedido = ProyectoConcedido(
                    referencia=ref,
                    area=str(row.get('AREA', '')),
                    entidad_solicitante=str(row.get('ENTIDAD SOLICITANTE', '')),
                    comunidad_autonoma=str(row.get('CCAA Entidad Solicitante', '')),
                    costes_directos=presup.get('cd', 0.0),
                    costes_indirectos=presup.get('ci', 0.0),
                    anticipo=presup.get('anticipo', 0.0),
                    subvencion=presup.get('subvencion', 0.0),
                    anualidades=presup.get('anualidades', []),
                    num_contratos=presup.get('num_contratos', 0)
                )
                gestor_concedidos.agregar(proyecto_concedido)
                gestor_todos.agregar(proyecto_concedido)
                    
        # 5. Leemos Anexo III (Proyectos Denegados)
        df_anexo3 = pd.read_excel(ruta_anexo3)
        for row in df_anexo3.to_dict('records'):
            proyecto_denegado = Proyecto(
                referencia=str(row['REFERENCIA']),
                area=str(row.get('AREA', '')),
                entidad_solicitante=str(row.get('ENTIDAD SOLICITANTE', '')),
                comunidad_autonoma=str(row.get('CCAA Entidad Solicitante', '')),
                concedido=False
            )
            gestor_todos.agregar(proyecto_denegado)
                
        return gestor_todos, gestor_concedidos, gestor_contratos
    