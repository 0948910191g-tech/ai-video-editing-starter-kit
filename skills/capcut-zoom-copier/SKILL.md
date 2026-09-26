---
name: capcut-zoom-copier
description: Automatically applies slow zooms and static punch-cuts to a CapCut Desktop project timeline based on subtitle text triggers and segment durations to replicate professional narrative visual pacing.
---

# CapCut Dynamic Zoom Pacer

This skill automates the application of visual pacing to CapCut Desktop drafts by injecting zoom keyframes (Slow Zoom In) and static crop changes (Static Zoom) into `draft_info.json`. It maps timeline segments to subtitle text and triggers specific zoom styles based on pacing rules.

## Zoom Pacing Rules

1. **Slow Zoom In (Smooth Narrative Focus)**
   - Applied to segments with a duration $\ge$ 4.5 seconds or the Intro/Hook segment.
   - Scale transitions smoothly from `1.00x` to `1.08x` using keyframes.

2. **Static Zoom (Pacing Punch-In)**
   - Applied to segments containing emotion or narrative trigger words (e.g., "เฮ้ย", "โอ้โห", "แต่แม่ง", "เจ็บ", "รู้ไหม", "ใช่ป้ะ", "ส่วนใหญ่") OR very short clips ($< 1.0$s) to maintain rapid pacing.
   - Scale is set statically to a punchier level (typically `1.07x` or `1.08x`) across the entire segment, creating a jump-cut effect.

3. **Standard (1.0x Scale)**
   - Serves as the default baseline to reset viewer focus.

## Setup & Files

The automated helper script is stored at:
[apply_smart_zooms.py](file://~/.local/share/ai-video-editing-starter-kit/skills/capcut-zoom-copier/scripts/apply_smart_zooms.py)

### Usage

Run the helper script pointing to the project directory:
```bash
python3 "~/.local/share/ai-video-editing-starter-kit/skills/capcut-zoom-copier/scripts/apply_smart_zooms.py" "~/Movies/CapCut/User Data/Projects/com.lveditor.draft/YOUR_PROJECT_NAME"
```
