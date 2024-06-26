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


class EnhancedScroll(object):
    """
    The provided functions remove the need to manually input the co-ordinates when performing a swipe/scroll.
    Instead, it will calculate the upper and lower bounds of the viewport and use this to specify the start-end of the action.

    Example Usage:
        ```
        gestures = new EnhancedScroll(driver)
        gestures.swipe_up()
        gestures.swipe_element_into_view(AppiumBy.XPATH, '//button[@name='submit']')
        ```

    Default crop factors can be overwritten via **kwargs.

    Example Usage:
        ```
        gestures = new EnhancedScroll(driver, upper_cf = 0.10, lower_cf = 0.90)
        ```
    """

    def __init__(self, driver, **kwargs):
        super(EnhancedScroll, self).__init__()
        self.driver = driver

        # Set viewport dimensions
        self.view_port_width, self.view_port_height = self.retrieve_viewport_dimensions
        self.view_port_x_mid_point, self.view_port_y_mid_point = self.view_port_width // 2, self.view_port_height // 2
        
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


    def swipe_on_element(self, locator_method: AppiumBy, locator_value: str, direction: Direction):
        """
        DocString

        Example Usage:
        ```
        gestures.swipe_on_element(AppiumBy.XPATH, '//button[@name='submit']', Direction.RIGHT)
        ```

        To-do: Refactor the element calculations into a standalone function (return a dict maybe)
        """
        action = ActionChains(self.driver)
        action.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(Interaction.POINTER_TOUCHER, "touch"))

        element = self.driver.find_element(by=locator_method, value=locator_value)

        element.location["x"], element.location["y"]
    
        element_top_left_point  = element.location["x"], element.location["y"]
        element_top_mid_point = element.location["x"] + (element.size["width"] // 2), element.location["y"]
        element_top_right_point = element.location["x"] + element.size["width"], element.location["y"]
        
        element_left_mid_point = element.location["x"], element.location["y"] + (element.size["height"] // 2)
        element_mid_point = element.location["x"] + (element.size["width"] // 2), element.location["y"] + (element.size["height"] // 2)
        element_right_mid_point = element.location["x"] + element.size["width"], element.location["y"] + (element.size["height"] // 2)

        element_bottom_left_point = element.location["x"], element.location["y"] + element.size["height"]
        element_bottom_mid_point = element.location["x"] + (element.size["width"] // 2), element.location["y"] + element.size["height"]
        element_bottom_right_point = element.location["x"] + element.size["width"], element.location["y"] + element.size["height"]

        match direction:
            case Direction.UP:
                self.perform_navigation_on_element(action, element_bottom_mid_point, element_top_mid_point)
            case Direction.DOWN:
                self.perform_navigation_on_element(action, element_top_mid_point, element_bottom_mid_point)
            case Direction.RIGHT:
                self.perform_navigation_on_element(action, element_right_mid_point, element_left_mid_point)
            case Direction.LEFT:
                self.perform_navigation_on_element(action, element_left_mid_point, element_right_mid_point)


    def swipe_element_into_view(self, locator_method: AppiumBy, locator_value: str):
        """"
        Swipe an element into view. If the element is already in view, it will attempt to bring it to the top.
        This function calculates the distance from the upper bound to the element, and then determines the number of swipes required to bring the element into view.
        A full action is a swipe from the lower bound to the upper bound, and therefore considered '1' action.
        Pauses are required between actions, otherwise the swipe action is given interia and will be interpreted by the OS as a 'flick'.
        If the pointer move is somewhere below 50px, the OS will interpret this as a 'double-click' action. Therefore a check is needed to prevent this from occuring.

        The floor division operator '//' is used to calculate the full actions, as it rounds down.
        Casting the remainder to int() allows us to calculate the partial action as a percentage of the scrollable area.

        Explanation:
            1400 (distance to element) / 800 (scrollable area) = 1.75 swipe actions
            Full Actions: 1400 // 800 = 1.00
            Partial Actions: 1400 / 800 - int(1400 / 800) = 0.75
            Then we multiply the scrollable area by the partial actions (800 * 0.75) to get the remaining distance (600)

        Parameters:
            `locator_method`: AppiumBy locator (e.g. AppiumBy.XPATH, AppiumBy.ACCESSIBILITY_ID)
            `locator_value`: XPath or Attribute to match (e.g. `//ion-nav-view/ion-item[1]` or `android.widget.TextView`).

        Example Usage:
            ```
            gestures = new EnhancedScroll(driver)
            gestures.swipe_element_into_view(AppiumBy.XPATH, 'android.widget.TextView')
            ```
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
                if actions_partial > 50:
                    self.perform_navigation_partial(action, self.lower_bound, self.upper_bound)
            
            if direction_y == Direction.UP:
                if actions_total > 1:
                    self.perform_navigation_full(action, self.upper_bound, self.lower_bound, actions_complete)
                if actions_partial > 50:
                    self.perform_navigation_partial(action, self.upper_bound, self.lower_bound)

        # Need to adjust the approach for elements outside the viewport on the x-axis
        # This is because an elements location (at least in Android) is the top-right point of the element
        # Therefore it will always be treated as < of the x mid-point, even if the element is visually centered

        x_scroll_flag = False

        if x_scroll_flag:
            if direction_x in [Direction.LEFT, Direction.RIGHT]:
                distance_to_element = element_x - self.lower_bound
                actions_total = distance_to_element / self.scrollable_y
                actions_complete = distance_to_element // self.scrollable_y
                actions_partial = self.scrollable_y * (actions_total - int(actions_total))
                actions_complete = int(actions_complete)
            
            if actions_total > 1:
                for i in range(actions_total):
                    self.perform_navigation_full(action, self.lower_bound, self.upper_bound, actions_complete)
            if actions_partial > 50:
                self.perform_navigation_partial


    def retrieve_relative_direction(self, element_x, element_y):
        # Is element outside of viewport?
        # outside_x = False
        # outside_y = False
        # element_relative_x = element_x - self.view_port_x_mid_point
        # element_relative_y = element_y - self.view_port_y_mid_point

        # if (element_relative_x  < 0 or
        # element_relative_x > self.view_port_width):
        #     outside_x = True
        
        # if (element_relative_y  < 0 or
        # element_relative_y > self.view_port_height):
        #     outside_y = True       

        if element_x < self.view_port_x_mid_point:
            direction_x = Direction.LEFT
        if element_x > self.view_port_x_mid_point:
            direction_x = Direction.RIGHT
        if element_y < self.view_port_y_mid_point:
            direction_y = Direction.UP
        if element_y > self.view_port_y_mid_point:
            direction_y = Direction.DOWN
        return direction_x, direction_y


    def perform_navigation_full(self, action: ActionChains, initial_bound: int, finish_bound: int, iterations: int = 1):
        """
        Create and perform an action chain (swipe/scroll action) for a given number of iterations.
        Iterations corresponds to the number of complete actions required to bring the element within the viewport.
        """
        for i in range(iterations):
            action.w3c_actions.pointer_action.move_to_location(self.view_port_x_mid_point, initial_bound)
            action.w3c_actions.pointer_action.pointer_down()
            action.w3c_actions.pointer_action.move_to_location(self.view_port_x_mid_point, finish_bound)
            action.w3c_actions.pointer_action.pause(1)
            action.w3c_actions.pointer_action.release()
            action.perform()


    def perform_navigation_partial(self, action: ActionChains, initial_bound: int, partial_perecentage: int):
        """
        Create and perform an action chain (swipe/scroll action).
        """
        action.w3c_actions.pointer_action.move_to_location(self.view_port_mid_point, initial_bound)
        action.w3c_actions.pointer_action.pointer_down()
        action.w3c_actions.pointer_action.move_to_location(self.view_port_mid_point, initial_bound + partial_perecentage)
        action.w3c_actions.pointer_action.pause(1)
        action.w3c_actions.pointer_action.release()
        action.perform()


    def perform_navigation_on_element(self, action: ActionChains, initial_bound: tuple, finish_bound: tuple):
        action.w3c_actions.pointer_action.move_to_location(initial_bound[0], initial_bound[1])
        action.w3c_actions.pointer_action.pointer_down()
        action.w3c_actions.pointer_action.move_to_location(finish_bound[0], finish_bound[1])
        action.w3c_actions.pointer_action.pause(1)
        action.w3c_actions.pointer_action.release()
        action.perform()


    def retrieve_element_location(self, locator_method: AppiumBy, locator_value: str):
        """
        Retireves the element location.
        """
        element = self.driver.find_element(by=locator_method, value=locator_value)
        return element.location["x"], element.location["y"]


    def retrieve_viewport_dimensions(self):
        """
        Calculates the viewport dimensions.
        """
        view_port = self.driver.get_window_size()
        return view_port["width"], view_port["height"]
    
