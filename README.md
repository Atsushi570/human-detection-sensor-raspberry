
# 環境
## 開発マシン
* macOS Sonoma 14.2.1
* xquartz: 2.8.5

## Raspberry　Pi
* Raspberry Pi 3 model B
* Raspberry Pi OS with desktop
  * Release date: July 4th 2024
  * System: 64-bit
  * Kernel version: 6.6
  *Debian version: 12 (bookworm)
* Python 3.11.2

## ピンアサイン
### Raspberry Pi 3 model B
![pin assign raspberry3b](docs/images/raspberry3b-pin-assign.png)

### PIR Motion Sensor
![pin assign motion](docs/images//motion-pin-assign.png)

## 環境構築
I2Cを有効化
```
sudo raspi-config
-> 3 Interfacing Options
--> I5 I2C enable
```

接続確認
```
i2cdetect -y 1
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- 69 -- -- -- -- -- --
70: -- -- -- -- -- -- -- --
```
