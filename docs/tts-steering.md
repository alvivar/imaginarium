# TTS steering guide

How to write the `text` argument for `tts.py` to control _how_ a voice performs,
not just what it says. Everything here is driven by the text you pass — no extra
flags. The underlying model is `inworld/realtime-tts-2` (`inworld-tts-2`), which
fully supports steering.

```bash
python tts.py "[say excitedly with a high pitch and fast pace] We shipped it!"
```

## How steering works

Wrap a natural-language instruction in square brackets and place it **before**
the text it applies to. Think of it as directing a voice actor before a take.

- **Instructions must be written in English**, even when the spoken text is in
  another language.
- Inside an instruction, **avoid capital letters and punctuation** — they can
  leak into the delivery. Save capitalization for the spoken text (see
  [Emphasis](#emphasis)).
- Put the delivery instruction **once, at the start**. Non-verbal sounds like
  `[laugh]` are the exception and may be placed inline.

```
[say quietly in a low tone with deliberate pauses] Bonjour, je suis ravi de vous rencontrer.
```

## Tag reference

Single-property tags that target one aspect of delivery. These are starting
points — any natural-language phrasing works.

| Aspect           | What it controls                                    | Examples                                                                 |
| ---------------- | --------------------------------------------------- | ------------------------------------------------------------------------ |
| **Articulation** | Force, crispness, deliberate rhythm                 | `[say with force]` `[articulate clearly]` `[say with deliberate pauses]` |
| **Intonation**   | Whether pitch lands decisively or stays open        | `[say with a falling pitch]` `[say with a rising pitch]`                 |
| **Volume**       | Amplitude, from barely audible to room-filling      | `[very quiet]` `[very loud]`                                             |
| **Pitch**        | Baseline register — low for weight, high for energy | `[say in a low tone]` `[say in a high pitch]`                            |
| **Range**        | How much pitch varies — flat vs. expressive         | `[say playfully]` `[say with no pitch variation]`                        |
| **Speed**        | Pace — fast for urgency, slow for weight            | `[very fast]` `[very slow]`                                              |
| **Vocal style**  | Switches speaking mode                              | `[whisper in a hushed style]` `[sing joyfully]` `[give a nasal quality]` |
| **Emotion**      | Mood of the delivery                                | `[say excitedly]` `[sound sad]` `[sound concerned]` `[sound terrified]`  |

## Free-form direction

For maximum control, describe the full character of a delivery in one tag —
layering emotion, energy, pacing, and manner. The more fully you describe it,
the more precisely the voice performs. A bare `[sad]` gives the model one
dimension; a fuller instruction gives it several.

```
[speak as if barely holding back rage forcing every word through gritted teeth] I have told you. Repeatedly. And you STILL didn't listen.

[overwhelmed with excitement and barely able to contain yourself] We just hit a million users. I still can't believe it — we actually did it!

[slow and hushed with every word weighted by grief] I got the call this morning. He's gone.

[say sadly with deliberate pauses in a low voice and hushed style] I don't think I can do this anymore.
```

## Non-verbals

Insert organic human sounds anywhere in the text — these are the one kind of tag
that belongs **inline**, where the sound should occur.

**Supported:** `[laugh]` `[breathe]` `[clear throat]` `[sigh]` `[cough]` `[yawn]`

```
[clear throat] If I could have everyone's attention, please.
I told him what happened, and he just [laugh] couldn't believe it!
```

## Emphasis

Capitalize letters in the **spoken text** (not inside instructions) to stress
words or syllables. A fully-capitalized word stresses the whole word;
capitalizing part of a word stresses that syllable. Use sparingly.

```
I told you NOT to open that door.
Are you seriously asking if I want pizza? AbsoLUTEly I do.
```

## Pauses

Add measured pauses with an SSML break tag inside the text:

```
Let me think about that. <break time="1s" /> Okay, here's my answer.
```

## Best practices

- **English instructions only**, regardless of the spoken language.
- **No caps or punctuation inside instructions** — keep them lowercase.
- **Don't put opposing directions in one tag**
  (`[whisper in a hushed style]` + `[very loud]`) — results are unpredictable.
  Combining _complementary_ qualities in one instruction is encouraged, though
  — see [Free-form direction](#free-form-direction).
- **Match the tag to the content.** `[say sadly]` on celebratory text sends
  contradictory signals and degrades quality.
- **One delivery instruction per input**, at the start. Placing multiple delivery
  tags mid-text produces inconsistent results. (Non-verbals are the exception.)
- **Prefer full descriptions over bare tags** for nuanced, convincing output.

_Avoid:_ `[say in a low tone] I can't believe this happened. [say in a high pitch] Things are looking up though!`

## Languages

`tts.py --language` accepts `auto` (detect from the text) or one of these codes:

```
en  zh  ja  ko  ru  it  es  pt  fr  de  pl  nl  hi  he  ar
```

> **Note — Replicate limitation.** `inworld-tts-2` natively supports 200+
> BCP-47 languages and locales (e.g. `es-MX`, `en-GB`, `pt-BR`), but the
> Replicate endpoint this tool calls hard-restricts `language` to the 16 codes
> above. Passing anything else is rejected server-side with a `422`. Regional
> locales require Inworld's own API, not this Replicate wrapper.

Setting `--language` does two things: applies text normalization for that
language (speaking numbers/dates in it, where supported) and uses the voice's
localized prompt if one exists. When omitted (`auto`), the original voice prompt
is used and the language is detected from the text — but short numeric inputs
(e.g. a phone number) may not give auto-detect enough context, so specify a
language for those.

**Cross-lingual:** by default the model attempts to speak the target language
natively, without carrying over the voice's original accent. To keep the
original accent, ask for it via steering. For accent-free native delivery,
localize the voice in the Inworld portal.

## Recipes

```bash
# Joyful announcement
python tts.py "[say excitedly with a high pitch and fast pace] Your package has arrived!"

# Grave, grief-stricken
python tts.py "[slow and hushed with every word weighted by grief] I got the call this morning."

# Intimate whisper
python tts.py "[whisper in a hushed style] Don't make a sound. There's someone right outside." --voice Ashley

# Technical narration (measured, clear)
python tts.py "[very slow with deliberate pauses and clear articulation] Step one. Run the installer as root."

# Playful, conversational
python tts.py "So anyway, I was telling her about the trip, and she just [laugh] lost it."

# Non-English, English steering, native delivery
python tts.py "[say warmly in a gentle tone] Bonjour, je suis ravi de vous rencontrer." --language fr

# es-MX and other locales are NOT supported by the Replicate endpoint; use es
python tts.py "[say warmly] Hola, mucho gusto en conocerte." --language es
```
