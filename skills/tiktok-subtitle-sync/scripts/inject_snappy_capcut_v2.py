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

def inject_subtitles(project_name, project_id=None):
    # Locate project draft_content.json (CapCut Desktop local draft storage)
    draft_dir = Path(rf"C:\Users\Admin\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\{project_name}")
    draft_file = draft_dir / "draft_content.json"
    
    if not draft_file.exists():
        raise FileNotFoundError(f"CapCut project '{project_name}' not found at {draft_file}")
        
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
        
        # Preserve approved phrase blocks; use soft token grouping only for genuinely long text.
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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inject_snappy_capcut_v2.py <project_name> [project_id]")
        sys.exit(1)
    p_name = sys.argv[1]
    p_id = sys.argv[2] if len(sys.argv) > 2 else None
    print(f"Injecting snappy subtitles for project: {p_name}")
    try:
        inject_subtitles(p_name, p_id)
        print("Successfully synchronized subtitles and timestamps across all draft files!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
