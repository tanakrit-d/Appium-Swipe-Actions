import pytest
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.webelement import WebElement

from src.interaction.gesture.drag_and_drop import DragAndDropGestures


class TestDragAndDropGestures:
    @pytest.fixture
    def mock_driver(self, mocker):
        """Create a mock WebDriver instance."""
        mock_driver = mocker.Mock(spec=WebDriver)
        mock_driver.get_display_density.return_value = 495
        return mock_driver

    @pytest.fixture
    def mock_source_element(self, mocker):
        """Create a mock source WebElement."""
        mock_element = mocker.Mock(spec=WebElement)
        mock_element.location = {"x": 100, "y": 200}
        mock_element.size = {"width": 50, "height": 75}
        return mock_element

    @pytest.fixture
    def mock_target_element(self, mocker):
        """Create a mock target WebElement."""
        mock_element = mocker.Mock(spec=WebElement)
        mock_element.location = {"x": 300, "y": 400}
        mock_element.size = {"width": 50, "height": 75}
        return mock_element

    @pytest.fixture
    def drag_and_drop_gestures_android(self, mock_driver):
        """Create a DragAndDropGestures instance."""
        return DragAndDropGestures(mock_driver, "android")

    @pytest.fixture
    def drag_and_drop_gestures_ios(self, mock_driver):
        """Create a DragAndDropGestures instance."""
        return DragAndDropGestures(mock_driver, "ios")

    @pytest.mark.parametrize("platform", ["ios", "android"])
    def test_drag_and_drop_platform_support(self, mock_driver, platform):
        """Test drag and drop initialisation with different platforms."""
        drag_drop = DragAndDropGestures(mock_driver, platform)

        assert drag_drop._driver == mock_driver
        assert drag_drop._platform == platform

    def test_drag_and_drop_method_android(
        self,
        drag_and_drop_gestures_android,
        mock_driver,
        mock_source_element,
        mock_target_element,
        mocker,
    ):
        """Test drag and drop method specifically for Android platform."""
        mock_execute_script = mocker.patch.object(mock_driver, "execute_script")

        mock_source_element.location = {"x": 125, "y": 237}
        mock_source_element.size = {"width": 50, "height": 75}
        mock_target_element.location = {"x": 325, "y": 437}
        mock_target_element.size = {"width": 50, "height": 75}

        drag_and_drop_gestures_android.drag_and_drop(
            mock_source_element, mock_target_element, speed=1.0
        )

        dpi = 495
        velocity = (2500 * dpi) * 1.0

        mock_execute_script.assert_called_once_with(
            "mobile: dragGesture",
            {"startX": 150, "startY": 274, "endX": 350, "endY": 474, "speed": velocity},
        )

    def test_drag_and_drop_method_ios(
        self,
        drag_and_drop_gestures_ios,
        mock_driver,
        mock_source_element,
        mock_target_element,
        mocker,
    ):
        """Test the drag_and_drop method."""
        mock_execute_script = mocker.patch.object(mock_driver, "execute_script")

        mock_source_element.location = {"x": 125, "y": 237}
        mock_source_element.size = {"width": 50, "height": 75}
        mock_target_element.location = {"x": 325, "y": 437}
        mock_target_element.size = {"width": 50, "height": 75}

        drag_and_drop_gestures_ios.drag_and_drop(
            mock_source_element, mock_target_element, speed=1.5
        )

        mock_execute_script.assert_called_once_with(
            "mobile: dragFromToWithVelocity",
            {
                "pressDuration": 0.5,
                "holdDuration": 0.1,
                "fromX": 150,
                "fromY": 274,
                "toX": 350,
                "toY": 474,
                "velocity": 600.0,
            },
        )

    def test_drag_and_drop_invalid_speed_android(
        self, drag_and_drop_gestures_android, mock_source_element, mock_target_element
    ):
        """Test drag_and_drop method with invalid speed."""
        speeds = [-1, 10.1, 15, 16.0]

        for speed in speeds:
            with pytest.raises(
                ValueError, match=f"Speed must be between 0.0 and 10.0, got {speed}"
            ):
                drag_and_drop_gestures_android.drag_and_drop(
                    mock_source_element, mock_target_element, speed=speed
                )

    def test_drag_and_drop_invalid_speed_ios(
        self, drag_and_drop_gestures_ios, mock_source_element, mock_target_element
    ):
        """Test drag_and_drop method with invalid speed."""
        speeds = [-1, 10.1, 15, 16.0]

        for speed in speeds:
            with pytest.raises(
                ValueError, match=f"Speed must be between 0.0 and 10.0, got {speed}"
            ):
                drag_and_drop_gestures_ios.drag_and_drop(
                    mock_source_element, mock_target_element, speed=speed
                )

    def test_drag_and_drop_same_element_android(
        self, drag_and_drop_gestures_android, mock_source_element
    ):
        """Test drag_and_drop method with same source and target element."""
        with pytest.raises(
            ValueError, match="Source and target elements must be different"
        ):
            drag_and_drop_gestures_android.drag_and_drop(
                mock_source_element, mock_source_element
            )

    def test_drag_and_drop_same_element_ios(
        self, drag_and_drop_gestures_ios, mock_source_element
    ):
        """Test drag_and_drop method with same source and target element."""
        with pytest.raises(
            ValueError, match="Source and target elements must be different"
        ):
            drag_and_drop_gestures_ios.drag_and_drop(
                mock_source_element, mock_source_element
            )
