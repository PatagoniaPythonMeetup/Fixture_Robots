from functools import reduce

class Ronda(object):
    def __init__(self, numero, encuentros, promovidos=None):
        self.numero = numero
        self.encuentros = encuentros
        self.promovidos = promovidos or []

    @property
    def robots(self):
        return reduce(lambda a, e: a + [e.robot_1] + [e.robot_2], self.encuentros, self.promovidos)

    def finalizada(self):
        return all([e.finalizado() for e in self.encuentros])

    def ganadores(self):
        return [e.ganador() for e in self.encuentros] + self.promovidos
    
    def get_encuentro(self, numero):
        return self.encuentros[numero - 1]

    def gano(self, robot):
        assert robot in self.robots, "El robot ganador no es parte de la ronda"
        encuentro = [ e for e in self.encuentros if e.participa(robot)].pop()
        encuentro.gano(robot)
    
    def vuelta(self):
        return max([e.vuelta() for e in self.encuentros])
    
    def to_dict(self):
        return {
            "numero": self.numero,
            "encuentros": [ encuentro.to_dict() for encuentro in self.encuentros ],
            "promovidos": self.promovidos
        }