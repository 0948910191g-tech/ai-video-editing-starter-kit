---
name: ai-video-visual-polish
description: Use when a AI Video Editing CapCut talking-head edit needs insert planning, image-vs-video placeholder labeling, B-roll marker ranges, or punch zoom emphasis after the speech cut and subtitles are stable.
---

# AI Video Editing CapCut Visual Polish

## Principle

Visual polish follows meaning. Use inserts when a visual explains faster than the talking head; use punch zoom only when the spoken line deserves emphasis. The latest user-edited timeline is the creative source of truth.

## Before editing

1. Read the latest root and Timeline `draft_info.json`.
2. Preserve picture cuts, subtitles, audio, and duration unless explicitly scoped.
3. Close CapCut and create a versioned backup before direct writes.
4. Read subtitle phrases to find semantic beats; do not choose moments from timestamps alone.

## Decide รูป vs VDO

Choose **VDO** when motion helps: screen recording, clicking/scrolling, before-after transformation, workflow in action, demo behavior, or any sequence where change over time is the point.

Choose **รูป** when one frame is enough: prompt/result screenshot, diagram, checklist, static comparison, callout, document excerpt, or CTA instruction.

If both work, prefer the simpler option that communicates the idea completely. Never label a slot `รูป,Vdo`.

## Placeholder marking

1. Use the black still currently starred/favorited in CapCut Library; verify metadata first.
2. Current known fallback: category `รายการโปรด`, name `黑`, material id `7106436374370454811`.
3. If that verified material remains in Draft metadata but its cache is missing, a pure-black PNG may be restored only at the same cache path.4. Put the black placeholder on its own video track and cover the full semantic beat.
5. Add centered marker text for the same interval using exactly `รูป` or `VDO`.
6. These are planning markers, not final B-roll.

## Punch zoom

Use the existing talking-head scale as baseline and apply a relative multiplier while preserving crop/position/rotation.

- Normal emphasis: `1.05–1.06x`
- Strong number, warning, contrast, or CTA: up to `1.08x`
- Most of the clip stays at baseline.

Good triggers: key number, warning, contrast, conclusion, decision line, CTA. Repetition, silence, or short-clip length alone are not triggers.

Prefer a fast punch over a long drift. If one semantic punch crosses a picture cut, split keyframes across the affected physical segments while keeping one perceived beat.

## Validation

Verify after writing:
- main video source/target ranges unchanged;
- subtitle text/timing unchanged;
- placeholder count equals marker count;
- marker range exactly matches placeholder range;
- labels are only `รูป` or `VDO`;
- zoom keyframe offsets stay inside their video segments;
- root Draft and Timeline Draft match;
- duration and metadata timestamps are consistent.

Reopen CapCut only after validation and confirm autosave does not overwrite the new state.