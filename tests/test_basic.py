# pylint: disable=C0115,C0116,R0903

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from appium.webdriver.common.appiumby import AppiumBy
from src.appium.swipe.actions import Direction, SeekDirection, SwipeActions


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


@pytest.fixture(name="swipe_actions")
def swipe_actions(mock_driver):
    return SwipeActions(mock_driver)


def test_init(swipe_actions):
    assert swipe_actions.viewport_width == 1080
    assert swipe_actions.viewport_height == 2340
    assert swipe_actions.bounds["upper"] == 468
    assert swipe_actions.bounds["lower"] == 2106
    assert swipe_actions.bounds["left"] == 108
    assert swipe_actions.bounds["right"] == 972


def test_swipe_up(swipe_actions):
    swipe_actions.swipe_up()
    assert len(swipe_actions.driver.actions) > 0


def test_swipe_down(swipe_actions):
    swipe_actions.swipe_down()
    assert len(swipe_actions.driver.actions) > 0


def test_swipe_left(swipe_actions):
    swipe_actions.swipe_left()
    assert len(swipe_actions.driver.actions) > 0


def test_swipe_right(swipe_actions):
    swipe_actions.swipe_right()
    assert len(swipe_actions.driver.actions) > 0


def test_swipe_next(swipe_actions):
    swipe_actions.swipe_next()
    assert len(swipe_actions.driver.actions) > 0


def test_swipe_previous(swipe_actions):
    swipe_actions.swipe_previous()
    assert len(swipe_actions.driver.actions) > 0


def test_swipe_on_element(swipe_actions):
    swipe_actions.swipe_on_element(AppiumBy.XPATH, "//existing_element", Direction.UP)
    assert len(swipe_actions.driver.actions) > 0


def test_swipe_element_into_view_success(swipe_actions):
    swipe_actions.swipe_element_into_view(
        AppiumBy.XPATH, "//existing_element", SeekDirection.DOWN
    )
    assert len(swipe_actions.driver.actions) > 0


def test_swipe_element_into_view_not_found(swipe_actions):
    with pytest.raises(NoSuchElementException):
        swipe_actions.swipe_element_into_view(
            AppiumBy.XPATH, "//non_existing_element", SeekDirection.UP
        )


def test_retrieve_element_location(swipe_actions):
    x, y = swipe_actions.retrieve_element_location(AppiumBy.XPATH, "//existing_element")
    assert x == 100
    assert y == 200


def test_retrieve_element_location_not_found(swipe_actions):
    with pytest.raises((NoSuchElementException, TimeoutException)):
        swipe_actions.retrieve_element_location(
            AppiumBy.XPATH, "//non_existing_element"
        )
