import graphene
from graphene import resolve_only_args

class Estado(graphene.ObjectType):
    iniciado = graphene.Boolean()
    compitiendo = graphene.Boolean()
    finalizado = graphene.Boolean()
    vuelta = graphene.Int()
    jugadas = graphene.Int()

    def resolve_iniciado(self, args, context, info):
        return self.iniciado()

    def resolve_compitiendo(self, args, context, info):
        return self.compitiendo()
    
    def resolve_finalizado(self, args, context, info):
        return self.finalizado()

    def resolve_vuelta(self, args, context, info):
        return self.vuelta()

    def resolve_jugadas(self, args, context, info):
        return self.jugadas()


class Robot(graphene.ObjectType):
    key = graphene.String()
    nombre = graphene.String()
    escuela = graphene.String()
    encargado = graphene.String()
    escudo = graphene.String()
    score = graphene.List(graphene.Int)

    def resolve_score(self, args, context, info):
        return context["fixture"].score(self)

class Encuentro(graphene.ObjectType):
    numero = graphene.Int()
    robots = graphene.List(Robot)
    estado = graphene.Field(Estado)
    puntos = graphene.List(graphene.Int)

    def resolve_robots(self, args, context, info):
        return [self.robot_1, self.robot_2]

    def resolve_puntos(self, args, context, info):
        return self.score(self.robot_1)

    def resolve_estado(self, args, context, info):
        return self

class Ronda(graphene.ObjectType):
    numero = graphene.Int()
    encuentros = graphene.List(Encuentro)
    promovidos = graphene.List(Robot)
    tct = graphene.Boolean()
    estado = graphene.Field(Estado)

    def resolve_estado(self, args, context, info):
        return self

class Fixture(graphene.ObjectType):
    robot = graphene.Field(Robot, key=graphene.Argument(graphene.String))
    robots = graphene.List(Robot)
    encuentro = graphene.Field(Encuentro, numero=graphene.Argument(graphene.Int))
    encuentros = graphene.List(Encuentro)
    encuentros_actuales = graphene.List(Encuentro)
    ronda = graphene.Field(Ronda, numero=graphene.Argument(graphene.Int))
    rondas = graphene.List(Ronda)
    ronda_actual = graphene.Field(Ronda)
    ganador = graphene.Field(Robot)
    estado = graphene.Field(Estado)

    def resolve_robot(self, args, context, info):
        key = args['key']
        return self.get_robot_por_key(key)

    def resolve_robots(self, args, context, info):
        return self.get_robots()

    def resolve_encuentro(self, args, context, info):
        numero = args['numero']
        return self.get_encuentro(numero)

    def resolve_encuentros(self, args, context, info):
        return self.get_encuentros()

    def resolve_encuentros_actuales(self, args, context, info):
        return self.get_encuentros_actuales()

    def resolve_ronda(self, args, context, info):
        numero = args['numero']
        return self.get_ronda(numero)

    def resolve_rondas(self, args, context, info):
        return self.get_rondas()

    def resolve_ronda_actual(self, args, context, info):
        return self.get_ronda_actual()
    
    def resolve_ganador(self, args, context, info):
        return self.ganador()
    
    def resolve_estado(self, args, context, info):
        return self

class Query(graphene.ObjectType):
    fixture = graphene.Field(Fixture)

    def resolve_fixture(self, args, context, info):
        return context["fixture"]

# Mutaciones
class GenerarRonda(graphene.Mutation):
    class Input:
        tct = graphene.Boolean()

    ok = graphene.Boolean()
    mensaje = graphene.String()
    ronda = graphene.Field(lambda: Ronda)
    
    @staticmethod
    def mutate(root, args, context, info):
        tct = args.get('tct')
        try:
            ronda = context["fixture"].generar_ronda(tct)
            return GenerarRonda(ok = True, mensaje = "Ronda creada", ronda = ronda)
        except Exception as ex:
            return GenerarRonda(ok = False, mensaje = str(ex))

class GanaRobot(graphene.Mutation):
    class Input:
        key = graphene.String()
        ronda = graphene.Int()
        encuentro = graphene.Int()
    
    ok = graphene.Boolean()
    mensaje = graphene.String()
    encuentro = graphene.Field(lambda: Encuentro)
    
    @staticmethod
    def mutate(root, args, context, info):
        key = args.get('key')
        ronda = args.get('ronda')
        encuentro = args.get('encuentro')
        try:
            robot = context["fixture"].get_robot_por_key(key)
            encuentro = context["fixture"].gano(robot, ronda=ronda, encuentro=encuentro)
            return GanaRobot(ok = True, mensaje = "Robot declarado ganador", encuentro = encuentro)
        except Exception as ex:
            return GanaRobot(ok = False, mensaje = str(ex))

class Mutations(graphene.ObjectType):
    generar_ronda = GenerarRonda.Field()
    gana_robot = GanaRobot.Field()

schema = graphene.Schema(query=Query, mutation=Mutations)