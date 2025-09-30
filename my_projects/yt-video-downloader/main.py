import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
import yt_dlp
import os

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("500x200")

        self.url_label = ttk.Label(root, text="YouTube URL:")
        self.url_label.pack(pady=5)

        self.url_entry = ttk.Entry(root, width=60)
        self.url_entry.pack(pady=5)

        self.download_button = ttk.Button(root, text="Download", command=self.start_download)
        self.download_button.pack(pady=10)

        self.progress_label = ttk.Label(root, text="Progress:")
        self.progress_label.pack()

        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=5)

        self.percentage_label = ttk.Label(root, text="0%")
        self.percentage_label.pack()

        self.stop_event = False

    def start_download(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return

        self.download_button.config(state="disabled")
        self.progress["value"] = 0
        self.percentage_label.config(text="0%")

        download_thread = Thread(target=self.download_video, args=(url,))
        download_thread.daemon = True
        download_thread.start()

    def download_video(self, url):
        try:
            ydl_opts = {
                'progress_hooks': [self.progress_hook],
                'outtmpl': os.path.join(os.path.expanduser("~"), "Downloads", "%(title)s.%(ext)s")
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            messagebox.showinfo("Success", "Download completed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.download_button.config(state="normal")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total_bytes:
                downloaded_bytes = d.get('downloaded_bytes', 0)
                progress = int((downloaded_bytes / total_bytes) * 100)
                self.progress["value"] = progress
                self.percentage_label.config(text=f"{progress}%")
                self.root.update_idletasks()
        elif d['status'] == 'finished':
            self.progress["value"] = 100
            self.percentage_label.config(text="100%")
            self.root.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()
