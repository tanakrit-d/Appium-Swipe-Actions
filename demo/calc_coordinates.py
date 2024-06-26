class Element:
    def __init__(self, x, y, width, height):
        self.location = {"x": x, "y": y}
        self.size = {"width": width, "height": height}

def calculate_coordinates():
    element = Element(20, 20, 40, 20)

    element_top_left_point      = element.location["x"], element.location["y"]
    element_top_mid_point       = element.location["x"] + (element.size["width"] // 2), element.location["y"]
    element_top_right_point     = element.location["x"] + element.size["width"], element.location["y"]
    
    element_left_mid_point      = element.location["x"], element.location["y"] + (element.size["height"] // 2)
    element_mid_point           = element.location["x"] + (element.size["width"] // 2), element.location["y"] + (element.size["height"] // 2)
    element_right_mid_point     = element.location["x"] + element.size["width"], element.location["y"] + (element.size["height"] // 2)

    element_bottom_left_point   = element.location["x"], element.location["y"] + element.size["height"]
    element_bottom_mid_point    = element.location["x"] + (element.size["width"] // 2), element.location["y"] + element.size["height"]
    element_bottom_right_point  = element.location["x"] + element.size["width"], element.location["y"] + element.size["height"]

    print("Top-Left-Point: ", element_top_left_point)
    print("Top-Mid-Point: ", element_top_mid_point)
    print("Top-Right-Point: ", element_top_right_point)
    print()
    print("Left-Mid-Point: ", element_left_mid_point)
    print("Mid-Point: ", element_mid_point)
    print("Right-Mid-Point: ", element_right_mid_point)
    print()
    print("Bottom-Left-Point: ", element_bottom_left_point)
    print("Bottom-Mid-Point: ", element_bottom_mid_point)
    print("Bottom-Right-Point: ", element_bottom_right_point)

if __name__ == "__main__":
    calculate_coordinates()