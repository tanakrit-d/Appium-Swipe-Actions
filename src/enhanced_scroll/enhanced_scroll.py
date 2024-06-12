import time
import logging
from enum import Enum, unique

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import Interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.support import expected_conditions as Conditions
import appium.webdriver.errorhandler as AppiumException
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
    NoSuchElementException,
)

@unique
class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

class Direction_X(Enum):
    LEFT = "left"
    RIGHT = "right"

class Direction_Y(Enum):
    UP = "up"
    DOWN = "down"

class EnhancedScroll(object):
    """
    Description

    The functions removes the need to manually input the co-ordinates when performing a swipe/scroll action.

    Example:
        ```
        gestures = new EnhancedScroll(driver)
        gestures.swipe_right()
        gestures.swipe_element_into_view(AppiumBy.XPATH, '//button[@name='submit']', Direction.UP)
        ```

    Default crop factors can be overwritten via kwargs.

    Example:
        ```
        gestures = new EnhancedScroll(driver, upper_cf = 0.10, lower_cf = 0.90)
        ```
    """

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

    def swipe_up(self):
        """
        Performs a full upward swipe of the calculated viewport.
        """
        action = ActionChains(self.driver)
        action.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(Interaction.POINTER_TOUCHER, "touch"))
        self.perform_navigation_full(action, self.lower_bound, self.upper_bound)
    
    def swipe_down(self):
        """
        Performs a full downward swipe of the calculated viewport.
        """
        action = ActionChains(self.driver)
        action.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(Interaction.POINTER_TOUCHER, "touch"))
        self.perform_navigation_full(action, self.upper_bound, self.lower_bound)
    
    def swipe_up_on_element(self, locator_method: AppiumBy, locator_value: str):
        """
        DocString
        """
        # Need to use crop factors on the element itself based on size + location
        print() 
            
    def swipe_element_into_view(self, locator_method: AppiumBy, locator_value: str):
        """"
        DocString
        """
        action = ActionChains(self.driver)
        action.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(Interaction.POINTER_TOUCHER, "touch"))
        element_x, element_y = self.retrieve_element_location(locator_method, locator_value)
        direction_x, direction_y = self.retrieve_relative_direction(element_x, element_y)

        if direction_y in [Direction.UP, Direction.DOWN]:
            distance_to_element = element_y - self.lower_bound
            actions_total = distance_to_element / self.scrollable_x
            actions_complete = distance_to_element // self.scrollable_x
            actions_partial = self.scrollable_x * (actions_total - int(actions_total))
            actions_complete = int(actions_complete)

            if direction_y == Direction.DOWN:
                if actions_total > 1:
                    self.perform_navigation_full(action, self.lower_bound, self.upper_bound, actions_complete)
                if actions_partial > 0:
                    self.perform_navigation_partial(action, self.lower_bound, self.upper_bound)
            
            if direction_y == Direction.UP:
                if actions_total > 1:
                    self.perform_navigation_full(action, self.upper_bound, self.lower_bound, actions_complete)
                if actions_partial > 0:
                    self.perform_navigation_partial(action, self.upper_bound, self.lower_bound)

        if direction_x in [Direction.LEFT, Direction.RIGHT]:
            distance_to_element = element_x - self.lower_bound
            actions_total = distance_to_element / self.scrollable_y
            actions_complete = distance_to_element // self.scrollable_y
            actions_partial = self.scrollable_y * (actions_total - int(actions_total))
            actions_complete = int(actions_complete)
        
        if actions_total > 1:
            self.perform_navigation_full(action, self.lower_bound, self.upper_bound, actions_complete)
        if actions_partial > 0:
            self.perform_navigation_partial

    def retrieve_relative_direction(self, element_x, element_y):
        # Is element outside of viewport?
        outside_x = False
        outside_y = False
        element_relative_x = element_x - self.view_port_x_midpoint
        element_relative_y = element_y - self.view_port_y_midpoint

        if (element_relative_x  < 0 or
        element_relative_x > self.view_port_width):
            outside_x = True
        
        if (element_relative_y  < 0 or
        element_relative_y > self.view_port_height):
            outside_y = True       

        
        #######

        if element_x < self.view_port_x_midpoint:
            direction_x = Direction_X.LEFT
        if element_x > self.view_port_x_midpoint:
            direction_x = Direction_X.RIGHT
        if element_y < self.view_port_y_midpoint:
            direction_y = Direction_Y.UP
        if element_y > self.view_port_y_midpoint:
            direction_y = Direction_Y.DOWN
        return direction_x, direction_y

    def perform_navigation_full(self, action: ActionChains, initial_bound: int, finish_bound: int, iterations: int = 1):
        """
        DocString
        """
        for i in range(iterations):
            action.w3c_actions.pointer_action.move_to_location(self.view_port_x_midpoint, initial_bound)
            action.w3c_actions.pointer_action.pointer_down()
            action.w3c_actions.pointer_action.move_to_location(self.view_port_x_midpoint, finish_bound)
            action.w3c_actions.pointer_action.pause(1)
            action.w3c_actions.pointer_action.release()
            action.perform()

    def perform_navigation_partial(self, action: ActionChains, initial_bound: int, partial_perecentage: int):
        """
        DocString
        """
        action.w3c_actions.pointer_action.move_to_location(self.view_port_midpoint, initial_bound)
        action.w3c_actions.pointer_action.pointer_down()
        action.w3c_actions.pointer_action.move_to_location(self.view_port_midpoint, initial_bound + partial_perecentage)
        action.w3c_actions.pointer_action.pause(1)
        action.w3c_actions.pointer_action.release()
        action.perform()

    def retrieve_element_location(self, locator_method: AppiumBy, locator_value: str):
        """
        DocString
        """
        element = self.driver.find_element(by=locator_method, value=locator_value)
        return element.location["x"], element.location["y"]
    
    def retrieve_viewport_dimensions(self):
        """
        DocString
        """
        view_port = self.driver.get_window_size()
        return view_port["width"], view_port["height"]
    
