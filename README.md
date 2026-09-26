# AI Video Editing Starter Kit

Draft starter system for controlling CapCut with ChatGPT through Remote Desktop Commander.

## Status

**Draft v0.1 — macOS Apple Silicon first.**

This repository packages the workflow into four layers:

1. **Control** — ChatGPT + Remote Desktop Commander
2. **Video environment** — CapCut + Python + FFmpeg / FFprobe
3. **Thai ASR** — Typhoon Whisper Turbo MLX + mlx-whisper / MLX
4. **Editing intelligence** — reusable local skills + master prompt

## Quick start

1. Connect Remote Desktop Commander.
2. Copy `prompts/setup-installer-th.txt` into ChatGPT.
3. Wait for the installer prompt to validate the machine.
4. Put the source clip on the CapCut timeline.
5. Run the master video-editing prompt.

## Model used by the reference machine

- Model: `chayapats/typhoon-whisper-turbo-mlx`
- Based on: `typhoon-ai/typhoon-whisper-turbo`
- Local path convention: `~/.local/share/typhoon-asr/models/typhoon-whisper-turbo-mlx`
- Runtime: MLX / `mlx-whisper`
- Goal: Thai/English speech recognition with word timestamps for timeline mapping

## Included skills

- `ai-video-speech-editing` — meaning-first speech edit and safe CapCut write rules
- `tiktok-subtitle-sync` — phrase-first Thai subtitle mapping/styling
- `ai-video-visual-polish` — insert planning and punch-zoom logic
- `capcut-zoom-copier` — CapCut zoom automation helper
- `talking-head-polish` — overall talking-head workflow
- `kim-sfx` — optional SFX timing/injection

## Important

- The installer checks before installing and should not overwrite a working environment blindly.
- Direct CapCut draft edits must be backed up before writes.
- Current public draft targets **Mac with Apple Silicon** because the reference ASR stack uses MLX.
- Windows support needs a separate ASR/runtime path and is not included in Draft v0.1.

## Repository layout

```text
prompts/
  setup-installer-th.txt
skills/
  ai-video-speech-editing/
  tiktok-subtitle-sync/
  ai-video-visual-polish/
  capcut-zoom-copier/
  talking-head-polish/
  kim-sfx/
docs/
```

## Draft delivery

The Master Video Editing Prompt is currently included in the review HTML draft. It will be committed here after the first content review.
