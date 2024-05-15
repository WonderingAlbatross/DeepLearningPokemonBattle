from pokemon import Pokemon
from player import Player

class Battle:
    def __init__(self, reg, num):
        self.reg = reg
        self.num = num
        self.player = {}
        self.turn = {}
        self.condition = {}     #weather and xx rooms
        
    