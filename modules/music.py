import pygame
from .engine import *


class Music:
    def __init__(self, master, is_ambience=False):
        self.master = master
        if not is_ambience:
            master.music = self
        self.tracks = {
            "cave": "music/Music_Cave.ogg",
            "crash_site": "music/Music_Crash_Site.ogg",
            "plains": "music/Music_Plains.ogg",
            "main_menu": "music/Music_MainMenu.ogg"
        }
        self.stream = pygame.mixer.music
        self.is_ambience = is_ambience
        
        self.is_playing = False
        self.can_play = True

        self.is_loaded = False

        self.change_track_to = None
        self.current_track = None
        self.current_sound = None

        self.START_NEW_TRACK_TIMER = CustomTimer()

        self.START_NEW_TRACK_TIMER.start(500)
        self.change_track_to = "main_menu"

    def fadeout(self, time=2_000):
        if self.is_loaded:
            self.stream.fadeout(time)
            self.current_track = None

    def change_track(self, track_type):
        if track_type == self.current_track: return
        delay = 0
        if self.is_loaded:
            self.stream.fadeout(2_000)
            delay = 2_100
        self.START_NEW_TRACK_TIMER.start(delay)
        self.current_track = track_type
        self.change_track_to = track_type

    def process_events(self):

        if self.START_NEW_TRACK_TIMER.check():
            if self.is_ambience:
                self.current_sound = self.tracks[self.change_track_to]
            else:
                self.stream.load(self.tracks[self.change_track_to])
            self.play_stream(loops=-1, fade_ms=2_000, sound=self.current_sound)
            self.current_track = self.change_track_to
            self.change_track_to = None
            self.is_loaded = True

    def play_stream(self, loops=0, fade_ms=0, sound=None):

        if sound is None:
            self.stream.play(loops=loops, fade_ms=fade_ms)
        else:
            self.stream.play(sound, loops=loops, fade_ms=fade_ms)
    
    def run(self):

        self.can_play = not self.master.game.paused

        self.process_events()

        if not self.is_loaded: return

        if self.can_play and not self.is_playing:
            self.stream.unpause()
            self.is_playing = True

        elif not self.can_play and self.is_playing:
            self.stream.pause()
            self.is_playing = False


class Ambience(Music):

    def __init__(self, master):

        super().__init__(master, is_ambience=True)
        master.ambience = self

        self.START_NEW_TRACK_TIMER.stop()

        self.tracks["ambient_cave"] = pygame.mixer.Sound("music/Ambience_Cave.ogg")
        self.tracks["ambient_plains"] = pygame.mixer.Sound("music/Ambience_Plains.ogg")
        self.tracks["ambient_crash_site"] = pygame.mixer.Sound("music/Ambience_Crash_Site.ogg")

        r = pygame.mixer.set_reserved(1)
        print(F"{r} channels reserved")
        self.stream = pygame.mixer.find_channel()
        # self.change_track_to = "ambient_crash_site"
        # self.START_NEW_TRACK_TIMER.start(500)
