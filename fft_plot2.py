import numpy as np
import matplotlib.pyplot as plt

data = np.fromfile("out.bin", dtype=np.float32)
# data = data[120238464:]
# int(4e6 * 12.5)
# # print((data[1:] - data[:-1])[:1000])
# plt.hist(data[1:] - data[:-1], bins=255)
# # plt.scatter(range(0, len(data[:-1])), data[:-1] - data[1:])
# plt.show()
# bits = np.unpackbits(data, bitorder='big')
avg = max(data) // 2
avg *= 1.5
vec_map = data > avg
data[vec_map] = 1
data[~vec_map] = 0
bits = data
array = (bits.astype(np.int8) * 2 - 1)
# Now separate into i and q
samples = array[::2] + array[1::2] * 1j
print(samples.shape)
sample_rate = 4e6

fft_size = 1024
num_rows = len(samples) // fft_size # // is an integer division which rounds down
spectrogram = np.zeros((num_rows, fft_size))
for i in range(num_rows):
    spectrogram[i,:] = 10*np.log10(np.abs(np.fft.fftshift(np.fft.fft(samples[i*fft_size:(i+1)*fft_size])))**2)

otp = plt.imshow(spectrogram, aspect='auto', extent = [sample_rate/-2/1e6, sample_rate/2/1e6, len(samples)/sample_rate, 0])
plt.colorbar(otp, label='Power [dB]')
# plt.scatter(array[::2], array[1::2])
plt.show()
