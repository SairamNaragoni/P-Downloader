# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 11:58:02 2020

@author: Rogue
"""
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import ActionChains
import time
import datetime
import requests
import sys, os
import zipfile
import requests
import re
from multiprocessing import Pool, cpu_count
from functools import partial
from io import BytesIO
from tqdm import tqdm
import concurrent.futures
  
def init_chrome_selenium():
    # Initializing selenium and chrome browser
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    # UnComment and give the path to use your chrome profile
    # options.add_argument("--user-data-dir=C:/Users/Rogue/AppData/Local/Google/Chrome/User Data")
    options.add_experimental_option("excludeSwitches", ['enable-automation']);
    driver = webdriver.Chrome(executable_path="C:\\Users\\Rogue\\Downloads\\Compressed\\chromedriver", chrome_options=options)
    driver.maximize_window()
    return driver  

def init_mozilla_selenium(headless=False):
    # Initializing selenium and mozilla browser
    options = Options()
    options.headless = headless
    # UnComment and give the path to use your mozilla profile
    # fp = webdriver.FirefoxProfile('C:/Users/Rogue/AppData/Roaming/Mozilla/Firefox/Profiles/4ahj70v9.default-release')
    driver = webdriver.Firefox(options=options,executable_path=r'C:/Users/Rogue/Downloads/WebDrivers/geckodriver.exe')
    driver.maximize_window()
    return driver

def download_file(url, filePath):
    try:
        file_name = filePath+"\\"+url.split("/")[-1]
        file_name = re.sub(r"%20", "-", file_name)
        response = requests.get(url, stream=True)
        total = int(response.headers.get('content-length', 0))
        with open(file_name, 'wb') as file, tqdm(
            desc=file_name,
            total=total,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                bar.update(size)
    except Exception as e:
        print("[ERROR] Exception while downloading file from %s"%(url),e)

filename="zippyShare.txt"
log_filename="dlinks.txt"
with open(filename) as f:
    content = list(f)
content = list(filter(None,map(lambda s: s.strip(), content)))

itr = 0
dlinks=[]
# Use any one of the below functions
driver = init_mozilla_selenium(True)
# driver = init_chrome_selenium(True)

print("[INFO] Extracting Download Links ...")
for link in content:
    print("[INFO] Iterating link[%d] - %s"%(itr,link))
    driver.get(link)
    dlink = driver.find_element_by_id("dlbutton")
    dlinks.append(dlink.get_attribute("href"))
    itr+=1
driver.close()

print("[INFO] Writing download links to a file ... saved at %s"%(log_filename))
with open(log_filename, "w") as outfile:
    outfile.write("\n".join(dlinks))

try: 
    directory = "files"
    if not os.path.exists(directory):
        os.makedirs(directory)
    downloadFilePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), directory) 
except OSError as error: 
    downloadFilePath = os.path.dirname(os.path.abspath(__file__)) 
    print("[ERROR] Error creating a directory files ...",error)

print("[INFO] Downloading file to the path : %s " % downloadFilePath)
print("[INFO] There are %d CPUs on this machine "%(cpu_count()))
 
download_func = partial(download_file, filePath = downloadFilePath)
with concurrent.futures.ThreadPoolExecutor(cpu_count()) as exector : 
   exector.map(download_func, dlinks)