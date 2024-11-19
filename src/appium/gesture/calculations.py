import logging

from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)

from appium.webdriver.webdriver import WebDriver
from appium.webdriver.webelement import WebElement

from .exceptions import ViewportError

logger = logging.getLogger(__name__)


def calculate_boundaries_and_scrollable_area(driver: WebDriver, **kwargs: any) -> tuple[dict, dict]:
    """
    Calculate and return scrolling boundaries and scrollable area based on crop factors.

    Returns:
        tuple: A tuple containing two dictionaries:
            - boundaries: Dictionary with upper, lower, left, and right bounds
            - scrollable_area: Dictionary with x and y dimensions

    """
    viewport_width, viewport_height = retrieve_viewport_dimensions(driver)
    crop_factors = {
        "upper_cf": kwargs.get("upper_cf", 0.20),
        "lower_cf": kwargs.get("lower_cf", 0.90),
        "left_cf": kwargs.get("left_cf", 0.10),
        "right_cf": kwargs.get("right_cf", 0.90),
    }
    boundaries = {
        "upper": int(viewport_height * crop_factors["upper_cf"]),
        "lower": int(viewport_height * crop_factors["lower_cf"]),
        "left": int(viewport_width * crop_factors["left_cf"]),
        "right": int(viewport_width * crop_factors["right_cf"]),
    }
    scrollable_area = {
        "x": boundaries["right"] - boundaries["left"],
        "y": boundaries["lower"] - boundaries["upper"],
    }

    return crop_factors, boundaries, scrollable_area


def _get_element_coordinates(element: WebElement) -> tuple[int, int, int, int]:
    """
    Get the location and size of an element.

    Args:
        element: The WebElement to calculate points for.

    Returns:
        A tuple containing x, y, width, and height of the element.

    Raises:
        ValueError: If the element dimensions are invalid.
    """
    x, y = element.location["x"], element.location["y"]
    width, height = element.size["width"], element.size["height"]

    if width <= 0 or height <= 0:
        msg = "Invalid element dimensions"
        raise ValueError(msg)

    return x, y, width, height


def calculate_element_points(element: WebElement) -> dict[str, tuple[int, int]]:
    """
    Calculate various points on an element.

    Args:
        element: The WebElement to calculate points for.

    Returns:
        A dictionary containing coordinates of various points on the element.

    Raises:
        ValueError: If the element dimensions are invalid.
    """
    try:
        x, y, width, height = _get_element_coordinates(element)

        return {
            "top_left": (x, y),
            "top_mid": (x + width // 2, y),
            "top_right": (x + width, y),
            "left_mid": (x, y + height // 2),
            "mid": (x + width // 2, y + height // 2),
            "right_mid": (x + width, y + height // 2),
            "bottom_left": (x, y + height),
            "bottom_mid": (x + width // 2, y + height),
            "bottom_right": (x + width, y + height),
        }
    except ValueError as e:
        msg = f"Failed to calculate element points: {str(e)}"
        logger.error(msg)
        raise


def retrieve_element_location(element: WebElement) -> tuple[int, int]:
    """
    Retrieve the location of an element.

    Args:
        locator_method: The method to locate the element (e.g., AppiumBy.XPATH).
        locator_value: The value to use with the locator method.

    Returns:
        A tuple containing the x and y coordinates of the element.
    """
    try:
        return element.location["x"], element.location["y"]
    except TimeoutException as e:
        msg = f"Element not found: {str(e)}"
        logger.error(msg)
        raise NoSuchElementException(msg) from e


def retrieve_viewport_dimensions(driver: WebDriver) -> tuple[int, int] | None:
    """
    Retrieve the viewport dimensions from the driver.

    Returns:
        A tuple of (width, height) or None if dimensions couldn't be retrieved.
    """
    try:
        viewport = driver.get_window_size()
        if viewport is None:
            msg = "Failed to retrieve viewport dimensions"
            raise ViewportError(msg)
        return viewport["width"], viewport["height"]
    except WebDriverException as e:
        msg = f"Failed to get viewport dimensions: {str(e)}"
        logger.error(msg)
        raise ViewportError(msg) from e
