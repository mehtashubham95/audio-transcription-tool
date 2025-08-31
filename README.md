# Audio Transcription Tool

A **GUI-based transcription tool** designed to transcribe audio and video files into text with precise timestamps. This tool is specifically built for **content creators** who want to extract key moments from long-form content and use them with **LLM models like ChatGPT** to generate short-form content such as highlights, summaries, or social media clips.

---

## 🚀 Features

- **Accurate Transcription**: Uses OpenAI's **Whisper** model for high-quality speech-to-text transcription.
- **Precise Timestamps**: Provides both **segment-level** and **word-level** timestamps, making it easy to locate exact moments in the content.
- **Audio/Video Support**: Handles a wide range of formats:
  - **Video**: MP4, AVI, MOV, MKV, WMV, FLV, WebM.
  - **Audio**: MP3, WAV, FLAC, AAC, OGG, M4A.
- **User-Friendly Interface**: A simple and intuitive GUI built with **Tkinter** for easy file selection, progress tracking, and previewing results.
- **Content Creator Focus**: Designed to help creators extract timelines and transcriptions for use with tools like **ChatGPT** to generate short-form content from long videos.
- **Customizable Models**: Choose from Whisper's model sizes (`tiny`, `base`, `small`, `medium`, `large`) to balance speed and accuracy.

---

## 🎯 Use Case

This tool is ideal for **content creators** who work with long-form videos (e.g., podcasts, webinars, interviews) and want to:
1. **Transcribe content** into text with precise timestamps.
2. **Identify key moments** in the video using timestamps.
3. Use the transcription and timestamps with **LLM models like ChatGPT** to:
   - Generate short-form content (e.g., TikToks, YouTube Shorts, Instagram Reels).
   - Create summaries, captions, or highlight reels.
   - Automate content repurposing workflows.

---

## 🛠️ Requirements

- **Python**: Version 3.8 or higher.
- **Libraries**:
  - `whisper`
  - `moviepy`
  - `tkinter`

To install the required libraries, run:
```bash
pip install whisper moviepy tkinter
