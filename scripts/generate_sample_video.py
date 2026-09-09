#!/usr/bin/env python3
"""
RECALL: Deterministic Benchmark Video Generator
Generates a 75-second high-contrast MP4 video with labeled visual scenes,
timestamps, and state changes matching sample_data/kitchen_mystery_events.json.
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = Path(__file__).resolve().parent.parent
EVENTS_FILE = ROOT_DIR / "sample_data" / "kitchen_mystery_events.json"
OUTPUT_MP4 = ROOT_DIR / "sample_data" / "kitchen_mystery_demo.mp4"

WIDTH, HEIGHT = 1280, 720
FPS = 2  # 2 frames per second for smooth timeline tracking

def get_font(size: int):
    # Try system fonts or default
    try:
        # macOS standard fonts
        for font_path in [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/Library/Fonts/Arial.ttf"
        ]:
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, size)
    except Exception:
        pass
    return ImageFont.load_default()

def format_time(seconds: float) -> str:
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"

def render_frame(sec: float, total_sec: float, event: dict) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), color=(15, 23, 42))  # Deep slate #0F172A
    draw = ImageDraw.Draw(img)

    font_large = get_font(40)
    font_med = get_font(26)
    font_small = get_font(20)
    font_bold = get_font(32)

    # 1. Header Bar
    draw.rectangle([(0, 0), (WIDTH, 70)], fill=(30, 41, 59))
    draw.text((30, 18), "RECALL | Visual Memory Benchmark: The Kitchen Hand-off", fill=(56, 189, 248), font=font_med)

    # Timestamp badge
    time_str = f"{format_time(sec)} / {format_time(total_sec)}"
    draw.rounded_rectangle([(WIDTH - 220, 14), (WIDTH - 30, 56)], radius=8, fill=(245, 158, 11))
    draw.text((WIDTH - 200, 20), time_str, fill=(0, 0, 0), font=font_bold)

    # 2. Main Visual Canvas Box
    draw.rounded_rectangle([(50, 95), (WIDTH - 50, 430)], radius=16, fill=(2, 6, 23), outline=(51, 65, 85), width=3)

    # Interior scene representation
    # Kitchen outline
    draw.rectangle([(80, 120), (WIDTH - 80, 405)], outline=(71, 85, 105), width=2)
    draw.text((100, 130), f"ZONE: {event.get('location', 'KITCHEN').upper()}", fill=(148, 163, 184), font=font_small)

    # Schematic entities
    # Dining Table
    table_fill = (45, 30, 15)
    table_outline = (180, 83, 9)
    draw.rounded_rectangle([(300, 200), (620, 370)], radius=10, fill=table_fill, outline=table_outline, width=3)
    draw.text((330, 210), "DINING TABLE", fill=(251, 191, 36), font=font_small)

    # Cabinet & Drawers
    cab_fill = (30, 41, 59)
    cab_outline = (96, 165, 250)
    draw.rounded_rectangle([(750, 160), (1150, 370)], radius=10, fill=cab_fill, outline=cab_outline, width=3)
    draw.text((770, 175), "CABINET STORAGE", fill=(147, 197, 253), font=font_small)

    # Determine State based on timestamp
    # 0 - 7s: Table bare, Drawer closed, Envelope in Maya's hand
    # 7 - 19s: Envelope on Table
    # 19 - 38s: Envelope in Daniel's hand
    # 38 - 65s: Envelope inside Cabinet Drawer (Closed)
    # 65 - 75s: Envelope in Sofia's hand / Drawer Open
    envelope_on_table = (7.0 <= sec < 19.0)
    drawer_open = (34.0 <= sec < 45.0) or (sec >= 65.0)
    envelope_in_drawer = (38.0 <= sec < 69.0)

    # Draw Table Content
    if envelope_on_table:
        draw.rounded_rectangle([(400, 260), (520, 320)], radius=6, fill=(217, 119, 6), outline=(254, 240, 138), width=2)
        draw.text((410, 280), "ENVELOPE", fill=(255, 255, 255), font=font_small)
    else:
        draw.text((410, 280), "[Bare Table]", fill=(100, 116, 139), font=font_small)

    # Draw Drawer
    drawer_fill = (51, 65, 85) if not drawer_open else (71, 85, 105)
    drawer_outline = (245, 158, 11) if drawer_open else (148, 163, 184)
    draw.rounded_rectangle([(800, 240), (1100, 320)], radius=6, fill=drawer_fill, outline=drawer_outline, width=3)
    drawer_state = "OPEN (Top-Right Drawer)" if drawer_open else "CLOSED (Top-Right Drawer)"
    draw.text((820, 255), drawer_state, fill=(255, 255, 255), font=font_small)

    if envelope_in_drawer:
        draw.rounded_rectangle([(930, 285), (1050, 312)], radius=4, fill=(217, 119, 6))
        draw.text((945, 290), "ENVELOPE", fill=(255, 255, 255), font=get_font(16))

    # Characters indicator
    characters = event.get("characters", [])
    if characters:
        char_text = " | ".join([f"👤 {c}" for c in characters])
        draw.rounded_rectangle([(100, 320), (280, 370)], radius=8, fill=(16, 185, 129))
        draw.text((115, 332), char_text, fill=(0, 0, 0), font=font_med)

    # 3. Action Description Area (Below visual box)
    draw.rounded_rectangle([(50, 450), (WIDTH - 50, 680)], radius=16, fill=(30, 41, 59), outline=(51, 65, 85), width=2)

    # Event ID & Type
    ev_type = event.get("event_type", "ACTION").upper()
    draw.text((80, 470), f"EVENT [{event.get('event_id', 'evt')}] • {ev_type}", fill=(56, 189, 248), font=font_med)

    # Action line
    action_text = event.get("action", "")
    draw.text((80, 515), f"ACTION: {action_text}", fill=(245, 158, 11), font=font_bold)

    # Visual description (multi-line wrap if needed)
    vis_desc = event.get("visual_description", "")
    draw.text((80, 565), f"OBSERVATION:\n\"{vis_desc}\"", fill=(241, 245, 249), font=font_med)

    # Status pills at bottom right
    p1 = "Envelope: On Table" if envelope_on_table else ("Envelope: In Drawer" if envelope_in_drawer else "Envelope: Carried/None")
    p2 = f"Drawer: {'Open' if drawer_open else 'Closed'}"
    draw.rounded_rectangle([(WIDTH - 480, 630), (WIDTH - 280, 665)], radius=6, fill=(15, 23, 42))
    draw.text((WIDTH - 465, 638), p1, fill=(56, 189, 248), font=get_font(18))

    draw.rounded_rectangle([(WIDTH - 260, 630), (WIDTH - 80, 665)], radius=6, fill=(15, 23, 42))
    draw.text((WIDTH - 245, 638), p2, fill=(251, 191, 36), font=get_font(18))

    return img

def generate_video():
    if not EVENTS_FILE.exists():
        raise FileNotFoundError(f"Events file {EVENTS_FILE} not found!")

    with open(EVENTS_FILE, "r") as f:
        data = json.load(f)

    events = data.get("events", [])
    total_seconds = data.get("duration_seconds", 75.0)

    print(f"Generating {total_seconds}s video at {FPS} fps from {len(events)} events...")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        frame_idx = 0
        total_frames = int(total_seconds * FPS)

        for f in range(total_frames):
            curr_sec = f / FPS
            # Find active event
            active_event = events[0]
            for ev in events:
                if ev["start_seconds"] <= curr_sec < ev["end_seconds"]:
                    active_event = ev
                    break
                elif curr_sec >= ev["start_seconds"]:
                    active_event = ev

            frame_img = render_frame(curr_sec, total_seconds, active_event)
            frame_file = temp_path / f"frame_{frame_idx:05d}.png"
            frame_img.save(frame_file)
            frame_idx += 1

        print(f"Rendered {frame_idx} frames. Encoding MP4 using ffmpeg...")
        OUTPUT_MP4.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(FPS),
            "-i", str(temp_path / "frame_%05d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            str(OUTPUT_MP4)
        ]

        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print("FFmpeg stderr:\n", res.stderr)
            raise RuntimeError(f"FFmpeg failed with code {res.returncode}")

    print(f"Successfully created benchmark video: {OUTPUT_MP4} ({OUTPUT_MP4.stat().st_size} bytes)")

if __name__ == "__main__":
    generate_video()
