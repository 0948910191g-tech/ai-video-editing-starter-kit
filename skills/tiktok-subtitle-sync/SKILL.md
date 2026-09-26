---
name: tiktok-subtitle-sync
description: Use when injecting, styling, splitting, or aligning Thai subtitles directly in CapCut Desktop local drafts to achieve snappy, synchronized TikTok-style captions.
---

# Direct CapCut Subtitle Sync & Style Injector (Three-File Synchronization Standard)

## Overview
This skill defines the standard pipeline for parsing, splitting (snappy tokenization), styling, aligning, and injecting Thai subtitles **directly into CapCut Desktop local draft project files (`draft_content.json`)**. This bypasses external video compositing, giving the user 100% native control over subtitle positions, sizes, and text animations inside CapCut Desktop while maintaining a premium TikTok aesthetic.

It enforces the **Three-File Timestamp Synchronization Standard** to completely prevent CapCut's RAM cache or Cloud Sync from overwriting local disk edits upon project launch.

---

## When to Use
* Use when the user wants to adjust, resize, or animate subtitles directly inside CapCut Desktop rather than using baked-in subtitle videos.
* Use when subtitle segments in CapCut are long or badly chunked and need to be split into fast, readable **meaningful phrases** aligned with speech and picture-cut timings.
* Use when subtitle timeline segments are misaligned or lagged (e.g., due to video speed edits) and need to be synced with a Whisper audio transcription.
* Use when you need to automatically highlight specific key terms in neon yellow while keeping other words in the same segment white inside CapCut's native rich-text styles.

---

## Core Aesthetic & Timing Requirements
1. **Phrase-First, Cut-Aware Timings**: One caption should normally express one readable semantic phrase. **1–2 words / ~12 characters is only a soft aesthetic hint, never a hard cap.** Keep a longer phrase together when splitting it would leave a hanging or damaged meaning. Never fracture a Thai word or compound term. If a new picture cut lands inside a phrase, split/re-time the caption at that cut boundary rather than letting stale text bridge removed audio.
2. **Proper Word Tokenization**: Never fracture syllables or compound Thai words (e.g. do NOT split "แอร์โรบิก" into `['แอร์', 'โร', 'บิ', 'ก']` or "มานิต้า" into `['มา', 'นิ', 'ต้า']`). Keep them whole by injecting a custom `Trie` into PyThaiNLP's tokenizer.
3. **Thick Outlines**: Add a heavy black outline (`border_width: 0.03372548893094063`, corresponding to slider value **17** in CapCut's UI, `#000000`, `alpha: 1.0`) to make the text pop against any video background.
4. **Targeted Keyword Highlights**: Highlight *only* specific key terms/contrast elements (e.g. comparing brands, numbers, or actions like `"ไม่เหมือนกัน"`, `"บางๆ"`, `"จีน"`, `"ไทย"`, `"Hoya"`, `"80"`, `"40"`) in bright neon yellow (`[0.95686274766922, 0.7803921699523926, 0.05882352963089943]`). Avoid highlighting full sentences. If a segment contains no keywords, it must be kept **100% white** (`[1.0, 1.0, 1.0]`) to maintain high visual contrast.
5. **Positioning**: Align all text track clips to a chest-level vertical translation (`Y: -0.35` in CapCut's normalized viewport scale).
6. **Word-Timestamp Alignment First**: When cuts or speed edits change the timeline, map source transcription timestamps through the current video `source_timerange` → `target_timerange`. Use actual word/phrase timestamps whenever available. Character-length proportional timing is only a fallback when word timing is unavailable. The latest user-approved manual split/timing is the style source of truth.


### Subtitle Copy & Manual-Refinement Rules
- **Sync first, rewrite second.** Lock phrase timing from audible speech before cleaning the copy.
- After timing is trustworthy, subtitles may be tightened from spoken language toward concise written language without changing the message. Remove redundant polite particles/fillers (`นะครับ`, `ครับ`, `ครับผม`, redundant `แล้วก็`, `ก็คือ`, `หรือว่า`) when the sentence remains natural.
- Compress immediate repeated spoken words with `ๆ` when repetition is part of the delivery (`ไม่ ไม่` / `ไม่ไม่` → `ไม่ๆ`) instead of printing the word twice. Never remove negation or other meaning-bearing repetition.
- Prefer concise on-screen wording when the user demonstrates it (for example `ใส่ Prompt ได้เลย` → `ใส่ Prompt`) while preserving the spoken intent.
- **Picture-cut boundary beats stale caption geometry.** If the editor trims or ripple-deletes footage after subtitles exist, remap/split captions to the new current timeline. Adjacent identical caption pieces can be a structural artifact of a cut through one caption; do not treat them as intended repeated copy. Collapse them for visual continuity unless the user intentionally wants a cut-boundary hold.
- A user/manual correction outranks automatic chunking heuristics. Study the latest approved edit before regenerating captions.

---

## Implementation Code Patterns (Three-File Synchronization)

To write subtitle edits safely, the python script must update the microsecond modification timestamp (`tm_draft_modified`) across three crucial CapCut files simultaneously:
1. `draft_content.json`
2. `draft_meta_info.json`
3. `root_meta_info.json`

### Pattern A: Phrase-Preserving PyThaiNLP Tokenization & Subtitle Injector

> **Important:** Automatic token grouping is a fallback, not the editorial authority. If an upstream ASR/alignment pass already produced meaningful phrase blocks, preserve those exact blocks. Do not re-fragment them merely to hit a word/character quota.

Below is the standard python template (`inject_snappy_capcut_v2.py`):


```python
import json
import sys
import time
import uuid
import copy
import re
from pathlib import Path
from pythainlp.tokenize import Tokenizer, Trie
from pythainlp.corpus import thai_words

# 1. Setup custom vocabulary to prevent syllable/word fracture
custom_vocab = {
    "แอร์โรบิก", "มานิต้า", "ความรู้สึก", "ออกกำลังกาย", "เป็นไงบ้าง", 
    "เหนื่อยนะ", "ไพลิน", "ดีมากมาก", "สนุกมากมาก", "พอกผิว", 
    "สดชื่นมาก", "คนท้ายท้าย", "ติดลบ", "พี่ชาย", "สุดยอดมาก", 
    "เย็นชื่นใจ", "ดีมากค่ะ", "ขอบคุณครับ", "ขอบคุณครับผม", "มันมันมาก"
}
all_words = set(thai_words()) | custom_vocab
trie = Trie(all_words)
tokenizer = Tokenizer(trie)

def group_tokens(text, tokenizer, soft_max_chars=28):
    """Conservative fallback. Prefer a long intact phrase over a semantically broken caption."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= soft_max_chars:
        return [text]

    # Split only at explicit strong boundaries. Upstream ASR/editor phrase blocks are preferred.
    explicit = [part.strip() for part in re.split(r"(?<=[.!?。！？])\s*|\n+|\s+[|—–]\s+", text) if part.strip()]
    if len(explicit) > 1:
        return explicit

    # Thai polite sentence endings are safe fallback boundaries. Do NOT force a split
    # merely because a character/token count was exceeded; that can strand negation,
    # connectors, quantities, or incomplete clauses.
    tokens = [t for t in tokenizer.word_tokenize(text) if t and not t.isspace()]
    groups, current = [], []
    safe_endings = {"ครับ", "ค่ะ", "คะ", "นะครับ", "นะคะ"}
    for token in tokens:
        current.append(token)
        if token.strip() in safe_endings and len("".join(current)) >= 12:
            groups.append("".join(current).strip())
            current = []
    if current:
        groups.append("".join(current).strip())
    return groups if len(groups) > 1 else [text]

def inject_subtitles(project_name, project_id):
    # Locate project draft_content.json (CapCut Desktop local draft storage)
    draft_dir = Path(rf"C:\Users\Admin\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\{project_name}")
    draft_file = draft_dir / "draft_content.json"
    
    if not draft_file.exists():
        raise FileNotFoundError(f"CapCut project '{project_name}' not found.")
        
    # Generate unique microsecond timestamp
    current_time_us = int(time.time() * 1000000)
        
    # Backup original draft
    backup_file = draft_dir / "draft_content.json.backup_antigravity"
    if not backup_file.exists():
        backup_file.write_bytes(draft_file.read_bytes())
        
    data = json.loads(draft_file.read_text(encoding="utf-8"))
    texts_dict = {t['id']: t for t in data.get("materials", {}).get("texts", [])}
    
    # Target track
    text_track = next((tk for tk in data.get("tracks", []) if tk.get("type") == "text"), None)
    if not text_track:
        raise ValueError("No text track found in draft_content.json.")
        
    keywords = ["สดชื่น", "เหนื่อย", "สุดยอด", "เฟรช", "เย็น", "หอม", "คูลลิ่ง", "ตัวช่วย", "มีแรง", "ชอบ", "ออกกำลังกาย"]
    font_resource_id = "7550220628331089169"
    font_path = "C:/Users/Admin/AppData/Local/CapCut/User Data/Cache/effect/7550220628331089169/21911ea3966d1474fabf270b36ff3316/font.ttf"
    font_title = "คณิต-SB"
    border_width = 0.03372548893094063 # Slider value 17
    
    yellow_color = [0.95686274766922, 0.7803921699523926, 0.05882352963089943]
    white_color = [1.0, 1.0, 1.0]
    
    new_segments = []
    new_materials = []
    
    for seg in text_track.get("segments", []):
        parent_mat = texts_dict.get(seg.get("material_id"))
        if not parent_mat:
            continue
            
        txt_str = parent_mat.get("recognize_text", "") or parent_mat.get("text", "")
        t_range = seg.get("target_timerange", {})
        t_start = t_range.get("start", 0)
        t_duration = t_range.get("duration", 0)
        
        # Tokenize and group
        snappy_blocks = group_tokens(txt_str, tokenizer)
        
        total_chars = sum(len(b) for b in snappy_blocks)
        current_start = t_start
        
        for idx, block_txt in enumerate(snappy_blocks):
            # Proportional duration calculation
            if idx == len(snappy_blocks) - 1:
                block_dur = t_duration - (current_start - t_start)
            else:
                block_dur = int(round(t_duration * (len(block_txt) / total_chars)))
                
            new_mat_id = str(uuid.uuid4()).upper()
            new_seg_id = str(uuid.uuid4()).upper()
            
            # Smart character-level style override (Yellow highlights only on key terms)
            char_styles = []
            has_kw = False
            kw_indices = [False] * len(block_txt)
            
            for kw in keywords:
                start_idx = 0
                while True:
                    idx_kw = block_txt.find(kw, start_idx)
                    if idx_kw == -1:
                        break
                    has_kw = True
                    for i in range(idx_kw, idx_kw + len(kw)):
                        kw_indices[i] = True
                    start_idx = idx_kw + 1
                    
            if has_kw:
                # Group contiguous colors
                current_color = yellow_color if kw_indices[0] else white_color
                range_start = 0
                for i in range(1, len(block_txt)):
                    char_color = yellow_color if kw_indices[i] else white_color
                    if char_color != current_color:
                        char_styles.append({
                            "fill": {"alpha": 1.0, "content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": current_color}}},
                            "font": {"id": font_resource_id, "path": font_path},
                            "range": [range_start, i],
                            "size": 10.0,
                            "strokes": [{"alpha": 1.0, "content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": [0.0, 0.0, 0.0]}}, "width": border_width, "mode": 0}],
                            "useLetterColor": True
                        })
                        current_color = char_color
                        range_start = i
                char_styles.append({
                    "fill": {"alpha": 1.0, "content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": current_color}}},
                    "font": {"id": font_resource_id, "path": font_path},
                    "range": [range_start, len(block_txt)],
                    "size": 10.0,
                    "strokes": [{"alpha": 1.0, "content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": [0.0, 0.0, 0.0]}}, "width": border_width, "mode": 0}],
                    "useLetterColor": True
                })
            else:
                # Solid White block spanning the entire range
                char_styles.append({
                    "fill": {"alpha": 1.0, "content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": white_color}}},
                    "font": {"id": font_resource_id, "path": font_path},
                    "range": [0, len(block_txt)],
                    "size": 10.0,
                    "strokes": [{"alpha": 1.0, "content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": [0.0, 0.0, 0.0]}}, "width": border_width, "mode": 0}],
                    "useLetterColor": True
                })
                
            content_obj = {"styles": char_styles, "text": block_txt}
            content_str = json.dumps(content_obj, ensure_ascii=False)
            
            # Clone and update material
            new_mat = copy.deepcopy(parent_mat)
            new_mat.update({
                "id": new_mat_id,
                "recognize_text": block_txt,
                "text": None,
                "content": content_str,
                "base_content": content_str,
                "words": {"start_time": [0], "end_time": [int(block_dur // 1000)], "text": [block_txt]},
                "border_alpha": 1.0,
                "border_color": "#000000",
                "border_width": border_width,
                "font_title": font_title,
                "font_path": font_path,
                "font_resource_id": font_resource_id,
                "font_size": 10.0,
                "text_color": "#ffffff"
            })
            new_materials.append(new_mat)
            
            # Clone and update timeline segment
            new_seg = copy.deepcopy(seg)
            new_seg.update({
                "id": new_seg_id,
                "material_id": new_mat_id,
                "target_timerange": {"start": current_start, "duration": block_dur},
                "render_timerange": {"start": current_start, "duration": 0}
            })
            new_seg["clip"]["transform"] = {"x": 0.0, "y": -0.35} # Lower chest-level
            new_segments.append(new_seg)
            
            current_start += block_dur
            
    data["materials"]["texts"] = new_materials
    text_track["segments"] = new_segments
    
    # 1. Save draft_content.json
    draft_file.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")
    
    # 2. Save draft_meta_info.json with new timestamp
    meta_file = draft_dir / "draft_meta_info.json"
    if meta_file.exists():
        meta_data = json.loads(meta_file.read_text(encoding="utf-8"))
        meta_data["tm_draft_modified"] = current_time_us
        meta_file.write_text(json.dumps(meta_data, ensure_ascii=False, indent=4), encoding="utf-8")
        
    # 3. Save root_meta_info.json with new timestamp
    root_file = Path(r"C:\Users\Admin\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\root_meta_info.json")
    if root_file.exists():
        root_data = json.loads(root_file.read_text(encoding="utf-8"))
        for entry in root_data.get("all_draft_store", []):
            if entry.get("draft_name") == project_name or entry.get("draft_id") == project_id:
                entry["tm_draft_modified"] = current_time_us
        root_file.write_text(json.dumps(root_data, ensure_ascii=False, indent=4), encoding="utf-8")
```

### Prerequisite: Multi-Video Track Discovery (MANDATORY before Pattern B)

Before running ANY Whisper transcription or alignment, you **MUST** inspect the video track to discover how many source video files the project uses and their timeline mappings. Failure to do this will result in subtitles mapped to the wrong audio.

```python
# MANDATORY: Run this BEFORE any Whisper transcription
import json, os

def discover_video_tracks(draft_dir):
    """Returns list of {path, timeline_start, timeline_dur, source_offset} for each video segment."""
    draft_file = os.path.join(draft_dir, "draft_content.json")
    with open(draft_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    video_track = next((t for t in data.get("tracks", []) if t.get("type") == "video"), None)
    if not video_track:
        raise ValueError("No video track found!")

    videos = []
    materials = data.get("materials", {})
    mat_lookup = {}
    for m_type in ["videos", "video_effects"]:
        for m in materials.get(m_type, []):
            mat_lookup[m.get("id")] = m

    for seg in video_track.get("segments", []):
        target = seg.get("target_timerange", {})
        source = seg.get("source_timerange", {})
        mat = mat_lookup.get(seg.get("material_id"), {})
        videos.append({
            "path": mat.get("path") or mat.get("file_Path") or "UNKNOWN",
            "timeline_start_s": target.get("start", 0) / 1e6,
            "timeline_dur_s": target.get("duration", 0) / 1e6,
            "source_offset_s": source.get("start", 0) / 1e6,
            "speed": seg.get("speed", 1.0)
        })
    return videos

# Usage:
videos = discover_video_tracks(draft_dir)
for i, v in enumerate(videos):
    print(f"Video {i}: {v['path']}")
    print(f"  Timeline: {v['timeline_start_s']:.1f}s - {v['timeline_start_s']+v['timeline_dur_s']:.1f}s")
    print(f"  Source offset: {v['source_offset_s']:.1f}s, Speed: {v['speed']}")
```

**Timestamp mapping formula** (to convert Whisper source timestamps to CapCut timeline timestamps):
```
timeline_time = (whisper_source_time - source_offset) / speed + timeline_start
```

Example for a project with 2 video files:
| Video | Source Offset | Timeline Start | Formula |
|-------|--------------|----------------|----------|
| Part5.mp4 | 24.5s | 0.0s | `timeline = (whisper - 24.5) / 1.0 + 0` |
| Part6.mp4 | 0.0s | 31.733s | `timeline = (whisper - 0) / 1.0 + 31.733` |

### Whisper Model Selection for Thai

Always use `medium` or larger for Thai language transcription. Smaller models produce gibberish for Thai.

| Model | Thai Accuracy | When to Use |
|-------|--------------|-------------|
| `tiny`/`base` | ❌ Unusable | Never for Thai |
| `small` | ⚠️ Many errors | Only if `medium` is too slow |
| **`medium`** | **✅ Recommended** | **Default for all Thai projects** |
| `large` | ✅ Best | When `medium` still has errors |

```python
import whisper
model = whisper.load_model("medium")  # MINIMUM for Thai
result = model.transcribe(video_path, language="th", fp16=False, word_timestamps=True)
```

**Critical**: When a project has multiple video files, you MUST transcribe **each file separately** and map timestamps using the formula above. Never transcribe one file and apply its results across the entire timeline.

---

### Pattern B: Robust Sliding Window Alignment & Monotonic Interpolation

Use this pattern when the video has been edited and timeline subtitles no longer align with speech. This fuzzy matches CapCut subtitles to Whisper character-level timestamps in a sliding window, enforces monotonicity (chronological order), linearly interpolates fallback segments, and applies targeted yellow highlights.

Below is the standard python template (`robust_align_and_style.py`):

```python
import json
import time
import os
import sys
import difflib

def clean_text(text):
    import re
    text = re.sub(r'[\s\.\,\!\?\-\_]', '', text)
    return text.lower()

def align_and_style(draft_dir, whisper_configs, corrections=None, keywords=None):
    """
    whisper_configs: List of dicts, e.g. [
        {"path": "p5.json", "source_offset": 24.5, "timeline_start": 0.0, "speed": 1.0},
        {"path": "p6.json", "source_offset": 0.0, "timeline_start": 31.733, "speed": 1.0}
    ]
    """
    draft_file = os.path.join(draft_dir, "draft_content.json")
    meta_file = os.path.join(draft_dir, "draft_meta_info.json")
    root_file = r"C:\Users\Admin\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\root_meta_info.json"

    # Backup original draft
    backup_file = draft_file + ".backup_before_alignment"
    if not os.path.exists(backup_file):
        with open(draft_file, "rb") as f_in:
            with open(backup_file, "wb") as f_out:
                f_out.write(f_in.read())

    with open(draft_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Reconstruct Unified Whisper Character Timeline
    whisper_chars = []
    for cfg in whisper_configs:
        with open(cfg["path"], "r", encoding="utf-8") as f:
            w_data = json.load(f)
            
        offset = cfg["source_offset"]
        tl_start = cfg["timeline_start"]
        speed = cfg.get("speed", 1.0)
        
        for seg in w_data.get("segments", []):
            if "words" in seg:
                for w in seg["words"]:
                    # Convert to timeline using formula: timeline = (whisper - offset) / speed + tl_start
                    start = (w["start"] - offset) / speed + tl_start
                    end = (w["end"] - offset) / speed + tl_start
                    if end > tl_start:
                        whisper_chars.append({
                            "char": w["word"],
                            "start": max(tl_start, start),
                            "end": end
                        })
                        
    whisper_chars.sort(key=lambda x: x["start"])

    texts_list = data.get("materials", {}).get("texts", [])
    texts_dict = {t['id']: t for t in texts_list}

    # Find main text track
    text_track = next((tk for tk in data.get("tracks", []) if tk.get("type") == "text"), None)
    if not text_track:
        raise ValueError("Main text track not found")

    capcut_segs = text_track.get("segments", [])
    matched_info = []
    last_matched_end = 0.0

    # 2. Window-Based Fuzzy Matching with Monotonicity Guard
    for s_idx, seg in enumerate(capcut_segs):
        mat = texts_dict.get(seg.get("material_id"))
        txt_val = corrections.get(s_idx) if corrections and s_idx in corrections else ""
        if not txt_val and mat:
            try:
                txt_val = json.loads(mat.get("content", "{}")).get("text", "")
            except:
                txt_val = mat.get("text", "") or mat.get("recognize_text", "")
                
        target = seg.get("target_timerange", {})
        cc_start = target.get("start", 0) / 1e6
        cc_dur = target.get("duration", 0) / 1e6
        cc_end = cc_start + cc_dur

        clean_sub = clean_text(txt_val)
        if not clean_sub:
            matched_info.append({
                "idx": s_idx, "orig_start": cc_start, "orig_end": cc_end, "orig_dur": cc_dur,
                "aligned_start": cc_start, "aligned_end": cc_end, "is_matched": False, "text": txt_val
            })
            continue

        # Window starts after last_matched_end - 0.2s to enforce monotonicity
        min_search_time = max(0.0, last_matched_end - 0.2)
        window_chars = []
        window_mapping = []
        for idx, x in enumerate(whisper_chars):
            char_center = (x["start"] + x["end"]) / 2.0
            if min_search_time <= char_center <= (cc_start + 6.0):
                window_chars.append(x)
                window_mapping.append(idx)
                
        window_text_cleaned = []
        char_flat_mapping = []
        for w_idx, x in enumerate(window_chars):
            cleaned = clean_text(x["char"])
            for c in cleaned:
                window_text_cleaned.append(c)
                char_flat_mapping.append(w_idx)
                
        window_flat_text = "".join(window_text_cleaned)
        
        # Sliding window similarity search
        best_ratio = 0.0
        best_span = None
        pat_len = len(clean_sub)
        
        for size in range(max(1, pat_len - 3), pat_len + 4):
            for start in range(len(window_flat_text) - size + 1):
                sub = window_flat_text[start : start + size]
                ratio = difflib.SequenceMatcher(None, clean_sub, sub).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_span = (start, start + size - 1)
                    
        found = False
        if best_ratio >= 0.5 and best_span is not None:
            flat_start_idx, flat_end_idx = best_span
            w_idx_start = char_flat_mapping[flat_start_idx]
            w_idx_end = char_flat_mapping[flat_end_idx]
            global_idx_start = window_mapping[w_idx_start]
            global_idx_end = window_mapping[w_idx_end]
            aligned_start = whisper_chars[global_idx_start]["start"]
            aligned_end = whisper_chars[global_idx_end]["end"]
            
            drift = aligned_start - cc_start
            
            # Adaptive drift thresholds to prevent incorrect duplicate matches
            is_valid = False
            if best_ratio >= 0.85:
                is_valid = abs(drift) <= 5.0  # Exact match: allow larger systematic drift
            elif best_ratio >= 0.60:
                is_valid = abs(drift) <= 2.5
            else:
                is_valid = abs(drift) <= 1.0
                
            if is_valid and aligned_start >= (last_matched_end - 0.2):
                matched_info.append({
                    "idx": s_idx, "orig_start": cc_start, "orig_end": cc_end, "orig_dur": cc_dur,
                    "aligned_start": aligned_start, "aligned_end": aligned_end, "is_matched": True, "text": txt_val
                })
                last_matched_end = aligned_end
                found = True
                
        if not found:
            matched_info.append({
                "idx": s_idx, "orig_start": cc_start, "orig_end": cc_end, "orig_dur": cc_dur,
                "aligned_start": None, "aligned_end": None, "is_matched": False, "text": txt_val
            })

    # 3. Linear Interpolation for Fallback Segments
    matched_indices = [i for i, x in enumerate(matched_info) if x["is_matched"]]
    for i, x in enumerate(matched_info):
        if x["is_matched"]:
            continue
            
        prev_idx = next((idx for idx in reversed(matched_indices) if idx < i), None)
        next_idx = next((idx for idx in matched_indices if idx > i), None)
        
        if prev_idx is not None and next_idx is not None:
            orig_prev = matched_info[prev_idx]["orig_start"]
            orig_next = matched_info[next_idx]["orig_start"]
            orig_curr = x["orig_start"]
            
            aligned_prev = matched_info[prev_idx]["aligned_end"]
            aligned_next = matched_info[next_idx]["aligned_start"]
            
            t = (orig_curr - orig_prev) / (orig_next - orig_prev)
            aligned_start = aligned_prev + t * (aligned_next - aligned_prev)
            
            aligned_dur = x["orig_dur"] * ((aligned_next - aligned_prev) / (orig_next - orig_prev))
            aligned_dur = max(0.1, min(aligned_dur, x["orig_dur"] * 1.5))
            x["aligned_start"] = aligned_start
            x["aligned_end"] = aligned_start + aligned_dur
        elif prev_idx is not None:
            shift = matched_info[prev_idx]["aligned_start"] - matched_info[prev_idx]["orig_start"]
            x["aligned_start"] = x["orig_start"] + shift
            x["aligned_end"] = x["orig_end"] + shift
        elif next_idx is not None:
            shift = matched_info[next_idx]["aligned_start"] - matched_info[next_idx]["orig_start"]
            x["aligned_start"] = x["orig_start"] + shift
            x["aligned_end"] = x["orig_end"] + shift
        else:
            x["aligned_start"] = x["orig_start"]
            x["aligned_end"] = x["orig_end"]

    # 4. Apply Visual Styling & Highlight Overrides
    font_resource_id = "7550220628331089169"
    font_path = "C:/Users/Admin/AppData/Local/CapCut/User Data/Cache/effect/7550220628331089169/21911ea3966d1474fabf270b36ff3316/font.ttf"
    font_title = "คณิต-SB"
    border_width = 0.03372548893094063
    
    yellow_color = [0.95686274766922, 0.7803921699523926, 0.05882352963089943]
    white_color = [1.0, 1.0, 1.0]

    for x in matched_info:
        s_idx = x["idx"]
        aligned_start_us = int(round(x["aligned_start"] * 1000000))
        aligned_dur_us = int(round((x["aligned_end"] - x["aligned_start"]) * 1000000))
        
        seg = capcut_segs[s_idx]
        seg["target_timerange"] = {"start": aligned_start_us, "duration": aligned_dur_us}
        seg["render_timerange"] = {"start": 0, "duration": 0}
        seg["clip"]["transform"] = {"x": 0.0, "y": -0.35} # Chest level
        
        mat = texts_dict.get(seg.get("material_id"))
        if mat:
            txt_str = x["text"]
            char_styles = []
            kw_indices = [False] * len(txt_str)
            has_kw = False
            
            if keywords:
                for kw in keywords:
                    start_idx = 0
                    while True:
                        idx_kw = txt_str.find(kw, start_idx)
                        if idx_kw == -1: break
                        has_kw = True
                        for j in range(idx_kw, idx_kw + len(kw)):
                            kw_indices[j] = True
                        start_idx = idx_kw + 1

            if has_kw:
                current_color = yellow_color if kw_indices[0] else white_color
                range_start = 0
                for j in range(1, len(txt_str)):
                    char_color = yellow_color if kw_indices[j] else white_color
                    if char_color != current_color:
                        char_styles.append({
                            "fill": {"alpha": 1.0, "content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": current_color}}},
                            "font": {"id": font_resource_id, "path": font_path},
                            "range": [range_start, j], "size": 11.0,
                            "strokes": [{"alpha": 1.0, "content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": [0.0, 0.0, 0.0]}}, "width": border_width, "mode": 0}],
                            "useLetterColor": True
                        })
                        current_color = char_color
                        range_start = j
                char_styles.append({
                    "fill": {"alpha": 1.0, "content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": current_color}}},
                    "font": {"id": font_resource_id, "path": font_path},
                    "range": [range_start, len(txt_str)], "size": 11.0,
                    "strokes": [{"alpha": 1.0, "content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": [0.0, 0.0, 0.0]}}, "width": border_width, "mode": 0}],
                    "useLetterColor": True
                })
            else:
                char_styles.append({
                    "fill": {"alpha": 1.0, "content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": white_color}}},
                    "font": {"id": font_resource_id, "path": font_path},
                    "range": [0, len(txt_str)], "size": 11.0,
                    "strokes": [{"alpha": 1.0, "content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": [0.0, 0.0, 0.0]}}, "width": border_width, "mode": 0}],
                    "useLetterColor": True
                })

            content_obj = {"styles": char_styles, "text": txt_str}
            content_str_new = json.dumps(content_obj, ensure_ascii=False)
            
            mat.update({
                "recognize_text": txt_str, "text": txt_str, "content": content_str_new, "base_content": content_str_new,
                "words": {"start_time": [0], "end_time": [int(aligned_dur_us // 1000)], "text": [txt_str]},
                "border_alpha": 1.0, "border_color": "#000000", "border_width": border_width,
                "font_title": font_title, "font_path": font_path, "font_resource_id": font_resource_id, "font_size": 11.0,
                "text_color": "#ffffff", "font_name": font_title
            })

    # 5. Save and Sync
    current_time_us = int(time.time() * 1000000)
    data["update_time"] = current_time_us
    with open(draft_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    if os.path.exists(meta_file):
        with open(meta_file, "r", encoding="utf-8") as f:
            meta_data = json.load(f)
        meta_data["tm_draft_modified"] = current_time_us
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, ensure_ascii=False, indent=4)
            
    if os.path.exists(root_file):
        with open(root_file, "r", encoding="utf-8") as f:
            root_data = json.load(f)
        project_id = meta_data.get("draft_id", "") if os.path.exists(meta_file) else ""
        for entry in root_data.get("all_draft_store", []):
            if entry.get("draft_name") == os.path.basename(draft_dir) or (project_id and entry.get("draft_id") == project_id):
                entry["tm_draft_modified"] = current_time_us
        with open(root_file, "w", encoding="utf-8") as f:
            json.dump(root_data, f, ensure_ascii=False, indent=4)
```

---

## Common Mistakes & Red Flags

> [!CAUTION]
> **CapCut RAM Cache & Cloud Sync Overwrite (Three-File Conflict)**:
> CapCut Desktop relies on `tm_draft_modified` timestamps inside `draft_meta_info.json` and `root_meta_info.json` to verify project updates.
> **RED FLAG**: Editing only `draft_content.json` on disk. CapCut Desktop will assume the file is outdated/invalid and completely overwrite it with its old RAM cache or cloud backup upon next open.
> **CORRECTION**: Always update the local draft modification timestamps (`tm_draft_modified`) in `draft_meta_info.json` and `root_meta_info.json` to the current microsecond epoch timestamp (`int(time.time() * 1000000)`) simultaneously whenever writing disk updates!

> [!CAUTION]
> **Multi-Video File Transcription Mismatch (Timeline Corruption)**:
> CapCut projects often contain **multiple video files** spliced together on the timeline. Each file has its own `source_timerange` offset.
> **RED FLAG**: Transcribing only one video file with Whisper and mapping its timestamps across the entire CapCut timeline. This causes subtitles in the second file's region to receive completely wrong text from the first file's audio, corrupting half or more of all subtitles.
> **CORRECTION**: Always run `discover_video_tracks()` first to identify ALL source files and their timeline mappings. Transcribe EACH file separately with Whisper `medium`+, then apply the timestamp mapping formula `timeline = (whisper_time - source_offset) / speed + timeline_start` before alignment. This was discovered in the ไทยvsจีนep5 incident where 37 out of 113 subtitles were corrupted.

> [!WARNING]
> **Word Syllable Fractures**:
> Using a default Thai tokenizer will break syllable-based words like "แอร์โรบิก" into `['แอร์', 'โร', 'บิ', 'ก']`, producing disjointed, unreadable captions.
> **CORRECTION**: Always build a `Trie` of all custom terms and names and pass it to PyThaiNLP's tokenizer to keep compound words intact as a single block.


> [!WARNING]
> **Rigid 1–2 Word / 12-Character Splitting**:
> A hard word/character quota can split a Thai phrase at the wrong semantic point even when every individual word is technically intact.
> **CORRECTION**: Treat 1–2 words / ~12 characters as a pacing hint only. Prefer one complete readable phrase, then use word timestamps and picture-cut boundaries to decide the display change.

> [!WARNING]
> **Stale Captions After a New Picture Cut**:
> Ripple trims can split one caption into adjacent identical physical segments or leave old absolute subtitle times behind.
> **CORRECTION**: Re-map captions from the current source/target video ranges. Treat adjacent identical split pieces as structural until proven intentional; collapse/re-time them when visual continuity allows.

> [!WARNING]
> **Whisper Model Too Small for Thai**:
> Using Whisper `tiny`, `base`, or even `small` for Thai produces severe transcription errors — gibberish text, wrong words, and mixed-language hallucinations.
> **CORRECTION**: Always use Whisper `medium` as the minimum model for Thai transcription. Use `large` if `medium` still has significant errors.
