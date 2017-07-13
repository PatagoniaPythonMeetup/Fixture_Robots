import random
import json
import sys
from functools import reduce
from itertools import combinations

from .Robot import Robot
from .Encuentro import Encuentro
from .Ronda import Ronda
from .Grupo import Grupo
from .Fase import Clasificacion, Eliminacion, Final

class Fixture(object):
    def __init__(self, robots=None, jugadas=3, tracks=1):
        # Numero de tracks en paralelo que pueden ser sostenidos por disponibilidad de pistas
        Ronda.TRACKS = tracks
        # Numero minimo de jugadas para determinar un ganador en un encuentro
        Encuentro.JUGADAS = jugadas
        self.robots = robots or []
        self.fases = []

    # Robots
    def inscribir_robot(self, nombre, escuela, responsable, escudo=None):
        robot = Robot(nombre, escuela, responsable, escudo)
        self.robots.append(robot)
        return robot

    def get_robot_por_nombre(self, nombre):
        robots = [robot for robot in self.robots if robot.nombre == nombre]
        if len(robots) == 1:
            return robots.pop()

    def get_robot_por_key(self, key):
        robots = [robot for robot in self.robots if robot.key == key]
        if len(robots) == 1:
            return robots.pop()

    def get_robots(self):
        return self.robots[:]

    def robots_en_juego(self):
        ronda_actual = self.get_ronda_actual()
        return self.robots if ronda_actual is None else ronda_actual.get_robots()

    def clasificacion(self, grupos):
        fase_actual = self.get_fase_actual()
        assert fase_actual is None or fase_actual.finalizado(), "La fase actual no fue finalizada"
        robots = fase_actual.ganadores() if fase_actual is not None else self.get_robots()
        clas = Clasificacion(robots, grupos)
        self.fases.append(clas)
        return clas

    def eliminacion(self):
        fase_actual = self.get_fase_actual()
        assert fase_actual is None or fase_actual.finalizado(), "La fase actual no fue finalizada"
        robots = fase_actual.ganadores() if fase_actual is not None else self.get_robots()
        clas = Eliminacion(robots)
        self.fases.append(clas)
        return clas

    def final(self):
        fase_actual = self.get_fase_actual()
        assert fase_actual is None or fase_actual.finalizado(), "La fase actual no fue finalizada"
        robots = fase_actual.ganadores() if fase_actual is not None else self.get_robots()
        clas = Final(robots)
        self.fases.append(clas)
        return clas

    # Encuentros
    def get_encuentros(self):
        return reduce(lambda a, ronda: a + ronda.get_encuentros(), self.get_rondas(), [])

    def get_encuentro(self, numero):
        encuentros = [encuentro for encuentro in self.get_encuentros() \
            if encuentro.numero == numero]
        if len(encuentros) == 1:
            return encuentros.pop()

    def get_encuentros_actuales(self):
        ronda = self.get_ronda_actual()
        return ronda.get_encuentros_actuales() if ronda is not None else []

    # Rondas
    def generar_rondas(self, tct=False, allow_none=False, shuffle=True):
        fase = self.get_fase_actual()
        if fase:
            return fase.generar_rondas(tct, allow_none, shuffle)

    def get_ronda(self, numero):
        rondas = [ronda for ronda in self.get_rondas() if ronda.numero == numero]
        if len(rondas) == 1:
            return rondas.pop()

    def get_rondas(self):
        return reduce(lambda a, fase: a + fase.get_rondas(), self.get_fases(), [])

    def get_ronda_actual(self):
        rondas = self.get_rondas()
        if rondas:
            return rondas[-1]

    # Fases
    def get_fases(self):
        return self.fases[:]

    def get_fase_actual(self):
        fases = self.get_fases()
        if fases:
            return fases[-1]

    def limpiar(self):
        self.robots = []
        self.fases = []

    # Json dumps and loads
    def to_dict(self):
        return {
            "robots": self.robots,
            "fases": [fase.to_dict() for fase in self.get_fases()]
        }

    def from_dict(self, data):
        CLASES = {kls.__name__: kls for kls in [Clasificacion, Eliminacion, Final]}
        robots = [Robot(*robot_data) for robot_data in data["robots"]]
        fases = []
        for fase_data in data["fases"]:
            klass = fase_data["class"]
            grupos = []
            frobots = []
            for grupo_data in fase_data["grupos"]:
                rondas = []
                for ronda_data in grupo_data["rondas"]:
                    encuentros = []
                    for encuentro_data in ronda_data["encuentros"]:
                        r1 = [robot for robot in robots if robot == tuple(encuentro_data["robot_1"])].pop()
                        r2 = [robot for robot in robots if robot == tuple(encuentro_data["robot_2"])].pop()
                        ganadas = [tuple(gano) == r1 and r1 or r2 for gano in encuentro_data["ganadas"]]
                        encuentro = Encuentro(r1, r2, numero=encuentro_data["numero"], ganadas=ganadas)
                        encuentros.append(encuentro)
                    promovidos = [robot for robot in robots \
                        if robot in [tuple(p) for p in fase_data["promovidos"]]]
                    rondas.append(Ronda(encuentros=encuentros, \
                        promovidos=promovidos, tct=ronda_data.pop("tct", False)))
                grobots = [robot for robot in robots \
                    if robot in [tuple(p) for p in grupo_data["robots"]]]
                frobots = frobots + grobots
                grupos.append(Grupo(grobots, rondas))
            fases.append(CLASES[klass](frobots, grupos))
        self.robots = robots
        self.fases = fases

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, source):
        fixture = cls()
        fixture.from_dict(json.loads(source))
        return fixture

    # Estados
    def iniciado(self):
        tiene_robots = bool(self.robots)
        return tiene_robots and self.get_fase_actual().iniciado()

    def compitiendo(self):
        return self.get_fase_actual().compitiendo()

    def finalizado(self):
        tiene_robots = bool(self.robots)
        return tiene_robots and self.get_fase_actual().finalizado()

    def vuelta(self):
        encuentros = self.get_encuentros()
        return max([e.jugadas() for e in encuentros]) if encuentros else 0
    
    def jugadas(self):
        encuentros = self.get_encuentros()
        return sum([e.jugadas() for e in encuentros]) if encuentros else 0

    # Trabajando sobre el fixture
    def ganadores(self):
        fase = self.get_fase_actual()
        if fase is not None:
            return fase.ganadores()

    def ganador(self):
        fase = self.get_fase_actual()
        if fase is not None:
            return fase.ganador()
    
    def perdedores(self):
        fase = self.get_fase_actual()
        if fase is not None:
            return fase.perdedores()

    def perdedor(self):
        fase = self.get_fase_actual()
        if fase is not None:
            return fase.perdedor()

    def agregar_ganador(self, robot, nencuentro=None):
        encuentros = [e for e in self.get_encuentros() if e.participa(robot) and (nencuentro is None or (nencuentro is not None and e.numero == nencuentro))]
        assert len(encuentros) == 1, "El robot no participa de la ronda o debe especificar un encuentro"
        encuentro = encuentros[0]
        encuentro.agregar_ganador(robot)
        return encuentro

    def quitar_ganador(self, robot, nencuentro=None):
        encuentros = [e for e in self.get_encuentros() if e.participa(robot) and (nencuentro is None or (nencuentro is not None and e.numero == nencuentro))]
        assert len(encuentros) == 1, "El robot no participa de la ronda o debe especificar un encuentro"
        encuentro = encuentros[0]
        encuentro.quitar_ganador(robot)
        return encuentro

    def score(self, robot):
        """Retorna el *score* de un robot dentro del fixture
        score es una n-upla de la forma (jugados, triunfos, empates, derrotas, a favor, en contra, diferencia, puntos)
        """
        scores = [ronda.score(robot) for ronda in self.get_rondas()]
        return reduce(lambda acumulador, score: tuple([ a + b for a, b in zip(acumulador, score)]), scores, (0, 0, 0, 0, 0, 0, 0, 0))
        