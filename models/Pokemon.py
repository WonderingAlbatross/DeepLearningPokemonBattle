class Pokemon:
    def __init__(self, name):
        self.name = name
        self.hp = 100
        self.status = None              #"brn",etc, can only have one
        self.status_other = {}          #something like "|-start|p2a: Grimmsnarl|move: Taunt", can have several
        self.stat = {}                  #"atk",etc. why naming two totally different things stat change and status change??
        self.item = "unknown"
        self.ability = "unknown"
        self.details = None
        self.position = None            #"a" or "b"
        #self.exact_stat = [0,0,0,0,0,0]       #hp,atk,def,spa,spd,spe
