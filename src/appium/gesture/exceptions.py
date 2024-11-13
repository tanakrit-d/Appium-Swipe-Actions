from selenium.common.exceptions import WebDriverException


class GestureError(WebDriverException):
    """Base exception for all gesture-related errors."""

    pass


class ViewportError(GestureError):
    """Raised when there are issues with viewport dimensions or calculations."""

    pass


class ElementInteractionError(GestureError):
    """Raised when interaction with an element fails."""

    pass


class SwipeError(GestureError):
    """Raised when a swipe action fails."""

    pass


class ElementNotInViewError(GestureError):
    """Raised when an element cannot be brought into view after maximum attempts."""

    pass


class InvalidGestureError(GestureError):
    """Raised when an invalid gesture is attempted."""

    pass


class ZoomError(GestureError):
    """Raised when a zoom operation fails."""

    pass


class DragDropError(GestureError):
    """Raised when a drag and drop operation fails."""

    pass
