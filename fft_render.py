import numpy as np
import matplotlib.pyplot as plt
import sys
input_file = sys.argv[1]  
fs = 4e6                     # 4 MHz
NFFT = 4096                  # 
noverlap = NFFT // 2         # 
cmap = 'jet'             # 
# ============================

with open(input_file, "r") as f:
    hex_str = f.read()

hex_str_clean = hex_str.replace(" ", "").replace("\n", "").replace("\r", "")

data_bytes = bytes.fromhex(hex_str_clean)

bits = np.unpackbits(np.frombuffer(data_bytes, dtype=np.uint8))

samples = bits * 2 - 1  # 0->-1, 1->+1

print(f"✅  {len(samples)} samples, duration: {len(samples)/fs:.3f} Sec")

plt.figure(figsize=(10, 6))
Pxx, freqs, bins, im = plt.specgram(samples,
                                    NFFT=NFFT,
                                    Fs=fs,
                                    noverlap=noverlap,
                                    cmap=cmap)

plt.title('Waterfall Spectrum (Max2769 1-bit ADC)')
plt.xlabel('Time [s]')
plt.ylabel('Frequency [Hz]')
plt.colorbar(label='Power [dB]')
plt.tight_layout()
plt.show()