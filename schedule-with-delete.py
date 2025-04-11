period = 1 # Hours
target_bat = "C:\\Users\\Administrator\\Desktop\\mteam\\start-auto.cmd" 
qbt_bat = "C:\\Users\\Administrator\\Desktop\\mteam\\qbt.cmd" 
wait_to_finish=True
open_in_new_window=False
# No need to edit
import time
import subprocess
from tqdm import tqdm
wait_time = period * 3600  
while 1:
    process = subprocess.Popen(qbt_bat, shell=True); process.wait()
    if open_in_new_window: 
        process = subprocess.Popen(f'start cmd /k "{target_bat}"', shell=True)
    else:
        process = subprocess.Popen(target_bat, shell=True)
    if wait_to_finish: process.wait()
    print(f"Waiting for {period} hours...")
    for i in tqdm(range(wait_time), desc="Waiting", unit="Second", ncols=80):
        time.sleep(1)