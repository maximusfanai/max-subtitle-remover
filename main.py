import os
import subprocess
import cv2
import numpy as np
import streamlit as st
import shutil
import time

# Check FFmpeg Executable Path Automatically
FFMPEG_PATH = shutil.which("ffmpeg")
if not FFMPEG_PATH:
    try:
        import imageio_ffmpeg
        FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        FFMPEG_PATH = "ffmpeg"

# Directory Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
ASSETS_DIR = r"F:\subtitleremover\assets"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# Page Setup
st.set_page_config(
    page_title="MAX Subtitle Remover", page_icon="🎬", layout="centered"
)

# Custom CSS - Dark Neon Theme & Text Styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0B0F19;
        color: #F8FAFC;
    }
    
    /* Main Header Container */
    .header-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin-bottom: 5px;
    }

    .logo-container {
        width: 85px;
        height: 85px;
        border-radius: 50%;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #0B0F19;
        box-shadow: 0 0 18px rgba(56, 189, 248, 0.6);
        border: 2px solid #38BDF8;
        margin-bottom: 10px;
    }

    .logo-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    .sub-title {
        color: #0EA5E9 !important; /* Cyan / Sky Blue */
        text-align: center;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        margin-bottom: 20px;
    }

    /* Section Subheaders */
    div[data-testid="stMarkdownContainer"] h3 {
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        color: #38BDF8 !important;
        margin-top: 10px !important;
    }

    /* File Uploader Label */
    div[data-testid="stFileUploader"] label p {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #38BDF8 !important;
    }

    /* Radio Group Label */
    div[data-testid="stRadio"] > label {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #38BDF8 !important;
    }

    /* Radio Options Text */
    div[data-testid="stRadio"] label p {
        font-size: 1.0rem !important;
        font-weight: 500 !important;
        color: #F1F5F9 !important;
    }

    /* Process Button styling */
    div.stButton > button {
        background: linear-gradient(90deg, #0284C7 0%, #38BDF8 100%) !important;
        color: white !important;
        font-size: 1.15rem !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px 20px !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(56, 189, 248, 0.35) !important;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #0369A1 0%, #0284C7 100%) !important;
        box-shadow: 0 0 18px #38BDF8 !important;
    }

    video {
        border-radius: 12px !important;
        display: block !important;
        margin: 0 auto !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Header Section with Circular Logo
logo_path = os.path.join(ASSETS_DIR, "logo.png")
if os.path.exists(logo_path):
    import base64
    with open(logo_path, "rb") as img_file:
        encoded_logo = base64.b64encode(img_file.read()).decode()
    logo_html = f"""
    <div style="display: flex; justify-content: center; align-items: center;">
        <div class='logo-container'>
            <img src='data:image/png;base64,{encoded_logo}' class='logo-img'>
        </div>
    </div>
    """
    st.markdown(logo_html, unsafe_allow_html=True)
else:
    st.markdown("<div style='text-align: center; font-size: 3.0rem; margin-bottom: 5px;'>🎬</div>", unsafe_allow_html=True)

# Streamlit Native Title
st.markdown("<h1 style='text-align: center; font-size: 2.1rem; font-weight: 700; color: #38BDF8; margin-bottom: 0px; text-shadow: 0 0 12px rgba(56, 189, 248, 0.4);'><span style='color: #FFFFFF;'>MAX</span> Subtitle Remover</h1>", unsafe_allow_html=True)

st.markdown(
    "<div class='sub-title'>PURE CONTENT • CLEAN VIDEO • CHROME WEB APP</div>",
    unsafe_allow_html=True,
)

# File Upload
uploaded_file = st.file_uploader(
    "Select Video File (MP4, MKV, AVI, MOV)",
    type=["mp4", "mkv", "avi", "mov"],
)

if uploaded_file is not None:
    temp_input_path = os.path.join(TEMP_DIR, uploaded_file.name)

    with open(temp_input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # OpenCV Video Metadata Detection
    cap = cv2.VideoCapture(temp_input_path)
    v_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    v_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    cap.release()

    # Dynamic Video Display Sizing
    if v_height > v_width:
        st.markdown(
            """
            <style>
            video {
                max-width: 600px !important;
                max-height: 600px !important;
                width: 100% !important;
            }
            </style>
        """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <style>
            video {
                max-width: 700px !important;
                max-height: 700px !important;
                width: 100% !important;
            }
            </style>
        """,
            unsafe_allow_html=True,
        )

    # Video Preview
    st.video(temp_input_path)

    # Subtitle Mode Options
    st.subheader("Select Subtitle Action")
    mode = st.radio(
        "Choose Mode:",
        [
            "Soft Subtitle (Regional Static Blur)",
            "Hardcoded Subtitle (Stable Anti-Blur Text Removal)",
        ],
        index=0,
    )

    # Process Button with Circular Loading Ring & Clickable Ad Link
    if st.button("⚡ REMOVE SUBTITLES NOW"):
        output_file_name = f"nosub_{uploaded_file.name}"
        output_path = os.path.join(OUTPUT_DIR, output_file_name)

        # Circular Progress Container Placeholder
        progress_placeholder = st.empty()

        # 30-Second Advertisement Countdown UI with Clickable Ad Link
        def render_ad_countdown(seconds_left):
            html_code = f"""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 20px 0;">
                <div style="
                    width: 180px; 
                    height: 180px; 
                    border-radius: 50%; 
                    background: conic-gradient(from 0deg, #F59E0B 0%, #FBBF24 {int((30 - seconds_left) / 30 * 100)}%, #0F172A {int((30 - seconds_left) / 30 * 100)}% 100%); 
                    display: flex; 
                    align-items: center; 
                    justify-content: center;
                    box-shadow: 0 0 30px rgba(245, 158, 11, 0.4);
                ">
                    <div style="
                        width: 145px; 
                        height: 145px; 
                        border-radius: 50%; 
                        background-color: #0B0F19; 
                        display: flex; 
                        flex-direction: column; 
                        align-items: center; 
                        justify-content: center;
                        box-shadow: inset 0 0 12px rgba(0,0,0,0.8);
                    ">
                        <div style="font-size: 2.0rem; margin-bottom: 2px;">📢</div>
                        <div style="font-size: 1.6rem; font-weight: 700; color: #FBBF24; text-shadow: 0 0 10px rgba(245, 158, 11, 0.6);">{seconds_left}s</div>
                    </div>
                </div>
                <div style="font-size: 1.2rem; font-weight: 600; color: #F8FAFC; margin-top: 16px; letter-spacing: 0.3px;">Sponsored Advertisement</div>
                <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 4px; margin-bottom: 12px;">Please wait while the ad plays...</div>
                <a href="https://www.google.com" target="_blank" style="
                    background: linear-gradient(90deg, #D97706 0%, #F59E0B 100%);
                    color: white;
                    padding: 8px 18px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-size: 0.95rem;
                    font-weight: 600;
                    box-shadow: 0 0 12px rgba(245, 158, 11, 0.4);
                ">🔗 Click Here to Visit Sponsor Ad</a>
            </div>
            """
            progress_placeholder.markdown(html_code, unsafe_allow_html=True)

        # Run 30 Seconds Ad Countdown
        for sec in range(30, 0, -1):
            render_ad_countdown(sec)
            time.sleep(1.0)

        # Neon Dark Sky Blue Circular Progress Ring UI for Processing
        def render_circular_progress(percentage, status_text="Removing Subtitles..."):
            display_pct = min(100, max(0, percentage))
            if status_text == "Completed!":
                display_pct = 100

            sub_text = (
                "Please do not close the app"
                if display_pct < 100
                else "Subtitle Removal Completed!"
            )

            html_code = f"""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 20px 0;">
                <div style="
                    width: 180px; 
                    height: 180px; 
                    border-radius: 50%; 
                    background: conic-gradient(from 0deg, #0284C7 0%, #38BDF8 {display_pct}%, #0F172A {display_pct}% 100%); 
                    display: flex; 
                    align-items: center; 
                    justify-content: center;
                    box-shadow: 0 0 30px rgba(56, 189, 248, 0.4);
                ">
                    <div style="
                        width: 145px; 
                        height: 145px; 
                        border-radius: 50%; 
                        background-color: #0B0F19; 
                        display: flex; 
                        flex-direction: column; 
                        align-items: center; 
                        justify-content: center;
                        box-shadow: inset 0 0 12px rgba(0,0,0,0.8);
                    ">
                        <div style="font-size: 2.2rem; margin-bottom: 2px;">🎬</div>
                        <div style="font-size: 1.8rem; font-weight: 700; color: #FFFFFF; text-shadow: 0 0 10px rgba(56, 189, 248, 0.6);">{display_pct}%</div>
                    </div>
                </div>
                <div style="font-size: 1.2rem; font-weight: 600; color: #F8FAFC; margin-top: 16px; letter-spacing: 0.3px;">{status_text}</div>
                <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 4px;">{sub_text}</div>
            </div>
            """
            progress_placeholder.markdown(html_code, unsafe_allow_html=True)

        render_circular_progress(0)

        try:
            if "Soft Subtitle" in mode:
                cmd = [
                    FFMPEG_PATH,
                    "-y",
                    "-progress",
                    "pipe:1",
                    "-i",
                    temp_input_path,
                    "-filter_complex",
                    f"[0:v]boxblur=20:enable='between(y,H*0.6,H)'[v_blurred]",
                    "-map", "[v_blurred]",
                    "-map",
                    "0:a?",
                    "-sn",
                    "-c:v", "libx264",
                    "-c:a", "copy",
                    output_path,
                ]
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    encoding="utf-8",
                    errors="replace",
                    bufsize=1,
                )
                last_pct = 0
                for line in process.stdout:
                    if "out_time_ms=" in line:
                        try:
                            time_ms = int(line.split("=")[1].strip())
                            time_sec = time_ms / 1_000_000
                            if duration > 0:
                                pct = min(int((time_sec / duration) * 100), 99)
                                if pct > last_pct:
                                    last_pct = pct
                                    render_circular_progress(pct)
                                    time.sleep(0.01)
                        except ValueError:
                            pass
                process.wait()

            else:
                temp_no_audio = os.path.join(TEMP_DIR, "temp_inpainted.mp4")
                cap = cv2.VideoCapture(temp_input_path)

                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                out = cv2.VideoWriter(
                    temp_no_audio, fourcc, fps, (v_width, v_height)
                )

                frame_idx = 0
                sub_y1 = int(v_height * 0.45)

                tophat_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
                dilate_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

                mask_history = []
                HISTORY_SIZE = 8

                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break

                    sub_roi = frame[sub_y1:v_height, :]
                    gray_roi = cv2.cvtColor(sub_roi, cv2.COLOR_BGR2GRAY)

                    tophat = cv2.morphologyEx(gray_roi, cv2.MORPH_TOPHAT, tophat_kernel)
                    _, binary_mask = cv2.threshold(tophat, 20, 255, cv2.THRESH_BINARY)

                    contours, _ = cv2.findContours(
                        binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                    )
                    clean_text_mask = np.zeros_like(binary_mask)

                    for cnt in contours:
                        x, y, w, h = cv2.boundingRect(cnt)
                        area = cv2.contourArea(cnt)
                        if 10 < area < 10000 and 6 < h < (v_height * 0.3) and w > 2:
                            cv2.drawContours(
                                clean_text_mask, [cnt], -1, 255, thickness=cv2.FILLED
                            )

                    dilated_mask = cv2.dilate(
                        clean_text_mask, dilate_kernel, iterations=1
                    )

                    mask_history.append(dilated_mask)
                    if len(mask_history) > HISTORY_SIZE:
                        mask_history.pop(0)

                    stable_mask = np.maximum.reduce(mask_history)

                    full_mask = np.zeros((v_height, v_width), dtype=np.uint8)
                    full_mask[sub_y1:v_height, :] = stable_mask

                    clean_frame = cv2.inpaint(
                        frame, full_mask, inpaintRadius=2, flags=cv2.INPAINT_NS
                    )

                    out.write(clean_frame)
                    frame_idx += 1

                    if total_frames > 0:
                        pct = min(int((frame_idx / total_frames) * 100), 99)
                        if pct % 2 == 0:
                            render_circular_progress(pct)

                cap.release()
                out.release()

                merge_cmd = [
                    FFMPEG_PATH,
                    "-y",
                    "-i",
                    temp_no_audio,
                    "-i",
                    temp_input_path,
                    "-c:v",
                    "libx264",
                    "-preset",
                    "fast",
                    "-crf",
                    "18",
                    "-map",
                    "0:v:0",
                    "-map",
                    "1:a:0?",
                    "-c:a",
                    "copy",
                    output_path,
                ]
                subprocess.run(merge_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            render_circular_progress(100, "Completed!")
            time.sleep(3)

            progress_placeholder.empty()
            with progress_placeholder.container():
                st.subheader("Result Preview & Download")
                st.video(output_path)

                with open(output_path, "rb") as file:
                    st.download_button(
                        label="⬇️ Download Processed Video",
                        data=file,
                        file_name=output_file_name,
                        mime="video/mp4",
                    )

        except Exception as id:
            st.error(f"Error occurred: {str(id)}")