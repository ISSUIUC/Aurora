import serial
# TODO Get right com port -- base it off the esp3
ser = serial.Serial("COMXX", 115200, timeout=0)
FFT_SIZE = 1024
while True:
    output = ser.read(FFT_SIZE)
    # Dump to file
    # Also FFT it
