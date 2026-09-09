#!/usr/bin/env python3
"""
RECALL: Deterministic Benchmark Video Generator
Generates a 75-second high-contrast, perfectly scaled 1280x720 MP4 video
with illustrated scene states, wrapped observations, and clean margins.
"""

import os
import json
import textwrap
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = Path(__file__).resolve().parent.parent
EVENTS_FILE = ROOT_DIR / "sample_data" / "kitchen_mystery_events.json"
OUTPUT_MP4 = ROOT_DIR / "sample_data" / "kitchen_mystery_demo.mp4"
PUBLIC_MP4 = ROOT_DIR / "frontend" / "public" / "sample_data" / "kitchen_mystery_demo.mp4"

WIDTH, HEIGHT = 1280, 720
FPS = 2

def get_font(size: int, bold: bool = False):
    # Try system fonts
    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf"
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()

def format_time(seconds: float) -> str:
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"

def render_frame(sec: float, total_sec: float, event: dict) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), color=(11, 15, 25))  # #0B0F19 deep slate
    draw = ImageDraw.Draw(img)

    f_title = get_font(22, bold=True)
    f_time = get_font(24, bold=True)
    f_sec_title = get_font(20, bold=True)
    f_action = get_font(24, bold=True)
    f_body = get_font(18)
    f_badge = get_font(15, bold=True)

    # 1. Top Header Bar
    draw.rectangle([(0, 0), (WIDTH, 56)], fill=(20, 27, 45))
    draw.line([(0, 56), (WIDTH, 56)], fill=(38, 50, 78), width=2)
    draw.text((32, 16), "RECALL • Visual Memory Benchmark: The Kitchen Hand-off", fill=(56, 189, 248), font=f_title)

    # Time pill on right
    time_str = f"{format_time(sec)} / {format_time(total_sec)}"
    draw.rounded_rectangle([(WIDTH - 210, 10), (WIDTH - 30, 46)], radius=6, fill=(245, 158, 11))
    draw.text((WIDTH - 185, 14), time_str, fill=(0, 0, 0), font=f_time)

    # 2. Main Visual Canvas Box (The Room)
    margin_x = 40
    draw.rounded_rectangle([(margin_x, 70), (WIDTH - margin_x, 480)], radius=12, fill=(4, 8, 16), outline=(38, 50, 78), width=2)

    # Room Location Tag
    loc_text = f"ZONE: {event.get('location', 'KITCHEN').upper()}"
    draw.rounded_rectangle([(margin_x + 20, 84), (margin_x + 360, 116)], radius=4, fill=(20, 27, 45))
    draw.text((margin_x + 32, 91), loc_text, fill=(148, 163, 184), font=f_badge)

    # State calculations
    # 0 - 7s: Maya enters carrying envelope
    # 7 - 19s: Envelope on Table
    # 19 - 38s: Envelope in Daniel's hand
    # 38 - 65s: Envelope hidden in Drawer
    # 65 - 75s: Sofia opens drawer and finds envelope
    envelope_on_table = (7.0 <= sec < 19.0)
    drawer_open = (34.0 <= sec < 45.0) or (sec >= 65.0)
    envelope_in_drawer = (38.0 <= sec < 69.0)
    envelope_in_hand = (4.0 <= sec < 7.0) or (19.0 <= sec < 38.0) or (sec >= 69.0)

    # Schematic Furniture: Dining Table (Left-Center)
    draw.rounded_rectangle([(180, 170), (520, 390)], radius=12, fill=(35, 24, 15), outline=(180, 83, 9), width=3)
    draw.text((290, 185), "DINING TABLE", fill=(251, 191, 36), font=f_sec_title)
    draw.ellipse([(310, 230), (390, 280)], fill=(55, 40, 25), outline=(140, 70, 15), width=2) # Fruit bowl
    draw.text((322, 248), "Bowl", fill=(160, 120, 80), font=f_badge)

    # Table Envelope Status
    if envelope_on_table:
        draw.rounded_rectangle([(280, 305), (420, 365)], radius=6, fill=(217, 119, 6), outline=(254, 240, 138), width=2)
        draw.text((298, 323), "ENVELOPE", fill=(255, 255, 255), font=get_font(18, bold=True))
    else:
        draw.text((290, 325), "[Table Clear]", fill=(85, 100, 120), font=f_body)

    # Schematic Furniture: Storage Cabinet & Drawer (Right-Center)
    draw.rounded_rectangle([(680, 140), (1160, 420)], radius=12, fill=(20, 27, 45), outline=(96, 165, 250), width=3)
    draw.text((820, 155), "KITCHEN CABINET STORAGE", fill=(147, 197, 253), font=f_sec_title)

    # Other drawers (Bottom & Left)
    draw.rounded_rectangle([(710, 310), (910, 395)], radius=6, fill=(30, 41, 59), outline=(51, 65, 85), width=2)
    draw.text((750, 345), "Lower Drawer", fill=(100, 116, 139), font=f_body)

    draw.rounded_rectangle([(930, 310), (1130, 395)], radius=6, fill=(30, 41, 59), outline=(51, 65, 85), width=2)
    draw.text((970, 345), "Lower Drawer", fill=(100, 116, 139), font=f_body)

    draw.rounded_rectangle([(710, 205), (910, 290)], radius=6, fill=(30, 41, 59), outline=(51, 65, 85), width=2)
    draw.text((755, 240), "Top-Left Drawer", fill=(100, 116, 139), font=f_body)

    # Target Top-Right Drawer
    tr_fill = (45, 55, 75) if not drawer_open else (71, 85, 105)
    tr_outline = (245, 158, 11) if drawer_open else (148, 163, 184)
    draw.rounded_rectangle([(930, 205), (1130, 290)], radius=6, fill=tr_fill, outline=tr_outline, width=3)
    tr_label = "TOP-RIGHT (OPEN)" if drawer_open else "TOP-RIGHT (CLOSED)"
    draw.text((945, 218), tr_label, fill=(255, 255, 255), font=f_badge)

    if envelope_in_drawer:
        draw.rounded_rectangle([(955, 248), (1105, 280)], radius=4, fill=(217, 119, 6), outline=(254, 240, 138), width=1)
        draw.text((975, 254), "ENVELOPE INSIDE", fill=(255, 255, 255), font=get_font(14, bold=True))
    elif not drawer_open:
        draw.text((990, 252), "[Empty]", fill=(120, 135, 155), font=f_body)

    # Active Characters Banner
    chars = event.get("characters", [])
    if chars:
        for idx, c in enumerate(chars):
            color = (56, 189, 248) if c == "Maya" else ((244, 63, 94) if c == "Daniel" else (16, 185, 129))
            pill_x = margin_x + 20 + (idx * 160)
            draw.rounded_rectangle([(pill_x, 430), (pill_x + 145, 465)], radius=6, fill=color)
            draw.text((pill_x + 12, 438), f"ACTOR: {c}", fill=(0, 0, 0), font=get_font(16, bold=True))

    # 3. Bottom Information & Observation Card
    card_top = 495
    draw.rounded_rectangle([(margin_x, card_top), (WIDTH - margin_x, 700)], radius=12, fill=(20, 27, 45), outline=(38, 50, 78), width=2)

    # Event ID & Type
    ev_type = event.get("event_type", "ACTION").upper().replace("_", " ")
    ev_id = event.get("event_id", "evt").upper()
    draw.text((margin_x + 24, card_top + 14), f"EVENT [{ev_id}] • {ev_type}", fill=(56, 189, 248), font=f_sec_title)

    # Action line
    act_text = f"ACTION: {event.get('action', '')}"
    draw.text((margin_x + 24, card_top + 46), act_text, fill=(245, 158, 11), font=f_action)

    # Observation line (wrapped)
    vis_desc = event.get("visual_description", "")
    wrapped_lines = textwrap.wrap(f"OBSERVATION: \"{vis_desc}\"", width=85)
    for l_idx, line in enumerate(wrapped_lines[:2]):
        draw.text((margin_x + 24, card_top + 88 + (l_idx * 26)), line, fill=(241, 245, 249), font=f_body)

    # Quick Status Badges on right of bottom card
    p1 = "Envelope: On Table" if envelope_on_table else ("Envelope: In Drawer" if envelope_in_drawer else ("Envelope: Carried" if envelope_in_hand else "Envelope: Concealed"))
    p2 = "Drawer: Open" if drawer_open else "Drawer: Closed"
    
    draw.rounded_rectangle([(WIDTH - margin_x - 390, card_top + 14), (WIDTH - margin_x - 190, card_top + 46)], radius=6, fill=(11, 15, 25), outline=(56, 189, 248), width=1)
    draw.text((WIDTH - margin_x - 378, card_top + 21), p1, fill=(56, 189, 248), font=f_badge)

    draw.rounded_rectangle([(WIDTH - margin_x - 175, card_top + 14), (WIDTH - margin_x - 20, card_top + 46)], radius=6, fill=(11, 15, 25), outline=(245, 158, 11), width=1)
    draw.text((WIDTH - margin_x - 160, card_top + 21), p2, fill=(251, 191, 36), font=f_badge)

    return img

def generate_video():
    if not EVENTS_FILE.exists():
        raise FileNotFoundError(f"Events file {EVENTS_FILE} not found!")

    with open(EVENTS_FILE, "r") as f:
        data = json.load(f)

    events = data.get("events", [])
    total_seconds = data.get("duration_seconds", 75.0)

    print(f"Generating optimized {total_seconds}s video at {FPS} fps from {len(events)} events...")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        frame_idx = 0
        total_frames = int(total_seconds * FPS)

        for f in range(total_frames):
            curr_sec = f / FPS
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

        print(f"Rendered {frame_idx} frames. Encoding MP4 with faststart...")
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

    # Also copy to frontend public directory
    PUBLIC_MP4.parent.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copyfile(OUTPUT_MP4, PUBLIC_MP4)
    print(f"Successfully generated and synced video to:\n- {OUTPUT_MP4}\n- {PUBLIC_MP4}")

if __name__ == "__main__":
    generate_video()
