# Getting started: your first story video

This guide makes a 20 to 25 minute "story" video (tale mode): one picture per paragraph, a narrator, large captions and chapters. You need no video-editing skills. Plan about 2 hours for the first one, mostly waiting.

What it costs: nothing, if you use the free voice and your Gemini account for pictures.

## 1. Install (once)

1. Install **Python 3.10 or newer**: https://www.python.org/downloads/ (on Windows, tick "Add python.exe to PATH" during install).
2. Install **FFmpeg**:
   - Windows: open PowerShell and run `winget install Gyan.FFmpeg`, then close and reopen PowerShell.
   - Mac: install Homebrew from https://brew.sh, then run `brew install ffmpeg`.
   - Linux: `sudo apt install ffmpeg`.
3. Download this project: the green **Code** button on GitHub, then **Download ZIP**, and unzip it. (Or `git clone`.)
4. Open a terminal in the project folder and run:

   ```
   python setup.py
   ```

   (On Mac/Linux it may be `python3`.) It installs what it needs, downloads the free voice (about 340 MB), asks for your channel name and keys (press Enter to skip any), and makes a 10-second test video in `films/_setup-test/test.mp4`. Open it: you should see captions.

Everything personal stays on your computer: `.env` (keys and settings), `models/`, `films/` and `local/` are never uploaded. Put your own logo, host picture or music in `local/`.

## 2. Write your script

Make a folder for the video, for example `films/napoleon/`, and create `script.md` in it:

```
# Napoleon: The Soldier Who Crowned Himself Emperor

## The Man Who Was Not Short

[host] Hello, and welcome to my channel. Today you will practise your English with one of the most famous lives in history.

You probably think Napoleon was a very short man. Many people do. But this is not true.

## A Boy From a Small Island

Our story begins on the fifteenth of August, seventeen sixty-nine...
```

- `#` is the video title, `##` starts a chapter (shown on screen and listed for YouTube).
- Each paragraph gets its own picture, so keep paragraphs to 2 to 5 sentences.
- `[host]` paragraphs show your presenter picture (same one each time).
- Write numbers as words ("seventeen sixty-nine") so every voice reads them correctly.
- About 2,800 words makes a 22 to 24 minute video.

Tip: ask ChatGPT or Gemini to write it for you in this format, then check every fact yourself.

Then run:

```
python tale/tale.py parse films/napoleon
```

## 3. Make the pictures (Gemini, free)

```
python tale/images.py prompts films/napoleon
```

This writes `films/napoleon/prompts.txt`: one line per picture, like `012 | Soldiers march through a French village at dawn`. It starts filled with your paragraph text. To get better picture descriptions, open `films/napoleon/ai-helper.txt`, paste all of it into ChatGPT or Gemini, and save the answer as `prompts.txt`.

Then make the browser script:

```
python tale/images.py snippet films/napoleon
```

(Add `--style watercolour`, `--style storybook`, `--style photo`, `--style paper` (cartoon on paper), `--style comic`, or your own style sentence in quotes. Add `--character "a round-faced old shopkeeper with a red scarf"` to keep the same invented main character in every picture. The default is classical oil painting. You can set your favourite in `.env` as `T2F_IMAGE_STYLE`.)

Now:

1. Open https://gemini.google.com/app in Chrome or Edge and sign in.
2. Press **F12** (Mac: **Cmd+Option+J**) and click **Console**.
3. Open `films/napoleon/gemini-snippet.js` in Notepad, copy all of it, paste it into the Console and press **Enter**. The first time, Chrome asks you to type `allow pasting` first.
4. Leave the tab open and in front. A box in the bottom corner shows progress (about 20 to 40 seconds a picture).
5. Every 25 pictures a zip file downloads (`napoleon-images-01.zip`, `-02`, ...). Keep them.
6. If it stops, paste the snippet again: finished pictures are skipped.

Import the pictures:

```
python tale/images.py import films/napoleon ~/Downloads/napoleon-images-*.zip --host local/host.jpg
```

`--host` is your presenter picture for `[host]` paragraphs (make one in Gemini once and keep it in `local/`). The command tells you if any picture is missing.

## 4. Narration (pick one)

**Free, offline (Kokoro):**

```
python tale/kvo.py films/napoleon --speed 0.83
```

Voices: `am_michael` (default), `am_fenrir`, `am_onyx`, `bm_george` (British), `af_heart` (female) and more. `--speed 0.83` is a calm pace for learners; 1.0 is normal.

**Google voices in AI Studio (free, no key, recommended):** the "Generate speech" voices, driven in your browser like the pictures.

```
python tale/aistudio.py snippet films/napoleon
```

1. Open https://aistudio.google.com/generate-speech and sign in, then click **Create new dialog**.
2. In the speech block, pick the voice (**Speaker**) and **Style** you want. Optional: "Run settings" (top right) for the model.
3. Press **F12**, click **Console**, paste all of `films/napoleon/aistudio-snippet.js`, press **Enter**.
4. Leave the tab open and in front. Each paragraph takes about 10 seconds; every 25 recordings a zip downloads (`napoleon-voice-01.zip`, ...). If it stops, paste it again: finished parts are skipped.
5. Import: `python tale/aistudio.py import films/napoleon ~/Downloads/napoleon-voice-*.zip`

Add `--mode chapter` to the snippet command to record a whole chapter per run (fewer runs); the import then splits each chapter into paragraphs at the pauses. It is usually exact, but listen to a few files to be sure.

**Google voices with an API key:** the same voices, without the browser.

1. Get a key at https://aistudio.google.com/apikey and add it with `python setup.py --keys`.
2. Run:

   ```
   python tale/gvo.py films/napoleon --voice Charon
   ```

   Good narrator voices: Charon, Iapetus, Algieba, Sadaltager, Gacrux, Sulafat. The free tier has a daily limit; if it is reached, the script stops and you run it again later. Finished paragraphs are kept.

**ElevenLabs (paid):** `python tale/tale.py vo films/napoleon --voice VOICE_ID` with `ELEVEN_KEY` in `.env`.

Listen to a few files in `films/napoleon/vo/` before building. To redo one paragraph, delete its two files (`012.mp3` and `012.json`) and run the narration command again.

## 5. Build the video

```
python tale/tale.py build films/napoleon
```

Add `--music local/music/calm.mp3` for a quiet music bed (or set `T2F_MUSIC` in `.env`). Your channel name from `.env` appears at the top left.

You get:

- `films/napoleon/final.mp4`: the video, 1080p, at YouTube's loudness (-14 LUFS).
- `films/napoleon/chapters.txt`: chapter times to paste into the YouTube description.

A 23-minute video takes about 30 to 60 minutes to build, depending on your computer.

## 6. Upload checklist

- Title: topic first, then the type, e.g. `Napoleon: The Soldier Who Crowned Himself Emperor | English Listening Practice`.
- Description: one line with your main search words, a short summary, then `chapters.txt`.
- Thumbnail: `python tale/thumb.py films/napoleon --top "The soldier who" --big "Crowned Himself" --pill "Learn English"` makes it from `thumb_src.jpg`. Try `--layout brand` or `--layout money` for a second one and run both in Test & Compare.
- Check your title ideas: `python tools/titlecheck.py "Title one" "Title two"`. A question, a number and a strong word usually win.
- Say in the description that the pictures and voice are AI-made.
- Category Education, video language set, "not made for kids" if true.
- New channels must verify a phone number before uploading videos over 15 minutes.

## Problems?

- `ffmpeg not found`: install FFmpeg (step 1) and open a new terminal.
- Captions in the wrong font: run `python setup.py` again (it makes the caption fonts).
- The Gemini snippet stops with "prompt box not found": make sure the page is `gemini.google.com/app`, not a shared link, and you're signed in.
- Gemini refuses a picture: edit that line in `prompts.txt` (less violence, no real living people), make the snippet again and paste it; finished pictures are skipped.
- To start the pictures from scratch: in the Console run `localStorage.removeItem("t2f_done_napoleon")`.
