import os
from PIL import Image

class Grid:
    '''This class takes the output image and turns it into a grid for manipulation in the algorithm'''
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.matrix = self.process_images()  # Process images into a matrix
        self.bst = self.build_bst()  # Build a binary search tree from the matrix

    def process_images(self):
        '''This parses the image files and creates a matrix of 1s and 0s corresponding to pixel color'''
        squares_matrix = []  # List to store the matrix values
        for i in range(9):  # Process only 8 files
            file_path = f"{self.folder_path}/{i}.png"
            try:
                img = Image.open(file_path).convert('L')  # Convert image to grayscale
            except FileNotFoundError:
                print(f"File {file_path} not found.")
                continue

            pixels = img.load()
            for grid_y in range(10):
                row = []
                for grid_x in range(10):
                    center_x = grid_x * 60 + 30  # Adjusting the center point to better capture the pixel value
                    center_y = grid_y * 60 + 30
                    pixel_value = pixels[center_x, center_y]  # Get the pixel value at the center
                    row.append(1 if pixel_value < 128 else 0)  # Append 1 if pixel is black, 0 if white
                squares_matrix.append(row)

        return squares_matrix  # No need to reshape since we are building rows directly

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
        matrix_size = len(self.matrix)
        print(matrix_size)
        for i in range(matrix_size - 4):  # Adjusted range to avoid index out of range
            for j in range(matrix_size - 4):
                section = []
                try:
                    for x in range(i, i + 5):
                        for y in range(j, j + 5):
                            section.append(self.matrix[x][y])
                except IndexError as e:
                    print(f"IndexError at i={i}, j={j}: {e}")
                    continue
                binary_number = ''.join(map(str, section))  # Convert section to binary number
                pattern_dict[binary_number] = (j, i)  # Swap the coordinates to match the expected orientation
        return pattern_dict

    def get_value_from_matrix(self, x_micrometers, y_micrometers):
        '''Gets the value from the matrix at specified coordinates in micrometers'''
        x_index = self.micrometer_to_index(x_micrometers)  # Convert x-coordinate to matrix index
        y_index = self.micrometer_to_index(y_micrometers)  # Convert y-coordinate to matrix index
        
        if 0 <= x_index < 10 and 0 <= y_index < 10:
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

if __name__ == "__main__":
    folder_path = "C:/Users/Xiejun/Desktop/Omniplaner/test"  
    grid = Grid(folder_path)
    grid.bst.print_tree()