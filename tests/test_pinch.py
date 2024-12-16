import pytest
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.webelement import WebElement

from src.interaction.gesture.exceptions import ZoomError
from src.interaction.gesture.pinch import PinchGestures, PinchParameters


class TestPinchParameters:
    @pytest.mark.parametrize("percent_value", [
        0.0,
        0.5,
        1.0,
    ])
    def test_percent_valid_values(self, mocker, percent_value):
        """Test setting valid percent values."""
        mock_element = mocker.Mock(spec=WebElement)
        pinch_params = PinchParameters(mock_element, percent_value)
        assert pinch_params.percent == percent_value

    @pytest.mark.parametrize("invalid_percent", [
        -0.1,
        1.1,
        2.0,
    ])
    def test_percent_invalid_values(self, mocker, invalid_percent):
        """Test setting invalid percent values raises ValueError."""
        mock_element = mocker.Mock(spec=WebElement)
        with pytest.raises(ValueError, match="Percent must be between 0.0 and 1.0"):
            PinchParameters(mock_element, invalid_percent)

class TestPinchGestures:
    @pytest.fixture
    def mock_driver(self, mocker):
        """Create a mock WebDriver."""
        mock_driver = mocker.Mock(spec=WebDriver)
        mock_driver.get_display_density.return_value = 495
        return mock_driver

    @pytest.fixture
    def mock_element(self, mocker):
        """Create a mock WebElement."""
        return mocker.Mock(spec=WebElement)

    @pytest.mark.parametrize("platform", ["android", "ios"])
    def test_pinch_gestures_initialisation(self, mock_driver, platform):
        """Test PinchGestures initialisation with different platforms."""
        pinch_gestures = PinchGestures(mock_driver, platform)
        assert pinch_gestures._driver == mock_driver
        assert pinch_gestures._platform == platform

    @pytest.mark.parametrize("platform,expected_method", [
        ("android", "_pinch_open_android"),
        ("ios", "_pinch_open_ios")
    ])
    def test_pinch_open(self, mock_driver, mock_element, platform, expected_method, mocker):
        """Test pinch open method for both platforms."""
        pinch_gestures = PinchGestures(mock_driver, platform)
        
        spy_method = mocker.spy(pinch_gestures, expected_method)
        mock_execute_script = mocker.patch.object(mock_driver, "execute_script")
        
        percent = 0.6
        speed = 0.8
        
        dpi = mock_driver.get_display_density()
        velocity = (2500 * dpi) * 0.8

        pinch_gestures.open(mock_element, percent=percent, speed=speed)
        
        if platform == "android":
            spy_method.assert_called_once_with(
                mock_element,
                percent,
                0.8,
            )
            mock_execute_script.assert_called_once_with(
                "mobile: pinchOpenGesture",
                {
                    "elementId": mock_element,
                    "percent": percent,
                    "speed": velocity,
                },
        )
        else:
            spy_method.assert_called_once_with(
                mock_element,
                percent,
                speed,
            )
            mock_execute_script.assert_called_once_with(
                "mobile: pinch",
                {
                    "elementId": mock_element,
                    "scale": percent,
                    "velocity": speed,
                },
            )

    def test_pinch_open_platform_specific_method_called(self, mock_driver, mock_element, mocker):
        """Verify the correct platform-specific method is called."""
        android_gestures = PinchGestures(mock_driver, "android")
        android_spy = mocker.spy(android_gestures, '_pinch_open_android')
        android_gestures.open(mock_element)
        android_spy.assert_called_once()

        ios_gestures = PinchGestures(mock_driver, "ios")
        ios_spy = mocker.spy(ios_gestures, '_pinch_open_ios')
        ios_gestures.open(mock_element)
        ios_spy.assert_called_once()

    @pytest.mark.parametrize("platform,expected_method", [
        ("android", "_pinch_close_android"),
        ("ios", "_pinch_close_ios")
    ])
    def test_pinch_close(self, mock_driver, mock_element, platform, expected_method, mocker):
        """Test pinch open method for both platforms."""
        pinch_gestures = PinchGestures(mock_driver, platform)
        
        spy_method = mocker.spy(pinch_gestures, expected_method)
        mock_execute_script = mocker.patch.object(mock_driver, "execute_script")
        
        percent = 0.6
        speed = 0.8
        
        dpi = mock_driver.get_display_density()
        velocity = (2500 * dpi) * 0.8

        pinch_gestures.close(mock_element, percent=percent, speed=speed)
        
        if platform == "android":
            spy_method.assert_called_once_with(
                mock_element,
                percent,
                0.8,
            )
            mock_execute_script.assert_called_once_with(
                "mobile: pinchCloseGesture",
                {
                    "elementId": mock_element,
                    "percent": percent,
                    "speed": velocity,
                },
        )
        else:
            spy_method.assert_called_once_with(
                mock_element,
                percent,
                speed,
            )
            mock_execute_script.assert_called_once_with(
                "mobile: pinch",
                {
                    "elementId": mock_element,
                    "scale": percent * 2,
                    "velocity": speed,
                },
            )

    @pytest.mark.parametrize("platform", ["android", "ios"])
    def test_pinch_close_exception(self, mock_driver, mock_element, platform, mocker):
        """Test pinch close method when an exception occurs."""
        pinch_gestures = PinchGestures(mock_driver, platform)
        mock_logger = mocker.patch('src.interaction.gesture.pinch.logger')
        
        method_to_mock = '_pinch_close_android' if platform == 'android' else '_pinch_close_ios'
        mocker.patch.object(pinch_gestures, method_to_mock, side_effect=Exception("Test error"))
        
        with pytest.raises(ZoomError, match="Failed to perform pinch close"):
            pinch_gestures.close(mock_element)
        
        mock_logger.error.assert_called_once()

    @pytest.mark.parametrize("platform", ["android", "ios"])
    def test_pinch_open_exception(self, mock_driver, mock_element, platform, mocker):
        """Test pinch open method when an exception occurs."""
        pinch_gestures = PinchGestures(mock_driver, platform)
        mock_logger = mocker.patch('src.interaction.gesture.pinch.logger')
        
        method_to_mock = '_pinch_open_android' if platform == 'android' else '_pinch_open_ios'
        mocker.patch.object(pinch_gestures, method_to_mock, side_effect=Exception("Test error"))
        
        with pytest.raises(ZoomError, match="Failed to perform pinch open"):
            pinch_gestures.open(mock_element)
        
        mock_logger.error.assert_called_once()