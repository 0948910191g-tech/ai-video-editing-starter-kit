# AI Video Editing Starter Kit

Starter system for controlling CapCut with ChatGPT through Remote Desktop Commander.

## Status

**Pre-release — customer page and prompts are prepared; tutorial video and final end-to-end device test are still pending.**

The system has four layers:

1. **Control** — ChatGPT + Remote Desktop Commander
2. **Video environment** — CapCut + Python + FFmpeg / FFprobe
3. **OS-specific ASR** — Mac and Windows use different Whisper runtimes
4. **Editing intelligence** — reusable local skills + master prompt

## Quick start

1. Connect Remote Desktop Commander.
2. Copy `prompts/setup-installer-th.txt` into ChatGPT.
3. Wait for the installer to detect the OS and validate the environment.
4. Put the source clip on the CapCut timeline.
5. Run `prompts/master-video-editing-th.txt`.

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
- macOS Apple Silicon uses MLX; Windows uses faster-whisper/CTranslate2.
- GPU/CUDA errors on Windows must be reported before changing drivers or system CUDA components.
- Keep this repository private until the release checklist is complete.

## Repository layout

```text
prompts/
  setup-installer-th.txt
  master-video-editing-th.txt
skills/
  ai-video-speech-editing/
  tiktok-subtitle-sync/
  ai-video-visual-polish/
  capcut-zoom-copier/
  talking-head-polish/
  kim-sfx/
docs/
  release-checklist.md
```

## Release state

The customer-facing HTML has been designed and QA-checked locally. Its video slot is intentionally empty until the tutorial clip is ready. Do not publish the repository or customer page until the final Windows/Mac smoke tests pass.