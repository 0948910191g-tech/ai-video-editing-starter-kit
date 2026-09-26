---
name: kim-sfx
description: Automatically detects timeline triggers (such as static zoom-ins or B-roll segment boundaries) in a CapCut desktop project, analyzes audio peak energy times, and injects customized sound effects (SFX) with perfect visual synchronization into separate tracks in draft_info.json.
---

# Kim sfx

This skill automates the detection of visual triggers on a CapCut Desktop timeline and programmatically injects synchronized sound effects (SFX) on separate audio tracks.

## Trigger Scenarios

- **Static Zoom-Ins**: Detects jump cuts where the player scale increases instantly (excluding slow/gradual zoom keyframes) and injects transition SFX (e.g., Whoosh, Swish).
- **B-Roll Starts**: Detects segment starts on B-Roll overlay video tracks (usually Track 1+) and injects indicator SFX (e.g., Camera Shutter, Pop).

## Key Workflow

### 1. Identify Visual Triggers in `draft_info.json`
- **Static Zoom-Ins**: Identify boundaries between segment $A$ and segment $B$ on Track 0 where scale $S_B > S_A$, and segment $B$ does not have multi-keyframe gradual zoom animations.
- **B-Roll Starts**: Read segment start times on the designated overlay video track(s).

### 2. Audio Peak Energy Analysis (Snappy Synchronization)
To make SFX feel snappy, the peak loudness of the sound effect must align precisely with the video transition frame.
- Use `ffmpeg` to extract mono PCM:
  `ffmpeg -i sfx.mp3 -f s16le -acodec pcm_s16le -ac 1 -ar 44100 sfx.pcm`
- Calculate the peak energy offset time $p$ (where the moving average of amplitude peaks).
- Offset target segment starts on the timeline by $-p$ so the audio peaks exactly on the transition.
- Adjust source start times if $-p$ results in a negative target timeline start (e.g., if transition is too close to 0s).

### 3. Database Injection
- **Materials**: Add entries to `materials.audios` with unique IDs, name, duration, and path.
- **Tracks**: Create dedicated audio track objects for each SFX type, keeping the timeline clean.
- **Segments**: Insert segments referencing the material IDs with target and source timeranges.

## File Templates

Example Python scripts for applying SFX and analyzing peaks are saved in the `scripts/` directory of this skill.
