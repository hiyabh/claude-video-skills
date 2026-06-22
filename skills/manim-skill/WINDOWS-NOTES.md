# Windows usage notes (added on install)

The upstream `SKILL.md` was written for macOS/Linux. On this Windows machine the
behavior is identical except for these two substitutions:

1. **Use `python`, not `python3`.** Windows has no `python3` alias. So the viewer
   command becomes:
   ```powershell
   python "<this-folder>\tools\video_viewer.py" final.mp4 --order concat.txt
   ```

2. **The `manim` command is installed via uv (isolated env on Python 3.13).**
   It is on PATH as a uv tool. Verify with `manim --version`.
   - System Python here is 3.14, which lacks some Manim wheels — that's why Manim
     runs in its own uv-managed 3.13 environment. Do NOT `pip install manim` into
     system Python.

3. **ffmpeg / ffprobe** are already installed globally (gyan.dev full build) and on
   PATH — scene stitching (`ffmpeg -f concat ...`) and the viewer's thumbnailing work
   as written.

4. **LaTeX (`MathTex` / `Tex`)** is provided by MiKTeX. On first use MiKTeX may
   auto-install missing TeX packages. If a `MathTex` render fails with a LaTeX error,
   ensure MiKTeX finished installing and that on-the-fly package install is enabled.
   `Text(...)`-based animations work without LaTeX.

Everything else in `SKILL.md` applies unchanged.
