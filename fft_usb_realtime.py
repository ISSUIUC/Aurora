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
else:
    ep_in = None
# =============================
# Update function for animation
# =============================
avg = []
def reading_thread():
    global usb_data_queue
    while True:
        start = time.time()
        data = ep_in.read(PACKET_SIZE, timeout=1000)
        end = time.time()
        if not (end - start == 0):
            rate = len(data) / (end - start)
            print(f"Data read: {end - start}: {rate} bytes per second {rate / 125000} Mbps")
        if len(data) == 0:
            continue
            # return [spec_img]
        data = np.frombuffer(data, dtype=np.uint8)
        bits = np.unpackbits(data,bitorder='big')
    # print(*bits)
        samples = (bits * 2 - 1).astype(np.int8)
        # print(samples)
        usb_data_queue.put_nowait(samples)
def update(frame):
    global waterfall, time_counter
    time_counter += 1
    # 1. Get raw data
    # if MODE == 'usb':
    #     try:
    #         # data_text = bytearray(data.tobytes())
    #         # # if data_text[0] != 0x20 and data_text[1] == 0x20:
    #         # #     data_text[0] = 0x20
    #         # # if data_text[-1] != 0x20 and data_text[-2] == 0x20:
    #         # #     data_text[-1] = 0x20
    #         # print(data_text)
    #         # data = bytes(data_text)
    #         # print(data)
    #     except usb.core.USBError:
    #         data = np.random.randint(0, 255, PACKET_SIZE, dtype=np.uint8)
    # else:
    #     # Generate a test sine signal
    #     t = np.arange(PACKET_SIZE) / FS
    #     freq = 100e3  # 100 kHz test tone
    #     samples = np.sin(2 * np.pi * freq * t)
    #     # Convert to 1-bit like ADC
    #     data = ((samples > 0).astype(np.uint8)) * 255
    # # 2. Convert to ±1 samples
    # # bits = np.unpackbits(np.frombuffer(data_text,dtype=np.uint8),bitorder='big')
    # # 3. Compute PSD
    global usb_data_queue
    # if usb_data_queue.empty():
    #     return [spec_img]
    is_okay = False
    while not is_okay:
        samples = usb_data_queue.get()
        Pxx, freqs = plt.mlab.psd(samples, NFFT=NFFT, Fs=FS,noverlap=NFFT//2)
        Pxx_dB = 10 * np.log10(Pxx + 1e-12)

        if len(samples) == 0 or sum(samples) == 0 or not np.isfinite(10*np.log10(abs(sum(samples))/len(samples))):
            continue
            return [spec_img]
        # print(10*np.log10(sum(samples)/len(samples)))
        # 4. Update waterfall (scroll up)
        waterfall = np.roll(waterfall, -1, axis=0)
        waterfall[-1, :] = Pxx_dB[:NFFT // 2]
        # 5. Update image
        spec_img.set_data(waterfall)
        spec_img.set_extent([0, FS / 2, time_counter - ROLL_LEN, time_counter])
        ax.set_ylim(((time_counter - ROLL_LEN), time_counter))
        is_okay = True
    return [spec_img]
# =============================
# Run animation
# =============================
usb_thread = threading.Thread(target=reading_thread,daemon=True)
usb_thread.start()
ani = FuncAnimation(fig, update, interval=0.01, blit=False)
plt.tight_layout()
plt.show()