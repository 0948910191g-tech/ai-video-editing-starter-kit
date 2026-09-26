import sys
import os
import subprocess
import numpy as np

def get_peak_time(audio_path, temp_pcm_dir="/tmp"):
    if not os.path.exists(audio_path):
        print(f"Error: file not found: {audio_path}")
        return None
        
    base = os.path.basename(audio_path)
    pcm_path = os.path.join(temp_pcm_dir, f"{os.path.splitext(base)[0]}.pcm")
    
    # Decode to PCM using ffmpeg
    cmd = [
        "ffmpeg", "-y", "-i", audio_path,
        "-f", "s16le", "-acodec", "pcm_s16le",
        "-ac", "1", "-ar", "44100", pcm_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if not os.path.exists(pcm_path):
        print("Error during ffmpeg decoding.")
        return None
        
    data = np.fromfile(pcm_path, dtype=np.int16)
    abs_data = np.abs(data)
    
    # 10ms window size
    window_size = 441
    energies = np.convolve(abs_data.astype(np.float32), np.ones(window_size)/window_size, mode='valid')
    peak_idx = np.argmax(energies) + window_size // 2
    peak_time = peak_idx / 44100.0
    
    # Cleanup temp PCM
    try:
        os.remove(pcm_path)
    except:
        pass
        
    return peak_time

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_peak.py <audio_file_path>")
        sys.exit(1)
    path = sys.argv[1]
    peak = get_peak_time(path)
    if peak is not None:
        print(f"Peak energy time: {peak:.3f}s ({int(peak*1000)}ms)")
