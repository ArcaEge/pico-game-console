# color_setup.py Customise for your hardware config

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2020 Peter Hinch

# As written, supports:
# Adafruit 1.5" 128*128 OLED display: https://www.adafruit.com/product/1431
# Adafruit 1.27" 128*96 display https://www.adafruit.com/product/1673
# Edit the driver import for other displays.

# Demo of initialisation procedure designed to minimise risk of memory fail
# when instantiating the frame buffer. The aim is to do this as early as
# possible before importing other modules.

# WIRING (Adafruit pin nos and names).
# Pyb   SSD
# 3v3   Vin (10)
# Gnd   Gnd (11)
# Y1    DC (3 DC)
# Y2    CS (5 OC OLEDCS)
# Y3    Rst (4 R RESET)
# Y6    CLK (2 CL SCK)
# Y8    DATA (1 SI MOSI)

import machine
import gc

# *** Choose your color display driver here ***
# Driver supporting non-STM platforms
# from drivers.ssd1351.ssd1351_generic import SSD1351 as SSD

# STM specific driver
from drivers.ssd1351.ssd1351 import SSD1351 as SSD

height = 128  # 1.27 inch 96*128 (rows*cols) display
# height = 128 # 1.5 inch 128*128 display

pdc = machine.Pin(15, machine.Pin.OUT, value=0)
pcs = machine.Pin(13, machine.Pin.OUT, value=1)
prst = machine.Pin(14, machine.Pin.OUT, value=1)
#spi = machine.SPI(1, baudrate=3_000_000)
spi = machine.SPI(1, sck=machine.Pin(10, machine.Pin.OUT), mosi=machine.Pin(11, machine.Pin.OUT), miso=machine.Pin(8, machine.Pin.OUT), baudrate=10_000_000)
gc.collect()  # Precaution before instantiating framebuf
ssd = SSD(spi, pcs, pdc, prst, height)  # Create a display instance

