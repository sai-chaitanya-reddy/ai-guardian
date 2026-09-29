from typing import Callable, Optional
from loguru import logger


class ScreenshotGuard:
    def __init__(self, on_screenshot_attempt: Optional[Callable] = None):
        self.on_screenshot_attempt = on_screenshot_attempt
        self.is_sensitive = False
        self.is_active = False

    def activate(self):
        try:
            import keyboard
            keyboard.on_press_key("print screen", self._handle)
            self.is_active = True
            logger.info("Screenshot guard active")
        except Exception as e:
            logger.warning(f"Screenshot guard unavailable: {e}")

    def deactivate(self):
        try:
            import keyboard
            keyboard.unhook_all()
            self.is_active = False
        except Exception:
            pass

    def set_sensitive_mode(self, val: bool):
        self.is_sensitive = val

    def _handle(self, event):
        if self.is_sensitive and self.on_screenshot_attempt:
            self.on_screenshot_attempt(
                "PrintScreen",
                "Screenshot blocked: Sensitive content visible on screen",
            )
