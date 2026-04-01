"""
Verify MAX2769 counting mode output.
 
Reads data from USB (live) or output.bin (offline) and checks whether
the serial bitstream contains a sequential counter pattern.
 
MAX2769 DSP interface frame format (when STAMPEN=1):
  [DIEID(2b) | STRMBITS(2b) | FRAME_NUMBER(28b)] [data (STRMCOUNT-dependent)]
 
Frame lengths by STRMCOUNT:
  000 = 128 bits, 001 = 256, 010 = 512, 011 = 1024,
  100 = 2048, 101 = 4096, 110 = 8192, 111 = 16384
 
Data is serialized in 16-bit segments: bit0 x16, then bit1 x16, etc.
"""
 
import numpy as np
import sys
import usb.core
import usb.util
 
# =============================
# Settings
# =============================
PACKET_SIZE = 1024
NUM_PACKETS = 64  # how many packets to capture
SOURCE = "usb"    # "usb" or "file"
FILE_PATH = "output.bin"
MAX_FILE_BYTES = NUM_PACKETS * PACKET_SIZE
# =============================
 
# STRMCOUNT value -> data bits per frame (excluding 32-bit stamp if enabled)
STRMCOUNT_FRAME_LENGTHS = {
    0: 128,
    1: 256,
    2: 512,
    3: 1024,
    4: 2048,
    5: 4096,
    6: 8192,
    7: 16384,
}
 
 
def read_from_usb(num_packets, packet_size):
    dev = usb.core.find(idVendor=0x155, idProduct=0xa40a)
    if dev is None:
        raise ValueError("USB device not found!")
    dev.set_configuration()
    cfg = dev.get_active_configuration()
    intf = cfg[(1, 0)]
    ep_in = usb.util.find_descriptor(
        intf,
        custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
    )
 
    chunks = []
    for i in range(num_packets):
        try:
            data = ep_in.read(packet_size, 5000)
            chunks.append(np.frombuffer(data, dtype=np.uint8))
        except usb.core.USBError as e:
            print(f"USB read error on packet {i}: {e}")
            break
    if not chunks:
        raise RuntimeError("No data received from USB")
    return np.concatenate(chunks)
 
 
def read_from_file(path, max_bytes):
    data = np.fromfile(path, dtype=np.uint8, count=max_bytes)
    if len(data) == 0:
        raise RuntimeError(f"No data in {path}")
    return data
 
 
def bits_to_words(bits, word_width):
    """Group bits into words of given width, MSB-first within each word."""
    n = (len(bits) // word_width) * word_width
    bits = bits[:n]
    reshaped = bits.reshape(-1, word_width)
    powers = 2 ** np.arange(word_width - 1, -1, -1)
    return reshaped @ powers
 
 
def bits_to_words_lsb(bits, word_width):
    """Group bits into words of given width, LSB-first within each word."""
    n = (len(bits) // word_width) * word_width
    bits = bits[:n]
    reshaped = bits.reshape(-1, word_width)
    powers = 2 ** np.arange(word_width)
    return reshaped @ powers
 
 
def check_counter(words, word_width):
    """Check if words form a sequential counter. Returns stats."""
    if len(words) < 2:
        return None
 
    diffs = np.diff(words.astype(np.int64))
    max_val = 2 ** word_width
 
    # A counter increments by 1 each step, wrapping at max_val
    correct = (diffs == 1) | (diffs == -(max_val - 1))
    num_correct = np.sum(correct)
    total = len(diffs)
    pct = 100.0 * num_correct / total
 
    return {
        "word_width": word_width,
        "num_words": len(words),
        "correct_transitions": int(num_correct),
        "total_transitions": total,
        "percent_correct": pct,
        "first_errors": np.where(~correct)[0][:10],
    }
 
 
def try_frame_parse(bits, frame_len, stamp_enabled):
    """Try to parse the bitstream as MAX2769 frames and extract frame counters."""
    total_frame_bits = frame_len + (32 if stamp_enabled else 0)
    num_frames = len(bits) // total_frame_bits
 
    if num_frames < 2:
        return None
 
    frame_numbers = []
    for i in range(min(num_frames, 50)):  # check first 50 frames
        offset = i * total_frame_bits
        if stamp_enabled:
            stamp_bits = bits[offset:offset + 32]
            dieid = stamp_bits[0] * 2 + stamp_bits[1]
            strmbits = stamp_bits[2] * 2 + stamp_bits[3]
            # 28-bit frame number (bits 4-31 of stamp)
            fn_bits = stamp_bits[4:32]
            frame_num = 0
            for b in fn_bits:
                frame_num = (frame_num << 1) | int(b)
            frame_numbers.append({
                "frame": i,
                "dieid": dieid,
                "strmbits": strmbits,
                "frame_number": frame_num,
            })
 
    if not frame_numbers:
        return None
 
    # Check if frame numbers increment
    nums = [f["frame_number"] for f in frame_numbers]
    diffs = np.diff(nums)
    correct = np.sum(diffs == 1)
 
    return {
        "frame_len": frame_len,
        "total_frame_bits": total_frame_bits,
        "num_frames": num_frames,
        "frames_checked": len(frame_numbers),
        "frame_numbers": frame_numbers[:10],
        "counter_correct": int(correct),
        "counter_total": len(diffs),
        "counter_pct": 100.0 * correct / len(diffs) if len(diffs) > 0 else 0,
    }
 
 
def main():
    source = sys.argv[1] if len(sys.argv) > 1 else SOURCE
 
    print(f"Reading data from: {source}")
    if source == "usb":
        raw = read_from_usb(NUM_PACKETS, PACKET_SIZE)
    else:
        raw = read_from_file(source if source != "file" else FILE_PATH, MAX_FILE_BYTES)
 
    print(f"Got {len(raw)} bytes ({len(raw) * 8} bits)\n")
 
    # Print first 32 raw hex bytes
    print("First 64 raw bytes (hex):")
    for row in range(4):
        start = row * 16
        print(f"  {start:04x}: " + " ".join(f"{b:02x}" for b in raw[start:start+16]))
    print()
 
    # Try both bit orders and show results for each
    for bitorder in ['little', 'big']:
        bits = np.unpackbits(raw, bitorder=bitorder)
 
        print(f"{'=' * 60}")
        print(f"  Bit order: {bitorder}")
        print(f"{'=' * 60}")
 
        # Print first 64 bits
        print(f"\n  First 64 bits ({bitorder}-endian):")
        for i in range(0, 64, 16):
            chunk = bits[i:i+16]
            print(f"    {i:4d}: {' '.join(str(b) for b in chunk)}")
 
        # -------------------------------------------------------
        # 1) Raw counter detection (no framing, just sequential)
        # -------------------------------------------------------
        print(f"\n  --- Raw counter detection (no framing) ---")
        best_pct = 0
        best_width = 0
        for width in [1, 2, 4, 8, 16]:
            for to_words in [bits_to_words, bits_to_words_lsb]:
                order = "MSB" if to_words == bits_to_words else "LSB"
                words = to_words(bits, width)
                result = check_counter(words, width)
                if result is None:
                    continue
 
                if result['percent_correct'] > 10:  # only show if non-trivial
                    preview = min(20, len(words))
                    print(f"    {width:2d}-bit ({order}): {result['correct_transitions']}/{result['total_transitions']} "
                          f"({result['percent_correct']:.1f}%)  first values: {list(words[:preview])}")
 
                if result['percent_correct'] > best_pct:
                    best_pct = result['percent_correct']
                    best_width = width
 
                if result['percent_correct'] > 95:
                    print(f"    >>> COUNTER DETECTED: {width}-bit {order}-first <<<")
                    # Show around first error if any
                    if len(result['first_errors']) > 0:
                        err_idx = result['first_errors'][0]
                        start = max(0, err_idx - 2)
                        end = min(len(words), err_idx + 4)
                        print(f"    First error at word {err_idx}: ...{list(words[start:end])}...")
 
        # -------------------------------------------------------
        # 2) Frame-based parsing (with 32-bit stamp header)
        # -------------------------------------------------------
        print(f"\n  --- Frame-based parsing (STAMPEN=1) ---")
        for strmcount, frame_data_len in sorted(STRMCOUNT_FRAME_LENGTHS.items()):
            result = try_frame_parse(bits, frame_data_len, stamp_enabled=True)
            if result is None:
                continue
            if result['counter_pct'] > 50:
                print(f"    STRMCOUNT={strmcount} ({frame_data_len} data bits/frame, "
                      f"{result['total_frame_bits']} total bits/frame):")
                print(f"      Frames checked: {result['frames_checked']}")
                print(f"      Counter correct: {result['counter_correct']}/{result['counter_total']} "
                      f"({result['counter_pct']:.1f}%)")
                for f in result['frame_numbers'][:5]:
                    print(f"      Frame {f['frame']:3d}: DIEID={f['dieid']} STRMBITS={f['strmbits']} "
                          f"FRAME_NUM={f['frame_number']}")
                if result['counter_pct'] > 95:
                    print(f"      >>> FRAME COUNTER DETECTED: STRMCOUNT={strmcount} <<<")
 
        print()
 
 
if __name__ == "__main__":
    main()