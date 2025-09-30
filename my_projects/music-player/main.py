```python
import os
import pygame
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter.ttk import Style

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Player")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        pygame.mixer.init()

        self.playlist = []
        self.current_track = 0
        self.paused = False

        self.setup_ui()

    def setup_ui(self):
        style = Style()
        style.configure("TButton", padding=5, relief="flat", background="#ccc")
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        style.configure("TFrame", background="#f0f0f0")

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.track_label = ttk.Label(main_frame, text="No track selected", anchor=tk.CENTER)
        self.track_label.pack(fill=tk.X, pady=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        self.prev_button = ttk.Button(button_frame, text="⏮ Prev", command=self.prev_track)
        self.prev_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.play_button = ttk.Button(button_frame, text="▶ Play", command=self.play_music)
        self.play_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.pause_button = ttk.Button(button_frame, text="⏸ Pause", command=self.pause_music)
        self.pause_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.stop_button = ttk.Button(button_frame, text="⏹ Stop", command=self.stop_music)
        self.stop_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.next_button = ttk.Button(button_frame, text="⏭ Next", command=self.next_track)
        self.next_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.volume_frame = ttk.Frame(main_frame)
        self.volume_frame.pack(fill=tk.X, pady=5)

        ttk.Label(self.volume_frame, text="Volume:").pack(side=tk.LEFT, padx=5)

        self.volume_slider = ttk.Scale(self.volume_frame, from_=0, to=100, value=70, command=self.set_volume)
        self.volume_slider.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.load_button = ttk.Button(main_frame, text="Load Music Folder", command=self.load_music)
        self.load_button.pack(fill=tk.X, pady=10)

        pygame.mixer.music.set_volume(0.7)

    def load_music(self):
        folder_path = filedialog.askdirectory(title="Select Music Folder")
        if folder_path:
            self.playlist = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                           if f.endswith('.mp3') or f.endswith('.MP3')]
            if self.playlist:
                self.current_track = 0
                self.update_track_label()
            else:
                self.track_label.config(text="No MP3 files found in folder")

    def play_music(self):
        if not self.playlist:
            return

        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
        else:
            pygame.mixer.music.load(self.playlist[self.current_track])
            pygame.mixer.music.play()
            self.update_track_label()

    def pause_music(self):
        if pygame.mixer.music.get_busy() and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True

    def stop_music(self):
        pygame.mixer.music.stop()
        self.paused = False

    def next_track(self):
        if not self.playlist:
            return

        self.current_track = (self.current_track + 1) % len(self.playlist)
        self.play_music()

    def prev_track(self):
        if not self.playlist:
            return

        self.current_track = (self.current_track - 1) % len(self.playlist)
        self.play_music()

    def set_volume(self, volume):
        pygame.mixer.music.set_volume(float(volume) / 100)

    def update_track_label(self):
        if self.playlist:
            track_name = os.path.basename(self.playlist[self.current_track])
            self.track_label.config(text=track_name)
        else:
            self.track_label.config(text="No track selected")

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()
```