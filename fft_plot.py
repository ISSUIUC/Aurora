import numpy as np
import matplotlib.pyplot as plt

data = np.fromfile("output.bin", dtype=np.uint8)
bits = np.unpackbits(data, bitorder='big')

array = (bits.astype(np.int8) * 2 - 1) * 64
# Now separate into i and q
samples = array[::2] + array[1::2] * 1j
# print(np.sum(bits[1::2]) / len(bits[2::2]))
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


# 1. Define the frequency and time axes for mapping
freq_axis = np.linspace(sample_rate/-2/1e6, sample_rate/2/1e6, fft_size)
time_axis = np.linspace(0, len(samples)/sample_rate, num_rows)

# 2. Find the index of the peak power in each time slice (row)
peak_indices = np.argmax(spectrogram, axis=1)

# 3. Convert indices to actual frequency values (MHz)
peak_freqs = freq_axis[peak_indices]

# 4. Plotting
plt.figure(figsize=(10, 6))

# Plot the spectrogram
otp = plt.imshow(spectrogram, aspect='auto', 
                 extent=[freq_axis[0], freq_axis[-1], time_axis[-1], time_axis[0]],
                 cmap='viridis')


# Overlay the peak frequency in red
# plt.plot(peak_freqs, time_axis, color='red', linewidth=1, label='Highest Peak')
plt.colorbar(otp, label='Power [dB]')
plt.xlabel('Frequency [MHz]')
plt.ylabel('Time [s]')
plt.title('Vectorized Spectrogram (Windowed)')
plt.show()
