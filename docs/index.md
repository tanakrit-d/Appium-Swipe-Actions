---
hide:
  - toc

title: Appium Gesture Library
---
<style>
  .md-typeset h1 {
    display: none;
  }
</style>

<div style="text-align: left">
  <img src="assets/logo.png" style="max-width: 64px;" />
</div>

Welcome to the Appium Gesture Actions documentation!  

The purpose of this library is to provide a number of gesture/interaction functions for Appium mobile automation.  
The gestures are platform agnostic, which allows the user to provide a WebElement - or locators for both Android and iOS in the same function call.  

## Install

``` bash
pip install interaction-gesture-actions
# or
uv add interaction-gesture-actions
```

## Available Functions

### Swipe Gestures

- [__up()__](./reference/swipe.md#interaction.gesture.swipe.SwipeGestures.up)
- [__down()__](./reference/swipe.md#interaction.gesture.swipe.SwipeGestures.down)
- [__left()__](./reference/swipe.md#interaction.gesture.swipe.SwipeGestures.left)
- [__right()__](./reference/swipe.md#interaction.gesture.swipe.SwipeGestures.right)
- [__next()__](./reference/swipe.md#interaction.gesture.swipe.SwipeGestures.next)
- [__previous()__](./reference/swipe.md#interaction.gesture.swipe.SwipeGestures.previous)
- [__on_element()__](./reference/swipe.md#interaction.gesture.swipe.SwipeGestures.on_element)
- [__element_into_view()__](./reference/swipe.md#interaction.gesture.swipe.SwipeGestures.element_into_view)

### Drag and Drop Gestures

- [__drag_and_drop()__](./reference/drag_and_drop.md#interaction.gesture.drag_and_drop.DragAndDropGestures.drag_and_drop)

### Pinch Gestures

- [__open()__](./reference/pinch.md#interaction.gesture.pinch.PinchGestures.open)
- [__close()__](./reference/pinch.md#interaction.gesture.pinch.PinchGestures.close)

## Compatibility

- ✅ Android  
  Requires: `appium driver install uiautomator2`
- ❎ iOS (unverified)  
  Requires: `appium driver install xcuitest`
