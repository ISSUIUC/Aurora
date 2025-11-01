with open("bits.txt") as f:
    for line in f.readlines():
        splitted = line.strip().split()
        print([bin(int(a, 16))[2:].rjust(8) for a in splitted])