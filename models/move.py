import json
import os
class Move:
    with open('./data/moves.json', 'r', encoding='utf-8') as file:
        MOVEDATA = json.load(file)
        
    def __init__(self, name):
        self.code = ''.join(char.lower() for char in name if char not in ',\'- ')
        self.name = name

    def get_info(self,info):

        move_data = Move.MOVEDATA.get(self.code)
        if move_data:
            return move_data.get(info)
        else:
            self.write_error('MOVEDATA error',[self.code,info])
            return 99   

    def write_error(self,string, line):
        with open('error.txt', 'a') as file:
            file.write(string+'\n')
            for item in line:
                file.write(item + '\t')  
            file.write('\n')  