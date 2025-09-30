import os
import tkinter as tk
from tkinter import filedialog, ttk
from pygame import mixer
from mutagen.mp3 import MP3

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Player")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        mixer.init()

        self.playlist = []
        self.current_track = 0
        self.paused = False
        self.stopped = True

        self.create_ui()

    def create_ui(self):
        self.track_frame = tk.LabelFrame(self.root, text="Current Track", bg="#f0f0f0", bd=5, relief=tk.GROOVE)
        self.track_frame.place(x=0, y=0, width=500, height=100)

        self.track_label = tk.Label(self.track_frame, text="No track selected", bg="#f0f0f0", font=("Arial", 12))
        self.track_label.pack(pady=20)

        self.button_frame = tk.LabelFrame(self.root, text="Controls", bg="#f0f0f0", bd=5, relief=tk.GROOVE)
        self.button_frame.place(x=0, y=100, width=500, height=100)

        self.load_button = tk.Button(self.button_frame, text="Load Folder", command=self.load_folder, width=10, height=1)
        self.load_button.grid(row=0, column=0, padx=10, pady=10)

        self.play_button = tk.Button(self.button_frame, text="Play", command=self.play_music, width=10, height=1)
        self.play_button.grid(row=0, column=1, padx=10, pady=10)

        self.pause_button = tk.Button(self.button_frame, text="Pause", command=self.pause_music, width=10, height=1)
        self.pause_button.grid(row=0, column=2, padx=10, pady=10)

        self.stop_button = tk.Button(self.button_frame, text="Stop", command=self.stop_music, width=10, height=1)
        self.stop_button.grid(row=0, column=3, padx=10, pady=10)

        self.prev_button = tk.Button(self.button_frame, text="Previous", command=self.prev_track, width=10, height=1)
        self.prev_button.grid(row=1, column=1, padx=10, pady=10)

        self.next_button = tk.Button(self.button_frame, text="Next", command=self.next_track, width=10, height=1)
        self.next_button.grid(row=1, column=2, padx=10, pady=10)

        self.volume_frame = tk.LabelFrame(self.root, text="Volume", bg="#f0f0f0", bd=5, relief=tk.GROOVE)
        self.volume_frame.place(x=0, y=200, width=500, height=60)

        self.volume_slider = ttk.Scale(self.volume_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.set_volume)
        self.volume_slider.set(70)
        self.volume_slider.pack(pady=10, padx=10, fill=tk.X)

        self.playlist_frame = tk.LabelFrame(self.root, text="Playlist", bg="#f0f0f0", bd=5, relief=tk.GROOVE)
        self.playlist_frame.place(x=0, y=260, width=500, height=140)

        self.playlist_box = tk.Listbox(self.playlist_frame, selectbackground="lightblue", bg="#f0f0f0", font=("Arial", 10))
        self.playlist_box.pack(fill=tk.BOTH, expand=True)

        self.playlist_box.bind("<Double-1>", self.play_selected)

    def load_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.playlist = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.mp3')]
            self.playlist_box.delete(0, tk.END)
            for track in self.playlist:
                self.playlist_box.insert(tk.END, os.path.basename(track))
            if self.playlist:
                self.current_track = 0
                self.track_label.config(text=os.path.basename(self.playlist[self.current_track]))

    def play_music(self):
        if not self.playlist:
            return

        if self.paused:
            mixer.music.unpause()
            self.paused = False
            return

        if not self.stopped:
            mixer.music.stop()

        mixer.music.load(self.playlist[self.current_track])
        mixer.music.play()
        self.stopped = False
        self.track_label.config(text=os.path.basename(self.playlist[self.current_track]))
        self.playlist_box.selection_clear(0, tk.END)
        self.playlist_box.selection_set(self.current_track)
        self.playlist_box.activate(self.current_track)

    def pause_music(self):
        if not self.stopped and not self.paused:
            mixer.music.pause()
            self.paused = True

    def stop_music(self):
        mixer.music.stop()
        self.stopped = True
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

    def play_selected(self, event):
        if self.playlist_box.curselection():
            self.current_track = self.playlist_box.curselection()[0]
            self.play_music()

    def set_volume(self, volume):
        mixer.music.set_volume(float(volume) / 100)

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()
