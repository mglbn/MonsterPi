from kivy.app import App
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.animation import Animation


class LogoutButton(Button):
    """Button mit animiertem Fortschrittsbalken von links nach rechts"""
    
    progress = NumericProperty(0)  # 0 = leer, 1 = voll
    duration = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.duration = kwargs.pop("duration")
        self.anim = Animation(progress=1, duration= self.duration)
        self.radius = [dp(12)]
        self.background_color = (0, 0, 0, 0)  # Transparenter Hintergrund
        self.background_normal = ''

        
        
        # Initialisiere Canvas-Elemente
        with self.canvas.before:
            # Hintergrundfarbe 
            self.bg_color = Color(.05, .05, .05, 1)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius= self.radius)

             # Fortschrittsfarbe (z.B. rot)
            self.fill_color = Color(0.4, 0.1, 0.1, 1)
            self.fill_rect = RoundedRectangle(
                pos=self.pos,
                size=(0, self.height),
                radius= self.radius
            )

        App.get_running_app().ev.bind(
            on_timer_reset=self.on_timer_reset
        )
        
        # Binde Updates
        self.bind(
            pos=self._update_canvas, 
            size=self._update_canvas,
            progress=self._update_progress
        )

    def on_timer_reset(self, *args, **kwargs):
        self.reset()
        self.start_Animation()

    def on_release(self):
        App.get_running_app().ev.dispatch('on_logout')
        
    def _update_canvas(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _update_progress(self, *args):
        self.fill_rect.pos = self.pos
        self.fill_rect.size = (self.width * self.progress, self.height)

    def start_Animation(self):
        self.anim.start(self)

    def reset(self):
        self.anim.cancel(widget=self)
        self.progress= 0




