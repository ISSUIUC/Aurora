import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal
import threading

def shift(register, feedback, output):
    """GPS Shift Register
    
    :param list feedback: which positions to use as feedback (1 indexed)
    :param list output: which positions are output (1 indexed)
    :returns output of shift register:
    
    """
    
    # calculate output
    out = [register[i-1] for i in output]
    if len(out) > 1:
        out = sum(out) % 2
    else:
        out = out[0]
        
    # modulo 2 add feedback
    fb = sum([register[i-1] for i in feedback]) % 2
    
    # shift to the right
    for i in reversed(range(len(register[1:]))):
        register[i+1] = register[i]
        
    # put feedback in position 1
    register[0] = fb
    
    return out

SV = {
   1: [2,6],
   2: [3,7],
   3: [4,8],
   4: [5,9],
   5: [1,9],
   6: [2,10],
   7: [1,8],
   8: [2,9],
   9: [3,10],
  10: [2,3],
  11: [3,4],
  12: [5,6],
  13: [6,7],
  14: [7,8],
  15: [8,9],
  16: [9,10],
  17: [1,4],
  18: [2,5],
  19: [3,6],
  20: [4,7],
  21: [5,8],
  22: [6,9],
  23: [1,3],
  24: [4,6],
  25: [5,7],
  26: [6,8],
  27: [7,9],
  28: [8,10],
  29: [1,6],
  30: [2,7],
  31: [3,8],
  32: [4,9],
}

def PRN(sv):
    """Build the CA code (PRN) for a given satellite ID
    
    :param int sv: satellite code (1-32)
    :returns list: ca code for chosen satellite
    
    """
    
    # init registers
    G1 = [1 for i in range(10)]
    G2 = [1 for i in range(10)]

    ca = [] # stuff output in here
    
    # create sequence
    for i in range(1023):
        g1 = shift(G1, [3,10], [10])
        g2 = shift(G2, [2,3,6,8,9,10], SV[sv]) # <- sat chosen here from table
        
        # modulo 2 add and append to the code
        ca.append((g1 + g2) % 2)

    # return C/A code!
    return np.array(ca)

def add_to_array(input_array, sig, point):
    for i, v in enumerate(sig):
        input_array[i + point] += v

data = np.fromfile("output.bin", dtype=np.uint8)
bits = np.unpackbits(data, bitorder='big')
array = (bits.astype(np.int8) * 2 - 1)


# We rx at 8Mhz, gold code is at 1.023 Mhz
# How do we up frequency of it
sig = np.repeat(PRN(25), 4)
# Now 
imaginary = signal.hilbert(sig)
# Now let's shift
print(imaginary.shape)

print(np.linspace(0, imaginary.shape[0]))
shifted_array = imaginary * np.exp(1j * 2 * np.pi * 1e5/4e6 * np.arange(0, imaginary.shape[0]))
# print(np.fft.ifft(shifted_array))
# Scan across all signals...
# plt.plot(10*np.log10(np.abs(np.fft.fftshift(np.fft.fft(shifted_array))**2)))
# plt.plot(10*np.log10(np.abs(np.fft.fftshift(np.fft.fft(imaginary))**2)))
# plt.plot(10*np.log10(np.abs(np.fft.fftshift(np.fft.fft(np.real(shifted_array)))**2)))

y = np.random.normal(size=(len(sig) * 5)) * 10
print(array.shape)
# add_to_array(y, signal2, 20000)
# add_to_array(y, sig, 15000)
thread_bank = []
idx_bank = {
    i:[] for i in range(32)
}
signal_bank = {}

for i in range(1, 32):
    signal_bank[i] = np.repeat(PRN(i), 4)

def fn(i, point):
    sig = signal_bank[i]
    corr = np.correlate(array[point * 100000:(point + 1 ) * 100000], sig)
    idx_bank[i].append(np.max(corr))

for point in range(0, array.shape[0] // 100000):
    print(point, "/", (array.shape[0] // 100000))
    for i in range(1, 32):
        thread_bank.append(threading.Thread(target=fn, args=(i, point)))

for t in thread_bank:
    t.start()

for t in thread_bank:
    print(f"Thread {t} done")
    t.join()
# corr2 = np.correlate(y, sig)
# 54722560
# 700000
plt.legend()
for k, v in idx_bank.items():
    plt.plot(v, label=f"{k}")
plt.legend()
# plt.plot(10*np.log10(corr2))
plt.show()
