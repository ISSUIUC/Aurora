import numpy as np
import matplotlib.pyplot as plt

data = np.fromfile("output.bin", dtype=np.uint8)

print(data[:1000])

# # print((data[1:] - data[:-1])[:1000])
# plt.hist(data[1:] - data[:-1], bins=255)
# # plt.scatter(range(0, len(data[:-1])), data[:-1] - data[1:])
# plt.show()
bits = np.unpackbits(data, bitorder='big')
samples = (bits * 2 - 1).astype(np.int8)

sample_rate = 4e6

fft_size = 1024
num_rows = len(samples) // fft_size # // is an integer division which rounds down
spectrogram = np.zeros((num_rows, fft_size))
for i in range(num_rows):
    spectrogram[i,:] = 10*np.log10(np.abs(np.fft.fftshift(np.fft.fft(samples[i*fft_size:(i+1)*fft_size])))**2)

otp = plt.imshow(spectrogram, aspect='auto', extent = [sample_rate/-2/1e6, sample_rate/2/1e6, len(samples)/sample_rate, 0])
plt.colorbar(otp, label='Power [dB]')

plt.show()
