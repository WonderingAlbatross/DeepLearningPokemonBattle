# This scripe is for getting battle log from pokemonshowdown replay. Before running it, save a website in mhtml using your browser. 

import webbrowser
import pyautogui
import time
import requests
import re
from bs4 import BeautifulSoup

def extract_filename_from_url(url):
    if not url:
        return None
    return url.split('/')[-1][:-3]+"txt"



def get_log_from_mhtml(mhtml_file):
    with open(mhtml_file, 'r', encoding='utf-8') as file:
        html_content = file.read()
    clean_content = re.sub(r'=\n', '', html_content)
    soup = BeautifulSoup(clean_content, 'html.parser')
    replay_links = soup.find_all('a', href=True)
    replay_urls = [
        link['href'] for link in replay_links if 'gen9vgc2024regg' in link['href']
    ]

    for url in replay_urls:
        url = url[3:-1]+".log"
        output_path = extract_filename_from_url(url)
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(output_path, 'w', encoding='utf-8') as file:
                    file.write(response.text)
                print(f"download completed：{output_path}")
            else:
                print(f"download failed. code：{response.status_code}")
                return 0
        except Exception as e:
            print(f"download failed. error：{e}")
            return 0
        time.sleep(0.1)
    return 1




for page in range(1,50):
    mhtml_file = f'saved_page{page}.mhtml'
    url = f"https://replay.pokemonshowdown.com/?format=%5BGen%209%5D%20VGC%202024%20Reg%20G&page={page}&sort=rating"
    webbrowser.open(url)
    time.sleep(3)
    pyautogui.hotkey('ctrl', 's')
    time.sleep(2)
    pyautogui.typewrite(mhtml_file)
    pyautogui.press('tab') 
    pyautogui.press('down')  
    pyautogui.press('enter')
    pyautogui.press('enter')
    time.sleep(3)
    pyautogui.hotkey('ctrl', 'w')
    time.sleep(1)
    if get_log_from_mhtml(mhtml_file):
        continue