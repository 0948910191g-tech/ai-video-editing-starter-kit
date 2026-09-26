import json
import os
import uuid
import shutil
import sys

def apply_sfx(project_dir, whoosh_path, whoosh_peak_s, whoosh_vol, shutter_path, shutter_vol):
    draft_info_path = os.path.join(project_dir, "draft_info.json")
    if not os.path.exists(draft_info_path):
        print(f"Error: draft_info.json not found in {project_dir}")
        return False

    # Back up
    backup_path = draft_info_path + ".backup_sfx"
    shutil.copyfile(draft_info_path, backup_path)
    print(f"Backup created at: {backup_path}")

    # Load JSON
    with open(draft_info_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Get durations using ffprobe helper
    def get_duration_us(path):
        import subprocess
        cmd = ["ffprobe", "-i", path, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"]
        out = subprocess.check_output(cmd).decode().strip()
        return int(float(out) * 1_000_000)

    try:
        whoosh_dur_us = get_duration_us(whoosh_path)
        shutter_dur_us = get_duration_us(shutter_path)
    except Exception as e:
        print(f"Error reading audio file durations: {e}")
        return False

    whoosh_peak_us = int(whoosh_peak_s * 1_000_000)

    # Find or register audio materials
    audios = data.setdefault("materials", {}).setdefault("audios", [])
    
    whoosh_mat_id = None
    shutter_mat_id = None
    for audio in audios:
        if audio.get("path") == whoosh_path:
            whoosh_mat_id = audio.get("id")
        elif audio.get("path") == shutter_path:
            shutter_mat_id = audio.get("id")

    def create_material(name, path, duration):
        return {
            "id": str(uuid.uuid4()).upper(),
            "unique_id": "",
            "type": "extract_music",
            "name": name,
            "duration": duration,
            "path": path,
            "category_name": "local",
            "wave_points": [],
            "local_material_id": str(uuid.uuid4()).lower(),
            "check_flag": 1,
            "copyright_limit_type": "none",
            "similiar_music_info": {"original_song_id": "", "original_song_name": ""},
            "tts_benefit_info": {"benefit_type": "none", "benefit_log_id": "", "benefit_log_extra": "", "benefit_amount": -1}
        }

    if not whoosh_mat_id:
        mat = create_material(os.path.basename(whoosh_path), whoosh_path, whoosh_dur_us)
        whoosh_mat_id = mat["id"]
        audios.append(mat)
    if not shutter_mat_id:
        mat = create_material(os.path.basename(shutter_path), shutter_path, shutter_dur_us)
        shutter_mat_id = mat["id"]
        audios.append(mat)

    # 1. Identify Whoosh triggers (static zoom-ins on Track 0)
    track0 = data["tracks"][0]
    whoosh_times = []
    for idx, seg in enumerate(track0.get("segments", [])):
        target_range = seg.get("target_timerange", {})
        start_us = target_range.get("start", 0)
        
        scale_x = seg.get("clip", {}).get("scale", {}).get("x", 1.0)
        common_kf = seg.get("common_keyframes", [])
        scale_kf = [kf.get("keyframe_list", []) for kf in common_kf if kf.get("property_type") in ["KFTypeScaleX", "KFTypeScaleY"]]
        scale_keyframes = scale_kf[0] if scale_kf else []
        
        is_gradual = len(scale_keyframes) > 1 and scale_keyframes[0].get("values", [1.0])[0] != scale_keyframes[-1].get("values", [1.0])[0]
        
        current_scale = scale_keyframes[0].get("values", [1.0])[0] if scale_keyframes else scale_x
        
        prev_scale = 1.0
        if idx > 0:
            prev_seg = track0["segments"][idx - 1]
            prev_scale = prev_seg.get("clip", {}).get("scale", {}).get("x", 1.0)
            prev_kf = [kf.get("keyframe_list", []) for kf in prev_seg.get("common_keyframes", []) if kf.get("property_type") in ["KFTypeScaleX", "KFTypeScaleY"]]
            prev_scale_keyframes = prev_kf[0] if prev_kf else []
            if prev_scale_keyframes:
                prev_scale = prev_scale_keyframes[-1].get("values", [1.0])[0]
                
        if current_scale > prev_scale and not is_gradual and current_scale > 1.01:
            whoosh_times.append(start_us)

    # 2. Identify Shutter triggers (B-roll starts on Track 1)
    track1 = data["tracks"][1]
    shutter_times = [seg.get("target_timerange", {}).get("start", 0) for seg in track1.get("segments", [])]

    # Helper for creating segment
    def create_segment(material_id, start_target, duration_target, start_source, duration_source, volume, render_idx):
        return {
            "id": str(uuid.uuid4()).upper(),
            "source_timerange": {"start": start_source, "duration": duration_source},
            "target_timerange": {"start": start_target, "duration": duration_target},
            "render_timerange": {"start": 0, "duration": 0},
            "desc": "", "state": 0, "speed": 1.0, "is_loop": False, "is_tone_modify": False, "reverse": False,
            "intensifies_audio": False, "cartoon": False, "volume": volume, "last_nonzero_volume": 1.0,
            "clip": None, "uniform_scale": None, "material_id": material_id, "extra_material_refs": [],
            "render_index": 0, "keyframe_refs": [], "enable_lut": False, "enable_adjust": False, "enable_hsl": False,
            "visible": True, "group_id": "", "enable_color_curves": True, "enable_hsl_curves": True,
            "track_render_index": render_idx, "hdr_settings": None, "enable_color_wheels": True, "track_attribute": 0,
            "is_placeholder": False, "template_id": "", "enable_smart_color_adjust": False, "template_scene": "default",
            "common_keyframes": [], "caption_info": None,
            "responsive_layout": {"enable": False, "target_follow": "", "size_layout": 0, "horizontal_pos_layout": 0, "vertical_pos_layout": 0},
            "enable_color_match_adjust": False, "enable_color_correct_adjust": False, "enable_adjust_mask": False,
            "raw_segment_id": "", "lyric_keyframes": None, "enable_video_mask": True, "digital_human_template_group_id": "",
            "color_correct_alg_result": "", "source": "segmentsourcenormal", "enable_mask_stroke": False,
            "enable_mask_shadow": False, "enable_color_adjust_pro": False
        }

    # Create Whoosh track
    whoosh_render_idx = len(data["tracks"])
    whoosh_segs = []
    for t in whoosh_times:
        target_start = max(0, t - whoosh_peak_us)
        source_start = max(0, whoosh_peak_us - t)
        duration = whoosh_dur_us - source_start
        whoosh_segs.append(create_segment(whoosh_mat_id, target_start, duration, source_start, duration, whoosh_vol, whoosh_render_idx))

    whoosh_track = {
        "id": str(uuid.uuid4()).upper(), "type": "audio", "segments": whoosh_segs,
        "flag": 0, "attribute": 0, "name": "Whoosh SFX", "is_default_name": False
    }

    # Create Shutter track
    shutter_render_idx = whoosh_render_idx + 1
    shutter_segs = []
    for t in shutter_times:
        shutter_segs.append(create_segment(shutter_mat_id, t, shutter_dur_us, 0, shutter_dur_us, shutter_vol, shutter_render_idx))

    shutter_track = {
        "id": str(uuid.uuid4()).upper(), "type": "audio", "segments": shutter_segs,
        "flag": 0, "attribute": 0, "name": "Shutter SFX", "is_default_name": False
    }

    data["tracks"].append(whoosh_track)
    data["tracks"].append(shutter_track)

    with open(draft_info_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print("Sound effects applied successfully.")
    return True
