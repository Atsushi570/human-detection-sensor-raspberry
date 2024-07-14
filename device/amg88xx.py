import smbus2
import numpy as np

class GridEYESensor:
    def __init__(self, address=0x69, bus_number=1, enable_ma=False):
        self.address = address
        self.bus = smbus2.SMBus(bus_number)
        self.pixel_start = 0x80
        self.pixel_end = 0xFF
        self.pixel_temp_conversion = 0.25
        self.enable_moving_average(enable_ma)  # 初期化時に移動平均の設定を行う

    def enable_moving_average(self, enable=False):
        # 移動平均を有効/無効にするためのレジスタ設定手順
        sequence = [
            (0x1F, 0x50),
            (0x1F, 0x45),
            (0x1F, 0x57),
            (0x07, 0x20 if enable else 0x00),
            (0x1F, 0x00)
        ]
        for reg, val in sequence:
            self.bus.write_byte_data(self.address, reg, val)

    def pixels(self):
        temperatures = []
        for i in range(self.pixel_start, self.pixel_end + 1, 2):
            data = self.bus.read_i2c_block_data(self.address, i, 2)
            raw = (data[1] << 8) | data[0]
            temp = self.twos_complement_to_float(raw) * self.pixel_temp_conversion
            temperatures.append(temp)
        
        return np.array(temperatures).reshape(8, 8)

    def twos_complement_to_float(self, val):
        if val & 0x800:  # 最上位ビットが1の場合、負の値
            val -= 0x1000
        return val

    def __del__(self):
        self.bus.close()
