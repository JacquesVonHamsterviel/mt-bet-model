
target_bat = "C:\\Users\\Administrator\\Desktop\\mteam\\start-auto-fast.cmd" 
wait_to_finish=True
open_in_new_window=False
# No need to edit
import time
import subprocess
from tqdm import tqdm
wait_time = 5 * 60 #second
while 1:
    if open_in_new_window: 
        process = subprocess.Popen(f'start cmd /k "{target_bat}"', shell=True)
    else:
        process = subprocess.Popen(target_bat, shell=True)
    if wait_to_finish: process.wait()
    print(f"Waiting for {wait_time} second...")
    for i in tqdm(range(wait_time), desc="Waiting", unit="Second", ncols=80):
        time.sleep(1)