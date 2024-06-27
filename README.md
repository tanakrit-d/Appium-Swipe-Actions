# Enhanced Swipe Actions Library
 
## Currently a Work in Progress
The goal of this library is to provide more robust and useful scrolling functionality for Appium mobile automation.  
It currently only targets use with Android, and has not been tested against iOS.

## To-Do
- Publish as a library

## Available Methods
```python
swipe_up()
swipe_down()
swipe_left()
swipe_right()
swipe_next() # Ignore scrollable region; full edge-to-edge swipe
swipe_previous() # Ignore scrollable region; full edge-to-edge swipe
swipe_on_element()
swipe_element_into_view()
```

## Defining a Scrollable Region
This library divides the viewport into four bounds: upper, lower, left, and right. The default values can be overwritten.  
Using these bounds, we then define a 'scrollable region'. We can then perform our scroll/swipe actions within this space.  
The impetus for this is to recreate scrolling/swiping behaviour more similar to a user and avoid hardcoding co-ordinates.  
Additionally, it avoids the automation attempting to perform actions on top of elements (such as headers or footers).  
![Viewport Diagram](resources/viewport_scrollable_bounds.png)

## Code Snippet
```python
    def swipe_element_into_view(
        self, locator_method: AppiumBy, locator_value: str, direction: Direction
    ):
        """
        Swipe to bring an element into view.

        Args:
            locator_method: The method to locate the element (e.g., AppiumBy.XPATH).
            locator_value: The value to use with the locator method.
            direction: The direction to swipe (UP, DOWN, LEFT, or RIGHT).
        """
        action = self._create_action()
        element_x, element_y = self.retrieve_element_location(
            locator_method, locator_value
        )

        if direction in [Direction.UP, Direction.DOWN]:
            self._swipe_element_into_view_vertical(action, element_y, direction)
        elif direction in [Direction.LEFT, Direction.RIGHT]:
            self._swipe_element_into_view_horizontal(action, element_x, direction)
```

## Understanding Element Location
For the purpose of this library, we are only concered with two attributes of an element: position and size.  
The element's co-ordinates within the viewport is considered the top-left-point.

We can then use the element size to determine where it occupies relative to the view-port position.
![Element Diagram](resources/understanding_element_position-dimension.png)

```python
element_top_left_point      = element.location["x"], element.location["y"]
element_top_mid_point       = element.location["x"] + (element.size["width"] // 2), element.location["y"]
element_top_right_point     = element.location["x"] + element.size["width"], element.location["y"]

element_left_mid_point      = element.location["x"], element.location["y"] + (element.size["height"] // 2)
element_mid_point           = element.location["x"] + (element.size["width"] // 2), element.location["y"] + (element.size["height"] // 2)
element_right_mid_point     = element.location["x"] + element.size["width"], element.location["y"] + (element.size["height"] // 2)

element_bottom_left_point   = element.location["x"], element.location["y"] + element.size["height"]
element_bottom_mid_point    = element.location["x"] + (element.size["width"] // 2), element.location["y"] + element.size["height"]
element_bottom_right_point  = element.location["x"] + element.size["width"], element.location["y"] + element.size["height"]
```
Using the example element from the image, the above code would output the following:  
> Top-Left-Point:  (20, 20)  
> Top-Mid-Point:  (40, 20)  
> Top-Right-Point:  (60, 20)
> 
> Left-Mid-Point:  (20, 30)  
> Mid-Point:  (40, 30)  
> Right-Mid-Point:  (60, 30)
> 
> Bottom-Left-Point:  (20, 40)  
> Bottom-Mid-Point:  (40, 40)  
> Bottom-Right-Point:  (60, 40)

An MRE is available here: [demo/calc_coordinates.py](demo/calc_coordinates.py)
