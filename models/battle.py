from .pokemon import Pokemon
from .player import Player
class Battle:
    def __init__(self, reg, num):
        self.reg = reg
        self.num = num
        self.player = {'p1':None,'p2':None}
        self.turn = 0
        self.weather = [None,0]
        self.field = [None,0]     
        self.condition = {}     #xx rooms

    def end_turn(self):
        self.turn += 1          #add turn-based field,space, stats later
        if self.field[0]:
            self.field[1] -= 1
        for cdt in self.condition:
            self.condition[cdt] -= 1
        for player in self.player.values():
            for sd in player.side:
                if sd in ['Reflect','Light Screen','Aurora Veil','Safeguard','Mist','Tailwind'] or sd.endswith("Pledge"):
                    player.side[sd] -= 1
            for name in player.position.values():
                if name:
                    pokemon = player.pokemon[name]
                    if pokemon.status[0] == 'tox':
                        pokemon.status[1] += 1
                    for sto in pokemon.status_other:
                        if sto in ['Taunt','Encore','Throat Chop','Heal Block','Slow Start']:
                            pokemon.status_other[sto] -= 1


    def rank(self):
        return (self.player['p1'].rank+self.player['p2'].rank)/2
    