# Appium Gestures Library

This library is to provide a number gesture/interaction functions for Appium mobile automation.  
The gestures are platform agnostic, which allows the user to provide a WebElement - or locators for both Android and iOS in the same function call.  

**Note:** This documentation is for the upcoming v0.2.0 release. It is available on [TestPyPi](https://test.pypi.org/project/appium-gesture-actions/0.2.0/)

## Available Functions

### Swipe Gestures

- [x] up()
- [x] down()
- [x] left()
- [x] right()
- [x] next()
- [x] previous()
- [x] on_element()
- [x] element_into_view()

### Drag and Drop Gestures

- [x] drag_and_drop()

### Pinch Gestures

- [x] open()
- [x] close()

-----

[Documentation](https://tanakrit-d.github.io/appium-gesture-actions/index.html)

-----

## Compatibility

- [x] Android  
  Requires: `appium driver install uiautomator2`
- [x] iOS (unverified)  
  Requires: `appium driver install xcuitest`

## Install

```bash
pip install appium-gesture-actions
# or
uv add appium-gesture-actions
```

### Changelog

```md
## 0.2.0 (2024-11-XX)

- Renamed package
- Complete re-write of functionality
- Added platform-specific code
- Added a number of new gestures
  - Drag and Drop
  - Pinch/Zoom In
  - Pinch/Zoom Out
- Added error handling
- Added API docs
- Changed to uv for packaging
```

See full list of changes: [CHANGES.md](https://github.com/tanakrit-d/appium-gesture-actions/raw/main/CHANGES.md)

## To-do

- [x] Expand functionality to include gestures
- [x] Add cross-platform functionality
- [x] Robust error handling
- [x] Add documentation
- [x] Add examples for other gestures
- [x] Return bool for most functions
- [ ] Allow for the specifying of values in sub-classes (such as `_max_attempts` or crop factors in `SwipeGestures`)
- [ ] Remove direct accessing of `ActionBuilder` - or not..
- [ ] Handling of different orientations
- [ ] Allow for re-initialisation of viewport calculations
- [ ] Reduce minimum Python version

## Demo and Example Usage

![Library Demo](https://github.com/tanakrit-d/appium-gesture-actions/raw/main/demo/example.gif)

```python
from appium.gesture.actions import GestureActions, SeekDirection

class TestDemo(TestCore):
    def test_cool_stuff(self):
        # Initialise class object
        action = GestureActions(self.driver, self.options["platformName"])

        # Drag and Drop
        image_element = driver.find_element(
            by=AppiumBy.XPATH,
            value='//android.widget.ImageView[0]',
        )
        delete_element = driver.find_element(
            by=AppiumBy.XPATH,
            value='//android.widget.ImageView[1]',
        )
        action.drag_drop.drag_and_drop(image_element, delete_element)

        # Swipe
        action.swipe.up()
        action.swipe.next()

        # Pinch
        action.pinch.open(image_element)

        # Scroll to Element
        action.swipe.element_into_view(
            value_a='new UiSelector().className("android.widget.EditText").instance(0)',
            locator_method_a=AppiumBy.ANDROID_UIAUTOMATOR,
        )

        # Scroll to Element (Multi-platform, single code base)
        action.swipe.element_into_view(
            value_a='//div[@class="menuIcon"][@ng-click="iconClick()"]',
            value_i='label == \'Submit\''
            locator_method_a=AppiumBy.XPATH,
            locator_method_i=AppiumBy.IOS_PREDICATE,
            direction=SeekDirection.DOWN,
        )
```

## An Explainer on Swipe Element Into View

This function (part of the [SwipeGestures](https://github.com/tanakrit-d/appium-gesture-actions/blob/ae1d229d14ced2a20169982d6284fcf7ed92c22b/src/appium/gesture/swipe.py#L45) class) has cross-platform support.  
It is achieved by using parameters with different suffixes (`_a` and `_i` for Android and iOS respectively) and support for `**kwargs`.  

This will allow you to use a single functional call for use on both platforms.

Additionally, it includes a fallback method (which is less efficient) if the element cannot be located initially.  
This is achieved by scrolling the viewport until the element is located, or the maximum number of swipes is achieved (default: 5).  
An example situation would be if an element is not yet present in the viewport, and is loaded after scrolling.  
If this situation applies to you, the `direction` parameter will need to be specified.  

### A Quick Word on Perform Navigation (Full and Partial)

The fallback method will calculate the viewport size, and then define a scrollable region based on crop factors to avoid triggering the notification shade/center or multi-tasking view.  
If it cannot locate the element, it will call `_perform_navigation_partial_` until it does - or it exceeds the max attempts.  
In the event that the element *is* present but *not* in the viewport, it will calculate the distance to the element.  
Then, it will determine the correct number of full (and if necessary) partial swipes to bring the element into the center of the viewport.  

Additionally, the `if actions_partial > SWIPE_ACTION_THRESHOLD` check ensures the pixel distance is large enough to warrant an action.  
When this value is less than 50px, the swipe action will be interpreted by the OS as a double-tap.

Please look at `_fallback_scroll_to_element` if you'd like to learn more.
https://github.com/tanakrit-d/appium-gesture-actions/blob/ae1d229d14ced2a20169982d6284fcf7ed92c22b/src/appium/gesture/swipe.py#L176

## Defining a Scrollable Region

This library divides the viewport into four bounds: upper, lower, left, and right. The default values cannot be overwritten (this will change in a future release).  
Using these bounds, we then define a 'scrollable region'. We can then perform our scroll/swipe actions within this space.  
The impetus for this is to recreate scrolling/swiping behaviour more similar to a user and avoid hardcoding co-ordinates.  
Additionally, it avoids the automation attempting to perform actions on top of elements (such as headers or footers).  
![Viewport Diagram](https://github.com/tanakrit-d/appium-gesture-actions/raw/main/resources/viewport_scrollable_bounds.png)

## Defining Element Points

The importance of dynamically generating 'points' of an element to interact with allows us to account for re-sizing under a number of conditions (such as different devices/resolutions).

For the purpose of this library, we are only concerned with two attributes of an element: position and size.  
The element's co-ordinates within the viewport is considered the top-left-point.

We can then use the element size to determine where it occupies relative to the view-port position.
![Element Diagram](https://github.com/tanakrit-d/appium-gesture-actions/raw/main/resources/understanding_element_position-dimension.png)

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

An example of this is available here: [demo/calc_coordinates.py](https://github.com/tanakrit-d/appium-gesture-actions/blob/dc16c82864212b68ee55c79540518810e5a4ee5a/demo/calc_coordinates.py)

## Notes

### Android

If you would like to see the pointer interactions and coordinates, this can be enabled on a device level in `Settings > Developer Options > Pointer location`
