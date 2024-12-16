# Changelog

## [Upcoming] 0.3.1 (2024-12-XX) ☃️

- Updated dependencies
- `swipe.element_into_view()` now returns a WebElement
- Added new tests

## 0.3.0 (2024-12-12) 🎄

- Renamed package to resolve namespace collisions
  - This also resolved the workaround required when building docs

      ```python
      from interaction.gestures.actions import GestureActions
      ```

- Change build backend from `hatchling` to `build`
- Migrating back from TypedDict allows for better Type Hinting/Intellisense
- Updated demo

## 0.2.0 (2024-11-20) 🥳

- Renamed package
- Complete re-write of functionality
- Added platform-specific code
- Added a number of new gestures
  - Drag and Drop
  - Pinch/Zoom In
  - Pinch/Zoom Out
- Added safe inserts for Swipe On Element
- Added error handling
- Added API docs
- Changed to uv for packaging

## 0.1.3 (2024-09-04)

- Updated import strategy, the structure is now:  

    ```python
    from appium.swipe.actions import SwipeActions, SeekDirection, Direction
    ```

- Changed to ruff for linting/formatting
- Changed to rye for packaging
