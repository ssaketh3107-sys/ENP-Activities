"""Activity 1: CAN arbitration for a smart vehicle (teaching model)."""

RATE = 500e3                # bit rate (bit/s)
DEADLINE = 2e-3             # 2 ms
ERROR_BITS = 20             # assumed error frame + overhead (bits)

# ECU, CAN id (lower = higher priority), data bytes, period (s)
MSGS = [
    ("ABS",       0x080, 8, 10e-3),
    ("Airbag",    0x040, 8, 20e-3),
    ("Engine",    0x180, 8, 10e-3),
    ("Dashboard", 0x300, 8, 50e-3),
]


def t_frame(d, rate=RATE):
    return (47 + 8 * d) * 1.2 / rate


def run(title, msgs, error_on=None):
    """All messages ready at t=0; lowest ID wins each round."""
    print(f"\n{title}")
    print(f"{'ECU':<10}{'ID':<7}{'wait ms':>9}{'tx ms':>8}{'done ms':>9}  deadline")
    t = 0.0
    for ecu, cid, d, _ in sorted(msgs, key=lambda m: m[1]):
        wait, tx = t, t_frame(d)
        if ecu == error_on:
            t += tx + ERROR_BITS / RATE      # corrupted attempt, then error frame
        t += tx                              # (re)transmission
        status = "OK" if t <= DEADLINE else "MISS"
        print(f"{ecu:<10}{cid:#05x}  {wait*1e3:9.4f}{tx*1e3:8.4f}{t*1e3:9.4f}  {status}")


run("1-3. Arbitration @ 500 kbit/s", MSGS)
run("4. Error on ABS frame, then retry", MSGS, error_on="ABS")

print("\n5. Bit rate vs bus load")
for rate in (250e3, 500e3, 1e6):
    load = sum(t_frame(d, rate) / p for _, _, d, p in MSGS)
    print(f"  {rate/1e3:6.0f} kbit/s  frame={t_frame(8, rate)*1e3:.4f} ms  load={load:.1%}")

# Q1: ABS given the lowest priority
demoted = [(e, 0x400 if e == "ABS" else c, d, p) for e, c, d, p in MSGS]
run("Q1. ABS demoted to ID 0x400", demoted)
