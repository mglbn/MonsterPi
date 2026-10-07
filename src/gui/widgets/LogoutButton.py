from kivy.graphics import Color, RoundedRectangle
from kivy.properties import ObjectProperty
from gui.widgets.RoundedButton import RoundedButton


class LogoutButton(RoundedButton):
    """Abmelde-Button mit Fortschrittsbalken, gebunden an SessionViewModel.logout_progress."""

    session = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            self.fill_color = Color(0.4, 0.1, 0.1, 1)
            self.fill_rect = RoundedRectangle(
                pos=self.pos,
                size=(0, self.height),
                radius=self.radius
            )

    def on_session(self, instance, session):
        session.bind(logout_progress=self._update_progress)
        self._update_progress()

    def _update_canvas(self, *_):
        super()._update_canvas()
        self._update_progress()

    def _update_progress(self, *_):
        if self.session is None:
            return
        self.fill_rect.pos = self.pos
        self.fill_rect.size = (self.width * self.session.logout_progress, self.height)
