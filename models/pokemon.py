class Pokemon:
    def __init__(self, name):
        self.name = name
        self.form = name
        self.hp = 100
        self.status = [None,0]              #'brn',etc, can only have one
        self.status_other = {}          #something like '|-start|p2a: Grimmsnarl|move: Taunt', can have several
        self.stat_boost = {}                  #'atk',etc. why naming two totally different things stat change and status change??
        self.item = 'unknown'
        self.ability = 'unknown'
        self.move = {}
        self.tera = False
        self.tera_type = 'unknown' 

        #self.exact_stat = [0,0,0,0,0,0]       #hp,atk,def,spa,spd,spe
    
    def show(self):
        return [self.form,self.hp,self.status]