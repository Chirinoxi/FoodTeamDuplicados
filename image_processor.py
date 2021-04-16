import os
import cv2
import shutil
import numpy as np
from PIL import Image

class ImageProcessor:

	def __init__(self, images_dir):
		self.current_dir = images_dir	

	def manhattan_distance(self, x, y):
		""" Calcula la 'distancia de manhattan' entre dos vectores.

			Parámetros:
			-----------
				- x (numpy): Primer vector.
				- y (numpy): Segundo vector.
		"""
		return (sum(abs(a-b) for a,b in zip(x,y)))/len(x)

	def compare_images(self, image1, image2):
		""" Compara dos imágenes en formato numpy, utilizando la métrica L1 (distancia de manhattan).

			Parámetros:
			-----------	
				- image1 (numpy): Primera imagen. 
				- image2 (numpy): Segunda imagen. 
		"""
		is_equal = False
		distance = self.manhattan_distance(image1, image2)
		
		# UMBRAL ====> 5%
		if(distance <= 0.05):
			is_equal = True
			
		return (is_equal, distance)

	def rename_files(self, directory):
		""" Renombra los ficheros de un directorio

			Parámetros:
			-----------
			- directory (string): directorio en donde se encuentran los ficheros.
		"""		
		files = sorted(os.listdir(directory))
		for i in range(len(files)):
			if(os.path.isdir(directory+files[i])):
				continue
			else:
				file_info = files[i].split('.')
				if (i >= 99):
					os.rename(f'{directory}{files[i]}', f'{directory}image_foodteam_{i+1}.{file_info[-1]}')
				elif (i >= 9):
					os.rename(f'{directory}{files[i]}', f'{directory}image_foodteam_0{i+1}.{file_info[-1]}')
				else:
					os.rename(f'{directory}{files[i]}', f'{directory}image_foodteam_00{i+1}.{file_info[-1]}')

	def resize_images(self, images, directory):
		""" Cambia el tamaño de una imagen, para retornar un arreglo con esta últimas con dimensionalidad 30x30.

			Parámetros:
			----------
				images (numpy): imagenes en formato numpy
				directory (string): directorio en donde se encuentran las imágenes

			Retorna:
			--------
				new_images (list): lista con las imágenes redimensionadas en formato PIL
		"""		
		files = os.listdir(directory)
		new_images = []
		for i in range(len(files)):
			if(os.path.isdir(directory + files[i])):
				continue
			else:
				img = Image.open(directory+files[i]).convert('RGB')
				img = img.resize((30, 30))
				new_images.append(img)
		return new_images

	def min_max_norm(self, data):
		"""Aplica normalización min_max a un input

			Parámetros:
			-----------
				data (numpy): entrada que deseamos normalizar

			Retorna:
			--------
				norm_data (numpy): corresponde al input normalizado
		"""		
		norm_data = (data - np.min(data))/(np.max(data) - np.min(data))
		return norm_data	 	

	def normalize (self, img):
		"""Aplica normalización z-score a un input

			Parámetros:
			-----------
				img (numpy): entrada que deseamos normalizar

			Retorna:
			--------
				norm_data (numpy): corresponde al input normalizado
		"""	
		norm_img =  (img - np.mean(img, axis=0)) /(np.std(img, axis=0))
		return norm_img

	def delete_directories(self, files, directory):
		""" Elimina los directorios dentro de un directorio específico

			Parámetros:
			-----------
				directory (string): directorio de interés
				files (list):     lista que contiene los ficheros

			Retorna:
			--------
				arreglo (list): lista identica a parámetro files, pero no contiene directorios
		"""	
		arreglo = files.copy()
		meta = len(arreglo)
		i = 0;
		while (i < meta):
			if (os.path.isdir(directory+arreglo[i])):
				del arreglo[i]
			meta = len(arreglo)
			i += 1
		return arreglo

	def delete_images(self, directory):
		""" Elimina los directorio dentro de un directorio en específico.

			Parámetros:
			-----------
				directory (string): directorio que contiene las imágened
		"""	
		files = sorted(os.listdir(directory)) # Leemos los archivos el directorio
		files = self.delete_directories(files, directory) # Eliminamos los directorios del arreglo
		splitted_dir = directory.split('/')
		current_food = splitted_dir[-2]
		pil_files = self.resize_images(files, directory) # Creamos un arreglo con los archivos en formato PIL y con dimensionsionalidad 300x300
		for (idx, file) in enumerate(pil_files): # Podríamos recorrer pil_files
			print("Imagen pivote: ", files[idx])
			pivot_image = np.asarray(file)
			pivot_image = self.min_max_norm(pivot_image)
			rango = len(files)
			i = idx
			while (i < rango):
				if (not os.path.isdir(directory+files[i])):
					img_name = files[i]
					deleted_imgs_dir = directory + current_food + "_eliminados"
					full_img_name = deleted_imgs_dir + "/" + img_name
					img_np = np.asarray(pil_files[i])
					img_np = self.min_max_norm(img_np)
					result, distance = self.compare_images(pivot_image.flatten(), img_np.flatten())
					if((idx != i) and (result == True)):
						if(not os.path.exists(deleted_imgs_dir)):
							print("Creando directorio {} !".format(deleted_imgs_dir))
							os.mkdir(deleted_imgs_dir)
						print("Eliminando imagen: ", full_img_name)
						shutil.move(directory+img_name, directory+current_food+"_eliminados/"+img_name)
						#os.remove(directory+img_name) # Si queremos eliminar la imagen descomentar esta línea
						del files[i]
						del pil_files[i]
						rango = len(files)
				i+=1

	def delete_repeated_images(self):
		""" Elimina las imágenes repetidas en un directorio, recorre las carpetas dentro del directorio principal.
		"""	
		self.delete_not_images(self.current_dir) # eliminamos los archivos que NO son imágenes
		files = sorted(os.listdir(self.current_dir)) # Leemos los archivos el directorio
		for file in files:
			element = self.current_dir+file+'/'
			if (os.path.isdir(element)):
				self.rename_files(element)
				print("Eliminando imágenes del directorio: ", element)
				self.delete_corrupted_images(element)
				self.delete_images(element)
			else:
				continue

	def delete_not_images(self, directory):
		""" Elimina los ficheros que no posean extensión de imagen.

			Parámetros:
			-----------
				- directory (string): directorio que contiene los ficheros.
		"""	
		folders = sorted(os.listdir(directory))
		for i in range(len(folders)):
			curr_folder_name = folders[i]
			current_folder_path = os.path.join(directory, curr_folder_name)
			if(os.path.isdir(current_folder_path)):
				folder_images = sorted(os.listdir(current_folder_path))
			else:
				folder_images = folders
				current_folder_path = directory

			for (idx, file) in enumerate(folder_images):
				full_file_name = os.path.join(current_folder_path, file)
				if(os.path.isdir(full_file_name)):
					continue
				else:
					try:
						im=Image.open(full_file_name)
					except IOError:
						print("Eliminando: ", full_file_name)
						os.remove(full_file_name)

	def delete_corrupted_images (self, directory):
		""" Elimina las imágenes corruptas en un directorio.

			Parámetros:
			-----------
				- directory (string): directorio que contiene los ficheros.
		"""	
		files = os.listdir(directory);
		for file in files:
			if (os.path.isdir(directory + file)):
				continue
			else:
				try:
					img = Image.open(directory+file)
					img.verify() #
				except Exception:
					print("Eliminando imagen corrupta: ", file)
					os.remove(directory+file) # Si queremos eliminar la imagen descomentar esta línea
		print("Se han eliminado todas las imágenes corruptas !")