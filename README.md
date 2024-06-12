# Enhanced Mobile Scroll Library
 
## Work in Progress

The goal of this library is to provide more robust and useful scrolling functionality for Appium mobile automation.

We achieve this by dividing the viewport/screen into 'scrollable' regions, and then performing w3c actions within this space.
Using percentages of the viewport and element locations, we can avoid the standard approach of specifiying co-ordinates for each swipe/or scroll action.

The current task is writing direction detection into the functionality. This will remove the use for specifying it manually via. parameter.

Will eventually publish it as a library :^)

Approach sample:
```
def __init__(self, driver, **kwargs):
    super(EnhancedScroll, self).__init__()
    self.driver = driver

    # Set viewport dimensions
    self.view_port_width, self.view_port_height = self.retrieve_viewport_dimensions
    self.view_port_x_midpoint, self.view_port_y_midpoint = self.view_port_width // 2, self.view_port_height // 2
    
    # Default crop factor percentage bounds of the viewport for the scrollable area
    self.upper_cf = kwargs.get('upper_cf', 0.05)  # 5% Removed from top of viewport
    self.lower_cf = kwargs.get('lower_cf', 0.80)  # 20% Removed from bottom of viewport
    self.left_cf = kwargs.get('left_cf', 0.05)    # 5% Removed from left of viewport
    self.right_cf = kwargs.get('right_cf', 0.95)  # 5% Removed from right of viewport
    
    # Set scrolling boundries
    self.upper_bound = self.view_port_height * self.upper_cf
    self.lower_bound = self.view_port_height * self.lower_cf
    self.left_bound = self.view_port_width * self.left_cf
    self.right_bound = self.view_port_width * self.right_cf

    # Set scrollable area
    self.scrollable_x = (self.view_port_height - self.upper_bound) - (self.view_port_height - self.lower_bound)
    self.scrollable_y = (self.view_port_width - self.left_bound) - (self.view_port_width - self.right_bound)
```