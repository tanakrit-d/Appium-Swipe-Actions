# Appium Gestures Library

The purpose of this library is to provide a number gesture/interaction functions for Appium mobile automation.  

## Available Functions

- [x] swipe_up()
- [x] swipe_down()
- [x] swipe_left()
- [x] swipe_right()
- [x] swipe_next()
- [x] swipe_previous()
- [x] swipe_on_element()
- [x] swipe_element_into_view()
- [x] double_tap()
- [x] triple_tap()
- [x] long_press()
- [x] drag_drop()
- [x] zoom_in()
- [x] zoom_out()

## Compatibility

- [x] Android  
  Requires: `appium driver install uiautomator2`
- [ ] iOS (unverified)  
  Requires: `appium driver install xcuitest`

## Install

```bash
pip install appium-gesture-actions
# or
uv add appium-gesture-actions
```

### Changelog

```md
## 0.2.0 (2024-11-14)

- Renamed package
- Added a number of new gestures
  - Double Tap
  - Triple Tap
  - Long Press
  - Drag and Drop
  - Zoom In
  - Zoom Out
- Added error handling
- Added more tests 😭
- Verified iOS compatibility
- Added API docs
- Changed to uv for packaging
```

See full list of changes: [CHANGES.md](https://github.com/Tanakrit-D/Appium-Swipe-Actions/raw/main/CHANGES.md)

## To-do

- [x] Expand functionality to include gestures
- [x] Robust error handling
- [x] Add documentation
- [ ] Add examples for other gestures
- [ ] Remove direct accessing of `ActionBuilder`
- [ ] Return bool for most functions
- [ ] Handling of different orientations
- [ ] Allow for re-initialisation of viewport calculations

## Demo and Example Usage

![Library Demo](https://github.com/Tanakrit-D/Appium-Swipe-Actions/raw/main/demo/example.gif)

```python
from appium.gesture.actions import GestureActions, SeekDirection, Direction

class TestDemo(TestCore):
    def test_element_search(self):
        gesture = GestureActions(self.driver)
        self.driver.find_element(
            by=AppiumBy.ANDROID_UIAUTOMATOR,
            value='new UiSelector().className("android.widget.Button")',
        ).click()
        gesture.swipe_element_into_view(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().descriptionContains("Day planted")',
            SeekDirection.DOWN,
        )
```

## Defining a Scrollable Region

This library divides the viewport into four bounds: upper, lower, left, and right. The default values can be overwritten.  
Using these bounds, we then define a 'scrollable region'. We can then perform our scroll/swipe actions within this space.  
The impetus for this is to recreate scrolling/swiping behaviour more similar to a user and avoid hardcoding co-ordinates.  
Additionally, it avoids the automation attempting to perform actions on top of elements (such as headers or footers).  
![Viewport Diagram](https://github.com/Tanakrit-D/Appium-Swipe-Actions/raw/main/resources/viewport_scrollable_bounds.png)

## Defining Element Points

The importance of dynamically generating 'points' of an element to interact with allows us to account for re-sizing under a number of conditions (such as different devices/resolutions).

For the purpose of this library, we are only concerned with two attributes of an element: position and size.  
The element's co-ordinates within the viewport is considered the top-left-point.

We can then use the element size to determine where it occupies relative to the view-port position.
![Element Diagram](https://github.com/Tanakrit-D/Appium-Swipe-Actions/raw/main/resources/understanding_element_position-dimension.png)

```python
top_left_point      = element.location["x"], element.location["y"]
top_mid_point       = element.location["x"] + (element.size["width"] // 2), element.location["y"]
top_right_point     = element.location["x"] + element.size["width"], element.location["y"]

left_mid_point      = element.location["x"], element.location["y"] + (element.size["height"] // 2)
mid_point           = element.location["x"] + (element.size["width"] // 2), element.location["y"] + (element.size["height"] // 2)
right_mid_point     = element.location["x"] + element.size["width"], element.location["y"] + (element.size["height"] // 2)

bottom_left_point   = element.location["x"], element.location["y"] + element.size["height"]
bottom_mid_point    = element.location["x"] + (element.size["width"] // 2), element.location["y"] + element.size["height"]
bottom_right_point  = element.location["x"] + element.size["width"], element.location["y"] + element.size["height"]
```

Using the example element from the image, the above calculations would output as follows:  

```console
Top-Left-Point:  (20, 20)  
Top-Mid-Point:  (40, 20)  
Top-Right-Point:  (60, 20)
  
Left-Mid-Point:  (20, 30)  
Mid-Point:  (40, 30)  
Right-Mid-Point:  (60, 30)
  
Bottom-Left-Point:  (20, 40)  
Bottom-Mid-Point:  (40, 40)  
Bottom-Right-Point:  (60, 40)
```

An example of this is available here: [demo/calc_coordinates.py](https://raw.githubusercontent.com/Tanakrit-D/Appium-Swipe-Actions/blob/main/demo/calc_coordinates.py)

## Notes

### Swipe Element Into View

The method `swipe_element_into_view()` calls the helper `_probe_for_element()`.  
This is because in the event an element is not loaded into the DOM yet or the driver context is NATIVE - it will not be able to locate the element.  
Instead, it will start calling `perform_navigation_partial_()` and seek the element for a set number of attempts.  
This can be set/overwritten when initialising the class with the `**kwargs("probe_attempts")`.

Additionally, the `if actions_partial > 50:` ensures the pixel distance is large enough to warrant an action.  
When this value is less than 50px, the swipe action will be interpreted by the OS as a double-tap.

### Wait/Expected Conditions

The library will not wait for the elements to be visible before interacting with them (such as `swipe_on_element()`).  
Ensure you implement this yourself before calling a gesture action on an element.

### Debugging

#### Android

If you would like to see the pointer interactions and coordinates, this can be enabled on a device level in `Settings > Developer Options > Pointer location`

## Acknowledgements

- [mmonfared](https://github.com/mmonfared) for his blog on writing a zoom function
