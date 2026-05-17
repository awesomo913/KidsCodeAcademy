# From: scripts/compress_audio_ogg.py:56
# Encode `src` (wav) → `dst` (ogg/opus). Returns True on success.

def convert_wav_to_ogg(ffmpeg: str, src: Path, dst: Path) -> bool:
    """Encode `src` (wav) → `dst` (ogg/opus). Returns True on success."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg, "-y", "-loglevel", "error",
        "-i", str(src),
        "-ac", "1",            # force mono
        "-c:a", "libopus",
        "-b:a", OPUS_BITRATE,
        "-application", "voip",  # speech optimization
        str(dst),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        log.error("ffmpeg FAIL %s: %s", src.name, exc.stderr.strip())
        return False
    return True
