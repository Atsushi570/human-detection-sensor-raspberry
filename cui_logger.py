import os
import time
import csv
from datetime import datetime
import numpy as np
import RPi.GPIO as GPIO
from device.amg88xx import GridEYESensor
import sys

# GPIO設定
GPIO.setmode(GPIO.BCM)
channel = 4
GPIO.setup(channel, GPIO.IN)

# Grid Eyeの初期化
grid_eye = GridEYESensor(address=0x69, enable_ma=False)
time.sleep(0.1)  # Grid Eyeの初期化待ち

def log_data(interval):
    # CSVファイル設定
    start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file_path = f'./out/data_{start_time}.csv'
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        headers = ['Time', 'PIR State'] + [f'Pixel_{i}_{j}' for i in range(8) for j in range(8)]
        writer.writerow(headers)
        
        try:
            while True:
                current_time = datetime.now()
                pir_value = GPIO.input(channel)
                grid_eye_data = grid_eye.pixels()
                flattened_data = [item for sublist in grid_eye_data for item in sublist]
                writer.writerow([current_time, pir_value] + flattened_data)
                
                print(f"Logged at {current_time}")  # コンソールにログ時間を表示
                time.sleep(interval)  # 指定された間隔で待機
        except KeyboardInterrupt:
            print("Logging stopped by user.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python log_sensor.py <interval_in_seconds>")
        sys.exit(1)
    
    interval = int(sys.argv[1])  # コマンドラインからの時間間隔の取得
    log_data(interval)
