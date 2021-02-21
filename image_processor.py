import os
import cv2
import numpy as np
from PIL import Image

class ImageProcessor:

	def __init__(self, images_dir):
		self.current_dir = images_dir	


	def manhattan_distance(self, x, y):
		""" Calcula la 'distancia de manhattan' entre dos vectores

			Parametros:
			----------
			
				- x: Primer vector 
				- y: Segundo vector
		"""
		return (sum(abs(a-b) for a,b in zip(x,y)))/len(x)

	def compare_images(self, image1, image2):
		is_equal = False
		distance = self.manhattan_distance(image1, image2)
		if(distance <= 0.15 or distance >= 0.95):
			is_equal = True
			
		return (is_equal, distance)

	def rename_files(self, directory):
		files = sorted(os.listdir(directory))
		for i in range(len(files)):
			file_info = files[i].split('.')
			if (i >= 99):
				os.rename(f'{directory}{files[i]}', f'{directory}image_{i+1}.{file_info[-1]}')
			elif (i >= 9):
				os.rename(f'{directory}{files[i]}', f'{directory}image_0{i+1}.{file_info[-1]}')
			else:
				os.rename(f'{directory}{files[i]}', f'{directory}image_00{i+1}.{file_info[-1]}')

	def resize_images(self, images, directory):
		new_images = images.copy() #Creamos una copia de la variable images.
		new_images = list(map(lambda x: Image.open(directory+x).convert('RGB'), images)) # Convertimos todas las imágenes a formato PIL con 3 canales.
		new_images = list(map(lambda x: x.resize((300, 300)), new_images)) # Cambiamos el tamaño de todas las imágenes a 300x300.
		return new_images

	def min_max_norm(self, data):
		norm_data = (data - np.min(data))/(np.max(data) - np.min(data))
		return norm_data	 	

	def normalize (self, img):
		norm_img =  (img - np.mean(img, axis=0)) /(np.std(img, axis=0))
		return norm_img

	def delete_images(self, directory):
		files = sorted(os.listdir(directory)) # Leemos los archivos el directorio
		pil_files = self.resize_images(files, directory) # Creamos un arreglo con los archivos en formato PIL y con dimensionsionalidad 300x300		
		for (idx, file) in enumerate(pil_files): # Podríamos recorrer pil_files
			print('\nLargo arreglo pil_files: ', len(pil_files))
			print('Largo arreglo files: ', len(files), '\n')
			pivot_image = np.asarray(file)
			pivot_image = self.min_max_norm(pivot_image)
			print("Pivot_image: {}".format(files[idx]), '\n')
			rango = len(files)
			i = idx
			while i < rango: # Comparamos desde el pivote en adelante
				#print('Iterador i: {}'.format(i))
				img_name = files[i]
				#print('\nLargo arreglo pil_files: ',len(pil_files))
				#print('Largo arreglo files: ',len(files), '\n')
				print("Comparando imagen {} con {} !".format(files[idx], img_name), '\n')
				img_np = np.asarray(pil_files[i])
				img_np = self.min_max_norm(img_np)
				result, distance = self.compare_images(pivot_image.flatten(), img_np.flatten())
				if((idx != i) and (result == True)):
					print('-'*30)
					print('Removiendo imagen ', img_name)
					print('-'*30, '\n')
					os.remove(directory+img_name)
					del files[i]
					del pil_files[i]
					rango = len(files)
				i+=1


	def delete_repeated_images(self):
		files = sorted(os.listdir(self.current_dir)) # Leemos los archivos el directorio
		for file in files:
			element = self.current_dir+file+'/'
			if (os.path.isdir(element)):
				self.rename_files(element)
				print("Eliminando imágenes del directorio: ", element)
				self.delete_images(element)
			else:
				continue

