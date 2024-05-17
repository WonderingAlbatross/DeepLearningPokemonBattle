# this script count the type of information in the pokemonshowdown battle logs, as a pre-procession.

import pandas as pd
import os

def read_battle_log(file_path):
    with open(file_path, 'r',encoding='utf-8') as file:
        lines = file.readlines()
    battle_data = list(filter(None,[list(filter(None, [item.strip() for item in line.split('|')])) for line in lines]))

    return battle_data


def process_files(directory):
    type_count = {}
    type_appear = {}

    for filename in os.listdir(directory):
        if filename.endswith('txt'):
            file_path = os.path.join(directory, filename)
            battle_log_data = read_battle_log(file_path)
            recording = False
            for line in battle_log_data:
                t = line[0]
                if t == "start":
                    recording = True
                    continue
                elif t == "win":
                    recording = False
                    break
                if recording:
                    if t.startswith("-"):
                        t = t[1:]
                    if t not in type_count:
                        type_count[t] = 1
                        type_appear[t] = filename[:-3]
                    else:
                        type_count[t] += 1


    df = pd.DataFrame(list(type_count.items()), columns=['Type', 'Frequency'])
    df['First Appearance File'] = df['Type'].map(type_appear)
    df.sort_values(by='Frequency', ascending=False, inplace=True)
    df.to_csv('type_info_summary.csv', index=False)
    print(df)


def check_string(directory,string,number):
    count = 0
    for filename in os.listdir(directory):
        if filename.endswith('txt'):
            file_path = os.path.join(directory, filename)
            battle_log_data = read_battle_log(file_path)
            for line in battle_log_data:
                if line and (line[0] == string or line[0] == '-'+string):
                    count += 1
                    print(line)
                    print(filename)
                    if count >= number:
                        return 0

def check_string(directory,string,number,exact = False):
    count = 0
    for filename in os.listdir(directory):
        if filename.endswith('txt'):
            file_path = os.path.join(directory, filename)
            battle_log_data = read_battle_log(file_path)
            for line in battle_log_data:
                for word in line:
                    if (not exact and string in word) or (exact and string == word):
                        count += 1
                        print(line)
                        print(filename)
                    if count >= number:
                        return 0
def count_string(directory,string,number):
    dic = {}
    for filename in os.listdir(directory):
        if filename.endswith('txt'):
            file_path = os.path.join(directory, filename)
            battle_log_data = read_battle_log(file_path)
            for line in battle_log_data:
                for word in line:
                    if string == word:
                        output = line[number]
                        if output in dic:
                            dic[output] += 1
                        else:
                            dic[output] = 1
    for d in dic:
        if dic[d]>5:
            print(d,dic[d])


check_string('./log','[from] item: ',1000)
#count_string('./log','Taunt',2)

