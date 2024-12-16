import pytest
from appium.webdriver.webdriver import WebDriver

from src.interaction.gesture.actions import GestureActions


class TestGestureActions:
    @pytest.fixture
    def mock_driver(self, mocker):
        """Fixture to create a mock WebDriver instance."""
        return mocker.Mock(spec=WebDriver)

    def test_gesture_actions_initialisation(self, mock_driver):
        """Test basic initialisation of GestureActions."""
        actions = GestureActions(mock_driver, "ios")

        assert actions._driver == mock_driver
        assert actions._platform == "ios"
        assert actions._drag_drop is None
        assert actions._pinch is None
        assert actions._swipe is None

    @pytest.mark.parametrize(
        "platform,expected",
        [
            ("ios", "ios"),
            ("iOS", "ios"),
            ("android", "android"),
            ("Android", "android"),
        ],
    )
    def test_platform_validation_valid_inputs(self, mock_driver, platform, expected):
        """Test platform validation with valid inputs."""
        actions = GestureActions(mock_driver, platform)
        assert actions._platform == expected

    @pytest.mark.parametrize(
        "invalid_type",
        [
            None,
            123,
            True,
            [],
            {},
            set(),
        ],
    )
    def test_platform_validation_invalid_types(self, mock_driver, invalid_type):
        """Test platform validation with invalid types."""
        expected_error = f"Invalid platform type: '{type(invalid_type).__name__}'. Platform must be of type 'str'."
        with pytest.raises(ValueError, match=expected_error):
            GestureActions(mock_driver, invalid_type)

    @pytest.mark.parametrize(
        "invalid_platform",
        [
            "",
            "windows",
            "web",
            "arm64v8",
            "macos",
            "Linux",
            "  ios  ",
            "android ",
            " ios",
        ],
    )
    def test_platform_validation_invalid_values(self, mock_driver, invalid_platform):
        """Test platform validation with invalid platform values."""
        expected_error = f"Invalid platform: '{invalid_platform.lower()}'. Platform must be either 'ios' or 'android'."
        with pytest.raises(ValueError, match=expected_error):
            GestureActions(mock_driver, invalid_platform)

    def test_drag_drop_lazy_loading(self, mock_driver, mocker):
        """Test lazy loading of drag_drop property."""
        actions = GestureActions(mock_driver, "ios")

        mock_drag_drop = mocker.patch(
            "src.interaction.gesture.actions.DragAndDropGestures"
        )
        drag_drop = actions.drag_drop

        mock_drag_drop.assert_called_once_with(mock_driver, "ios")

        second_access = actions.drag_drop
        assert second_access is drag_drop
        mock_drag_drop.assert_called_once()

    def test_pinch_lazy_loading(self, mock_driver, mocker):
        """Test lazy loading of pinch property."""
        actions = GestureActions(mock_driver, "ios")

        mock_pinch = mocker.patch("src.interaction.gesture.actions.PinchGestures")
        pinch = actions.pinch

        mock_pinch.assert_called_once_with(mock_driver, "ios")

        second_access = actions.pinch
        assert second_access is pinch
        mock_pinch.assert_called_once()

    def test_swipe_lazy_loading(self, mock_driver, mocker):
        """Test lazy loading of swipe property."""
        actions = GestureActions(mock_driver, "ios")

        mock_swipe = mocker.patch("src.interaction.gesture.actions.SwipeGestures")
        swipe = actions.swipe

        mock_swipe.assert_called_once_with(mock_driver, "ios")

        second_access = actions.swipe
        assert second_access is swipe
        mock_swipe.assert_called_once()

    def test_invalid_driver_type(self):
        """Test initialisation with invalid driver type."""
        with pytest.raises(TypeError):
            GestureActions("not_a_driver", "ios")

    def test_all_gestures_same_platform(self, mock_driver, mocker):
        """Test that all gesture instances use the same platform value."""
        actions = GestureActions(mock_driver, "android")

        mock_drag_drop = mocker.patch(
            "src.interaction.gesture.actions.DragAndDropGestures"
        )
        mock_pinch = mocker.patch("src.interaction.gesture.actions.PinchGestures")
        mock_swipe = mocker.patch("src.interaction.gesture.actions.SwipeGestures")

        _ = actions.drag_drop
        _ = actions.pinch
        _ = actions.swipe

        mock_drag_drop.assert_called_once_with(mock_driver, "android")
        mock_pinch.assert_called_once_with(mock_driver, "android")
        mock_swipe.assert_called_once_with(mock_driver, "android")
