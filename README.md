# AI Video Editing Starter Kit

Draft starter system for controlling CapCut with ChatGPT through Remote Desktop Commander.

## Status

**Draft v0.2 — OS-aware installer for macOS Apple Silicon and Windows.**

This repository packages the workflow into four layers:

1. **Control** — ChatGPT + Remote Desktop Commander
2. **Video environment** — CapCut + Python + FFmpeg / FFprobe
3. **OS-specific ASR** — Mac and Windows use different Whisper runtimes
4. **Editing intelligence** — reusable local skills + master prompt

## Quick start

1. Connect Remote Desktop Commander.
2. Copy `prompts/setup-installer-th.txt` into ChatGPT.
3. The installer detects OS/architecture and installs only missing dependencies.
4. Put the source clip on the CapCut timeline.
5. Run the master video-editing prompt.

## ASR routing

### macOS Apple Silicon

- Model: `chayapats/typhoon-whisper-turbo-mlx`
- Based on: `typhoon-ai/typhoon-whisper-turbo`
- Preferred local path: `~/.local/share/typhoon-asr/models/typhoon-whisper-turbo-mlx`
- Runtime: MLX / `mlx-whisper`
- Goal: Thai/English speech recognition with word timestamps for timeline mapping

### Windows

Reference stack from the Windows editing machine:

- Model: Whisper Large-v3 Turbo (`large-v3-turbo`)
- Runtime: `faster-whisper 1.2.1` / CTranslate2
- Preferred existing local model path: `D:\AI\whisper-large-v3-turbo`
- Python reference: 3.11
- GPU path: NVIDIA CUDA + float16 when validation passes
- Primary transcript: original continuous source + word timestamps
- VAD is not editorial authority; retry with VAD disabled if it causes speech to disappear

The installer must reuse an existing working model/runtime when present instead of downloading duplicates.

## Included skills

- `ai-video-speech-editing` — meaning-first speech edit, OS-specific ASR routing, safe CapCut write rules
- `tiktok-subtitle-sync` — phrase-first Thai subtitle mapping/styling
- `ai-video-visual-polish` — insert planning and punch-zoom logic
- `capcut-zoom-copier` — CapCut zoom automation helper
- `talking-head-polish` — overall talking-head workflow
- `kim-sfx` — optional SFX timing/injection

## Important

- The installer checks before installing and should not overwrite a working environment blindly.
- Direct CapCut draft edits must be backed up before writes.
- macOS Apple Silicon uses MLX; Windows uses faster-whisper/CTranslate2. Do not install the wrong ASR runtime for the OS.
- GPU/CUDA errors on Windows must be reported before changing drivers or system CUDA components.

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

The Master Video Editing Prompt is distributed with the current review HTML draft. It should always detect the current machine and read the installed skill pack for that OS before editing.