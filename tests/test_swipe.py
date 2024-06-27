# pylint: disable=C0114,C0116,W0212

from unittest.mock import Mock, patch
import pytest
from appium.webdriver.common.appiumby import AppiumBy
from src.swipe_utilities.swipe import SwipeActions, Direction

@pytest.fixture(name="mock_driver")
def mock_driver():
    driver = Mock()
    driver.get_window_size.return_value = {"width": 1080, "height": 2400}
    return driver

@pytest.fixture(name="swipe_actions_instance")
@patch.object(SwipeActions, '_retrieve_viewport_dimensions', return_value=(1080, 2400))
def swipe_actions_instance(mock_driver):
    return SwipeActions(mock_driver)

def test_initialization(swipe_actions_instance):
    assert swipe_actions_instance.viewport_width == 1080
    assert swipe_actions_instance.viewport_height == 2400
    assert swipe_actions_instance.viewport_x_mid_point == 540
    assert swipe_actions_instance.viewport_y_mid_point == 1200

def test_custom_crop_factors():
    driver = Mock()
    driver.get_window_size.return_value = {"width": 1080, "height": 2400}
    es = SwipeActions(driver, upper_cf=0.1, lower_cf=0.9, left_cf=0.1, right_cf=0.9)
    assert es.bounds["upper"] == 240
    assert es.bounds["lower"] == 2160
    assert es.bounds["left"] == 108
    assert es.bounds["right"] == 972

def test_swipe_up(swipe_actions_instance):
    with patch.object(swipe_actions_instance, 'perform_navigation_full_y') as mock_swipe:
        with patch.object(swipe_actions_instance, '_create_action', return_value="dummy_action"):
            swipe_actions_instance.swipe_up()
            mock_swipe.assert_called_once_with(
                swipe_actions_instance._create_action(),
                swipe_actions_instance.bounds["lower"],
                swipe_actions_instance.bounds["upper"]
            )

def test_swipe_down(swipe_actions_instance):
    with patch.object(swipe_actions_instance, 'perform_navigation_full_y') as mock_swipe:
        with patch.object(swipe_actions_instance, '_create_action', return_value="dummy_action"):
            swipe_actions_instance.swipe_down()
            mock_swipe.assert_called_once_with(
                swipe_actions_instance._create_action(),
                swipe_actions_instance.bounds["upper"],
                swipe_actions_instance.bounds["lower"]
            )

def test_swipe_left(swipe_actions_instance):
    with patch.object(swipe_actions_instance, 'perform_navigation_full_x') as mock_swipe:
        with patch.object(swipe_actions_instance, '_create_action', return_value="dummy_action"):
            swipe_actions_instance.swipe_left()
            mock_swipe.assert_called_once_with(
                swipe_actions_instance._create_action(),
                swipe_actions_instance.bounds["right"],
                swipe_actions_instance.bounds["left"]
            )

def test_swipe_right(swipe_actions_instance):
    with patch.object(swipe_actions_instance, 'perform_navigation_full_x') as mock_swipe:
        with patch.object(swipe_actions_instance, '_create_action', return_value="dummy_action"):
            swipe_actions_instance.swipe_right()
            mock_swipe.assert_called_once_with(
                swipe_actions_instance._create_action(),
                swipe_actions_instance.bounds["left"],
                swipe_actions_instance.bounds["right"]
            )

def test_swipe_next(swipe_actions_instance):
    with patch.object(swipe_actions_instance, 'perform_navigation_full_x') as mock_swipe:
        with patch.object(swipe_actions_instance, '_create_action', return_value="dummy_action"):
            swipe_actions_instance.swipe_next()
            mock_swipe.assert_called_once_with(
                swipe_actions_instance._create_action(),
                swipe_actions_instance.viewport_width,
                0
            )

def test_swipe_previous(swipe_actions_instance):
    with patch.object(swipe_actions_instance, 'perform_navigation_full_x') as mock_swipe:
        with patch.object(swipe_actions_instance, '_create_action', return_value="dummy_action"):
            swipe_actions_instance.swipe_previous()
            mock_swipe.assert_called_once_with(
                swipe_actions_instance._create_action(),
                0,
                swipe_actions_instance.viewport_width
            )

def test_swipe_on_element(swipe_actions_instance):
    mock_element = Mock()
    mock_element.location = {"x": 100, "y": 200}
    mock_element.size = {"width": 300, "height": 400}
    swipe_actions_instance.driver.find_element.return_value = mock_element

    with patch.object(swipe_actions_instance, 'perform_navigation_on_element') as mock_swipe:
        with patch.object(swipe_actions_instance, '_create_action', return_value="dummy_action"):
            swipe_actions_instance.swipe_on_element(AppiumBy.XPATH, "//some-xpath", Direction.UP)
            mock_swipe.assert_called_once_with(
                swipe_actions_instance._create_action(),
                (250, 600),  # bottom_mid
                (250, 200)   # top_mid
            )

def test_swipe_element_into_view(swipe_actions_instance):
    with patch.object(swipe_actions_instance, '_swipe_element_into_view_vertical') as mock_swipe:
        swipe_actions_instance.retrieve_element_location = Mock(return_value=(100, 3000))
        swipe_actions_instance.swipe_element_into_view(AppiumBy.XPATH, "//some-xpath", Direction.UP)
        mock_swipe.assert_called_once()

def test_perform_navigation_full_y(swipe_actions_instance):
    with patch.object(swipe_actions_instance, '_perform_swipe') as mock_swipe:
        action = swipe_actions_instance._create_action()
        swipe_actions_instance.perform_navigation_full_y(action, 2000, 1000, 2)
        assert mock_swipe.call_count == 2
        mock_swipe.assert_called_with(action, (540, 2000), (540, 1000))

def test_perform_navigation_partial_y(swipe_actions_instance):
    with patch.object(swipe_actions_instance, '_perform_swipe') as mock_swipe:
        action = swipe_actions_instance._create_action()
        swipe_actions_instance.perform_navigation_partial_y(action, 2000, 500)
        mock_swipe.assert_called_once_with(action, (540, 2000), (540, 2500))

def test_perform_navigation_full_x(swipe_actions_instance):
    with patch.object(swipe_actions_instance, '_perform_swipe') as mock_swipe:
        action = swipe_actions_instance._create_action()
        swipe_actions_instance.perform_navigation_full_x(action, 0, 1000, 2)
        assert mock_swipe.call_count == 2
        mock_swipe.assert_called_with(action, (0, 1200), (1000, 1200))

def test_perform_navigation_partial_x(swipe_actions_instance):
    with patch.object(swipe_actions_instance, '_perform_swipe') as mock_swipe:
        action = swipe_actions_instance._create_action()
        swipe_actions_instance.perform_navigation_partial_x(action, 0, 500)
        mock_swipe.assert_called_once_with(action, (0, 1200), (500, 1200))

def test_perform_swipe(swipe_actions_instance):
    mock_action = Mock()
    mock_action.w3c_actions.pointer_action.move_to_location = Mock()
    mock_action.w3c_actions.pointer_action.pointer_down = Mock()
    mock_action.w3c_actions.pointer_action.pause = Mock()
    mock_action.w3c_actions.pointer_action.release = Mock()
    mock_action.perform = Mock()

    with patch.object(swipe_actions_instance, '_create_action', return_value=mock_action):
        action = swipe_actions_instance._create_action()
        swipe_actions_instance._perform_swipe(action, (100, 200), (300, 400))

        action.w3c_actions.pointer_action.move_to_location.assert_any_call(100, 200)
        action.w3c_actions.pointer_action.pointer_down.assert_called_once()
        action.w3c_actions.pointer_action.move_to_location.assert_any_call(300, 400)
        action.w3c_actions.pointer_action.pause.assert_called_with(1)
        action.w3c_actions.pointer_action.release.assert_called_once()
        action.perform.assert_called_once()

def test_retrieve_element_location(swipe_actions_instance):
    mock_element = Mock()
    mock_element.location = {"x": 100, "y": 200}
    swipe_actions_instance.driver.find_element.return_value = mock_element
    result = swipe_actions_instance.retrieve_element_location(AppiumBy.XPATH, "//empty-xpath")
    assert result == (100, 200)
