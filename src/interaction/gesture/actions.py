import logging

from appium.webdriver.webdriver import WebDriver

from .drag_and_drop import DragAndDropGestures
from .pinch import PinchGestures
from .swipe import SwipeGestures

logger = logging.getLogger(__name__)


class GestureActions:
    """
    A class for enhanced gesture functionality in Appium.
    """

    def __init__(self, driver: WebDriver, platform: str) -> None:
        """
        Initialize the GestureActions object.

        Args:
            driver (WebDriver): The Appium driver instance.
            platform (str): The platform for which gestures are defined (e.g., 'android' or 'ios').

        """
        self._driver = self._validate_driver(driver)
        self._platform = self._validate_platform(platform)
        self._drag_drop: DragAndDropGestures | None = None
        self._pinch: PinchGestures | None = None
        self._swipe: SwipeGestures | None = None
    
    def _validate_driver(self, driver: WebDriver) -> WebDriver:
        """Validate the driver instance."""
        if not isinstance(driver, WebDriver):
            raise TypeError(f"Invalid driver type: '{type(driver).__name__}'. Platform must be of type 'WebDriver'.")
        
        return driver
    
    def _validate_platform(self, platform: str) -> str:
        """Validate and normalize the platform string."""
        if not isinstance(platform, str):
            raise ValueError(f"Invalid platform type: '{type(platform).__name__}'. Platform must be of type 'str'.")

        platform = platform.lower()

        if platform not in ['android', 'ios']:
            raise ValueError(f"Invalid platform: '{platform}'. Platform must be either 'ios' or 'android'.")
        
        return platform

    @property
    def drag_drop(self) -> "DragAndDropGestures":
        """Access drag-and-drop related gestures."""
        if self._drag_drop is None:
            self._drag_drop = DragAndDropGestures(self._driver, self._platform)
        return self._drag_drop

    @property
    def pinch(self) -> "PinchGestures":
        """Access pinch related gestures."""
        if self._pinch is None:
            self._pinch = PinchGestures(self._driver, self._platform)
        return self._pinch

    @property
    def swipe(self) -> "SwipeGestures":
        """Access swipe related gestures."""
        if self._swipe is None:
            self._swipe = SwipeGestures(self._driver, self._platform)
        return self._swipe
