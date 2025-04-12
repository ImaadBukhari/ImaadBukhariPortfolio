from PIL import Image, ImageDraw
import random
import os
import math
import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'Stylus_Data'
}

def save_image(img, filename, directory="squares"):
    """Self explanatory"""
    current_directory = os.getcwd()
    folder_path = os.path.join(current_directory, directory)

    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filepath = os.path.join(folder_path, filename)
    img.save(filepath)

def create_table(cursor):
    # Create a table with 81 output columns and 109 input columns
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Electrodes1 (
        id INT AUTO_INCREMENT PRIMARY KEY,
        """ +
        ', '.join([f'output{i} TINYINT(1)' for i in range(1, 82)]) +
        ', ' +
        ', '.join([f'input{i} TINYINT(1)' for i in range(1, 110)]) +
        ")"
    )

    # Commit the table creation
    cursor.execute("COMMIT")
        
def create_image(pattern_path):
    """Creates the pattern and returns"""
    
    # Create a 240 x 240 pixel image
    img = Image.new('RGB', (1500, 1500), color='black')  

    # Create a drawing object
    draw = ImageDraw.Draw(img)

    # Probability of the center 9x9 squares being white
    probability_of_white = random.random()

    count = 1
    binary = ""
    # Loop through the center 9x9 squares
    for row in range(15):
        for col in range(15):
            probability_of_white = random.random()
            if random.random() < probability_of_white:
                color = 'white'
                if (3<=row<12) and (3<=col<12):
                    binary += "0"
                    count += 1
                    
            else:
                color = 'black'
                if (3<=row<12) and (3<=col<12):
                    binary += "1"
                    count += 1
                    

            # Draw the 20x20 pixel square
            draw.rectangle([(col * 100, row * 100), ((col + 1) * 100, (row + 1) * 100)], fill=color)

    save_image(img,pattern_path)

    return binary
    

def upload_electrode_data(pattern_path,new_path):
    current_directory = os.getcwd()
    folder_path = os.path.join(current_directory, "squares")
    filepath = os.path.join(folder_path, pattern_path)
    pattern_image = Image.open(filepath).convert("L")
    #draw = ImageDraw.Draw(pattern_image)
    
    dot_list = []
    x0 = 750 + random.randint(-50,50)
    y0 = 750 + random.randint(-50,50)
    angle1 = random.randint(-500,500)/50
    angle2 = random.randint(-500,500)/25
    angle3 = random.randint(-500,500)/25
    theta1 = math.radians(angle1)
    theta2 = math.radians(angle2)
    theta3 = math.radians(angle3)
    count = 0
    counter = 0
    input_values = []
    step = {0:360,1:60, 2:30, 3:24, 4:18, 5:15,6:12,7:15, 8:12} #Use this dictionary to adjust the angles where dots are placed for every radius of the circle
    for y in range(0,  int(6* 100), int(0.9*100)):
        for x in range(0,360,step[counter]):
            ang = math.radians(x)
            center_x = x0 + int(y*math.sin(ang))
            center_y = y0 - int(y*math.cos(ang))
            new_x = center_x - x0
            new_y = center_y - y0
            new_z = 0

            calc_x = new_x*math.cos(theta1) - new_y*math.sin(theta1)
            calc_y = new_x*math.sin(theta1) + new_y*math.cos(theta1)
            calc_z = 0

            calc_y = calc_y*math.cos(theta2) - calc_z*math.sin(theta2)
            calc_z = calc_y*math.sin(theta2) + calc_z*math.cos(theta2)

            calc_x = calc_x*math.cos(theta3) + calc_z*math.sin(theta3)
            calc_z = calc_z*-1*math.sin(theta3) + calc_z*math.cos(theta3)
            
            rotated_x = int(x0 + calc_x)
            rotated_y = int(y0 + calc_y)
            pixel_value = pattern_image.getpixel((rotated_x, rotated_y))

            input_values.append(1 if pixel_value < 128 else 0)
                
            #for i in range(center_x - 1, center_x + 2):
                #for j in range(center_y - 1, center_y + 2):
                    #draw.point((i, j), fill="blue")
            #for i in range(rotated_x - 4, rotated_x + 5):
                #for j in range(rotated_y - 4, rotated_y + 5):
                    #draw.point((i, j), fill="red")
                
            count += 1
        counter +=1

    
    
    #save_image(pattern_image,new_path)

    return input_values



if __name__ == "__main__":
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    create_table(cursor)
    
    for pattern_index in range(0,10000):
        pattern_path = f"pattern{pattern_index}.png"
    
        # Assuming create_image returns the binary string
        binary_string = create_image(pattern_path)

        for new_index in range(50):
            new_path = f"pattern{pattern_index}_{new_index}.png"
            
            # Assuming upload_electrode_data returns the input list
            input_list = upload_electrode_data(pattern_path, new_path)
            
            # Combine input and output values into a single list
            combined_values = [int(bit) for bit in binary_string] + input_list
            
            # Assuming upload_electrode_data updates the Electrodes table
            cursor.execute(f"INSERT INTO Electrodes1 ({', '.join([f'output{i}' for i in range(1, len(binary_string) + 1)])}, {', '.join([f'input{i}' for i in range(1, len(input_list) + 1)])}) VALUES ({', '.join(['%s' for _ in combined_values])})", tuple(combined_values))
            
    connection.commit()
    connection.close()
   


