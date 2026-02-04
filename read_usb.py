import usb.core
import usb.util
import os
import time
import numpy as np

# =============================
# Settings
# =============================
FS = 4e6           # Sampling rate (Hz)
NFFT = 4096        # FFT size
PACKET_SIZE = 1024 # Bytes per USB packet
CMAP = 'jet'       # Colormap for display
ROLL_LEN = 200     # Number of time steps in waterfall
MODE = 'usb'       # 'usb' or 'sin'
# =============================


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

# csv_log = open("timings.csv", "w")
# csv_log.write("time,speed,bytes\n")
def update():
    try:
        start = time.time()
        data = ep_in.read(PACKET_SIZE, 10000)
        end = time.time()
        if start != end:
            rate = len(data) / (end - start)
            print(f"{rate:.2f} bytes/s", end="\r")
            # csv_log.write(f"{end},{len(data) / (end - start)},{len(data)}\n")

        data = np.frombuffer(data, dtype=np.uint8)
    except usb.core.USBError:
        data = np.random.randint(0, 255, PACKET_SIZE, dtype=np.uint8)
    return data

with open("output.bin", "wb") as f:
    while True:
        out = update()
        f.write(out.tobytes())
