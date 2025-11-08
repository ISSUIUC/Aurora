import numpy as np

import matplotlib.pyplot as plt


with open("bits2.txt") as f:
    out = f.read().split()
    print(out)
    # Now convert to bits (LSB)
    samples = 1024
    sample_frequency = 4e6
    output = []
    for a in out:
        output += *(bin(int(a, 16))[2:][::-1].zfill(8))
    print([ for a in out])
    
    binary_array = np.array([bin(int(a, 16))[2:][::-1] for a in out])
    batch = np.array_split(binary_array, samples)
    Y = np.fft.fft(batch[0])
    freq = np.fft.fftfreq(samples, 1/sample_frequency * samples)
    print(batch)
    print(Y)
    plt.plot( freq, np.abs(Y))
