import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import usb.core
import usb.util
import os
from queue import Queue
import threading
import time
# =============================
# Settings
# =============================
FS = 4e6           # Sampling rate (Hz)
PACKET_SIZE =  4096  * 8 # Bytes per USB packet
NFFT = PACKET_SIZE        # FFT size
CMAP = 'jet'       # Colormap for display
ROLL_LEN = 200     # Number of time steps in waterfall
MODE = 'usb'       # 'usb' or 'sin'
# =============================
# Create figure
usb_data_queue = Queue(-1)
if MODE == 'usb':
    dev = usb.core.find(idVendor=0x155, idProduct=0xa40a)
    if dev is None:
        raise ValueError("USB device not found!")
    dev.set_configuration()
    cfg = dev.get_active_configuration()
    print(cfg)
    intf = cfg[(1, 0)]
    ep_in = usb.util.find_descriptor(
        intf,
        custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
    )
else:
    ep_in = None

# Constants for CDC control requests
# Request Type: Class (0x02), Interface (0x01), Host to Device (0x00) -> 0x21
CDC_REQUEST_TYPE = 0x21
SET_LINE_CODING = 0x20
SET_CONTROL_LINE_STATE = 0x22

# Target Interface Number for CDC Control is Interface 0
COMM_INTERFACE_NUM = 0 

# --- A. SET_CONTROL_LINE_STATE (DTR and RTS) ---
# Set DTR (b1=1) and RTS (b0=1). Value 0x03 is usually required to activate the port.
try:
    dev.ctrl_transfer(
        bmRequestType=CDC_REQUEST_TYPE,
        bRequest=SET_CONTROL_LINE_STATE,
        wValue=0x03,  # DTR=1, RTS=1 (Data Terminal Ready and Request to Send)
        wIndex=COMM_INTERFACE_NUM,
        data_or_wLength=None,
        timeout=1000
    )
    print("Sent SET_CONTROL_LINE_STATE.")
except usb.core.USBError as e:
    print(f"Error sending SET_CONTROL_LINE_STATE: {e}")

# --- B. SET_LINE_CODING (Baud Rate, Stop Bits, Parity, Data Bits) ---
# TinyUSB often requires this, even if the values don't matter for bulk data.
# 115200 baud, 8N1 (default for many terminals)
LINE_CODING_DATA = [
    0x00, 0xC2, 0x01, 0x00,  # Baud Rate 115200 (0x0001C200) - LSB first
    0x00,                    # Stop bits (0: 1 stop bit)
    0x00,                    # Parity (0: None)
    0x08                     # Data bits (8)
]
try:
    dev.ctrl_transfer(
        bmRequestType=CDC_REQUEST_TYPE,
        bRequest=SET_LINE_CODING,
        wValue=0,
        wIndex=COMM_INTERFACE_NUM,
        data_or_wLength=LINE_CODING_DATA,
        timeout=1000
    )
    print("Sent SET_LINE_CODING.")
except usb.core.USBError as e:
    print(f"Error sending SET_LINE_CODING: {e}")

# Wait a moment for the device to process the commands
# The ESP32 should now be connected!
time.sleep(0.1) 
# Now proceed to your data reading logic using Interface 1
while True:
    start = time.time()
    data = ep_in.read(PACKET_SIZE, timeout=1000)
    print(data)