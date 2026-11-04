"""Activity 2: CAN vs FlexRay for an autonomous vehicle (teaching model)."""

CAN, FLEXRAY = 500e3, 5e6          # bit rates (bit/s)
CYCLE, SLOT = 5e-3, 1e-3           # FlexRay cycle and static slot (s)
ERROR_BITS, ERRORS = 31, 3         # assumed error overhead (bits) and number of faults
BURST = 5                          # infotainment frames released together at t=0

# name, CAN id (assumed: lower = higher priority), period (s), deadline (s)
MSGS = [
    ("Brake",        0x010, 5e-3,   5e-3),
    ("Steering",     0x020, 5e-3,   5e-3),
    ("Wheel-speed",  0x030, 10e-3,  10e-3),
    ("Battery",      0x200, 100e-3, 100e-3),
    ("Infotainment", 0x400, 10e-3,  100e-3),   # event-driven: 10 ms spacing assumed
]
SLOTS = ["Brake", "Steering", "Wheel-speed"]  # FlexRay static slots 1-3 (slot 4 spare)


def t_frame(rate):
    return (47 + 8 * 8) * 1.2 / rate          # 8 data bytes


def verdict(t, deadline):
    return "OK" if t <= deadline else "MISS"


tc, tf = t_frame(CAN), t_frame(FLEXRAY)
retry = ERROR_BITS / CAN + tc                 # one error: error frame + resend
by_id = sorted(MSGS, key=lambda m: m[1])

print(f"1. Frame time: CAN {tc*1e3:.4f} ms | FlexRay {tf*1e3:.4f} ms")

# 2. Busy CAN bus: everything ready at t=0 plus an infotainment burst, lowest ID goes first
order = [m[0] for m in by_id] + ["Infotainment"] * (BURST - 1)
finish = {name: (i + 1) * tc for i, name in enumerate(order)}   # last frame of a name wins

print("\n2,4,5. CAN only: worst latency (ms)")
print(f"{'message':<13}{'deadline':>9}{'busy bus':>10}{'worst':>8}{f'{ERRORS} errors':>10}  verdict")
for i, (name, _, _, deadline) in enumerate(by_id):
    blocking = tc if i < len(by_id) - 1 else 0   # frame already on the bus can't be stopped
    worst = blocking + (i + 1) * tc              # + higher-priority frames + own frame
    with_errors = worst + ERRORS * retry
    print(f"{name:<13}{deadline*1e3:9.1f}{finish[name]*1e3:10.3f}{worst*1e3:8.3f}"
          f"{with_errors*1e3:10.3f}  {verdict(max(finish[name], with_errors), deadline)}")

# 3-5. FlexRay: one static slot per critical message, slot i starts i ms into the cycle
print("\n3-5. FlexRay: worst latency (ms)")
print(f"{'message':<13}{'slot':>5}{'aligned':>9}{'unaligned':>13}")
for name, _, period, deadline in MSGS:
    if name in SLOTS:
        i = SLOTS.index(name)
        aligned = i * SLOT + tf       # data produced at the start of the cycle
        unaligned = period + tf       # slot just missed: wait one full period
        print(f"{name:<13}{i+1:>5}{aligned*1e3:9.3f} {verdict(aligned, deadline):<5}"
              f"{unaligned*1e3:7.3f} {verdict(unaligned, deadline)}")

# 6. Hybrid architecture: how much is left on CAN?
all_can = sum(tc / m[2] for m in MSGS)
left_on_can = sum(tc / m[2] for m in MSGS if m[0] not in SLOTS)
print(f"\n6. CAN load: all on CAN {all_can:.1%} | non-critical only {left_on_can:.1%}")
print(f"   FlexRay: {len(SLOTS)} of 4 slots used, each frame fills {tf / SLOT:.1%} of its slot")