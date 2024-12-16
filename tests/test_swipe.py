import pytest
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.webelement import WebElement

from src.interaction.gesture.swipe import SwipeGestures


class TestSwipeActions:
    @pytest.fixture
    def mock_driver(self, mocker):
        """Create a mock WebDriver with mocked window size."""
        mock_driver = mocker.Mock(spec=WebDriver)
        mock_driver.get_window_size.return_value = {
            "width": 1280,
            "height": 2856,
        }
        return mock_driver

    @pytest.mark.parametrize("platform", [
        "ios", 
        "iOS", 
        "android", 
        "Android"
    ])
    def test_platform_validation_valid_inputs(self, mock_driver, platform):
        """Test platform validation with valid inputs."""
        swipe_actions = SwipeGestures(mock_driver, platform)
        assert swipe_actions._platform == platform.lower()
        assert swipe_actions._viewport_width == 1280
        assert swipe_actions._viewport_height == 2856

    @pytest.mark.parametrize("direction", [
        "up",
        "down",
        "left",
        "right",
    ])
    def test_swipe_valid_inputs(self, mock_driver, mocker, direction):
        """Test swipe method with valid inputs."""
        swipe_actions = SwipeGestures(mock_driver, "android")
        
        mock_perform_swipe = mocker.patch.object(swipe_actions, '_perform_swipe', autospec=True)

        getattr(swipe_actions, direction)()
        
        mock_perform_swipe.assert_called_once()

# on_element tests

# element_into_view tests