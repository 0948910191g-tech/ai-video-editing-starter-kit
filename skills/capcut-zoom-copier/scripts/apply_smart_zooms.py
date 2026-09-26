import json
import os
import sys
import uuid

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 apply_smart_zooms.py <path_to_capcut_project>")
        sys.exit(1)

    project_path = sys.argv[1]
    draft_info_path = os.path.join(project_path, "draft_info.json")

    if not os.path.exists(draft_info_path):
        print(f"Error: {draft_info_path} does not exist.")
        sys.exit(1)

    with open(draft_info_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Load text materials
    text_materials = {}
    for text_mat in data.get("materials", {}).get("texts", []):
        mat_id = text_mat.get("id")
        content_str = text_mat.get("content", "{}")
        try:
            content_json = json.loads(content_str)
            text_materials[mat_id] = content_json.get("text", "")
        except:
            pass

    # Extract subtitles
    subtitles = []
    for track in data.get("tracks", []):
        if track.get("type") == "text":
            for seg in track.get("segments", []):
                start = seg.get("target_timerange", {}).get("start", 0) / 1000000.0
                duration = seg.get("target_timerange", {}).get("duration", 0) / 1000000.0
                mat_id = seg.get("material_id")
                text = text_materials.get(mat_id, "")
                if text:
                    subtitles.append({"start": start, "end": start + duration, "text": text})

    subtitles.sort(key=lambda x: x["start"])

    def get_subtitles_in_range(start_time, end_time):
        overlapping = []
        for sub in subtitles:
            if max(start_time, sub["start"]) < min(end_time, sub["end"]):
                overlapping.append(sub["text"])
        return " ".join(overlapping)

    # Keywords that trigger a static zoom
    static_zoom_keywords = [
        "เฮ้ย", "โอ้โห", "เดี๋ยว", "เนี่ย", "แต่แม่ง", "โคตร", "เจ็บ", "รู้ไหม", 
        "ไหม", "ป้ะ", "ย้ำว่า", "ส่วนใหญ่", "บอกเลยนะ", "แปลก", "สุดท้าย", 
        "ระวัง", "คุณคิดว่า", "ลองสังเกต", "ฟังผมดีๆ", "เชื่อผม", "แต่ว่า", "จริงๆแล้ว",
        "หรือว่า", "ผิดไหม"
    ]

    def make_uuid():
        return str(uuid.uuid4()).upper()

    def create_scale_keyframe_list(duration_us, start_scale, end_scale, prop_type):
        return {
            "id": make_uuid(),
            "material_id": "",
            "property_type": prop_type,
            "keyframe_list": [
                {
                    "id": make_uuid(),
                    "curveType": "Line",
                    "time_offset": 0,
                    "values": [start_scale],
                    "left_control": {"x": 0.0, "y": 0.0},
                    "right_control": {"x": 0.0, "y": 0.0}
                },
                {
                    "id": make_uuid(),
                    "curveType": "Line",
                    "time_offset": duration_us,
                    "values": [end_scale],
                    "left_control": {"x": 0.0, "y": 0.0},
                    "right_control": {"x": 0.0, "y": 0.0}
                }
            ]
        }

    video_tracks = [t for t in data.get("tracks", []) if t.get("type") == "video"]
    main_video_track = None
    if video_tracks:
        main_video_track = max(video_tracks, key=lambda t: len(t.get("segments", [])))

    stats = {"slow_zooms": 0, "static_zooms": 0, "standard": 0}

    if main_video_track:
        segments = main_video_track.get("segments", [])
        for idx, seg in enumerate(segments):
            duration_us = seg.get("target_timerange", {}).get("duration", 0)
            start_us = seg.get("target_timerange", {}).get("start", 0)
            start_sec = start_us / 1000000.0
            dur_sec = duration_us / 1000000.0
            end_sec = start_sec + dur_sec
            
            speech = get_subtitles_in_range(start_sec, end_sec)
            
            zoom_type = "standard"
            is_trigger_word = any(kw in speech for kw in static_zoom_keywords)
            
            if dur_sec >= 4.5:
                zoom_type = "slow_zoom"
            elif is_trigger_word and dur_sec < 4.0:
                zoom_type = "static_zoom"
            elif dur_sec < 1.0 and idx % 3 == 0:
                zoom_type = "static_zoom"
                
            if idx == 0 and zoom_type != "slow_zoom" and dur_sec > 2.5:
                zoom_type = "slow_zoom"

            if "clip" not in seg or not seg["clip"]:
                seg["clip"] = {}
            seg["clip"]["scale"] = {"x": 1.0, "y": 1.0}
            
            common_kf = seg.get("common_keyframes", [])
            common_kf = [kf for kf in common_kf if kf.get("property_type") not in ["KFTypeScaleX", "KFTypeScaleY", "KFTypeScale"]]
            seg["common_keyframes"] = common_kf
            
            if zoom_type == "slow_zoom":
                kx = create_scale_keyframe_list(duration_us, 1.0, 1.08, "KFTypeScaleX")
                ky = create_scale_keyframe_list(duration_us, 1.0, 1.08, "KFTypeScaleY")
                seg["common_keyframes"].append(kx)
                seg["common_keyframes"].append(ky)
                stats["slow_zooms"] += 1
                
            elif zoom_type == "static_zoom":
                zoom_level = 1.08
                seg["clip"]["scale"] = {"x": zoom_level, "y": zoom_level}
                stats["static_zooms"] += 1
                
            else:
                stats["standard"] += 1

            seg["enable_adjust_mask"] = True

    with open(draft_info_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

    print(f"Zoom processing completed: {stats}")

if __name__ == "__main__":
    main()
