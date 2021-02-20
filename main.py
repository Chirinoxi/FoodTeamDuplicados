import os
from image_processor import *

def main():

	images_dir = input("Ingrese el directorio en donde están sus imágenes: ")

	while(not os.path.isdir(images_dir)):
		images_dir = input("Ingrese el directorio en donde están sus imágenes: ")

	our_image_processor = ImageProcessor(images_dir=images_dir)
	our_image_processor.delete_repeated_images()

if __name__ == '__main__':
	main()