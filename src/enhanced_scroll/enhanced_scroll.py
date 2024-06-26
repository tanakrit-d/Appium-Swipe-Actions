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
        self.viewport_width, self.viewport_height = self.retrieve_viewport_dimensions
        self.viewport_x_mid_point, self.viewport_y_mid_point = self.viewport_width // 2, self.viewport_height // 2
        
        # Default crop factor percentage bounds of the viewport for the scrollable area
        self.upper_cf = kwargs.get('upper_cf', 0.05)  # 5% Removed from top of viewport
        self.lower_cf = kwargs.get('lower_cf', 0.80)  # 20% Removed from bottom of viewport
        self.left_cf = kwargs.get('left_cf', 0.05)    # 5% Removed from left of viewport
        self.right_cf = kwargs.get('right_cf', 0.95)  # 5% Removed from right of viewport
        
        # Set scrolling boundries
        self.upper_bound = self.viewport_height * self.upper_cf
        self.lower_bound = self.viewport_height * self.lower_cf
        self.left_bound = self.viewport_width * self.left_cf
        self.right_bound = self.viewport_width * self.right_cf

        # Set scrollable area
        self.scrollable_x = (self.viewport_height - self.upper_bound) - (self.viewport_height - self.lower_bound)
        self.scrollable_y = (self.viewport_width - self.left_bound) - (self.viewport_width - self.right_bound)


    def swipe_up(self):
        """
        Performs a full upward swipe of the calculated viewport.
        """
        action = ActionChains(self.driver)
        action.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(Interaction.POINTER_TOUCHER, "touch"))
        self.perform_navigation_full_y(action, self.lower_bound, self.upper_bound)


    def swipe_down(self):
        """
        Performs a full downward swipe of the calculated viewport.
        """
        action = ActionChains(self.driver)
        action.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(Interaction.POINTER_TOUCHER, "touch"))
        self.perform_navigation_full_y(action, self.upper_bound, self.lower_bound)


    def swipe_left(self):
        """
        Performs a full leftward swipe of the calculated viewport.
        """
        action = ActionChains(self.driver)
        action.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(Interaction.POINTER_TOUCHER, "touch"))
        self.perform_navigation_full_x(action, self.right_bound, self.left_bound)


    def swipe_right(self):
        """
        Performs a full rightward swipe of the calculated viewport.
        """
        action = ActionChains(self.driver)
        action.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(Interaction.POINTER_TOUCHER, "touch"))
        self.perform_navigation_full_x(action, self.left_bound, self.right_bound)


    def swipe_on_element(self, locator_method: AppiumBy, locator_value: str, direction: Direction):
        """
        Swipe on an element. The primary use case is interacting with a scrollview or carrousel.
        This function calculates the respective mid-points of an element and their location relative to the viewport co-ordinates.
        It then performs a complete ActionChain (swipe/scroll action) for the given direction.

        Explanation:
            - See the provided diagram `./resources/understanding_element_position-dimension.png

        Parameters:
            `locator_method`: AppiumBy locator (e.g. AppiumBy.XPATH, AppiumBy.ACCESSIBILITY_ID)
            `locator_value`: XPath or Attribute to match (e.g. `//ion-nav-view/ion-item[1]` or `android.widget.TextView`)
            `direction`: Direction for the action (e.g. a LEFT swipe starts from the right and finishes left)
        
        Example Usage:
            ```
            gestures.swipe_on_element(AppiumBy.XPATH, '//android.widget.ScrollView', Direction.RIGHT)
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


    def swipe_element_into_view(self, locator_method: AppiumBy, locator_value: str, direction: Direction):
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
            `locator_value`: XPath or Attribute to match (e.g. `//ion-nav-view/ion-item[1]` or `android.widget.TextView`)
            `direction`: Direction for the action (e.g. a LEFT swipe starts from the right and finishes left)

        Example Usage:
            ```
            gestures = new EnhancedScroll(driver)
            gestures.swipe_element_into_view(AppiumBy.XPATH, 'android.widget.TextView')
            ```
        """
        action = ActionChains(self.driver)
        action.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(Interaction.POINTER_TOUCHER, "touch"))
        element_x, element_y = self.retrieve_element_location(locator_method, locator_value)

        if direction in [Direction.UP, Direction.DOWN]:
            distance_to_element = element_y - self.lower_bound
            actions_total = distance_to_element / self.scrollable_x
            actions_complete = distance_to_element // self.scrollable_x
            actions_partial = self.scrollable_x * (actions_total - int(actions_total))
            actions_complete = int(actions_complete)
            
            match direction:
                case Direction.UP:
                    if actions_total > 1:
                        self.perform_navigation_full_y(action, self.upper_bound, self.lower_bound, actions_complete)
                    if actions_partial > 50:
                        self.perform_navigation_partial_y(action, self.upper_bound, self.lower_bound)
                case Direction.DOWN:
                    if actions_total > 1:
                        self.perform_navigation_full_y(action, self.lower_bound, self.upper_bound, actions_complete)
                    if actions_partial > 50:
                        self.perform_navigation_partial_y(action, self.lower_bound, self.upper_bound)
        
        
        if direction in [Direction.LEFT, Direction.RIGHT]:
            distance_to_element = element_x - self.lower_bound
            actions_total = distance_to_element / self.scrollable_y
            actions_complete = distance_to_element // self.scrollable_y
            actions_partial = self.scrollable_y * (actions_total - int(actions_total))
            actions_complete = int(actions_complete)
            
            match direction:
                case Direction.LEFT:
                    if actions_total > 1:
                        self.perform_navigation_full_x(action, self.right_bound, self.left_bound, actions_complete)
                    if actions_partial > 50:
                        self.perform_navigation_partial_x(action, self.right_bound, self.left_bound)
                case Direction.RIGHT:
                    if actions_total > 1:
                        self.perform_navigation_full_x(action, self.left_bound, self.right_bound, actions_complete)
                    if actions_partial > 50:
                        self.perform_navigation_partial_x(action, self.left_bound, self.right_bound)


    def perform_navigation_full_y(self, action: ActionChains, initial_bound: int, finish_bound: int, iterations: int = 1):
        """
        _y denotes the action direction occurs on the y-axis
        Create and perform an ActionChain (swipe/scroll action) for a given number of iterations.
        Iterations corresponds to the number of complete actions required to bring the element within the viewport.
        """
        for i in range(iterations):
            action.w3c_actions.pointer_action.move_to_location(self.viewport_x_mid_point, initial_bound)
            action.w3c_actions.pointer_action.pointer_down()
            action.w3c_actions.pointer_action.move_to_location(self.viewport_x_mid_point, finish_bound)
            action.w3c_actions.pointer_action.pause(1)
            action.w3c_actions.pointer_action.release()
            action.perform()


    def perform_navigation_partial_y(self, action: ActionChains, initial_bound: int, partial_perecentage: int):
        """
        _y denotes the action direction occurs on the y-axis
        Create and perform an ActionChain (swipe/scroll action).
        """
        action.w3c_actions.pointer_action.move_to_location(self.viewport_x_mid_point, initial_bound)
        action.w3c_actions.pointer_action.pointer_down()
        action.w3c_actions.pointer_action.move_to_location(self.viewport_x_mid_point, initial_bound + partial_perecentage)
        action.w3c_actions.pointer_action.pause(1)
        action.w3c_actions.pointer_action.release()
        action.perform()


    def perform_navigation_full_x(self, action: ActionChains, initial_bound: int, finish_bound: int, iterations: int = 1):
        """
        _x denotes the action direction occurs on the x-axis
        Create and perform an ActionChain (swipe/scroll action) for a given number of iterations.
        Iterations corresponds to the number of complete actions required to bring the element within the viewport.
        """
        for i in range(iterations):
            action.w3c_actions.pointer_action.move_to_location(initial_bound, self.viewport_y_mid_point)
            action.w3c_actions.pointer_action.pointer_down()
            action.w3c_actions.pointer_action.move_to_location(finish_bound, self.viewport_y_mid_point)
            action.w3c_actions.pointer_action.pause(1)
            action.w3c_actions.pointer_action.release()
            action.perform()


    def perform_navigation_partial_x(self, action: ActionChains, initial_bound: int, partial_perecentage: int):
        """
        _x denotes the action direction occurs on the x-axis
        Create and perform an ActionChain (swipe/scroll action).
        """
        action.w3c_actions.pointer_action.move_to_location(initial_bound, self.viewport_y_mid_point)
        action.w3c_actions.pointer_action.pointer_down()
        action.w3c_actions.pointer_action.move_to_location(initial_bound + partial_perecentage, self.viewport_y_mid_point)
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
        viewport = self.driver.get_window_size()
        return viewport["width"], viewport["height"]
    
