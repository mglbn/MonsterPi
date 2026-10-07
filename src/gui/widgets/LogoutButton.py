from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import ObjectProperty


class LogoutButton(Button):
    """Abmelde-Button mit Fortschrittsbalken, gebunden an SessionViewModel.logout_progress."""

    session = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.radius = [dp(12)]
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''

        with self.canvas.before:
            self.bg_color = Color(.05, .05, .05, 1)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
            self.fill_color = Color(0.4, 0.1, 0.1, 1)
            self.fill_rect = RoundedRectangle(
                pos=self.pos,
                size=(0, self.height),
                radius=self.radius
            )

        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def on_session(self, instance, session):
        session.bind(logout_progress=self._update_progress)
        self._update_progress()

    def _update_canvas(self, *_):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self._update_progress()

    def _update_progress(self, *_):
        if self.session is None:
            return
        self.fill_rect.pos = self.pos
        self.fill_rect.size = (self.width * self.session.logout_progress, self.height)
