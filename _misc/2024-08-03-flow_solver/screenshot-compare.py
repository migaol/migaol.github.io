import os
import time
from PIL import ImageGrab
import mss
from pathlib import Path

OUT_DIR = str(Path.home() / "Downloads")
# 'full' or '1/3'
MODE = '1/3'

def get_capture_area():
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Assumes the primary monitor
        width = monitor["width"]
        height = monitor["height"]
        if MODE == '1/3':
            return {"left": 0, "top": 0, "width": width // 3, "height": height}
        else:
            return {"left": 0, "top": 0, "width": width, "height": height}

def measure_screencapture():
    area = get_capture_area()
    start_time = time.time()
    os.system(f"screencapture -R{area['left']},{area['top']},{area['width']},{area['height']} {OUT_DIR}/ss_screencapture.png")
    end_time = time.time()
    return end_time - start_time

def measure_pillow():
    area = get_capture_area()
    start_time = time.time()
    screenshot = ImageGrab.grab(bbox=(area['left'], area['top'], area['left'] + area['width'], area['top'] + area['height']))
    screenshot.save(f"{OUT_DIR}/ss_pillow.png")
    end_time = time.time()
    return end_time - start_time

def measure_mss():
    area = get_capture_area()
    start_time = time.time()
    with mss.mss() as sct:
        sct_img = sct.grab(area)
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=f"{OUT_DIR}/ss_mss.png")
    end_time = time.time()
    return end_time - start_time

def run_trials(n_trials=10):
    screencapture_times = []
    pillow_times = []
    mss_times = []

    for _ in range(n_trials):
        screencapture_times.append(measure_screencapture())
        pillow_times.append(measure_pillow())
        mss_times.append(measure_mss())

    avg_screencapture = sum(screencapture_times) / n_trials
    avg_pillow = sum(pillow_times) / n_trials
    avg_mss = sum(mss_times) / n_trials

    print(f"Average screencapture time: {avg_screencapture:.4f} seconds")
    print(f"       Average Pillow time: {avg_pillow:.4f} seconds")
    print(f"          Average mss time: {avg_mss:.4f} seconds")

if __name__ == "__main__":
    run_trials(10)
