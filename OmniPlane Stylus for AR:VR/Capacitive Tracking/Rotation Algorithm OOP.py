#Imaad Bukhari
#Rotation File OOP
#This simulates and processes sensor data into coordinates for tracking the stylus location
#Date last edited: 16/5/2024


import logging
import unittest
import math
from PIL import Image
import random
import numpy as np
from PIL import Image, ImageDraw


class Pixel:
    '''Defines each point where a sensor might be found, assigning each one a number as they appear in the arrangement'''
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value

    def translate(self, dx, dy):
        '''Translates the pixel by dx and dy'''
        self.x += dx
        self.y += dy

    def rotate(self, angle, center_x, center_y):
        '''Rotates the pixel around a center point by a given angle in degrees'''
        angle = math.radians(angle)  # Convert angle to radians for math functions
        x = self.x - center_x  # Translate point to origin
        y = self.y - center_y
        new_x = x * math.cos(angle) - y * math.sin(angle)  # Apply rotation transformation
        new_y = x * math.sin(angle) + y * math.cos(angle)
        self.x = new_x + center_x  # Translate point back
        self.y = new_y + center_y


class CircleArrangement:
    """This is an arrangement of pixels/sensors in the pattern they will appear in on the stylus tip"""
    def __init__(self, x0, y0, box_size, step, theta1, theta2, theta3):
        self.x0 = x0  # Center x-coordinate
        self.y0 = y0  # Center y-coordinate
        self.box_size = box_size  # Size of each box in the grid
        self.step = step  # Step sizes for angle increments
        self.theta1 = theta1  # Rotation angle theta1
        self.theta2 = theta2  # Rotation angle theta2
        self.theta3 = theta3  # Rotation angle theta3
        self.pixels = self.generate_circle_coordinates()  # Generate pixel coordinates

    def generate_circle_coordinates(self):
        '''Generates the arrangement of pixels in the appropriate pattern. This is a predetermined pattern that is used to track the stylus location'''
        coord_list = []  # List to store pixel coordinates
        num = 1  # Initialize numbering for each point
        count = 0  # Initialize count for each point
        for y in range(0, 4 * self.box_size, self.box_size):  # Iterate over y positions
            angle_step = self.step[count]  # Get the step size for current count
            angles = np.arange(0, 360, angle_step)  # Generate angle values

            for x in angles:
                # Calculate the angle with an offset if count is even
                ang = math.radians(x + angle_step / 2) if count % 2 == 0 else math.radians(x)

                center_x = self.x0 + int(y * math.cos(ang))  # Calculate x-coordinate
                center_y = self.y0 + int(y * math.sin(ang))  # Calculate y-coordinate

                # Apply rotation transformations
                new_x = center_x - self.x0
                new_y = center_y - self.y0
                new_z = 0

                # Apply the first rotation
                calc_x = new_x * math.cos(self.theta1) - new_y * math.sin(self.theta1)
                calc_y = new_x * math.sin(self.theta1) + new_y * math.cos(self.theta1)
                calc_z = 0

                # Apply the second rotation
                calc_y = calc_y * math.cos(self.theta2) - new_z * math.sin(self.theta2)
                calc_z = calc_y * math.sin(self.theta2) + new_z * math.cos(self.theta2)

                # Apply the third rotation
                calc_x = calc_x * math.cos(self.theta3) + calc_z * math.sin(self.theta3)
                calc_z = calc_z * -1 * math.sin(self.theta3) + calc_z * math.cos(self.theta3)

                # Calculate the rotated x and y coordinates
                rotated_x = int(self.x0 + calc_x)
                rotated_y = int(self.y0 + calc_y)

                coord_list.append(Pixel(rotated_x, rotated_y, num))  # Append coordinates with number
                logging.debug(f'Pixels value generated: {num}')
                num += 1
            count += 1  # Increment count
        return coord_list
    
    def check_lines(self, line_spacing_micrometers=300, line_width_micrometers=15):
        '''Given the location of the pixels in the arrangement, this method checks if any 3 pixels lie on a thin line or on two lines'''
        aligned_triples = []  # List to store aligned triples
        for i in range(len(self.pixels)):
            x1, y1 = self.pixels[i].x, self.pixels[i].y  # Get coordinates of pixel i
            for j in range(i + 1, len(self.pixels)):
                x2, y2 = self.pixels[j].x, self.pixels[j].y  # Get coordinates of pixel j
                for k in range(j + 1, len(self.pixels)):
                    x3, y3 = self.pixels[k].x, self.pixels[k].y  # Get coordinates of pixel k
                    if self.check_triple_on_lines(x1, y1, x2, y2, x3, y3, line_spacing_micrometers, line_width_micrometers):
                        print(f"Aligned triple found: {self.pixels[i]}, {self.pixels[j]}, {self.pixels[k]}")
                        aligned_triples.append((self.pixels[i], self.pixels[j], self.pixels[k]))
        print(f"Total aligned triples found: {len(aligned_triples)}")
        return aligned_triples

    def check_triple_on_lines(self, x1, y1, x2, y2, x3, y3, line_spacing_micrometers, line_width_micrometers):
        '''Checks if three points are on the same line or if two points are on one line and two other points are on another line'''
        # Check if all three points are on the same horizontal line
        if (self.is_on_horizontal_line(y1, line_spacing_micrometers, line_width_micrometers) and
                self.is_on_horizontal_line(y2, line_spacing_micrometers, line_width_micrometers) and
                self.is_on_horizontal_line(y3, line_spacing_micrometers, line_width_micrometers)):
            return True
        # Check if all three points are on the same diagonal line
        if (self.is_on_diagonal_line(x1, y1, line_spacing_micrometers, line_width_micrometers) and
                self.is_on_diagonal_line(x2, y2, line_spacing_micrometers, line_width_micrometers) and
                self.is_on_diagonal_line(x3, y3, line_spacing_micrometers, line_width_micrometers)):
            return True
        # Check if two points are on one line and the other two are on another line
        if (self.is_on_horizontal_line(y1, line_spacing_micrometers, line_width_micrometers) and
                self.is_on_horizontal_line(y2, line_spacing_micrometers, line_width_micrometers)) or \
                (self.is_on_diagonal_line(x1, y1, line_spacing_micrometers, line_width_micrometers) and
                self.is_on_diagonal_line(x2, y2, line_spacing_micrometers, line_width_micrometers)):
            return self.is_on_horizontal_line(y3, line_spacing_micrometers, line_width_micrometers) or \
                self.is_on_diagonal_line(x3, y3, line_spacing_micrometers, line_width_micrometers)
        if (self.is_on_horizontal_line(y1, line_spacing_micrometers, line_width_micrometers) and
                self.is_on_horizontal_line(y3, line_spacing_micrometers, line_width_micrometers)) or \
                (self.is_on_diagonal_line(x1, y1, line_spacing_micrometers, line_width_micrometers) and
                self.is_on_diagonal_line(x3, y3, line_spacing_micrometers, line_width_micrometers)):
            return self.is_on_horizontal_line(y2, line_spacing_micrometers, line_width_micrometers) or \
                self.is_on_diagonal_line(x2, y2, line_spacing_micrometers, line_width_micrometers)
        if (self.is_on_horizontal_line(y2, line_spacing_micrometers, line_width_micrometers) and
                self.is_on_horizontal_line(y3, line_spacing_micrometers, line_width_micrometers)) or \
                (self.is_on_diagonal_line(x2, y2, line_spacing_micrometers, line_width_micrometers) and
                self.is_on_diagonal_line(x3, y3, line_spacing_micrometers, line_width_micrometers)):
            return self.is_on_horizontal_line(y1, line_spacing_micrometers, line_width_micrometers) or \
                self.is_on_diagonal_line(x1, y1, line_spacing_micrometers, line_width_micrometers)
        return False
        

    def is_on_horizontal_line(self, y, line_spacing_micrometers=300, line_width_micrometers=15):
            '''Checks if a point lies on a horizontal line'''
            w = line_width_micrometers / 2  # Half of the line width
            for c in range(0, 30000, line_spacing_micrometers):
                if c - w <= y <= c + w:
                    return True
            return False

    def is_on_diagonal_line(self, x, y, line_spacing_micrometers=300, line_width_micrometers=15):
            '''Checks if a point lies on a diagonal line'''
            w = line_width_micrometers / 2  # Half of the line width
            for c in range(-30000, 30000, line_spacing_micrometers):
                if c - w <= y - x <= c + w or c - w <= y + x <= c + w:
                    return True
            return False

    def find_and_rotate_points(self, triple):
        '''Knowing the triples that lie on the thin lines, those could be connected via a line at set angles. This returns the possible pixels at different angles'''
        rotated_translated_sets = {}
        x0, y0 = self.x0, self.y0
        x1, y1 = triple[0].x, triple[0].y
        x2, y2 = triple[1].x, triple[1].y
        x3, y3 = triple[2].x, triple[2].y

        # Calculate the angle between each pair of points in the triple
        def angle_between_points(x1, y1, x2, y2):
            return math.degrees(math.atan2(y2 - y1, x2 - x1))

        angle_with_horizontal_1_2 = angle_between_points(x1, y1, x2, y2)
        angle_with_horizontal_1_3 = angle_between_points(x1, y1, x3, y3)
        angle_with_horizontal_2_3 = angle_between_points(x2, y2, x3, y3)

        # Average angle for the triple
        average_angle = (angle_with_horizontal_1_2 + angle_with_horizontal_1_3 + angle_with_horizontal_2_3) / 3

        target_angles = [0, 45, -45, 180, 135, -135]

        for target_angle in target_angles:
            rotation_needed = target_angle - average_angle
            new_coords = [Pixel(pixel.x, pixel.y, pixel.value) for pixel in self.pixels]
            for pixel in new_coords:
                pixel.rotate(rotation_needed, x0, y0)

            # Calculate translations needed for alignment
            ref_x1, ref_y1 = self.rotate_point(x1, y1, rotation_needed, x0, y0)
            ref_x2, ref_y2 = self.rotate_point(x2, y2, rotation_needed, x0, y0)
            ref_x3, ref_y3 = self.rotate_point(x3, y3, rotation_needed, x0, y0)

            translation_needed_x = -ref_x1
            translation_needed_y = -ref_y1

            translated_coords = []
            for pixel in new_coords:
                nx, ny = pixel.x - x0, pixel.y - y0
                translated_coords.append(Pixel(nx + translation_needed_x, ny + translation_needed_y, pixel.value))

            rotated_translated_sets[target_angle] = translated_coords

        return rotated_translated_sets

    def rotate_point(self, x, y, angle, center_x, center_y):
        '''Rotates a point around a center point by a given angle in degrees'''
        angle = math.radians(angle)  # Convert angle to radians for math functions
        x -= center_x  # Translate point to origin
        y -= center_y
        new_x = x * math.cos(angle) - y * math.sin(angle)  # Apply rotation transformation
        new_y = x * math.sin(angle) + y * math.cos(angle)
        return new_x + center_x, new_y + center_y  # Translate point back


class Grid:
    '''This class takes the output image and turns it into a grid for manipulation in the algorithm'''
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.matrix = self.process_images()  # Process images into a matrix
        self.bst = self.build_bst()  # Build a binary search tree from the matrix

    def process_images(self):
        '''This parses the image files and creates a matrix of 1s and 0s corresponding to pixel color'''
        squares_matrix = []  # List to store the matrix values
        for i in range(100):
            file_path = f"{self.folder_path}/{i}.png"
            img = Image.open(file_path).convert('L')  # Convert image to grayscale
            pixels = img.load()

            for grid_y in range(10):
                for grid_x in range(10):
                    center_x = grid_x * 60 + 10
                    center_y = grid_y * 60 + 10
                    pixel_value = pixels[center_x, center_y]  # Get the pixel value at the center
                    squares_matrix.append(1 if pixel_value < 128 else 0)  # Append 1 if pixel is black, 0 if white

        return self.reshape_list_to_matrix(squares_matrix, size=100)  # Reshape the list into a matrix

    @staticmethod
    def reshape_list_to_matrix(flat_list, size=100):
        '''Reshapes a flat list into a matrix of given size'''
        return [flat_list[i * size:(i + 1) * size] for i in range(size)]

    def build_bst(self):
        '''This method builds a binary search tree with a binary number corresponding to every location'''
        pattern_dict = self.get_5x5_sections()  # Get 5x5 sections from the matrix
        bst = BinarySearchTree()
        for binary_number, coord in pattern_dict.items():
            bst.insert(binary_number, coord)  # Insert binary number and coordinates into BST
        return bst

    def get_5x5_sections(self):
        '''Generates a dictionary of 5x5 sections of the matrix and their corresponding binary numbers'''
        pattern_dict = {}
        for i in range(3, 97):  # Iterate over the matrix with a margin of 2
            for j in range(3, 97):
                section = [self.matrix[x][y] for x in range(i - 2, i + 3) for y in range(j - 2, j + 3)]  # Extract 5x5 section
                binary_number = ''.join(map(str, section))  # Convert section to binary number
                pattern_dict[binary_number] = (i, j)  # Map binary number to coordinates
        return pattern_dict

    def get_value_from_matrix(self, x_micrometers, y_micrometers):
        '''Gets the value from the matrix at specified coordinates in micrometers'''
        x_index = self.micrometer_to_index(x_micrometers)  # Convert x-coordinate to matrix index
        y_index = self.micrometer_to_index(y_micrometers)  # Convert y-coordinate to matrix index
        
        if 0 <= x_index < 100 and 0 <= y_index < 100:
            value = self.matrix[y_index][x_index]  # Get value from matrix
            return value
        else:
            return None  # Return None if coordinates are out of bounds

    @staticmethod
    def micrometer_to_index(coord, square_size=300):
        '''Converts coordinates in micrometers to matrix index'''
        return coord // square_size



class Node:
    '''Represents a node in the binary search tree'''
    def __init__(self, key, coord=None):
        self.left = None
        self.right = None
        self.key = key
        self.coord = coord


class BinarySearchTree:
    '''Includes methods to build a Binary Search Tree from which the coordinates are searched'''
    def __init__(self):
        self.root = None

    def insert(self, key, coord):
        '''Inserts a key-coordinate pair into the BST'''
        if self.root is None:
            self.root = Node(key, coord)  # If tree is empty, set root node
        else:
            self._insert(self.root, key, coord)  # Otherwise, insert recursively

    def _insert(self, node, key, coord):
        '''Recursive helper method for inserting a key-coordinate pair'''
        if key < node.key:
            if node.left is None:
                node.left = Node(key, coord)
            else:
                self._insert(node.left, key, coord)
        else:
            if node.right is None:
                node.right = Node(key, coord)
            else:
                self._insert(node.right, key, coord)

    def search(self, key):
        '''Searches for a key in the BST and returns its coordinates'''
        return self._search(self.root, key)

    def _search(self, node, key):
        '''Recursive helper method for searching a key in the BST'''
        if node is None:
            return None
        elif node.key == key:
            return node.coord
        elif key < node.key:
            return self._search(node.left, key)
        else:
            return self._search(node.right, key)

    def print_tree(self):
        '''Prints the entire tree'''
        self._print_tree(self.root)

    def _print_tree(self, node):
        '''Recursive helper method for printing the tree'''
        if node:
            self._print_tree(node.left)
            print(f'Key: {node.key}, Coord: {node.coord}')
            self._print_tree(node.right)

class ImageProcessor:
    """This class pulls everything together. For a given image it returns all possible coordinates"""
    def __init__(self, folder_path):
        self.grid = Grid(folder_path)  # Initialize the grid with the folder path
        self.found_coordinates = []  # List to store found coordinates
        logging.basicConfig(filename='image_processor_debug.log', level=logging.DEBUG, format='%(message)s')

    def main(self, desired_results=100):
        '''Main method to process the image and find coordinates'''
        margin = 2000
        x0 = random.randint(margin, 30000 - margin)  # Random starting x-coordinate
        y0 = random.randint(margin, 30000 - margin)  # Random starting y-coordinate

        step = {0: 360, 1: 45, 2: 22.5, 3: 18, 4: 18, 5: 18, 6: 12, 7: 15, 8: 12}  # Step sizes for angle increments
        max_iterations = 1000  # Increase the maximum number of iterations
        iteration_count = 0  # Initialize count of iterations

        angle_combinations = [(theta1, theta2, theta3)
                              for theta1 in np.arange(0, math.pi * 2, math.pi / 6)
                              for theta2 in np.arange(0, math.pi / 12, math.pi / 24)
                              for theta3 in np.arange(0, math.pi / 12, math.pi / 24)]

        while len(self.found_coordinates) < desired_results and iteration_count < max_iterations:
            # Make slight adjustments to x0 and y0 each iteration
            x0 += random.uniform(-100, 100)
            y0 += random.uniform(-100, 100)

            x0 = max(min(x0, 30000 - margin), margin)  # Ensure x-coordinate is within bounds
            y0 = max(min(y0, 30000 - margin), margin)  # Ensure y-coordinate is within bounds

            for theta1, theta2, theta3 in angle_combinations:
                circle = CircleArrangement(x0, y0, 300, step, theta1, theta2, theta3)  # Create a circle arrangement
                logging.debug(f'Pixels generated: {[(pixel.x, pixel.y) for pixel in circle.pixels]}')

                aligned_triples = circle.check_lines()  # Check for aligned triples
                logging.debug(f"Aligned triples found: {[(triple[0].x, triple[0].y, triple[1].x, triple[1].y, triple[2].x, triple[2].y) for triple in aligned_triples]}")
                
                if not aligned_triples:
                    continue

                point_values = [(pixel, self.grid.get_value_from_matrix(int(pixel.x), int(pixel.y))) for pixel in circle.pixels]
                logging.debug(f"Searching for point values: {point_values}")

                for triple in aligned_triples:
                    rotated_sets = circle.find_and_rotate_points(triple)  # Find and rotate points
                    for angle, rotated_coords in rotated_sets.items():
                        binary_number = self.calculate_binary_number(rotated_coords, point_values, angle)  # Calculate binary number
                        search_result = self.grid.bst.search(binary_number)  # Search for binary number in BST
                        if search_result:
                            logging.debug(f"Found at: {search_result}")
                            self.found_coordinates.append(search_result)  # Append found coordinates

            iteration_count += 1

        logging.debug(f"Total iterations: {iteration_count}")
        return self.found_coordinates
    


    @staticmethod
    def calculate_binary_number(coords, point_values, angle):
        '''Calculates the binary number for a set of coordinates after rotation'''
        grid_size = 5
        cell_size = 300  # Assuming 300 micrometers per grid cell
        grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]  # Create a 5x5 grid initialized to 0

        # Map coordinates to values
        coord_to_value = {(round(pixel.x), round(pixel.y)): value for pixel, value in point_values}
        logging.debug(f"coord_to_value mapping: {coord_to_value}")

        # Centering logic: Translate coordinates to be around (0, 0) if not already centered
        center_x = sum(pixel.x for pixel in coords) / len(coords)
        center_y = sum(pixel.y for pixel in coords) / len(coords)

        transformed_coords = [
            Pixel(*rotate_point(pixel.x, pixel.y, angle, center_x, center_y), pixel.value)
            for pixel in coords
        ]

        # Invert the coordinates to ensure they are positive
        positive_transformed_coords = [
            Pixel(pixel.x * -1, pixel.y * -1, pixel.value) for pixel in transformed_coords
        ]

        grid_coords = [
            Pixel(*rotate_point(pixel.x - center_x, pixel.y - center_y, angle, 0, 0), pixel.value)
            for pixel in coords
        ]

        logging.debug(f"Transformed coordinates: {[(round(pixel.x), round(pixel.y)) for pixel in positive_transformed_coords]}")
        logging.debug(f"Grid coordinates: {[(round(pixel.x), round(pixel.y)) for pixel in grid_coords]}")

        for grid_pixel, transformed_pixel in zip(grid_coords, positive_transformed_coords):
            x, y = round(grid_pixel.x), round(grid_pixel.y)  # Round the coordinates
            grid_x = (x // cell_size) + grid_size // 2  # Translate to grid coordinates
            grid_y = (y // cell_size) + grid_size // 2

            logging.debug(f"Grid coordinate: ({x}, {y}) -> Grid coordinate: ({grid_x}, {grid_y})")

            if 0 <= grid_x < grid_size and 0 <= grid_y < grid_size:
                tx, ty = round(transformed_pixel.x), round(transformed_pixel.y)
                logging.debug(f"Looking up value for transformed coordinate ({tx}, {ty})")
                value = coord_to_value.get((tx, ty), 0)  # Adjust lookup to original coordinates
                if value != 0:
                    logging.debug(f"Setting grid[{grid_y}][{grid_x}] = {value} for transformed coordinate ({tx}, {ty})")
                grid[grid_y][grid_x] = value  # Set the value in the grid

        logging.debug(f"Grid after setting values: {grid}")

        binary_number = ''.join(str(bit) for row in grid for bit in row)  # Convert grid to binary number
        logging.debug(f"Generated binary number: {binary_number}")
        return binary_number
        
    
def visualize_coord_to_value(coord_to_value, image_size=(500, 500), point_size=5):
    '''
    Visualizes the coord_to_value mapping as an image.
    Red for value 1 and blue for value 0.
    '''
    # Create a blank image with a white background
    img = Image.new('RGB', image_size, color='white')
    draw = ImageDraw.Draw(img)

    # Normalize the coordinates to fit within the image
    coords = list(coord_to_value.keys())
    min_x = min(x for x, y in coords)
    min_y = min(y for x, y in coords)
    max_x = max(x for x, y in coords)
    max_y = max(y for x, y in coords)

    scale_x = (image_size[0] - point_size) / (max_x - min_x)
    scale_y = (image_size[1] - point_size) / (max_y - min_y)

    for (x, y), value in coord_to_value.items():
        # Normalize coordinates
        norm_x = (x - min_x) * scale_x
        norm_y = (y - min_y) * scale_y

        # Set the color based on the value
        color = 'red' if value == 1 else 'blue'

        # Draw the point
        draw.ellipse([(norm_x, norm_y), (norm_x + point_size, norm_y + point_size)], fill=color)

    # Show the image
    img.show()

    
     
def rotate_point(x, y, angle, center_x, center_y):
    '''Rotates a point around a center point by a given angle in degrees'''
    angle = math.radians(angle)  # Convert angle to radians for math functions
    x -= center_x  # Translate point to origin
    y -= center_y
    new_x = x * math.cos(angle) - y * math.sin(angle)  # Apply rotation transformation
    new_y = x * math.sin(angle) + y * math.cos(angle)
    new_x += center_x  # Translate point back
    new_y += center_y
    return new_x, new_y



# Example usage

if __name__ == "__main__":
    processor = ImageProcessor("/Users/Xiejun/Desktop/Omniplaner/parts")
    coordinates_list = processor.main()
    print(coordinates_list)


    

