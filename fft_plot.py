import numpy as np
import matplotlib.pyplot as plt

data = np.fromfile("output.bin", dtype=np.uint8)
# data = data[120238464:]
# int(4e6 * 12.5)
# # print((data[1:] - data[:-1])[:1000])
# plt.hist(data[1:] - data[:-1], bins=255)
# # plt.scatter(range(0, len(data[:-1])), data[:-1] - data[1:])
# plt.show()
bits = np.unpackbits(data, bitorder='big')

array = (bits.astype(np.int8) * 2 - 1)
# Now separate into i and q
samples = array[::2] + array[1::2] * 1j
print(np.sum(bits[1::2]) / len(bits[2::2]))
print(samples.shape)
sample_rate = 4e6

fft_size = 4096
num_rows = len(samples) // fft_size # // is an integer division which rounds down


i_channel = bits[::2]
q_channel = bits[1::2]

print(f"I-channel Activity: {np.mean(i_channel)}")
print(f"Q-channel Activity: {np.mean(q_channel)}")

# If this correlation is near 1.0, you have no quadrature information!
correlation = np.corrcoef(i_channel[:1000], q_channel[:1000])[0,1]
print(f"I/Q Correlation: {correlation}")

# 1. Reshape the samples into a 2D array (rows = time, cols = frequency)
samples_trimmed = samples[:num_rows * fft_size].reshape(num_rows, fft_size)

# 2. Apply a Hamming window
# This reduces "spectral leakage" from strong signals
window = np.hamming(fft_size)
windowed_samples = samples_trimmed * window

# 3. Perform the FFT across the rows
# Using axis=1 processes all rows simultaneously
fft_data = np.fft.fft(windowed_samples, axis=1)
fft_data = np.fft.fftshift(fft_data, axes=1)

# 4. Convert to Power (dB)
spectrogram = 10 * np.log10(np.abs(fft_data)**2 + 1e-12)

# 5. Plotting
plt.figure(figsize=(10, 6))
otp = plt.imshow(spectrogram, aspect='auto', 
                 extent=[sample_rate/-2/1e6, sample_rate/2/1e6, len(samples)/sample_rate, 0],
                 cmap='viridis') # 'viridis' or 'magma' often look better for SDR data
plt.colorbar(otp, label='Power [dB]')
plt.xlabel('Frequency [MHz]')
plt.ylabel('Time [s]')
plt.title('Vectorized Spectrogram (Windowed)')
plt.show()
