import tkinter as tk
from tkinter import messagebox, ttk, StringVar, simpledialog
import threading
from yt_dlp import YoutubeDL
import os

def fetch_formats():
    url = url_entry.get()
    if not url.strip():
        messagebox.showerror("Error", "Please enter a YouTube URL")
        return
    formats_label.config(text="Fetching formats...")
    threading.Thread(target=lambda: perform_format_fetch(url)).start()


def display_formats(formats):
    format_listbox.delete(0, tk.END)
    for format_line in formats:
        format_listbox.insert(tk.END, format_line)
def perform_format_fetch(url):
    try:
        ydl_opts = {
            'progress_hooks': [progress_hook],
        }
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', [])
            
        # Header for the formats display
        formatted_lines = [
            "ID   EXT RESOLUTION  FPS  CH │   FILESIZE    TBR  PROTO │ VCODEC         VBR  ACODEC       ABR  ASR  MORE INFO"
        ]
        formatted_lines.append("────────────────────────────────────────────────────────────────────────────────────────────────────────────────")
        
        # Loop through each format and extract/format the required details
        for f in formats:
            line = "{:<4} {:<4} {:<10} {:<5} {:<4}│ {:<12} {:<5} {:<6}│ {:<15} {:<5} {:<10} {:<5} {:<5} {}".format(
                f.get('format_id', '') or '-',
                f.get('ext', '') or '-',
                (f.get('resolution', '') or "audio only") if f.get('resolution') is not None else "audio only",
                str(f.get('fps', '') or '-') if f.get('fps') is not None else '-',
                '-',  # Placeholder for Channels, as it's not directly available
                '-',  # Placeholder for Filesize, as it's not always present
                str(f.get('tbr', '') or '-') if f.get('tbr') is not None else '-',  # Total Bitrate
                f.get('protocol', '') or '-',
                (f.get('vcodec', '') or 'audio only') if f.get('vcodec') is not None else 'audio only',
                str(f.get('vbr', '') or '-') if f.get('vbr') is not None else '-',
                f.get('acodec', '') or '-',
                str(f.get('abr', '') or '-') if f.get('abr') is not None else '-',  # Audio Bitrate
                str(f.get('asr', '') or '-') if f.get('asr') is not None else '-',  # Audio sample rate
                f.get('format_note', '') or '-',
            )
            formatted_lines.append(line)

        display_formats(formatted_lines)
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        formats_label.config(text="")

def progress_hook(d):
    if d['status'] == 'downloading':
        # Extract total bytes and bytes downloaded from the `d` dictionary
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded_bytes = d.get('downloaded_bytes')
        if total_bytes and downloaded_bytes:
            # Calculate the percentage completed
            percentage = (downloaded_bytes / total_bytes) * 100
            # Update the progress bar
            progress['value'] = percentage
            app.update_idletasks()  # Update the UI to reflect the progress bar change
    elif d['status'] == 'finished':
        print("Download completed")
        progress['value'] = 100  # Fill the progress bar at the end of the download

def resource_path(relative_path):
    """Get the absolute path to the resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
        
    return os.path.join(base_path, relative_path)

def download_video():
    url = url_entry.get()
    selected_index = format_listbox.curselection()
    if not url.strip() or not selected_index:
        messagebox.showerror("Error", "Please enter a YouTube URL and select a format")
        return
    selected_format = format_listbox.get(selected_index[0]).split()[0]  # Extract format code
    status_label.config(text="Downloading...")
    # threading.Thread(target=lambda: perform_download(url, selected_format)).start()
    progress['value'] = 0  # Reset progress bar to 0 before starting the download
    threading.Thread(target=lambda: perform_download(url, selected_format)).start()

        
def perform_download(url, format_code):
    try:
        ydl_opts = {
            'format': format_code,
            'progress_hooks': [progress_hook],  # Include the progress hook
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        messagebox.showinfo("Success", "Download complete!")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        status_label.config(text="")
        progress['value'] = 0  # Reset progress bar after download


app = tk.Tk()
app.title("YouTube Video Downloader")
app.geometry("800x550")
icon_path = resource_path("cheeze1.ico")
app.iconbitmap(icon_path)
app.resizable(False, False)
tk.Label(app, text="Enter YouTube URL:").pack(pady=10)
url_entry = tk.Entry(app, width=50)
url_entry.pack(pady=5)

fetch_formats_button = tk.Button(app, text="Fetch Formats", command=fetch_formats)
fetch_formats_button.pack(pady=10)

formats_frame = tk.Frame(app)
formats_scrollbar = tk.Scrollbar(formats_frame, orient="vertical")
format_listbox = tk.Listbox(
    formats_frame, 
    width=100, 
    height=16, 
    yscrollcommand=formats_scrollbar.set, 
    selectmode=tk.SINGLE
)
formats_scrollbar.config(command=format_listbox.yview)
formats_scrollbar.pack(side="right", fill="y")
format_listbox.pack(side="left")
formats_frame.pack(pady=5)

formats_label = tk.Label(app, text="")
formats_label.pack(pady=5)

download_button = tk.Button(app, text="Download", command=download_video)
download_button.pack(pady=15)

status_label = tk.Label(app, text="")
status_label.pack(pady=2)

progress = ttk.Progressbar(app, orient="horizontal", length=400, mode="determinate")
progress.pack(pady=2)


app.mainloop()
