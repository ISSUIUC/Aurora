import numpy as np
data = "bf e4 6b 9b 4a ff db 7f be 76 f3 9b fe f6 fb cb bd f9 9f cb dd 7f 99 ff 66 65 ff 8f ab e7 6f f6 ec ff db 7f fe 46 f3 97 fe f6 ff 49 ef f7 ff 28 ff f4 7f c1 ef fb 81 f0 fb 7f a1 e7 f7 15 fc ff ff 88 ff 4e ff 2c bf fe 7f c9 6f f7 89 f4 6f bc 8b fe 6f "

data = data.split()
print(len(data))
data = ~np.array([int(a, 16) for a in data], dtype=np.uint8)
array = np.unpackbits(data)
array

import matplotlib.pyplot as plt


plt.plot(array)
plt.show()