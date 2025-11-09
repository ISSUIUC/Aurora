import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import usb.core
import usb.util
import os

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
def update(frame):
    global waterfall, time_counter

    time_counter += 1

    # 1. Get raw data
    if MODE == 'usb':
        try:
            data = ep_in.read(PACKET_SIZE)
            if len(data) == 0:
                return [spec_img]
            data = np.frombuffer(data, dtype=np.uint8)
            # data_text = bytearray(data.tobytes())
            # # if data_text[0] != 0x20 and data_text[1] == 0x20:
            # #     data_text[0] = 0x20
            # # if data_text[-1] != 0x20 and data_text[-2] == 0x20:
            # #     data_text[-1] = 0x20
            # print(data_text)
            # data = bytes(data_text)
            # print(data)
        except usb.core.USBError:
            data = np.random.randint(0, 255, PACKET_SIZE, dtype=np.uint8)
    else:
        # Generate a test sine signal
        t = np.arange(PACKET_SIZE) / FS
        freq = 100e3  # 100 kHz test tone
        samples = np.sin(2 * np.pi * freq * t)
        # Convert to 1-bit like ADC
        data = ((samples > 0).astype(np.uint8)) * 255

    # 2. Convert to ±1 samples
    # bits = np.unpackbits(np.frombuffer(data_text,dtype=np.uint8),bitorder='big')
    bits = np.unpackbits(data,bitorder='big')
    # print(*bits)

    samples = (bits * 2 - 1).astype(np.int8)
    # 3. Compute PSD
    Pxx, freqs = plt.mlab.psd(samples, NFFT=NFFT, Fs=FS,noverlap=NFFT//2)
    Pxx_dB = 10 * np.log10(Pxx + 1e-12)
    print(10*np.log10(sum(samples)/len(samples)))

    # 4. Update waterfall (scroll up)
    waterfall = np.roll(waterfall, -1, axis=0)
    waterfall[-1, :] = Pxx_dB[:NFFT // 2]

    # 5. Update image
    spec_img.set_data(waterfall)
    spec_img.set_extent([0, FS / 2, time_counter - ROLL_LEN, time_counter])
    NFFT / FS
    ax.set_ylim(((time_counter - ROLL_LEN) * NFFT / FS, time_counter* NFFT / FS))
    return [spec_img]

# =============================
# Run animation
# =============================
ani = FuncAnimation(fig, update, interval=1, blit=False)
plt.tight_layout()
plt.show()