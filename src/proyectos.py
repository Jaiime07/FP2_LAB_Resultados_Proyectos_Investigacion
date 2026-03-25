from typing import List

class Proyecto:
    """Clase base para todos los proyectos (concedidos y denegados)."""
    
    def __init__(self, referencia: str, area: str, entidad_solicitante: str, 
                 comunidad_autonoma: str, concedido: bool = False):
        self.referencia: str = referencia
        self.area: str = area
        self.entidad_solicitante: str = entidad_solicitante
        self.comunidad_autonoma: str = comunidad_autonoma
        self.concedido: bool = concedido


class ProyectoConcedido(Proyecto):
    """Clase para proyectos que han sido aprobados. Hereda de Proyecto."""
    
    def __init__(self, referencia: str, area: str, entidad_solicitante: str, 
                 comunidad_autonoma: str, costes_directos: float, 
                 costes_indirectos: float, anticipo: float, subvencion: float, 
                 anualidades: List[float], num_contratos: int):
        
        # Inicializamos la clase padre forzando concedido a True
        super().__init__(referencia, area, entidad_solicitante, comunidad_autonoma, concedido=True)
        
        self.costes_directos: float = costes_directos
        self.costes_indirectos: float = costes_indirectos
        self.anticipo: float = anticipo
        self.subvencion: float = subvencion
        self.anualidades: List[float] = anualidades
        
        # Será True si num_contratos es mayor que 0
        self.contratado_predoctoral: bool = num_contratos > 0

    @property
    def presupuesto(self) -> float:
        """Propiedad derivada: suma de costes directos e indirectos."""
        suma_costes = self.costes_directos + self.costes_indirectos
        suma_ayudas = self.anticipo + self.subvencion
        
        # Comprobación de integridad sugerida en el enunciado
        if round(suma_costes, 2) != round(suma_ayudas, 2):
            print(f"Aviso en {self.referencia}: La suma de costes ({suma_costes}) no coincide con anticipo+subvención ({suma_ayudas}).")
            
        return suma_costes


class ProyectoContrato(ProyectoConcedido):
    """Clase para proyectos concedidos que además tienen contrato predoctoral."""
    
    def __init__(self, referencia: str, area: str, entidad_solicitante: str, 
                 comunidad_autonoma: str, costes_directos: float, 
                 costes_indirectos: float, anticipo: float, subvencion: float, 
                 anualidades: List[float], num_contratos: int, titulo_proyecto: str):
        
        # Inicializamos la clase padre
        super().__init__(referencia, area, entidad_solicitante, comunidad_autonoma, 
                         costes_directos, costes_indirectos, anticipo, subvencion, 
                         anualidades, num_contratos)
        
        # Forzamos a True según el enunciado, aunque num_contratos ya lo gestionaría
        self.contratado_predoctoral: bool = True
        self.titulo_proyecto: str = titulo_proyecto
        