import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import usb.core
import usb.util
import os
import threading
import queue

# =============================
# Settings
# =============================
FS = 4e6           # Sampling rate (Hz)
NFFT = 4096        # FFT size
PACKET_SIZE = 4096*8 # Bytes per USB packet
CMAP = 'jet'       # Colormap for display
ROLL_LEN = 200     # Number of time steps in waterfall
MODE = 'usb'       # 'usb' or 'sin'
# =============================

# Create figure
fig, ax = plt.subplots(figsize=(10, 6))
waterfall = np.zeros((ROLL_LEN, NFFT // 2))
time_counter = 0
spec_img = ax.imshow(
    waterfall,
    aspect='auto',
    origin='lower',
    extent=[0, FS / 2, 0, ROLL_LEN],
    cmap=CMAP,
    vmin=-100,
    vmax=0,
)
plt.title('Rolling Waterfall Spectrum')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Time [frames]')
plt.colorbar(spec_img, label='Power [dB]')

# =============================
# Initialize USB if needed
# =============================
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

# =============================
# Update function for animation
# =============================

# thread it
buffer_queue = queue.Queue()

def read_data():
    while True:
        try:
            data = ep_in.read(PACKET_SIZE)
            if len(data) == 0:
                print("empty buffer!")
            buffer_queue.put(data)
            # data_text = bytearray(data.tobytes())
            # # if data_text[0] != 0x20 and data_text[1] == 0x20:
            # #     data_text[0] = 0x20
            # # if data_text[-1] != 0x20 and data_text[-2] == 0x20:
            # #     data_text[-1] = 0x20
            # print(data_text)
            # data = bytes(data_text)
            # print(data)
        except usb.core.USBError as e:
            print(f"USB ERROR {str(e)}")
            break


def write_data_to_file():
    with open("output.bin", "wb") as f:
        while True:
            # Now write the bytes
            f.write(buffer_queue.get())

threads = []
threads.append(threading.Thread(target=read_data))

for t in threads:
    t.start()

# Wait for all threads to finish
for t in threads:
    t.join()
