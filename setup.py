#!/usr/bin/env python3
"""Topic2Film setup: run this once after downloading the project.

  python setup.py            set up tale mode (story videos), ask for your keys, and make a 10-second test video
  python setup.py --keys     change your keys, channel name and default voices
  python setup.py --full     also set up documentary mode (Node.js packages, larger Python packages)
  python setup.py --yes      answer yes to every question (no prompts)

Everything personal (keys, channel name, logo, music, your films) stays in your own copy:
.env, models/, films/ and local/ are never uploaded to GitHub.
"""
import os, platform, shutil, subprocess, sys, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
ENV = os.path.join(ROOT, ".env")
KOKORO = os.path.join(ROOT, "models", "kokoro")
KOKORO_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
FONTS_SRC = os.path.join(ROOT, "video", "public", "fonts")
FONTS_DST = os.path.join(ROOT, "tale", "fonts")
TALE_PKGS = ["numpy", "opencv-python-headless", "kokoro-onnx", "soundfile", "fonttools", "brotli"]
YES = "--yes" in sys.argv
OS = platform.system()          # Windows, Darwin, Linux


def step(t): print("\n== " + t)
def ok(t): print("   ok: " + t)
def warn(t): print("   !! " + t)


def ask(q, default=""):
    if YES:
        return default
    try:
        a = input(f"   {q}" + (f" [{default}]" if default else "") + ": ").strip()
    except EOFError:
        a = ""
    return a or default


def yes(q, default=True):
    a = ask(q + (" (Y/n)" if default else " (y/N)"), "y" if default else "n")
    return a.lower().startswith("y")


def pip_install(pkgs):
    base = [sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "-q"] + pkgs
    r = subprocess.run(base)
    if r.returncode and OS == "Linux":              # system Python on newer Linux needs this flag
        r = subprocess.run(base + ["--break-system-packages"])
    return r.returncode == 0


def check_python():
    step("Python")
    if sys.version_info < (3, 10):
        sys.exit(f"   Python 3.10 or newer is needed; you have {platform.python_version()}. Get it from https://www.python.org/downloads/")
    ok(platform.python_version())


def check_ffmpeg():
    step("FFmpeg (makes the video files)")
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        out = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
        if " subtitles " not in out:
            warn("your FFmpeg has no 'subtitles' filter (libass). Captions need it: install the full build below.")
        ok(shutil.which("ffmpeg"))
        return True
    hint = {"Windows": "open PowerShell and run:  winget install Gyan.FFmpeg   then close and reopen the terminal",
            "Darwin": "install Homebrew (https://brew.sh), then run:  brew install ffmpeg",
            "Linux": "run:  sudo apt install ffmpeg   (or your system's package manager)"}.get(OS, "see https://ffmpeg.org/download.html")
    warn("FFmpeg not found. To install it, " + hint)
    warn("then run  python setup.py  again.")
    return False


def install_tale():
    step("Python packages for story videos")
    if pip_install(TALE_PKGS):
        ok(", ".join(TALE_PKGS))
    else:
        warn("pip could not install everything. Try:  " + sys.executable + " -m pip install " + " ".join(TALE_PKGS))


def make_fonts():
    step("Caption fonts")
    os.makedirs(FONTS_DST, exist_ok=True)
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        warn("fonttools missing; captions will use a system font"); return
    for fam, w in (("inter", 700), ("inter", 400), ("playfair-display", 700)):
        src = os.path.join(FONTS_SRC, f"{fam}-latin-{w}-normal.woff2")
        dst = os.path.join(FONTS_DST, f"{fam}-{w}.ttf")
        if os.path.exists(dst):
            continue
        try:
            f = TTFont(src); f.flavor = None; f.save(dst)
        except Exception as e:
            warn(f"could not convert {os.path.basename(src)}: {e}")
    ok(", ".join(sorted(os.listdir(FONTS_DST))))


def get_kokoro():
    step("Free voice (Kokoro, about 340 MB, works offline)")
    need = [f for f in ("kokoro-v1.0.onnx", "voices-v1.0.bin") if not os.path.exists(os.path.join(KOKORO, f))]
    if not need:
        ok("already downloaded"); return
    if not yes("Download the free voice now?"):
        warn("skipped. You can still use Google (Gemini) or ElevenLabs voices."); return
    os.makedirs(KOKORO, exist_ok=True)
    for f in need:
        dst = os.path.join(KOKORO, f); tmp = dst + ".part"
        print(f"   downloading {f} ...", flush=True)
        try:
            with urllib.request.urlopen(KOKORO_URL + f, timeout=60) as r, open(tmp, "wb") as out:
                total = int(r.headers.get("Content-Length") or 0); got = 0
                while True:
                    b = r.read(1 << 20)
                    if not b: break
                    out.write(b); got += len(b)
                    pct = got * 100 // total if total else 0
                    if total and pct // 10 != (got - len(b)) * 100 // total // 10:
                        print(f"   {pct}%", flush=True)
            os.replace(tmp, dst)
        except Exception as e:
            warn(f"download failed ({e}). Run setup again later."); return
    ok("saved in models/kokoro")


def read_env():
    d = {}
    if os.path.exists(ENV):
        for line in open(ENV, encoding="utf-8"):
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1); d[k.strip()] = v.strip()
    return d


def write_env(d):
    lines = ["# Your private settings. This file stays on your computer and is never uploaded.",
             "",
             "# Google AI Studio key for Gemini voices (free): https://aistudio.google.com/apikey",
             f"GEMINI_API_KEY={d.get('GEMINI_API_KEY', '')}",
             "# ElevenLabs key (optional, paid voices): https://elevenlabs.io/app/settings/api-keys",
             f"ELEVEN_KEY={d.get('ELEVEN_KEY', '')}",
             "# Stock footage keys (documentary mode only)",
             f"PIXABAY_KEY={d.get('PIXABAY_KEY', '')}",
             f"COVERR_KEY={d.get('COVERR_KEY', '')}",
             "",
             "# Your channel name, shown at the top left of story videos (leave empty for none)",
             f"T2F_CHANNEL={d.get('T2F_CHANNEL', '')}",
             "# Default voices and picture style",
             f"T2F_KOKORO_VOICE={d.get('T2F_KOKORO_VOICE', 'am_michael')}",
             f"T2F_GEMINI_VOICE={d.get('T2F_GEMINI_VOICE', 'Charon')}",
             f"T2F_GEMINI_TTS_MODEL={d.get('T2F_GEMINI_TTS_MODEL', 'gemini-3.8-flash-tts')}",
             f"T2F_IMAGE_STYLE={d.get('T2F_IMAGE_STYLE', 'oil')}",
             "# Optional background music file for story videos, e.g. local/music/calm.mp3",
             f"T2F_MUSIC={d.get('T2F_MUSIC', '')}", ""]
    open(ENV, "w", encoding="utf-8").write("\n".join(lines))


def keys():
    step("Your keys and channel (saved only in .env on this computer)")
    d = read_env()
    show = lambda k: ("(saved)" if d.get(k) else "")
    print("   Press Enter to keep what is there or to skip.")
    for k, label in (("T2F_CHANNEL", "Channel name"),
                     ("GEMINI_API_KEY", "Google AI Studio key (free, for Gemini voices)"),
                     ("ELEVEN_KEY", "ElevenLabs key (optional)")):
        v = ask(f"{label} {show(k)}")
        if v:
            d[k] = v
    write_env(d)
    ok(".env saved")


def full():
    step("Documentary mode")
    if not shutil.which("npm"):
        warn("Node.js not found. Install the LTS version from https://nodejs.org and run  python setup.py --full  again.")
    else:
        r = subprocess.run("npm ci", cwd=os.path.join(ROOT, "video"), shell=True)
        ok("Node packages installed") if r.returncode == 0 else warn("npm ci failed; see the messages above")
    if pip_install(["-r", os.path.join(ROOT, "tools", "requirements.txt")]):
        ok("Python packages for documentary mode")
    else:
        warn("some documentary packages failed; the README lists them")


def test_video(have_ffmpeg):
    step("Test video")
    if not have_ffmpeg:
        warn("skipped (FFmpeg missing)"); return
    film = os.path.join(ROOT, "films", "_setup-test")
    os.makedirs(film, exist_ok=True)
    open(os.path.join(film, "script.md"), "w", encoding="utf-8").write(
        "# Setup test\n\n## It works\n\n[host] Hello, this is a short test of Topic2Film.\n\nIf you can read this caption, your setup is ready.\n")
    tale = os.path.join(ROOT, "tale", "tale.py")
    for args in (["fake", film], ["build", film, "--out", "test.mp4"]):
        r = subprocess.run([sys.executable, tale] + args, capture_output=True, text=True)
        if r.returncode:
            warn("test failed:\n" + (r.stderr or r.stdout)[-1500:]); return
    ok("made " + os.path.join("films", "_setup-test", "test.mp4") + "  (open it: you should see captions on two coloured pictures)")


def main():
    print("Topic2Film setup (" + OS + ")")
    if "--keys" in sys.argv:
        keys(); return
    check_python()
    have_ffmpeg = check_ffmpeg()
    install_tale()
    make_fonts()
    get_kokoro()
    if not os.path.exists(ENV) or not YES:
        keys()
    if "--full" in sys.argv:
        full()
    test_video(have_ffmpeg)
    print("\nAll set. Next: read GETTING_STARTED.md (step 2: write your script).")


if __name__ == "__main__":
    main()
