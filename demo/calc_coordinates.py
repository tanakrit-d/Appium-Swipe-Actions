class Element:
    def __init__(self, x, y, width, height):
        self.location = {"x": x, "y": y}
        self.size = {"width": width, "height": height}


def calculate_coordinates():
    element = Element(20, 20, 40, 20)

    top_left_point = element.location["x"], element.location["y"]
    top_mid_point = (
        element.location["x"] + (element.size["width"] // 2),
        element.location["y"],
    )
    top_right_point = (
        element.location["x"] + element.size["width"],
        element.location["y"],
    )

    left_mid_point = (
        element.location["x"],
        element.location["y"] + (element.size["height"] // 2),
    )
    mid_point = (
        element.location["x"] + (element.size["width"] // 2),
        element.location["y"] + (element.size["height"] // 2),
    )
    right_mid_point = (
        element.location["x"] + element.size["width"],
        element.location["y"] + (element.size["height"] // 2),
    )

    bottom_left_point = (
        element.location["x"],
        element.location["y"] + element.size["height"],
    )
    bottom_mid_point = (
        element.location["x"] + (element.size["width"] // 2),
        element.location["y"] + element.size["height"],
    )
    bottom_right_point = (
        element.location["x"] + element.size["width"],
        element.location["y"] + element.size["height"],
    )

    print("Top-Left-Point: ", top_left_point)
    print("Top-Mid-Point: ", top_mid_point)
    print("Top-Right-Point: ", top_right_point)
    print()
    print("Left-Mid-Point: ", left_mid_point)
    print("Mid-Point: ", mid_point)
    print("Right-Mid-Point: ", right_mid_point)
    print()
    print("Bottom-Left-Point: ", bottom_left_point)
    print("Bottom-Mid-Point: ", bottom_mid_point)
    print("Bottom-Right-Point: ", bottom_right_point)


if __name__ == "__main__":
    calculate_coordinates()
