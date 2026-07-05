# Gemini TTS steering guide

How to direct `gemini_tts.py` for expressive speech. The model is
`google/gemini-3.1-flash-tts` — you set the overall delivery with a **style
prompt** (`--style`) and shape specific moments with **inline tags** written in
the `text`.

```bash
python gemini_tts.py "[laughing] I did NOT expect that!" \
  --voice Callirrhoe --style "a casual chat with a friend, friendly and amused"
```

## How steering works

Gemini gives you two complementary controls:

- **`--style`** sets the *overall* feel — who is speaking, the scene, and the
  delivery direction. Maps to the model's `prompt` field.
- **Inline `[tags]`** in the `text` give *targeted* control over specific
  moments — a laugh, a whisper, a pause.

Rule of thumb: **prompts for tone, tags for precision.**

## Style prompting

The `--style` prompt sets the context and delivery direction. The more specific
you are, the better the result. A strong prompt can describe:

- **Who is speaking** — a radio DJ, a documentary narrator, a children's book
  reader. Giving the speaker a name and identity grounds the performance.
- **The scene** — where they are and what's happening. Environmental context
  subtly shapes delivery.
- **Director's notes** — style, accent, and pacing. "Infectious enthusiasm, the
  listener should feel part of a community event" beats "energetic."

### Example

`--style`:

```
AUDIO PROFILE: Jaz R., "The Morning Hype"

THE SCENE: A glass-walled studio overlooking the London skyline.
The red ON AIR tally light is blazing. Jaz is bouncing on the balls
of their heels to the rhythm of a thumping backing track.

DIRECTOR'S NOTES:
- Style: You must hear the grin in the audio. Bright, sunny, inviting.
- Accent: Jaz is from Brixton, London.
- Pace: Energetic bouncing cadence, high-speed delivery, no dead air.
```

`text`:

```
[excitedly] Yes, massive vibes in the studio! You are locked in and
it is absolutely popping off in London right now. [shouting] Turn
this up! We've got the project roadmap landing in three, two... let's go!
```

## Inline tags

Bracketed modifiers placed directly in the `text`.

```
[laughing] That's hilarious! [whispering] But don't tell anyone.
```

### Non-speech sounds

These insert an audible vocalization without speaking the tag.

| Tag          | What it does              |
| ------------ | ------------------------- |
| `[sigh]`     | Inserts a sigh            |
| `[laughing]` | Inserts a laugh           |
| `[uhm]`      | Inserts a hesitation sound |

### Style modifiers

These change the delivery of the text that follows.

| Tag               | What it does               |
| ----------------- | -------------------------- |
| `[whispering]`    | Quiet, whispered delivery  |
| `[shouting]`      | Loud, projected delivery   |
| `[sarcasm]`       | Sarcastic tone             |
| `[robotic]`       | Robotic-sounding delivery  |
| `[extremely fast]`| Speeds up the speech       |

### Pauses

These insert silence for rhythm and pacing.

| Tag              | Duration                     |
| ---------------- | ---------------------------- |
| `[short pause]`  | ~250 ms (like a comma)       |
| `[medium pause]` | ~500 ms (like a sentence break) |
| `[long pause]`   | ~1000 ms+ (dramatic effect)  |

### Custom tags

You can also experiment with descriptive tags — `[excitedly]`, `[bored]`,
`[reluctantly]`, `[singing]`, `[asmr]`, even `[like dracula]` — and the model
will try to interpret them. **Test unlisted tags before relying on them**: some
may be spoken aloud instead of applied as a modifier. For broad character or
emotion, prefer `--style`.

## Voices

30 prebuilt voices (`--voice`, default `Kore`), each with a distinct character:

| Voice           | Gender | Character     |
| --------------- | ------ | ------------- |
| `Achernar`      | Female | Soft          |
| `Achird`        | Male   | Friendly      |
| `Algenib`       | Male   | Gravelly      |
| `Algieba`       | Male   | Smooth        |
| `Alnilam`       | Male   | Firm          |
| `Aoede`         | Female | Breezy        |
| `Autonoe`       | Female | Bright        |
| `Callirrhoe`    | Female | Easy-going    |
| `Charon`        | Male   | Informative   |
| `Despina`       | Female | Smooth        |
| `Enceladus`     | Male   | Breathy       |
| `Erinome`       | Female | Clear         |
| `Fenrir`        | Male   | Excitable     |
| `Gacrux`        | Female | Mature        |
| `Iapetus`       | Male   | Clear         |
| `Kore`          | Female | Firm          |
| `Laomedeia`     | Female | Upbeat        |
| `Leda`          | Female | Youthful      |
| `Orus`          | Male   | Firm          |
| `Pulcherrima`   | Female | Forward       |
| `Puck`          | Male   | Upbeat        |
| `Rasalgethi`    | Male   | Informative   |
| `Sadachbia`     | Male   | Lively        |
| `Sadaltager`    | Male   | Knowledgeable |
| `Schedar`       | Male   | Even          |
| `Sulafat`       | Female | Warm          |
| `Umbriel`       | Male   | Easy-going    |
| `Vindemiatrix`  | Female | Gentle        |
| `Zephyr`        | Female | Bright        |
| `Zubenelgenubi` | Male   | Casual        |

## Languages

Gemini can auto-detect the input language, but through this Replicate endpoint
`language_code` always carries a value — `gemini_tts.py` defaults it to `en-US`
— so set `--language` explicitly for non-English text. Supported languages
include English, French, German, Spanish, Portuguese, Italian, Dutch, Japanese,
Korean, Hindi, Arabic, Russian, Polish, Romanian, Turkish, Thai, Vietnamese,
Indonesian, and 50+ more in preview.

`gemini_tts.py --language` validates against the 87 BCP-47 codes the Replicate
endpoint accepts (default `en-US`); the full list is in the README. See
[Google's language reference](https://cloud.google.com/text-to-speech/docs/gemini-tts#available_languages)
for details.

## Tips

- **Align everything.** The style prompt, the text, and the tags should all
  point the same way. A scared-sounding prompt works best with text that
  actually sounds alarming.
- **Don't overspecify.** The model fills gaps naturally; leaving some room often
  sounds more natural than controlling every detail.
- **Use rich text.** "I just heard a window break" produces a more genuinely
  scared result than "Something happened."
- **Tags for precision, prompts for tone.** Tags for a specific moment (a laugh,
  a pause, a whisper); the prompt for the overall feel.
- **Punctuation matters.** Commas, periods, and semicolons create natural
  pauses — use them to help the model breathe.

## Limits

- `text` — max 4,000 bytes (enforced by `gemini_tts.py`).
- `--style` — max 4,000 bytes.
- `text` + `--style` combined — max 8,000 bytes.
- Output audio — capped at roughly 655 seconds.

The last three are enforced by the endpoint, not the CLI: exceeding them returns
a server-side error.

## Recipes

```bash
# Amused, conversational
python gemini_tts.py "[laughing] I did NOT expect that. [sigh] Can you believe it!" \
  --voice Callirrhoe --style "a casual chat with a friend, friendly and amused"

# Character voice via a custom tag (experimental — test unlisted tags; --style is safer)
python gemini_tts.py "[like dracula] Good evening. I have been expecting you." --voice Algenib

# High-energy radio DJ (style prompt does the heavy lifting)
python gemini_tts.py "[excitedly] Massive vibes in the studio! [shouting] Turn this up!" \
  --voice Fenrir --style "a Brixton radio DJ, bright and grinning, high-speed delivery, no dead air"

# Dramatic pacing with pauses
python gemini_tts.py "I have news. [long pause] We won." --voice Charon

# Non-English, explicit language
python gemini_tts.py "Bonjour, ravi de vous rencontrer." --voice Sulafat --language fr-FR
```
