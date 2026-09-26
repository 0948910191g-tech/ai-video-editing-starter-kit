# Release Checklist

Use this checklist before making the starter kit public or sending the customer page broadly.

## Customer page

- [x] Brandroomagency header and logo are in place
- [x] Customer-facing copy is cleaned up
- [x] Only one tutorial video slot is shown
- [x] Prompt 1 and Prompt 2 are copyable
- [x] Prompt details can be expanded without cluttering the page
- [x] Mac / Windows support is explained in customer-friendly language
- [x] Video slot is ready to accept one final URL
- [ ] Add final tutorial video
- [ ] Test customer page on mobile after video is inserted

## Setup prompt

- [x] Detect OS before installing ASR dependencies
- [x] Mac Apple Silicon routes to Typhoon Whisper Turbo MLX
- [x] Windows routes to faster-whisper + Large-v3 Turbo / CTranslate2
- [x] Reuse existing working dependencies before downloading again
- [x] Validate Node.js, Python, FFmpeg, FFprobe and ASR runtime
- [x] Install and validate Skill Pack
- [ ] Fresh-machine smoke test on macOS Apple Silicon
- [ ] Fresh-machine smoke test on Windows
- [ ] Verify Windows CUDA fallback behavior on the company PC

## Master editing workflow

- [x] Meaning First, Waveform Second
- [x] User Cut > AI Cut
- [x] Current Timeline = Source of Truth
- [x] Speech editing routes through `ai-video-speech-editing`
- [x] Subtitle routes through `tiktok-subtitle-sync`
- [x] Visual polish and zoom skills are present
- [x] Safe-write / backup / validation rules are present
- [ ] Final end-to-end test: raw clip → setup → edit → subtitle → QA

## Repository

- [x] Skill Pack committed
- [x] Setup prompt committed
- [x] Master editing prompt committed
- [x] Release checklist committed
- [ ] Customer HTML committed after video URL is final
- [ ] Final secret/path scan before making repository public
- [ ] Change repository visibility to Public only after all required checks pass

## Release gate

Do not call the kit release-ready until all unchecked items above that are required for the first public release are complete.