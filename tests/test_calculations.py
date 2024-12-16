import pytest
from selenium.webdriver.remote.webelement import WebElement

from src.interaction.gesture.calculations import (
    calculate_element_points,
    retrieve_element_location,
)


class TestCalculations:
    @pytest.fixture
    def mock_element(self, mocker):
        """Create a mock WebElement with typical location and size attributes."""
        mock_element = mocker.Mock(spec=WebElement)
        mock_element.location = {"x": 100, "y": 200}
        mock_element.size = {"width": 50, "height": 75}
        return mock_element

    def test_calculate_element_points_default(self, mock_element):
        """Test calculate_element_points with default parameters."""
        points = calculate_element_points(mock_element)

        assert points == {
            # Corners
            "top_left": (100, 200),
            "top_right": (150, 200),
            "bottom_left": (100, 275),
            "bottom_right": (150, 275),
            # Edge midpoints
            "top_mid": (125, 200),
            "right_mid": (150, 237),
            "bottom_mid": (125, 275),
            "left_mid": (100, 237),
            # Center point
            "mid": (125, 237),
        }

    def test_calculate_element_points_safe_inset(self, mock_element):
        """Test calculate_element_points with safe_inset=True."""
        points = calculate_element_points(mock_element, safe_inset=True)

        assert points["top_left"] == (105, 207)
        assert points["bottom_right"] == (145, 268)

    def test_calculate_element_points_invalid_dimensions(self, mocker):
        """Test calculate_element_points with invalid element dimensions."""
        invalid_element = mocker.Mock(spec=WebElement)
        invalid_element.location = {"x": 100, "y": 200}
        invalid_element.size = {"width": 0, "height": 0}

        with pytest.raises(ValueError, match="Invalid element dimensions"):
            calculate_element_points(invalid_element)

    def test_retrieve_element_location(self, mock_element):
        """Test retrieve_element_location returns correct coordinates."""
        location = retrieve_element_location(mock_element)

        assert location == (100, 200)

    @pytest.mark.parametrize("safe_inset", [True, False])
    def test_calculate_element_points_type_consistency(self, mock_element, safe_inset):
        """Ensure calculate_element_points returns consistent dictionary structure."""
        points = calculate_element_points(mock_element, safe_inset)

        expected_keys = [
            "top_left",
            "top_right",
            "bottom_left",
            "bottom_right",
            "top_mid",
            "right_mid",
            "bottom_mid",
            "left_mid",
            "mid",
        ]
        assert set(points.keys()) == set(expected_keys)

        for point in points.values():
            assert isinstance(point, tuple)
            assert len(point) == 2
            assert all(isinstance(coord, int) for coord in point)
