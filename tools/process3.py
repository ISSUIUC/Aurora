with open("bits2.txt") as f:
    out = f.read().split()
    print(out)
    # Now convert to bits (LSB)
    print("".join([bin(int(a, 16))[2:][::-1] for a in out]))
