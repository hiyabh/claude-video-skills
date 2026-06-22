# ערכת סקילי וידאו ל-Claude Code — *בין קודש לקלוד*

אוסף של **27 סקילים** (skills) ל-[Claude Code](https://claude.com/claude-code) ליצירה ועריכה של וידאו:
מסרטוני הסבר עם מוושן-גרפיקס, דרך קליפים מצוירים לילדים, סרטוני ברכות משוזרים, דברי תורה מונפשים,
סיכומי אירוע, ועד חיתוך אוטומטי עם מעקב פנים.

> כל סקיל הוא תיקייה עם `SKILL.md` (ההוראות ל-Claude) + סקריפטים/תבניות. מעתיקים את התיקיות אל
> `~/.claude/skills/` ו-Claude Code מזהה אותן אוטומטית.

---

## התקנה מהירה (מומלץ)

פותחים את Claude Code ומדביקים את הבלוק הבא. Claude יוריד את החבילה ויתקין את כל הסקילים:

```
הי קלוד! התקן לי בבקשה את ערכת סקילי הווידאו "בין קודש לקלוד".
1. זהה את מערכת ההפעלה שלי ואת הנתיב ~/.claude/skills/ (ב-Windows: C:\Users\<user>\.claude\skills\). צור את התיקייה אם אינה קיימת.
2. הורד את החבילה: https://hiyabh.github.io/claude-video-skills/claude-video-skills.tar.gz
3. חלץ ממנה את כל תיקיות הסקילים אל ~/.claude/skills/ — אל תדרוס סקיל קיים בלי לשאול אותי.
4. אמת שכל 27 הסקילים הותקנו והצג לי רשימה מקובצת (יצירה / אנימציה / הורדה).
5. בדוק אילו תלויות מערכת מותקנות אצלי (Node 22+, FFmpeg, Python 3.9+) ותגיד לי בדיוק מה חסר ואיך להתקין — אל תתקין תלויות כבדות לבד.
```

זהו. אחרי שזה רץ, אפשר פשוט לבקש מ-Claude דברים כמו *"תעשה לי סרטון הסבר מטורף על X"* או
*"תכין קליפ שיר מצויר לילד"* — הוא יבחר את הסקיל המתאים.

---

## התקנה ידנית

```bash
# הורדה + חילוץ אל תיקיית הסקילים
curl -L -o cvs.tar.gz https://hiyabh.github.io/claude-video-skills/claude-video-skills.tar.gz
mkdir -p ~/.claude/skills
tar -xzf cvs.tar.gz --strip-components=1 -C ~/.claude/skills
```

או, למשתמשי Mac/Linux/Git-Bash, סקריפט עזר:

```bash
curl -L https://hiyabh.github.io/claude-video-skills/install.sh | bash
```

---

## תלויות (Prerequisites)

רוב הסקילים עובדים מקומית. לפי הצורך:

| נדרש | בשביל מה |
|---|---|
| **Node.js 22+** | מנוע HyperFrames (`npx hyperframes`) — לב מערכת הווידאו |
| **FFmpeg** | כמעט כל עריכה/רינדור של וידאו ואודיו |
| **Python 3.9+** | סקריפטים של Manim, event-recap, blessing, face-track, kids-song |
| **GOOGLE_API_KEY** (env var) | רק לסקילים שמייצרים תמונות/וידאו ב-AI: `kids-song-video`, `dvar-torah-animation` (מפתח חינמי ב-Google AI Studio) |

מודלים מקומיים (TTS/Whisper/הסרת רקע) יורדים אוטומטית בהרצה הראשונה ונשמרים ב-`~/.cache/`.

---

## הסקילים שבחבילה (27)

### יצירה ועריכה
- **epic-video-studio** — מנצח על HyperFrames + Manim + Lottie לסרטון "וואו" מורכב
- **hyperframes** (+`-cli` / `-media` / `-registry`) — מנוע הקומפוזיציה: טקסט קינטי, כתוביות, קריינות, מעברים, רינדור
- **event-recap-video** — סרטון סיכום אירוע מתמונות+קליפים גולמיים (ffmpeg)
- **kids-song-video** — קליפ שיר מצויר ומושר לילד (Suno + תמונות AI + אנימציה)
- **blessing-video-weaver** — שזירת קליפי ברכה מכל המשפחה לסרטון אחד
- **dvar-torah-animation** — דבר תורה מונפש 9:16 עם כתוביות מנוקדות ו-B-roll מאויר
- **face-track-reframe** — חיתוך וידאו ליחס אחר עם מעקב פנים (הפנים לא נחתכות)
- **website-to-hyperframes** — הפיכת אתר לסרטון מוצר

### מנועי אנימציה ועזר
- **manim-skill** / **manim-composer** / **manimce-best-practices** — אנימציות מתמטיות/הסבר בסגנון 3Blue1Brown
- **text-to-lottie** / **lottie** — מיקרו-אנימציות וקטוריות
- **remotion-best-practices** / **remotion-to-hyperframes** — וידאו ב-React + תרגום ל-HyperFrames
- **gsap** / **animejs** / **css-animations** / **waapi** / **three** / **framer-motion** / **threejs-scroll-cinema** — מנועי אנימציה ל-HyperFrames

### הורדת חומרי גלם (בונוס)
- **universal-downloader** — הורדת וידאו/אודיו/גלריות מ-1000+ אתרים (yt-dlp/gallery-dl)
- **browser-album-downloader** — הורדת אלבומים פרטיים מאחורי התחברות (Playwright)

> הערה: סקיל `video-production` (הפקת וידאו ב-AI דרך OpenMontage) אינו כלול — הוא דורש פרויקט נפרד
> ומפתח Google API, והקמה נפרדת.

---

## רישוי
הסקילים משותפים כפי-שהם (as-is) לשימוש חופשי בקהילת "בין קודש לקלוד". מנועים חיצוניים (HyperFrames,
Manim, Remotion, GSAP וכו') כפופים לרישיונות שלהם.
