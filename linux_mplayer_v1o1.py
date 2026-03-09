#!/usr/bin/env python3

# linux_mplayer1.py
# Mon, 09-03-2026
# @author: Ankur Saxena
# A Linux-based music player app written in python

# linux_mplayer_v2.py
# Enhanced version with playlist, volume, shuffle, repeat, drag-drop

import sys
import os
import time
import random
import vlc

from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QFileDialog,
    QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QListWidget, QListWidgetItem
)

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut, QPalette, QBrush, QPixmap


class MusicPlayer(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Krithi Linux Music Player")
        self.setGeometry(300, 200, 1000, 500)

        self.setAcceptDrops(True)

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        self.playlist = []
        self.index = 0

        self.shuffle = False
        self.repeat = False

        self.build_ui()
        self.setup_shortcuts()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(500)

    def build_ui(self):

        main_layout = QHBoxLayout()

        # LEFT SIDE (PLAYER AREA)
        left_layout = QVBoxLayout()

        top_bar = QHBoxLayout()

        self.browse_btn = QPushButton("Browse Music")
        self.browse_btn.clicked.connect(self.open_files)

        self.wallpaper_btn = QPushButton("Set Wallpaper")
        self.wallpaper_btn.clicked.connect(self.set_wallpaper)

        top_bar.addWidget(self.browse_btn)
        top_bar.addWidget(self.wallpaper_btn)
        top_bar.addStretch()

        left_layout.addLayout(top_bar)

        self.song_label = QLabel("No music loaded")
        self.song_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        left_layout.addWidget(self.song_label)

        # Timeline
        timeline_layout = QHBoxLayout()

        self.current_time = QLabel("0:00")

        self.timeline = QSlider(Qt.Orientation.Horizontal)
        self.timeline.setRange(0, 1000)
        self.timeline.sliderMoved.connect(self.seek)

        self.total_time = QLabel("0:00")

        timeline_layout.addWidget(self.current_time)
        timeline_layout.addWidget(self.timeline)
        timeline_layout.addWidget(self.total_time)

        left_layout.addLayout(timeline_layout)

        # Controls
        controls = QHBoxLayout()

        self.prev_btn = QPushButton("Prev")
        self.play_btn = QPushButton("Play/Pause")
        self.next_btn = QPushButton("Next")

        self.prev_btn.clicked.connect(self.prev_song)
        self.play_btn.clicked.connect(self.play_pause)
        self.next_btn.clicked.connect(self.next_song)

        controls.addWidget(self.prev_btn)
        controls.addWidget(self.play_btn)
        controls.addWidget(self.next_btn)

        left_layout.addLayout(controls)

        # Volume
        volume_layout = QHBoxLayout()

        volume_label = QLabel("Volume")

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.valueChanged.connect(self.change_volume)

        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)

        left_layout.addLayout(volume_layout)

        # Shuffle Repeat
        mode_layout = QHBoxLayout()

        self.shuffle_btn = QPushButton("Shuffle OFF")
        self.repeat_btn = QPushButton("Repeat OFF")

        self.shuffle_btn.clicked.connect(self.toggle_shuffle)
        self.repeat_btn.clicked.connect(self.toggle_repeat)

        mode_layout.addWidget(self.shuffle_btn)
        mode_layout.addWidget(self.repeat_btn)

        left_layout.addLayout(mode_layout)

        main_layout.addLayout(left_layout)

        # RIGHT SIDE PLAYLIST
        playlist_layout = QVBoxLayout()

        playlist_label = QLabel("Playlist")

        self.playlist_widget = QListWidget()
        self.playlist_widget.itemDoubleClicked.connect(self.play_selected_song)

        playlist_layout.addWidget(playlist_label)
        playlist_layout.addWidget(self.playlist_widget)

        main_layout.addLayout(playlist_layout)

        self.setLayout(main_layout)

    def setup_shortcuts(self):

        open_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        open_shortcut.activated.connect(self.open_files)

        space_shortcut = QShortcut(QKeySequence("Space"), self)
        space_shortcut.activated.connect(self.play_pause)

    def open_files(self):

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Music Files",
            "",
            "Audio Files (*.mp3 *.wav *.flac *.aac *.m4a *.wma *.ogg *.mid *.midi *.alac)"
        )

        if files:
            for f in files:
                self.playlist.append(f)
                self.playlist_widget.addItem(os.path.basename(f))

            if not self.player.is_playing():
                self.index = 0
                self.play_song()

    def play_song(self):

        if self.index < len(self.playlist):

            media = self.instance.media_new(self.playlist[self.index])
            self.player.set_media(media)
            self.player.play()

            filename = os.path.basename(self.playlist[self.index])
            self.song_label.setText(filename)

            self.playlist_widget.setCurrentRow(self.index)

    def play_pause(self):

        if self.player.is_playing():
            self.player.pause()
        else:
            self.player.play()

    def next_song(self):

        if self.shuffle:
            self.index = random.randint(0, len(self.playlist)-1)
        else:
            self.index += 1

        if self.index >= len(self.playlist):

            if self.repeat:
                self.index = 0
            else:
                return

        time.sleep(0.2)
        self.play_song()

    def prev_song(self):

        if self.index > 0:
            self.index -= 1
            self.play_song()

    def play_selected_song(self, item):

        self.index = self.playlist_widget.row(item)
        self.play_song()

    def change_volume(self, value):

        self.player.audio_set_volume(value)

    def toggle_shuffle(self):

        self.shuffle = not self.shuffle

        if self.shuffle:
            self.shuffle_btn.setText("Shuffle ON")
        else:
            self.shuffle_btn.setText("Shuffle OFF")

    def toggle_repeat(self):

        self.repeat = not self.repeat

        if self.repeat:
            self.repeat_btn.setText("Repeat ON")
        else:
            self.repeat_btn.setText("Repeat OFF")

    def seek(self, position):

        if self.player.get_length() > 0:
            self.player.set_position(position / 1000.0)

    def update_ui(self):

        if self.player is None:
            return

        length = self.player.get_length()
        pos = self.player.get_time()

        if length > 0 and pos >= 0:

            slider_value = int((pos * 1000) / length)

            if slider_value <= 1000:
                self.timeline.blockSignals(True)
                self.timeline.setValue(slider_value)
                self.timeline.blockSignals(False)

            self.current_time.setText(self.format_time(pos))
            self.total_time.setText(self.format_time(length))

        if self.player.get_state() == vlc.State.Ended:
            self.next_song()

    def format_time(self, ms):

        seconds = int(ms / 1000)

        m = seconds // 60
        s = seconds % 60

        return f"{m}:{s:02d}"

    def set_wallpaper(self):

        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )

        if file:

            palette = QPalette()
            palette.setBrush(QPalette.ColorRole.Window, QBrush(QPixmap(file)))

            self.setPalette(palette)

    # Drag and Drop Support
    def dragEnterEvent(self, event):

        if event.mimeData().hasUrls():
            event.accept()

    def dropEvent(self, event):

        for url in event.mimeData().urls():

            path = url.toLocalFile()

            if os.path.isfile(path):

                self.playlist.append(path)
                self.playlist_widget.addItem(os.path.basename(path))


app = QApplication(sys.argv)

player = MusicPlayer()
player.show()

sys.exit(app.exec())
