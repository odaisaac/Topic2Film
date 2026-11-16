# Topic2Film

Turn a topic into a finished YouTube video: script, narration, stock footage, motion graphics, captions, music mix, render, thumbnail and an upload pack.

Two modes:

- **Documentary mode** (`tools/`, `video/`): 7 to 15 minute documentaries built from a shot list (`spec.json`), with stock footage, animated stats, maps, lists and charts, 8 visual style presets, and retention rules built in.
- **Tale mode** (`tale/`): slow, captioned story videos from a plain-text script and one picture per paragraph, for example "learn English through history" channels. Free narration with Kokoro, or ElevenLabs.

Rendering uses [Remotion](https://www.remotion.dev) (documentary mode) and FFmpeg + OpenCV (tale mode).

## Requirements

- Node.js 20+ and Python 3.10+
- FFmpeg
- Chrome or Chromium (Remotion downloads its own if needed)
- Tale mode: just run `python setup.py`. Documentary mode: `python setup.py --full` (adds Node packages and `tools/requirements.txt`)

Keys live in your local `.env` (made by `python setup.py`) or in environment variables. Never commit them.

| Variable | Used for |
|---|---|
| `GEMINI_API_KEY` | Google Gemini voices (`tale/gvo.py`), free from https://aistudio.google.com/apikey |
| `ELEVEN_KEY` | ElevenLabs narration (`tools/vo.py`, `tale/tale.py vo`) |
| `PIXABAY_KEY`, `COVERR_KEY` | stock footage (`tools/stock.py`) |

## Documentary mode

Each film lives in its own folder (`films/<slug>/`) with `spec.json`, narration in `vo/`, your own images in `own/` and stock in `stock/`.

```
ELEVEN_KEY=... python3 tools/vo.py FILM          # narration
python3 tools/timing.py FILM                     # shot timing from the audio
python3 tools/plancheck.py FILM                  # score the plan before spending time on visuals
PIXABAY_KEY=... COVERR_KEY=... python3 tools/stock.py FILM
python3 tools/mix.py FILM music.mp3 --bed -31    # music bed, ducked under the voice, -14 LUFS
tools/render.sh FILM 4                           # chunked render
python3 tools/pack.py FILM                       # youtube-pack.md + captions.srt
```

Run the Remotion CLI from `video/`.

### Channel name

Set `"channel": "Your Channel"` in `spec.json` (or `--props='{"channel":"Your Channel"}'`). It appears on the title tag, the subscribe prompt, the Shorts end card and the thumbnail badge. Leave it out and nothing is shown. Put your own logo at `video/public/logo.png` (square PNG); the one included is a placeholder.

### Style presets

Set `"style"` in `spec.json` (or `--props='{"style":"noir"}'`). Leave shot `look` fields out so the style's palette rotation applies.

| key | name | best for |
|---|---|---|
| editorial | Editorial | general documentaries, society, housing, work |
| noir | Documentary Noir | true crime, scams, mysteries, investigations |
| bold | Bold Explainer | top-10 lists, fast explainers, shorts |
| tech | Tech Signal | AI, tech, internet, cyber, future of work |
| warm | Warm Stories | human stories, culture, history, travel |
| news | News Desk | current affairs, politics explainers, economy |
| finance | Money Matters | money, markets, salaries, cost of living |
| cosmic | Cinematic Future | space, science, climate, big-picture futures |

Each preset sets display and body fonts, palette rotation, accent colour, transitions, caption style, footage grade, grain, vignette and a music mood. Defined in `video/src/styles.ts`.

### Retention rules

- **Cuts:** footage shots cut about every 4.5 s (`"cutEvery"` in `spec.json`). `stock.py` and `match.py` take one clip per cut and re-use a clip with a punch-in when there are too few.
- **Overlay beats:** any shot can carry `"then": [overlay, ...]`. The overlays play in turn, on the narration's sentence starts, on an explicit `"cue": sentenceIndex`, or on a spoken word with `"on": "word"`.
- **Cold open:** no logo card at the start. Show the title as `{"type": "title"}` on an early footage shot.
- **Subscribe:** `"nudge": true` on a shot plays a corner subscribe prompt over the film.
- **Plan check:** `plancheck.py` scores hook, title, pace, re-hooks, viewer stakes, sentence length, target length (`"targetMin"`), subscribe nudge and end card.

### Packaging

- `tools/pack.py FILM` builds `youtube-pack.md` and `captions.srt` from `FILM/pack.json` (set `"channel"` there too) and checks YouTube's limits.
- `ThumbBig` (Remotion still) makes a bold thumbnail; `tools/thumbcheck.py FILM a.png b.png` previews thumbnails at feed size.

## Tale mode

Story videos from a plain-text script, one picture per paragraph. **New here? Read [GETTING_STARTED.md](GETTING_STARTED.md)** for the full step-by-step guide.

```
python setup.py                                   # once: installs, fonts, free voice, your keys, test video
python tale/tale.py parse FILM                    # script.md -> plan.json
python tale/images.py prompts FILM                # prompts.txt: one picture description per paragraph
python tale/images.py snippet FILM                # gemini-snippet.js: paste into the Gemini page, pictures arrive as zips
python tale/images.py import FILM *.zip --host local/host.jpg
python tale/kvo.py FILM --speed 0.83              # free narration (Kokoro), or:
python tale/aistudio.py snippet FILM               # Google voices in AI Studio, free, no key (paste into the page), then:
python tale/aistudio.py import FILM *-voice-*.zip  # or:
python tale/gvo.py FILM --voice Charon            # Google voices with an API key, or:
python tale/tale.py vo FILM --voice VOICE_ID      # ElevenLabs
python tale/tale.py build FILM                    # final.mp4 + chapters.txt
```

`build` renders each picture with a slow camera move and a dissolve, large captions with one highlighted word, chapter titles, your channel name, an exact voice track and a -14 LUFS mix.

### Your own settings stay local

`python setup.py` writes `.env` (keys, channel name, default voices, picture style, music). `.env`, `models/`, `films/` and `local/` are git-ignored, so each person's keys, logo, host picture and films stay in their own copy. See `.env.example` for every setting.

## Licences and credits

- Code: MIT, see `LICENSE`.
- Fonts in `video/public/fonts`: SIL Open Font License 1.1, see `video/public/fonts/LICENSE.md`.
- Remotion has its own licence: free for individuals and small teams, but some companies need a paid company licence. Check https://www.remotion.dev/license before using this commercially.
- Kokoro is Apache 2.0. Google (Gemini, AI Studio), ElevenLabs, Pexels, Pixabay and Coverr have their own terms; follow them and their attribution rules. The Gemini picture and AI Studio voice snippets automate your own signed-in Google pages; use them within Google's terms.
- Disclose AI-generated narration and images where your platform asks for it.
