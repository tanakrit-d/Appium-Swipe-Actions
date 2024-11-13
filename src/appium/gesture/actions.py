import logging
from enum import Enum
from typing import Optional

from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.support import expected_conditions as Conditions
from selenium.webdriver.support.wait import WebDriverWait

from appium.webdriver.common.appiumby import AppiumBy

from .exceptions import (
    DragDropError,
    ElementInteractionError,
    ElementNotInViewError,
    InvalidGestureError,
    SwipeError,
    ViewportError,
    ZoomError,
)

logger = logging.getLogger(__name__)


class Direction(Enum):
    """
    Direction of the swipe action.
    """

    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    IN = "in"
    OUT = "out"


class SeekDirection(Enum):
    """
    Direction in which to seek for an element.
    """

    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


class GestureActions:
    """
    A class for enhanced swiping and scrolling functionality in Appium.
    """

    def __init__(self, driver, **kwargs):
        """
        Initialize the GestureActions object.

        Args:
            driver: The Appium driver instance.
            **kwargs: Optional keyword arguments for customising crop factors, element probe attempts, and probe timeout.
        """
        self.driver = driver
        self.probe_attempts = kwargs.get("probe_attempts", 5)
        self.timeout = kwargs.get("timeout", 0.25)

        try:
            self.viewport_width, self.viewport_height = (
                self._retrieve_viewport_dimensions()
            )
            if not self.viewport_width or not self.viewport_height:
                raise ViewportError("Could not retrieve valid viewport dimensions")

            self.viewport_x_mid_point = self.viewport_width // 2
            self.viewport_y_mid_point = self.viewport_height // 2

            self.crop_factors = {
                "upper_cf": kwargs.get("upper_cf", 0.20),
                "lower_cf": kwargs.get("lower_cf", 0.90),
                "left_cf": kwargs.get("left_cf", 0.10),
                "right_cf": kwargs.get("right_cf", 0.90),
            }

            self._set_boundaries_and_scrollable_area()

        except Exception as e:
            msg = f"Failed to initialize GestureActions: {str(e)}"
            logger.error(msg)
            raise ViewportError(msg) from e

    def _retrieve_viewport_dimensions(self) -> Optional[tuple[int, int]]:
        """
        Retrieve the viewport dimensions from the driver.

        Returns:
            A tuple of (width, height) or None if dimensions couldn't be retrieved.
        """
        try:
            viewport = self.driver.get_window_size()
            if viewport is None:
                raise ViewportError("Failed to retrieve viewport dimensions")
            return viewport["width"], viewport["height"]
        except WebDriverException as e:
            msg = f"Failed to get viewport dimensions: {str(e)}"
            logger.error(msg)
            raise ViewportError(msg) from e

    def _set_boundaries_and_scrollable_area(self):
        """
        Calculate scrolling boundaries and scrollable area based on crop factors.
        """
        self.bounds = {
            "upper": int(self.viewport_height * self.crop_factors["upper_cf"]),
            "lower": int(self.viewport_height * self.crop_factors["lower_cf"]),
            "left": int(self.viewport_width * self.crop_factors["left_cf"]),
            "right": int(self.viewport_width * self.crop_factors["right_cf"]),
        }

        self.scrollable_area = {
            "x": self.bounds["right"] - self.bounds["left"],
            "y": self.bounds["lower"] - self.bounds["upper"],
        }

    def _create_action(self) -> ActionChains:
        """
        Create and return an ActionChains object for touch interactions.

        Returns:
            An ActionChains object configured for touch input.
        """
        try:
            action = ActionChains(self.driver)
            action.w3c_actions = ActionBuilder(
                self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch")
            )
            return action
        except Exception as e:
            msg = f"Failed to create action chains: {str(e)}"
            logger.error(msg)
            raise InvalidGestureError(msg) from e

    def _calculate_element_points(self, element):
        """
        Calculate various points on an element.

        Args:
            element: The WebElement to calculate points for.

        Returns:
            A dictionary containing coordinates of various points on the element.
        """
        try:
            x, y = element.location["x"], element.location["y"]
            width, height = element.size["width"], element.size["height"]

            if width <= 0 or height <= 0:
                raise ElementInteractionError("Invalid element dimensions")

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
        except Exception as e:
            msg = f"Failed to calculate element points: {str(e)}"
            logger.error(msg)
            raise ElementInteractionError(msg) from e

    def _retrieve_element_location(
        self, locator_method: AppiumBy, locator_value: str
    ) -> tuple[int, int]:
        """
        Retrieve the location of an element.

        Args:
            locator_method: The method to locate the element (e.g., AppiumBy.XPATH).
            locator_value: The value to use with the locator method.

        Returns:
            A tuple containing the x and y coordinates of the element.
        """
        element = WebDriverWait(self.driver, self.timeout).until(
            Conditions.presence_of_element_located((locator_method, locator_value))
        )
        return element.location["x"], element.location["y"]

    def _probe_for_element(self, locator_method: AppiumBy, locator_value: str) -> bool:
        """
        Check if an element is within the viewport.
        Only necessary if the element is not yet loaded into the DOM, or if device context is NATIVE.
        This is because the library cannot swipe an element into view if it cannot initially locate it.
        """
        try:
            self._retrieve_element_location(locator_method, locator_value)
            return True
        except (NoSuchElementException, TimeoutException):
            return False

    def swipe_up(self):
        """Perform a full upward swipe of the calculated viewport."""
        action = self._create_action()
        self.perform_navigation_full_y(
            action, self.bounds["lower"], self.bounds["upper"]
        )

    def swipe_down(self):
        """Perform a full downward swipe of the calculated viewport."""
        action = self._create_action()
        self.perform_navigation_full_y(
            action, self.bounds["upper"], self.bounds["lower"]
        )

    def swipe_left(self):
        """Perform a full leftward swipe of the calculated viewport."""
        action = self._create_action()
        self.perform_navigation_full_x(
            action, self.bounds["right"], self.bounds["left"]
        )

    def swipe_right(self):
        """Perform a full rightward swipe of the calculated viewport."""
        action = self._create_action()
        self.perform_navigation_full_x(
            action, self.bounds["left"], self.bounds["right"]
        )

    def swipe_previous(self):
        """Perform a complete swipe from the left-edge of the viewport, simulating a 'previous page' type swipe."""
        action = self._create_action()
        self.perform_navigation_full_x(action, 0, self.viewport_width)

    def swipe_next(self):
        """Perform a complete swipe from the right-edge of the viewport, simulating a 'next page' type swipe."""
        action = self._create_action()
        self.perform_navigation_full_x(action, self.viewport_width, 0)

    def swipe_on_element(
        self, locator_method: AppiumBy, locator_value: str, direction: Direction
    ):
        """
        Swipe on a specific element in the given direction.

        Args:
            locator_method: The method to locate the element (e.g., AppiumBy.XPATH).
            locator_value: The value to use with the locator method.
            direction: The direction to swipe (UP, DOWN, LEFT, or RIGHT).
        """
        action = self._create_action()
        element = self.driver.find_element(by=locator_method, value=locator_value)

        element_points = self._calculate_element_points(element)

        match direction:
            case Direction.UP:
                self.perform_navigation_on_element(
                    action, element_points["bottom_mid"], element_points["top_mid"]
                )
            case Direction.DOWN:
                self.perform_navigation_on_element(
                    action, element_points["top_mid"], element_points["bottom_mid"]
                )
            case Direction.RIGHT:
                self.perform_navigation_on_element(
                    action, element_points["left_mid"], element_points["right_mid"]
                )
            case Direction.LEFT:
                self.perform_navigation_on_element(
                    action, element_points["right_mid"], element_points["left_mid"]
                )

    def swipe_element_into_view(
        self, locator_method: AppiumBy, locator_value: str, direction: SeekDirection
    ):
        """
        Swipe to bring an element into view.
        The multipliers in `swipe_actions` method scale the percentage factor for swipe for the partial_percentage argument.

        Args:
            locator_method: The method to locate the element (e.g., AppiumBy.XPATH).
            locator_value: The value to use with the locator method.
            direction: The direction to search for the element (UP, DOWN, LEFT, or RIGHT).
        """
        try:
            action = self._create_action()

            if self._probe_for_element(locator_method, locator_value):
                element_x, element_y = self._retrieve_element_location(
                    locator_method, locator_value
                )

                if direction in [SeekDirection.UP, SeekDirection.DOWN]:
                    self._swipe_element_into_view_vertical(action, element_y, direction)
                elif direction in [SeekDirection.LEFT, SeekDirection.RIGHT]:
                    self._swipe_element_into_view_horizontal(
                        action, element_x, direction
                    )
            else:
                swipe_actions = {
                    SeekDirection.UP: lambda: self.perform_navigation_partial_y(
                        action,
                        self.bounds["upper"],
                        self.bounds["lower"],
                        self.scrollable_area["y"] * -0.4,
                    ),
                    SeekDirection.DOWN: lambda: self.perform_navigation_partial_y(
                        action,
                        self.bounds["lower"],
                        self.bounds["upper"],
                        self.scrollable_area["y"] * 0.4,
                    ),
                    SeekDirection.LEFT: lambda: self.perform_navigation_partial_x(
                        action,
                        self.bounds["left"],
                        self.bounds["right"],
                        self.scrollable_area["x"] * -0.2,
                    ),
                    SeekDirection.RIGHT: lambda: self.perform_navigation_partial_x(
                        action,
                        self.bounds["right"],
                        self.bounds["left"],
                        self.scrollable_area["x"] * 0.2,
                    ),
                }

                for _ in range(self.probe_attempts):
                    if self._probe_for_element(locator_method, locator_value):
                        return
                    swipe_actions[direction]()

                raise ElementNotInViewError(
                    f"Element not found after {self.probe_attempts} attempts"
                )

        except ElementNotInViewError:
            raise
        except Exception as e:
            msg = f"Failed to swipe element into view: {str(e)}"
            logger.error(msg)
            raise SwipeError(msg) from e

    def _swipe_element_into_view_vertical(
        self, action: ActionChains, element_y: int, direction: SeekDirection
    ):
        """
        Perform vertical swipes to bring an element into view.

        Args:
            action: The ActionChains object to use for swiping.
            element_y: The y-coordinate of the element to bring into view.
            The direction to search for the element (UP or DOWN).
        """
        distance_to_element = element_y - self.bounds["lower"]
        actions_total = distance_to_element / self.scrollable_area["y"]
        actions_complete = int(distance_to_element // self.scrollable_area["y"])
        actions_partial = int(
            self.scrollable_area["y"] * (actions_total - actions_complete)
        )

        if direction == SeekDirection.UP:
            start, end = self.bounds["upper"], self.bounds["lower"]
        else:
            start, end = self.bounds["lower"], self.bounds["upper"]

        if actions_total > 1:
            self.perform_navigation_full_y(action, start, end, actions_complete)
        if actions_partial > 50:
            self.perform_navigation_partial_y(action, start, end, actions_partial)

    def _swipe_element_into_view_horizontal(
        self, action: ActionChains, element_x: int, direction: Direction
    ):
        """
        Perform horizontal swipes to bring an element into view.

        Args:
            action: The ActionChains object to use for swiping.
            element_x: The x-coordinate of the element to bring into view.
            The direction to search for the element (LEFT or RIGHT)
        """
        distance_to_element = element_x - self.bounds["left"]
        actions_total = distance_to_element / self.scrollable_area["x"]
        actions_complete = int(distance_to_element // self.scrollable_area["x"])
        actions_partial = int(
            self.scrollable_area["x"] * (actions_total - actions_complete)
        )

        if direction == Direction.LEFT:
            start, end = self.bounds["right"], self.bounds["left"]
        else:
            start, end = self.bounds["left"], self.bounds["right"]

        if actions_total > 1:
            self.perform_navigation_full_x(action, start, end, actions_complete)
        if actions_partial > 50:
            self.perform_navigation_partial_x(action, start, end, actions_partial)

    def perform_navigation_full_y(
        self,
        action: ActionChains,
        initial_bound: int,
        final_bound: int,
        iterations: int = 1,
    ):
        """
        Perform full vertical navigation swipes.

        Args:
            action: The ActionChains object to use for swiping.
            initial_bound: The starting y-coordinate.
            final_bound: The ending y-coordinate.
            iterations: The number of times to perform the swipe (default is 1).
        """
        for _ in range(iterations):
            self._perform_swipe(
                action,
                (self.viewport_x_mid_point, initial_bound),
                (self.viewport_x_mid_point, final_bound),
            )
            action.perform()

    def perform_navigation_partial_y(
        self,
        action: ActionChains,
        initial_bound: int,
        final_bound: int,
        partial_percentage: int,
    ):
        """
        Perform a partial vertical navigation swipe.

        Args:
            action: The ActionChains object to use for swiping.
            initial_bound: The starting y-coordinate.
            partial_percentage: The percentage of the full swipe to perform.
        """
        self._perform_swipe(
            action,
            (self.viewport_x_mid_point, initial_bound),
            (self.viewport_x_mid_point, final_bound + partial_percentage),
        )
        action.perform()

    def perform_navigation_full_x(
        self,
        action: ActionChains,
        initial_bound: int,
        final_bound: int,
        iterations: int = 1,
    ):
        """
        Perform full horizontal navigation swipes.

        Args:
            action: The ActionChains object to use for swiping.
            initial_bound: The starting x-coordinate.
            final_bound: The ending x-coordinate.
            iterations: The number of times to perform the swipe (default is 1).
        """
        for _ in range(iterations):
            self._perform_swipe(
                action,
                (initial_bound, self.viewport_y_mid_point),
                (final_bound, self.viewport_y_mid_point),
            )
            action.perform()

    def perform_navigation_partial_x(
        self,
        action: ActionChains,
        initial_bound: int,
        final_bound: int,
        partial_percentage: int,
    ):
        """
        Perform a partial horizontal navigation swipe.

        Args:
            action: The ActionChains object to use for swiping.
            initial_bound: The starting x-coordinate.
            partial_percentage: The percentage of the full swipe to perform.
        """
        self._perform_swipe(
            action,
            (initial_bound, self.viewport_y_mid_point),
            (final_bound + partial_percentage, self.viewport_y_mid_point),
        )
        action.perform()

    def perform_navigation_on_element(
        self,
        action: ActionChains,
        initial_bound: tuple[int, int],
        final_bound: tuple[int, int],
    ):
        """
        Perform a navigation swipe on a specific element.

        Args:
            action: The ActionChains object to use for swiping.
            initial_bound: The starting coordinates (x, y).
            final_bound: The ending coordinates (x, y).
        """
        self._perform_swipe(action, initial_bound, final_bound)
        action.perform()

    def _perform_swipe(
        self, action: ActionChains, start: tuple[int, int], end: tuple[int, int]
    ):
        """
        Perform a swipe action from start to end coordinates.

        Args:
            action: The ActionChains object to use for swiping.
            start: The starting coordinates (x, y).
            end: The ending coordinates (x, y).
        """
        action.w3c_actions.pointer_action.move_to_location(*start)
        action.w3c_actions.pointer_action.pointer_down()
        action.w3c_actions.pointer_action.move_to_location(*end)
        action.w3c_actions.pointer_action.pause(0.5)
        action.w3c_actions.pointer_action.release()

    def double_tap(self, locator_method: AppiumBy, locator_value: str):
        """
        Perform a double tap on the specified element using its locator.
        """
        self._tap_on_element(locator_method, locator_value, iterations=2)

    def triple_tap(self, locator_method: AppiumBy, locator_value: str):
        """
        Perform a triple tap on the specified element using its locator.
        """
        self._tap_on_element(locator_method, locator_value, iterations=3)

    def long_press(
        self, locator_method: AppiumBy, locator_value: str, duration: float = 0.5
    ):
        """
        Perform a long press on the specified element using its locator.

        Android and iOS share a default duration of 0.5.
        """
        self._tap_on_element(locator_method, locator_value, duration=duration)

    def _tap_on_element(
        self,
        locator_method: AppiumBy,
        locator_value: str,
        duration: float = 0.1,
        iterations: int = 1,
    ):
        """
        Helper method to tap on a specified element a given number of times.

        Args:
            locator_method: The method to locate the element (e.g., AppiumBy.XPATH).
            locator_value: The value to use with the locator method.
            iterations: The number of times to perform the tap.
        """
        action = self._create_action()
        element = self.driver.find_element(by=locator_method, value=locator_value)
        element_points = self._calculate_element_points(element)
        for _ in range(iterations):
            action.w3c_actions.pointer_action.move_to_location(*element_points["mid"])
            action.w3c_actions.pointer_action.pointer_down()
            action.w3c_actions.pointer_action.pause(duration)
            action.w3c_actions.pointer_action.release()
        action.perform()

    def drag_and_drop(
        self,
        initial_locator_method: AppiumBy,
        initial_locator_value: str,
        final_locator_method: AppiumBy,
        final_locator_value: str,
        pause_duration: float = 1.0,
    ):
        """
        Perform a drag and drop action from the source element to the target element.

        This function only supports initial and final elements which are both visible within the viewport.

        Args:
            initial_locator_method: The method to locate the source element (e.g., AppiumBy.XPATH).
            initial_locator_value: The value to use with the source locator method.
            final_locator_method: The method to locate the target element (e.g., AppiumBy.XPATH).
            final_locator_method: The value to use with the target locator method.
            pause_duration: The duration to pause after pressing down on the source element (default is 1.0 seconds).
        """
        try:
            action = self._create_action()

            initial_element = self.driver.find_element(
                by=initial_locator_method, value=initial_locator_value
            )
            final_element = self.driver.find_element(
                by=final_locator_method, value=final_locator_value
            )

            initial_points = self._calculate_element_points(initial_element)
            final_points = self._calculate_element_points(final_element)

            self._drag_and_drop(
                action, initial_points["mid"], final_points["mid"], pause_duration
            )
            action.perform()

        except Exception as e:
            msg = f"Drag and drop operation failed: {str(e)}"
            logger.error(msg)
            raise DragDropError(msg) from e

    def _drag_and_drop(
        self,
        action: ActionChains,
        initial_point: tuple[int, int],
        final_point: tuple[int, int],
        pause_duration: float = 1.0,
    ):
        """
        Perform a drag and drop action from start to end points.

        Args:
            action: The ActionChains object used for performing the drag and drop action.
            initial_point: The starting coordinates (x, y) from which to drag.
            final_point: The ending coordinates (x, y) to which to drop.
            pause_duration: The duration to pause after pressing the pointer down.
        """
        action.w3c_actions.pointer_action.move_to_location(*initial_point)
        action.w3c_actions.pointer_action.pointer_down()
        action.w3c_actions.pointer_action.pause(pause_duration)
        action.w3c_actions.pointer_action.move_to_location(*final_point)
        action.w3c_actions.pointer_action.pause(pause_duration)
        action.w3c_actions.pointer_action.pointer_up()

    def zoom_in(
        self, locator_method: AppiumBy, locator_value: str, duration: float = 0.5
    ) -> bool:
        """
        Performs a pinch-to-zoom-in gesture on the specified element.

        Args:
            locator_method (AppiumBy): The method to locate the element
            locator_value (str): The locator value to find the element
            duration (float, optional): Duration of the zoom animation in seconds

        Returns:
            bool: True if zoom in action was successful, False otherwise
        """
        try:
            return self._perform_zoom(
                locator_method, locator_value, Direction.IN, duration
            )
        except Exception as e:
            msg = f"Failed to perform zoom in: {str(e)}"
            logger.error(msg)
            raise ZoomError(msg) from e

    def zoom_out(
        self, locator_method: AppiumBy, locator_value: str, duration: float = 0.5
    ) -> bool:
        """
        Performs a pinch-to-zoom-out gesture on the specified element.

        Args:
            locator_method (AppiumBy): The method to locate the element
            locator_value (str): The locator value to find the element
            duration (float, optional): Duration of the zoom animation in seconds

        Returns:
            bool: True if zoom out action was successful, False otherwise
        """
        try:
            return self._perform_zoom(
                locator_method, locator_value, Direction.OUT, duration
            )
        except Exception as e:
            msg = f"Failed to perform zoom out: {str(e)}"
            logger.error(msg)
            raise ZoomError(msg) from e

    def _perform_zoom(
        self,
        locator_method: AppiumBy,
        locator_value: str,
        direction: Direction,
        duration: float = 0.5,
    ) -> bool:
        """
        Performs a pinch-to-zoom gesture on the specified element.

        Args:
            locator_method (AppiumBy): The method to locate the element (e.g., ID, XPATH)
            locator_value (str): The locator value to find the element
            direction (Literal["in", "out"]): Direction of zoom - "in" for zoom in, "out" for zoom out
            duration (float, optional): Duration of the zoom animation in seconds. Defaults to 0.5

        Returns:
            bool: True if zoom action was successful, False otherwise

        Raises:
            NoSuchElementException: If the target element cannot be found
            ElementNotInteractableException: If the element is not interactable
        """
        try:
            action = ActionChains(self.driver)

            element = self.driver.find_element(by=locator_method, value=locator_value)
            if not element.is_displayed() or not element.is_enabled():
                raise ElementNotInteractableException("Element is not interactable")

            element_points = self._calculate_element_points(element)

            if direction == Direction.IN:
                pointer_a_start = element_points["mid"]
                pointer_b_start = element_points["mid"]
                pointer_a_end = self.bounds["upper"]
                pointer_b_end = self.bounds["lower"]
            elif direction == Direction.OUT:
                pointer_a_start = self.bounds["upper"]
                pointer_b_start = self.bounds["lower"]
                pointer_a_end = element_points["mid"]
                pointer_b_end = element_points["mid"]

            pointer_a = action.w3c_actions.add_pointer_input("touch", "pointer_a")
            pointer_b = action.w3c_actions.add_pointer_input("touch", "pointer_b")

            pointer_a.create_pointer_move(**pointer_a_start)
            pointer_b.create_pointer_move(**pointer_b_start)

            pointer_a.create_pointer_down()
            pointer_b.create_pointer_down()

            pointer_a.create_pause(duration * 0.1)
            pointer_b.create_pause(duration * 0.1)

            pointer_a.create_pointer_move(duration=duration, **pointer_a_end)
            pointer_b.create_pointer_move(duration=duration, **pointer_b_end)

            pointer_a.create_pointer_up()
            pointer_b.create_pointer_up()

            action.perform()
            return True

        except (NoSuchElementException, ElementNotInteractableException) as e:
            print(f"Failed to perform zoom {direction} action: {str(e)}")
            return False
