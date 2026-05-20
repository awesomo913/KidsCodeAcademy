# From: scripts/prebake_audio.py:67
# Read SAPI wav, add leading silence + low-pass + slight gain, write final wav.

def _post_process(in_path: Path, out_path: Path) -> None:
    """Read SAPI wav, add leading silence + low-pass + slight gain, write final wav."""
    with wave.open(str(in_path), "rb") as r:
        n_channels = r.getnchannels()
        sample_width = r.getsampwidth()
        sr = r.getframerate()
        n_frames = r.getnframes()
        raw = r.readframes(n_frames)

    if sample_width != 2:
        log.warning("unexpected sample_width=%d for %s; copying through", sample_width, in_path)
        out_path.write_bytes(in_path.read_bytes())
        return

    fmt = f"<{n_frames * n_channels}h"
    samples = list(struct.unpack(fmt, raw))
    if n_channels > 1:
        per_chan: list[list[int]] = [samples[c::n_channels] for c in range(n_channels)]
        samples = [sum(c) // n_channels for c in zip(*per_chan)]
    floats = [s / 32768.0 for s in samples]

    dt = 1.0 / sr
    rc = 1.0 / (2.0 * math.pi * LPF_CUTOFF_HZ)
    a = dt / (rc + dt)
    filtered: list[float] = []
    y_prev = 0.0
    for x in floats:
        y = a * x + (1.0 - a) * y_prev
        filtered.append(y)
        y_prev = y

    final = [max(-1.0, min(1.0, s * POST_GAIN)) for s in filtered]

    silence = [0.0] * int(sr * LEADING_SILENCE_MS / 1000.0)
    final_with_silence = silence + final

    out_int16 = struct.pack(
        f"<{len(final_with_silence)}h",
        *(int(s * 32767) for s in final_with_silence),
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(out_int16)
