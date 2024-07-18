import os
import time
import csv
from datetime import datetime, timedelta
import RPi.GPIO as GPIO
import tkinter as tk
from tkinter import StringVar
import numpy as np
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from device.amg88xx import GridEYESensor

# GPIO設定
GPIO.setmode(GPIO.BCM)
channel = 4
GPIO.setup(channel, GPIO.IN)

# Grid Eyeの初期化
grid_eye = GridEYESensor(address=0x69, enable_ma=False)
time.sleep(0.1)  # Grid Eyeの初期化待ち

# Tkinter GUI設定
root = tk.Tk()
root.title("GPIO and GridEYE Sensor Monitor")

# matplotlibグラフ設定（Grid Eye画像表示用）
figure_grid_eye = Figure(figsize=(8, 4))
ax_grid_eye_org = figure_grid_eye.add_subplot(121)
ax_grid_eye_bicubic = figure_grid_eye.add_subplot(122)
canvas_grid_eye = FigureCanvasTkAgg(figure_grid_eye, master=root)
canvas_widget_grid_eye = canvas_grid_eye.get_tk_widget()
canvas_widget_grid_eye.pack(fill=tk.BOTH, expand=True)

# 初回のGrid Eyeデータ取得とカラーバーの作成
grid_eye_data = np.array(grid_eye.pixels())
grid_eye_image_org = ax_grid_eye_org.imshow(grid_eye_data, cmap='inferno')
grid_eye_image_bicubic = ax_grid_eye_bicubic.imshow(grid_eye_data, cmap='inferno', interpolation='bicubic')
colorbar_org = figure_grid_eye.colorbar(grid_eye_image_org, ax=ax_grid_eye_org)
colorbar_bicubic = figure_grid_eye.colorbar(grid_eye_image_bicubic, ax=ax_grid_eye_bicubic)

# matplotlibグラフ設定 (PIR時系列データ用)
figure_pir = Figure(figsize=(10, 4), dpi=100)
ax_pir = figure_pir.add_subplot(111)
ax_pir.set_title("GPIO Input Over Time")
ax_pir.set_xlabel("Time")
ax_pir.set_ylabel("GPIO State")
canvas_pir = FigureCanvasTkAgg(figure_pir, master=root)
canvas_widget_pir = canvas_pir.get_tk_widget()
canvas_widget_pir.pack(fill=tk.BOTH, expand=True)

# PIR表示用リスト
times = []
pir_values = []

# 記録状態を管理する変数
is_recording = False
csv_file_path = None
start_time = None

# Grid Eyeの縦軸初期値
min_temp = 28  # 初期Min温度
max_temp = 32  # 初期Max温度

# CSVファイルに保存するための関数
def start_recording():
    global is_recording, start_time, csv_file_path
    is_recording = True
    start_time = datetime.now().strftime("%Y%m%d_%H%M%S")  # 開始時刻
    # ファイル名に開始時刻を含む
    csv_file_path = './out/data_{}.csv'.format(start_time)
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        headers = ['Time', 'PIR State'] + ['Pixel_{}_{}'.format(i, j) for i in range(8) for j in range(8)]
        writer.writerow(headers)
    recording_status_label.config(text="記録中...") 

def stop_recording():
    global is_recording, csv_file_path
    is_recording = False
    recording_status_label.config(text="記録待機中") 

def update_min_temp(*args):
    global min_temp
    min_temp = int(min_temp_var.get())

def update_max_temp(*args):
    global max_temp
    max_temp = int(max_temp_var.get())


# ボタンの追加
record_start_button = tk.Button(root, text='記録開始', command=start_recording)
record_start_button.pack()

record_stop_button = tk.Button(root, text='記録停止', command=stop_recording)
record_stop_button.pack()

# 記録状態ラベルの追加
recording_status_label = tk.Label(root, text="記録待機中")
recording_status_label.pack()

# 温度範囲選択用セレクトボックス
temp_range = list(range(0, 41))
min_temp_var = StringVar(root)
min_temp_var.set(str(min_temp))  # 初期値設定
min_temp_menu = tk.OptionMenu(root, min_temp_var, *temp_range, command=update_min_temp)
min_temp_menu.pack()

max_temp_var = StringVar(root)
max_temp_var.set(str(max_temp))  # 初期値設定
max_temp_menu = tk.OptionMenu(root, max_temp_var, *temp_range, command=update_max_temp)
max_temp_menu.pack()

# 更新間隔選択用変数と関数
update_interval = tk.IntVar(value=1000)  # デフォルトは1秒(1000ミリ秒)

# 更新間隔選択用ドロップダウンメニュー
interval_options = tk.OptionMenu(root, update_interval, *list(range(1000, 11000, 1000)))
interval_options.pack()

# グラフ更新関数
def update_graph():
    # Grid Eyeデータ取得
    grid_eye_data = grid_eye.pixels()
    grid_eye_image_org.set_data(grid_eye_data)
    grid_eye_image_bicubic.set_data(grid_eye_data)

    # 軸をクリアせずに画像データだけ更新
    ax_grid_eye_org.draw_artist(grid_eye_image_org)
    ax_grid_eye_bicubic.draw_artist(grid_eye_image_bicubic)

    # カラーバーの範囲を固定
    grid_eye_image_org.set_clim(vmin=min_temp, vmax=max_temp)
    grid_eye_image_bicubic.set_clim(vmin=min_temp, vmax=max_temp)

    canvas_grid_eye.draw()

    # PIRデータ更新
    pir_value = GPIO.input(channel)
    current_time = datetime.now()
    pir_values.append(pir_value)
    times.append(current_time)

    ten_minutes_ago = current_time - timedelta(minutes=10)
    while times and times[0] < ten_minutes_ago:
        times.pop(0)
        pir_values.pop(0)

    ax_pir.clear()
    ax_pir.plot(times, pir_values, marker='o', linestyle='-')
    ax_pir.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax_pir.set_ylim(0, 1)
    figure_pir.autofmt_xdate()
    canvas_pir.draw()

    # CSV記録が有効な場合、データを記録
    if is_recording:
        current_time = datetime.now()
        pir_value = GPIO.input(channel)
        grid_eye_data = grid_eye.pixels()
        flattened_data = [item for sublist in grid_eye_data for item in sublist]
        with open(csv_file_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([current_time, pir_value] + flattened_data)

    root.after(update_interval.get(), update_graph)  # 1秒後に再度update_graphを呼び出す

update_graph()  # 初回のグラフ更新を呼び出し

# GUIの終了処理
def on_closing():
    GPIO.cleanup()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
