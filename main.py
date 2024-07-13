import RPi.GPIO as GPIO
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime, timedelta
import matplotlib.dates as mdates

# GPIO設定
GPIO.setmode(GPIO.BCM)
channel = 4
GPIO.setup(channel, GPIO.IN)

# データ保存用のリスト
times = []
values = []

# グラフ更新関数
def update_graph():
    input_val = GPIO.input(channel)
    current_time = datetime.now()
    
    # データをリストに追加
    times.append(current_time)
    values.append(input_val)
    
    # 過去10分間のデータのみを保持
    ten_minutes_ago = current_time - timedelta(minutes=10)
    while times and times[0] < ten_minutes_ago:
        times.pop(0)
        values.pop(0)
    
    # グラフデータを更新
    ax.clear()
    ax.plot(times, values, marker='o', linestyle='-')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    figure.autofmt_xdate()
    canvas.draw()
    root.after(1000, update_graph)  # 1秒後に再度update_graphを呼び出す

# Tkinter GUI設定
root = tk.Tk()
root.title("GPIO Status Time Series")

# matplotlibグラフ設定
figure = Figure(figsize=(10, 4), dpi=100)
ax = figure.add_subplot(111)
ax.set_title("GPIO Input Over Time")
ax.set_xlabel("Time")
ax.set_ylabel("GPIO State")

canvas = FigureCanvasTkAgg(figure, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

update_graph()  # 初回のグラフ更新を呼び出し

# GUIの終了処理
def on_closing():
    GPIO.cleanup()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
