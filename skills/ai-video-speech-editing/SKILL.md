---
name: ai-video-speech-editing
description: Use when editing talking-head clips in CapCut, especially dead-air cleanup, removing unwanted speech, re-syncing Thai subtitles after cuts, or learning the user's preferred cut rhythm from an existing timeline.
---

# AI Video Speech Editing

## Core rule
**Meaning first, waveform second.** The user's latest manual CapCut timeline is the creative source of truth. Silence detection and ASR support the edit; they do not decide it.

## Hard rules
- Inspect the latest video/source/target ranges before editing; never assume the previous AI state is current.
- **User cut > AI cut.** Never restore, re-cut, or overwrite user edits unless explicitly asked.
- Repetition alone is not a deletion rule. Keep repetition if it adds setup, reasoning, instruction, transition, Human Check, proof, CTA, or deliberate emphasis.
- If semantic value is uncertain, keep the phrase and flag it.
- Use waveform/silence only to choose trim boundaries after deciding what should stay.
- Close CapCut and make a versioned backup before direct draft writes.

## Required companion
**REQUIRED SUB-SKILL:** `tiktok-subtitle-sync` for native CapCut subtitle styling/injection. Generic dead-air/silence tools are analysis helpers only for the current footage.

## ASR routing — detect OS first
Before transcription, detect the current machine. Do not assume the model from history.

### macOS Apple Silicon
Use Typhoon Whisper Turbo MLX:
- model: `chayapats/typhoon-whisper-turbo-mlx`
- preferred local path: `~/.local/share/typhoon-asr/models/typhoon-whisper-turbo-mlx`
- runtime: MLX / `mlx-whisper`
- transcribe with word timestamps

### Windows
Use the Windows reference stack used by the editing machine:
- model: Whisper Large-v3 Turbo (`large-v3-turbo`)
- runtime: `faster-whisper 1.2.1` / CTranslate2
- preferred existing local model path when present: `D:\AI\whisper-large-v3-turbo`
- Python reference: 3.11
- use word timestamps
- if NVIDIA CUDA validation passes, prefer CUDA + float16
- if CUDA/cuBLAS fails, do not modify drivers blindly; report the real failure and use a safe fallback only when necessary
- VAD is not editorial authority. If VAD causes speech to disappear, retry transcription with VAD disabled before concluding the audio has no speech.

## Workflow
1. Compare the current timeline with the latest trustworthy backup. Classify differences as `user removed` vs `user restored`; use those as style evidence, not fixed thresholds.
2. Transcribe the **original continuous source media** with word timestamps using the OS-specific ASR route above. Use project/domain vocabulary where supported.
3. Map source timestamps through only the source ranges currently kept in CapCut. For multiple source files, transcribe/map each separately. Do not make post-jump-cut ASR the primary transcript; it can bridge cuts and hallucinate removed context.
4. Remove only clear false starts, superseded retakes, count-ins/off-takes, meaningless fillers, and dead air that serves no pacing/visual purpose. Preserve information-bearing passages.
5. After picture changes, rebuild/remap subtitles to the current video ranges; never change video cuts merely to preserve old caption timing.

## Subtitle reference
Clone the latest approved project text material whenever possible. **Default visual reference:** `คณิต-SB` / Kanit SemiBold, size `9`, Y `-0.35`, black stroke `0.03372548893094063`, white with selective yellow keywords. These values override generic size 10/11 examples in companion skills.

**Caption chunking override:** use **phrase-first subtitles**, not a rigid 1–2-word/12-character rule. Keep one meaningful phrase together even when it is longer; never split a Thai word or break a phrase so the meaning feels incomplete.

**Spoken-to-written cleanup after timing is locked:** preserve meaning and timing, but remove visually wasteful spoken particles/fillers such as `นะครับ`, `ครับ`, `ครับผม`, redundant `แล้วก็`, `ก็คือ`, `หรือว่า`, and similar filler when the sentence still reads naturally. Rewrite connectives concisely (`แล้วก็` → `และ` or omit) instead of deleting meaning. Compress immediate repeated spoken words with `ๆ` (`ไม่ ไม่` / `ไม่ไม่` → `ไม่ๆ`) rather than displaying the duplicate twice. Never remove negation, numbers, constraints, CTA keywords, tool/product names, warnings, or meaning-bearing transitions.

**User refinement learned 2026-09-07:** picture tightening can happen by trimming the **edges of already-kept segments** without increasing the number of video segments. Re-read the latest `source_timerange` / `target_timerange` before subtitle work. If a new trim crosses an existing caption, split/remap the caption at the new picture boundary; adjacent identical caption pieces may be a structural ripple-edit artifact, not intentional repeated copy. Keep the user's newest concise wording when it preserves intent.

## Safe-write QA
Detect the actual CapCut schema. Modern drafts may require synchronized project `draft_info.json`, main-timeline `draft_info.json`, `draft_meta_info.json`, and parent `root_meta_info.json`. Verify duration, material IDs, duplicate IDs, subtitle end time, and font resource existence before reopening CapCut.

Use the latest user-approved timeline as style evidence; do not depend on project-specific absolute paths.