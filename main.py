import time
from datetime import datetime, timedelta
import RPi.GPIO as GPIO
import tkinter as tk
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

# グラフ更新関数
def update_graph():
    # Grid Eyeデータ取得
    grid_eye_data = grid_eye.pixels()
    grid_eye_image_org.set_data(grid_eye_data)
    grid_eye_image_bicubic.set_data(grid_eye_data)

    # 軸をクリアせずに画像データだけ更新
    ax_grid_eye_org.draw_artist(grid_eye_image_org)
    ax_grid_eye_bicubic.draw_artist(grid_eye_image_bicubic)

    # カラーバーの範囲を調整
    grid_eye_image_org.set_clim(vmin=grid_eye_data.min(), vmax=grid_eye_data.max())
    grid_eye_image_bicubic.set_clim(vmin=grid_eye_data.min(), vmax=grid_eye_data.max())

    canvas_grid_eye.draw()

    # PIRデータ更新
    pir_value =GPIO.input(channel)
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
    figure_pir.autofmt_xdate()
    canvas_pir.draw()

    root.after(1000, update_graph)  # 1秒後に再度update_graphを呼び出す

update_graph()  # 初回のグラフ更新を呼び出し

# GUIの終了処理
def on_closing():
    GPIO.cleanup()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
