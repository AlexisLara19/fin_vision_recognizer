import cv2
import numpy as np

def apply_brightness(image, value):
    """
    Aplica el ajuste de brillo (iluminación) a la imagen usando cv2.convertScaleAbs.
    :param image: Matriz de imagen (BGR).
    :param value: Valor de ajuste (-100 a 100).
    :return: Imagen procesada.
    """
    # alpha=1 (contraste no se toca), beta=value (brillo)
    return cv2.convertScaleAbs(image, alpha=1, beta=value)

def apply_lightness_and_contrast(image, brightness_value, contrast_factor):
    """
    Aplica el ajuste de brillo (beta) y contraste (alpha) a la imagen usando cv2.convertScaleAbs.
    :param image: Matriz de imagen (BGR).
    :param brightness_value: Valor de ajuste del brillo (-100 a 100).
    :param contrast_factor: Factor de contraste (1.0 a 3.0).
    :return: Imagen procesada.
    """
    # Alpha controla el contraste, Beta controla el brillo/iluminación
    return cv2.convertScaleAbs(image, alpha=(contrast_factor), beta=brightness_value)

def apply_histogram_equalization(image):
    """
    Ecualización de Histograma: Mejora el contraste global.
    Se aplica al canal Y (luminancia) en el espacio de color YUV para imágenes a color.
    :param image: Matriz de imagen (BGR).
    :return: Imagen con histograma ecualizado.
    """
    """img_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    
    # Ecualizar el histograma solo en el canal Y (luminancia)
    img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
    
    # Convertir de YUV a BGR
    return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)"""

    # Crear el objeto CLAHE
    """clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    # Convertir la imagen a YUV, aplicar CLAHE al canal Y y volver a BGR
    img_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    img_yuv[:, :, 0] = clahe.apply(img_yuv[:, :, 0])
    result_img = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

    return cv2.cvtColor(result_img, cv2.COLOR_YUV2BGR)"""
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    result_gray = cv2.equalizeHist(gray_img)
    return cv2.cvtColor(result_gray, cv2.COLOR_GRAY2BGR) 

def apply_mask(image, mask_type):
    """
    Aplica diferentes filtros (máscaras) a la imagen.
    :param image: Matriz de imagen (BGR).
    :param mask_type: Tipo de filtro ('Escala de Grises', 'Filtro Gaussiano', 'Detección de Bordes (Canny)').
    :return: Imagen procesada (o None si el tipo no es reconocido).
    """
    processed_img = image.copy()
    
    if mask_type == "Escala de Grises":
        processed_img = cv2.cvtColor(processed_img, cv2.COLOR_BGR2GRAY)
        # Convertir a BGR de nuevo para consistencia en la visualización
        processed_img = cv2.cvtColor(processed_img, cv2.COLOR_GRAY2BGR) 

    elif mask_type == "Filtro Pasa Bajos (Averaging)":
        # ¡Nuevo!: Filtro de media (Averaging), elimina ruido y suaviza (Desenfoque).
        processed_img = cv2.blur(processed_img, (7, 7)) # Kernel 7x7
        
    elif mask_type == "Filtro Pasa Altos (Laplaciano)":
        # ¡Nuevo!: Filtro Laplaciano, resalta bordes y transiciones rápidas (Afilado).
        
        # 1. Convertir a escala de grises
        gray = cv2.cvtColor(processed_img, cv2.COLOR_BGR2GRAY)
        # 2. Aplicar Laplaciano
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        # 3. Convertir de vuelta a 8-bit y BGR para visualización
        laplacian_8bit = cv2.convertScaleAbs(laplacian)
        processed_img = cv2.cvtColor(laplacian_8bit, cv2.COLOR_GRAY2BGR)
        
    elif mask_type == "Filtro Gaussiano":
        # Kernel 5x5 para suavizado
        processed_img = cv2.GaussianBlur(processed_img, (5, 5), 0)
        
    elif mask_type == "Detección de Bordes (Canny)":
        gray = cv2.cvtColor(processed_img, cv2.COLOR_BGR2GRAY)
        # Ajustar umbrales según se requiera
        edges = cv2.Canny(gray, 100, 200) 
        # Convertir la imagen de bordes a BGR para mostrar
        processed_img = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
    elif mask_type == "Ninguna":
        pass # No hacer nada

    return processed_img

def apply_digital_zoom(image, factor):
    """
    Aplica zoom digital recortando el centro de la imagen y re-escalando.
    :param image: Matriz de imagen (BGR).
    :param factor: Factor de zoom (ej. 1.0, 2.5).
    :return: Imagen con zoom aplicado.
    """
    if factor <= 1.0 or image is None:
        return image
    h, w = image.shape[:2]
    new_w = int(w / factor)
    new_h = int(h / factor)
    start_x = (w - new_w) // 2
    start_y = (h - new_h) // 2
    cropped = image[start_y:start_y + new_h, start_x:start_x + new_w]
    
    return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)

def process_roi_heavy(image, brightness, contrast, equalize, mask_type, 
                     thresh_active, thresh_val, thresh_type, erode, dilate):
    """
    Aplica el procesamiento PESADO (Morfología, Filtros, Color).
    Esta función se usará SOLO en el pequeño recorte del ROI.
    """
    if image is None: return None
    
    # Nota: NO aplicamos zoom aquí, el zoom ya viene aplicado en la imagen de entrada
    
    # 1. Filtros Espaciales
    processed = apply_mask(image, mask_type)
    
    # 2. Ecualización
    if equalize:
        processed = apply_histogram_equalization(processed)
        
    # 3. Brillo y Contraste
    processed = apply_lightness_and_contrast(processed, brightness, contrast)
    
    # 4. Umbralización y Morfología (Lo más pesado)
    processed = apply_threshold_and_morphology(
        processed, thresh_active, thresh_val, thresh_type, erode, dilate
    )
    
    return processed

def apply_threshold_and_morphology(image, active, value, type, erode_iter, dilate_iter):
    """
    Aplica umbralización y luego operaciones morfológicas (erosión/dilatación).
    :param image: Matriz de imagen (BGR).
    :param active: Si la umbralización está activa (bool).
    # ... (resto de parámetros)
    :return: Imagen procesada (BGR para visualización).
    """
    if not active:
        # Si no está activo, retornamos la imagen tal cual (sin umbralizar)
        return image 
        
    # Paso 1: Convertir a Gris (Requisito para cv2.threshold)
    # Siempre convertimos a gris antes del thresholding.
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Paso 2: Umbralización (Thresholding)
    # max_value es 255.
    _, thresh_img = cv2.threshold(gray_img, value, 255, type)
    
    # Paso 3: Operaciones Morfológicas (Erosión y Dilatación)
    
    # Crear un kernel simple (matriz de 3x3 de unos)
    kernel = np.ones((2, 2), np.uint8)
    
    # Aplicar Erosión
    if erode_iter > 0:
        thresh_img = cv2.erode(thresh_img, kernel, iterations=erode_iter)

        
    # Aplicar Dilatación
    if dilate_iter > 0:
        thresh_img = cv2.dilate(thresh_img, kernel, iterations=dilate_iter)

    
    # Paso 4: Convertir a BGR para visualización en PyQt5
    return cv2.cvtColor(thresh_img, cv2.COLOR_GRAY2BGR)

def process_image(image, brightness_value, contrast_factor, equalize_hist, mask_type, zoom_factor, 
                  threshold_active, thresh_value, thresh_type, erode_iterations, dilate_iterations):
    """
    Función de utilidad para aplicar todos los procesos en orden.
    """
    if image is None:
        return None
        
    # 1. Aplicar Zoom Digital (se aplica primero sobre la imagen original)
    processed_img = apply_digital_zoom(image, zoom_factor)

    #processed_img = apply_mask(processed_img, mask_type)
        
    # 2. Aplicar Ecualización de Histograma
    if equalize_hist:
        processed_img = apply_histogram_equalization(processed_img)
        
    # 3. Aplicar Brillo y Contraste (Ajustes lineales)
    processed_img = apply_lightness_and_contrast(processed_img, brightness_value, contrast_factor)
    
    # 4. Aplicar Máscara/Filtro (Filtros espaciales)
    processed_img = apply_mask(processed_img, mask_type)

    # 5. Aplicar Umbralización y Morfología (se aplica al final para obtener imagen binaria)
    processed_img = apply_threshold_and_morphology(
        processed_img, 
        threshold_active, 
        thresh_value, 
        thresh_type, 
        erode_iterations, 
        dilate_iterations
    )
    
    return processed_img