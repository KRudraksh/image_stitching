import os
from PIL import Image
import sys

# Function to resize images to 912x513 and save them
def resize_images(input_folder, output_folder):
    # Check if the output folder exists, if not, create it
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Loop through all files in the input folder
    for filename in os.listdir(input_folder):
        # Construct full file path
        file_path = os.path.join(input_folder, filename)
        
        # Check if the file is an image by its extension
        if filename.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif')):
            with Image.open(file_path) as img:
                # Resize the image to 912x513
                resized_img = img.resize((912, 513))
                
                # Save the resized image to the output folder with the same filename
                output_path = os.path.join(output_folder, filename)
                resized_img.save(output_path)
                print(f"Saved resized image to {output_path}")

if __name__ == "__main__":
    # Check if the correct number of arguments are passed
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_folder> <output_folder>")
        sys.exit(1)
    
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    
    # Resize images
    resize_images(input_folder, output_folder)
