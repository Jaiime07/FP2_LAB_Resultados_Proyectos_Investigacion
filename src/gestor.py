from typing import List
from proyectos import Proyecto, ProyectoConcedido, ProyectoContrato

class Gestor_Proyecto:
    """Contenedor para todos los proyectos (concedidos y denegados)."""
    
    def __init__(self):
        self.proyectos: List[Proyecto] = []
        
    def agregar(self, proyecto: Proyecto) -> None:
        self.proyectos.append(proyecto)


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