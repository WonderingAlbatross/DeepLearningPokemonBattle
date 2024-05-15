from pokemon import Pokemon

class Player:
    def __init__(self, code, name):
        self.code = code
        self.name = name
        self.pokemon = {}
        self.side = {}
