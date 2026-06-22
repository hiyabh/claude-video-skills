# Suno — guided-manual song generation (Hebrew children's song)

This is the reference for **Step 2** of `kids-song-video`. Claude prepares everything here;
the user pastes it into Suno, generates, and returns the MP3.

## Why niqqud is mandatory
Suno pronounces Hebrew from the letters alone — without vowel marks it guesses wrong (wrong
vowels, wrong stress, sometimes a different word entirely). **Always hand Suno fully vocalized
(מנוקד) lyrics.** This is the single biggest quality lever for a Hebrew song, and the exact tip
the source guide highlights (echoing Israel's Ministry of Education guidance on Suno).

### Before / after
- ❌ Without niqqud: `פרה ופרד אכלו בשמחה`
- ✅ With niqqud: `פָּרָה וָפֶרֶד אָכְלוּ בְּשִׂמְחָה`

Give Suno the ✅ version.

## What to paste into Suno

Suno has two relevant fields in **Custom mode**:

### 1) Lyrics box — vocalized lyrics + structure tags
Use bracketed structure tags so Suno arranges the song; put the **niqqud** lyrics under each.

```
[Verse]
<שורה 1 מנוקדת>
<שורה 2 מנוקדת>

[Chorus]
<פזמון מנוקד — קצר וחוזר>

[Verse]
<בית 2 מנוקד>

[Chorus]
<פזמון מנוקד>

[Outro]
<סיום עדין מנוקד>
```

Supported tags include: `[Intro]`, `[Verse]`, `[Pre-Chorus]`, `[Chorus]`, `[Bridge]`,
`[Outro]`. You can also drop performance hints like `(soft)` / `(slowing down)`.

### 2) Style box — genre / mood prompt
Keep it short, descriptive, in English (Suno's style parser is strongest in English). Template:

```
gentle Hebrew children's <lullaby|sing-along>, <instrument(s)>, <vocal type> vocals,
warm and playful, <slow|medium> tempo, simple catchy melody, clean mix
```

Examples:
- Bedtime: `gentle Hebrew children's lullaby, soft acoustic guitar and piano, warm female vocals, slow tempo, dreamy, simple melody`
- Upbeat: `happy Hebrew children's sing-along, ukulele and light percussion, cheerful kids choir vocals, medium tempo, bouncy and catchy`

## Generation tips
- Generate **2 takes** (Suno returns variants) and pick the better vocal clarity / pronunciation.
- If a word is mispronounced, tweak its niqqud (or spell it phonetically) and regenerate.
- Keep total length ~1–2 minutes for young children's attention spans.
- **Free tier** is enough; note the **daily generation limit** — don't burn credits on tiny tweaks.

## Deliverable back to Claude
Download the chosen take as MP3 and save it to the project as:

```
<project>/assets/song.mp3
```

Tell Claude when it's ready — the song's real duration and rhythm drive captions, animation, and
the final timeline.

## ⚠️ Suno often adds a junk intro — trim it

Suno frequently prepends a few seconds of non-lyric vocalization (gibberish like
"מילים מילים מילים", a count-in, or a stray "la la") before the real first line. It is NOT
part of the song. Detect it via the whisper transcript (the first real lyric word starts
several seconds in) and trim it:

```bash
# keep the original, cut from just before the first real word (e.g. 6.80s):
cp assets/song.mp3 assets/song_full.mp3
ffmpeg -ss 6.80 -i assets/song_full.mp3 -af "afade=t=in:st=0:d=0.06" -c:a libmp3lame -q:a 2 assets/song.mp3 -y
```

After trimming, **shift every caption start/end by the same offset** (e.g. −6.80s) and set the
composition/song/background durations to the new (shorter) length. If the song now starts on
vocals immediately, anchor the title card to the TOP so it doesn't cover the first caption.

## Links
- Suno: <https://suno.com> · How to make a song: <https://suno.com/hub/how-to-make-a-song>
- Source guide: <https://yuvkesh.onrender.com/blog/kids-song-video-ai-he>
