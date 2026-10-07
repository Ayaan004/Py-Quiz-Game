"""Sound manager for playing game audio feedback in non-blocking threads."""
import threading
import sys
import time

class SoundManager:
    """Manages audio feedback for quiz actions with mute toggle."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundManager, cls).__new__(cls)
            cls._instance.enabled = True
        return cls._instance

    def toggle(self) -> bool:
        """Toggle sound on/off. Returns new status."""
        self.enabled = not self.enabled
        return self.enabled

    def _play_async(self, target_func, *args):
        """Runs the sound function in a daemon thread so GUI never lags."""
        if not self.enabled or sys.platform != "win32":
            return
        thread = threading.Thread(target=target_func, args=args, daemon=True)
        thread.start()

    def play_correct(self):
        """Happy ascending chime for correct answer."""
        def _play():
            try:
                import winsound
                # C5 -> E5 -> G5
                winsound.Beep(523, 110)
                time.sleep(0.02)
                winsound.Beep(659, 110)
                time.sleep(0.02)
                winsound.Beep(784, 180)
            except Exception:
                pass
        self._play_async(_play)

    def play_wrong(self):
        """Low descending buzzer for incorrect answer."""
        def _play():
            try:
                import winsound
                # E3 -> C3
                winsound.Beep(260, 160)
                time.sleep(0.03)
                winsound.Beep(196, 260)
            except Exception:
                pass
        self._play_async(_play)

    def play_tick(self):
        """Short tick for timer warning (low volume quick click)."""
        def _play():
            try:
                import winsound
                winsound.Beep(950, 35)
            except Exception:
                pass
        self._play_async(_play)

    def play_lifeline(self):
        """Mystical ascending blip when activating lifeline."""
        def _play():
            try:
                import winsound
                winsound.Beep(880, 80)
                time.sleep(0.02)
                winsound.Beep(1175, 120)
            except Exception:
                pass
        self._play_async(_play)

    def play_complete(self):
        """Celebratory fanfare when quiz is finished."""
        def _play():
            try:
                import winsound
                melody = [(523, 120), (659, 120), (784, 140), (1046, 320)]
                for freq, dur in melody:
                    winsound.Beep(freq, dur)
                    time.sleep(0.03)
            except Exception:
                pass
        self._play_async(_play)

# Global singleton helper
sound_fx = SoundManager()
