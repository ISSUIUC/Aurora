import numpy as np
data = "bf 17 0e 87 5f 10 14 a1 fa 50 e3 60 3f 45 68 94 25 d0 60 f0 8f f1 20 f8 0f 82 38 7e 17 e2 8a d0 fa 10 9a c3 fa 53 60 14 f8 21 ce c3 85 7f 22 0a af 05 3c 8f fa a5 d0 28 f3 41 e6 c1 3f cb a3 d0 41 40 60 f8 cf f9 28 fe 10 51 7c 2d e5 71 d1 2f 82 46 7c 1f 64 1a fd 93 1d 0d 1f 02 0e c6 57 9a e9 62 3d a7 8b 79 51 0c f3 fa 77 ce 06 f3 08 06 7e ff a7 79 b0 b7 83 c1 93 0f 9e 67 72 5e 89 c5"

data = data.split()
print(len(data))
data = np.array([int(a, 16) for a in data], dtype=np.uint8)
array = np.unpackbits(data)
array

import matplotlib.pyplot as plt


plt.plot(array)
plt.show()