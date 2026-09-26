---
name: talking-head-polish
description: Build or refine a talking-head or short-form clip workflow that combines dead-air removal, subtitle timing aligned to spoken phrases, selective zoom emphasis, and background music. Use when Codex needs to turn raw speech footage into a tighter social clip, preserve speech rhythm, prepare a semi-automated polish pass, or handle Thai requests such as ตัดเดทแอร์, จัดซับให้ตรงคำพูด, ซูมตามจังหวะ, ใส่เพลง, หรือทำคลิปสั้นจากไฟล์พูด.
---

# Talking Head Polish

## Overview

Use this skill for the current "good enough to automate" edit stack:

1. Remove dead air.
2. Align subtitles to natural spoken phrases.
3. Add selective zoom emphasis.
4. Add a background music bed last.

This skill is best for talking-head footage, educational clips, commentary, reaction, and short-form social edits where speech timing matters more than cinematic shot design.

## Default Workflow

1. Inspect the source and target.
   - Confirm the input file, desired output, target platform, and whether the goal is a long-form cleanup or a short-form social cut.
   - If the user already has a transcript or SRT, use it. If not, generate or request one before promising precise subtitle timing.

2. Start with dead-air removal.
   - Use `cut-dead-air` as the rough-cut layer whenever possible.
   - Preserve enough padding so speech still feels natural.
   - For short-form edits, lean slightly more aggressive. For educational or explanation clips, stay balanced or natural.

3. Build subtitle timing from speech phrases, not whole sentences.
   - Prefer short phrase-based subtitle chunks that land with the speaker's cadence.
   - Break on natural pauses, clause boundaries, emphasis, and breath timing.
   - Avoid overlong lines that force reading ahead of the speaker.
   - If Thai text needs segmentation, use a deterministic method and review edge cases before finalizing.

4. Add zoom only where emphasis helps.
   - Treat zoom as punctuation, not decoration.
   - Add zoom on hooks, punchlines, strong claims, emotional peaks, or transitions into the next idea.
   - Keep zoom ranges subtle by default. For talking-head footage, a restrained push-in is usually better than dramatic scaling.

5. Add background music last.
   - Choose music after the speech timing is stable.
   - Keep dialogue intelligible and let the music support energy, not compete with the voice.
   - Lower or simplify the music bed during dense information or emotional nuance.

6. Review the final pacing.
   - Check whether the clip still feels human after dead-air removal.
   - Check whether subtitles arrive with the voice, not before it.
   - Check whether zooms feel intentional.
   - Check whether music supports the clip instead of flattening it.

## Short-Form Guidance

When the goal is a short-form clip, optimize in this order:

1. Hook clarity in the first 1-3 seconds.
2. Fast but readable subtitle rhythm.
3. Dead-air removal that tightens without sounding robotic.
4. Zooms that reinforce key beats.
5. Music that adds momentum.

If a "fully automatic short-form generator" is requested, be honest about the missing piece: the hardest part is still choosing the right clip structure and hook segment, not the polish layer. This skill handles the polish layer well.

## Practical Boundaries

- Use HyperFrames or another structured timing workflow when audio understanding is central.
- Treat direct CapCut backend draft editing as a bridge or fallback, not the default, when a cleaner structured render path is available.
- Do not promise accurate subtitle timing without transcript-quality timing data.
- Do not add music before speech timing and edit pacing are settled.

## Output Shape

For most requests, aim to produce:

- A cleaned talking-head cut.
- Subtitle timing aligned to phrase-level delivery.
- A zoom event plan or applied zoom pass.
- A music-bed pass with conservative dialogue-first levels.

If the user wants repeatability, convert the workflow into presets or a reusable pipeline rather than treating every edit as bespoke.
