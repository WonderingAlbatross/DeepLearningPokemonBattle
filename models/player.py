from .pokemon import Pokemon

class Player:
    def __init__(self, code, name,rank):
        self.code = code
        self.name = name
        self.rank = int(rank)
        self.pokemon = {}
        self.side = {}      #walls, tail wind, etc
        self.position = {'a':None,'b':None}         #store name index
        self.backup = set()                         #store name index
        self.team = set()                           #store name index
        self.has_teraed = False
        self.alive_number = 4
    def show(self):
        return [self.code,self.side,self.position,self.backup]

    def show_all_pokemon(self):
        result = []
        for pokemon_name in self.pokemon:
            result.append(self.pokemon[pokemon_name].show())
        return result

  

    def alive_number(self):
        n = 4
        for pokemon in self.pokemon.values():
            if pokemon.status[0] == 'fnt':
                n -= 1
        return n
