import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from appium.webdriver.common.appiumby import AppiumBy
from src.appium.gesture.actions import Direction, GestureActions, SeekDirection
from src.appium.gesture.exceptions import ElementNotInViewError


class MockElement:
    def __init__(self, location, size):
        self.location = location
        self.size = size


@pytest.fixture(name="mock_driver")
def mock_driver():
    class MockDriver:
        def __init__(self):
            self.actions = []

        def get_window_size(self):
            return {"width": 1080, "height": 2340}

        def find_element(self, by, value):
            if by == AppiumBy.XPATH and value == "//existing_element":
                return MockElement({"x": 100, "y": 200}, {"width": 200, "height": 100})
            raise NoSuchElementException

        def execute(self, driver_command, params=None):
            self.actions.append((driver_command, params))

    return MockDriver()


@pytest.fixture(name="gesture_actions")
def gesture_actions(mock_driver):
    return GestureActions(mock_driver)


def test_init(gesture_actions):
    assert gesture_actions.viewport_width == 1080
    assert gesture_actions.viewport_height == 2340
    assert gesture_actions.bounds["upper"] == 468
    assert gesture_actions.bounds["lower"] == 2106
    assert gesture_actions.bounds["left"] == 108
    assert gesture_actions.bounds["right"] == 972


def test_swipe_up(gesture_actions):
    gesture_actions.swipe_up()
    assert len(gesture_actions.driver.actions) > 0


def test_swipe_down(gesture_actions):
    gesture_actions.swipe_down()
    assert len(gesture_actions.driver.actions) > 0


def test_swipe_left(gesture_actions):
    gesture_actions.swipe_left()
    assert len(gesture_actions.driver.actions) > 0


def test_swipe_right(gesture_actions):
    gesture_actions.swipe_right()
    assert len(gesture_actions.driver.actions) > 0


def test_swipe_next(gesture_actions):
    gesture_actions.swipe_next()
    assert len(gesture_actions.driver.actions) > 0


def test_swipe_previous(gesture_actions):
    gesture_actions.swipe_previous()
    assert len(gesture_actions.driver.actions) > 0


def test_swipe_on_element(gesture_actions):
    gesture_actions.swipe_on_element(AppiumBy.XPATH, "//existing_element", Direction.UP)
    assert len(gesture_actions.driver.actions) > 0


def test_swipe_element_into_view_success(gesture_actions):
    gesture_actions.swipe_element_into_view(
        AppiumBy.XPATH, "//existing_element", SeekDirection.DOWN
    )
    assert len(gesture_actions.driver.actions) > 0


def test_swipe_element_not_in_view(gesture_actions):
    with pytest.raises(ElementNotInViewError):
        gesture_actions.swipe_element_into_view(
            AppiumBy.XPATH, "//non_existing_element", SeekDirection.UP
        )


def test_retrieve_element_location(gesture_actions):
    x, y = gesture_actions._retrieve_element_location(AppiumBy.XPATH, "//existing_element")
    assert x == 100
    assert y == 200


def test_retrieve_element_location_not_found(gesture_actions):
    with pytest.raises((NoSuchElementException, TimeoutException)):
        gesture_actions._retrieve_element_location(
            AppiumBy.XPATH, "//non_existing_element"
        )
