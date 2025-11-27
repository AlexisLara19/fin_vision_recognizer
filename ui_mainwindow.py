import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QFrame, 
    QLabel, QSlider, QPushButton, QComboBox, QFileDialog, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage

# Importar las clases y funciones de los otros módulos
from video_thread import VideoThread
from image_processing import process_image
from custom_widgets import ROISelectableLabel, IntensityPlotWidget
from scipy.signal import find_peaks
from image_processing import apply_digital_zoom, process_roi_heavy

class MainWindow(QWidget):
    """Ventana principal de la aplicación con PyQt5 y OpenCV."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Procesamiento de Imágenes Modular (PyQt5 + OpenCV)")
        #self.setGeometry(100, 100, 1000, 700)
        self.setGeometry(100, 100, 1400, 800) # Aumentamos el tamaño
        
        
        # Variables de estado
        self.current_source_image = None  # Almacena la imagen original cargada o el frame de la cámara
        self.current_processed_image = None # Guardamos la imagen procesada actual para el ROI
        # Parámetros de imagen
        self.brightness_value = 0
        self.contrast_factor = 1.0  # ¡Nuevo!: Factor de contraste (Alpha)
        self.equalize_hist = False  # ¡Nuevo!: Estado de ecualización de histograma
        self.mask_type = "Ninguna"
        self.video_thread = None
        self.is_camera_mode = False
        self.focus_value = 0      # Nuevo: Valor de enfoque
        self.zoom_factor = 1.0    # Nuevo: Factor de zoom digital

        self.threshold_active = False # Activa/Desactiva la umbralización
        self.thresh_value = 127       # Valor umbral (0 a 255)
        self.thresh_type = cv2.THRESH_BINARY # Tipo de umbral (e.g., THRESH_BINARY)
        self.erode_iterations = 0     # Iteraciones de erosión
        self.dilate_iterations = 0    # Iteraciones de dilatación

        # Variable para guardar las coordenadas del ROI seleccionado
        # Formato: (x1, y1, x2, y2) referidos a la imagen ORIGINAL (no la pantalla)
        self.roi_coords = None

        self.setup_ui()

    def setup_ui(self):
        # 1. Layout Principal (Horizontal)
        main_layout = QHBoxLayout(self)

        # 2. Área de Controles (Creación de los widgets y sus layouts)
        controls_frame = self._create_controls_panel()

        # --- PANEL CENTRAL (Imagen Principal) ---
        center_frame = QFrame()
        center_frame.setFrameShape(QFrame.StyledPanel)
        center_layout = QVBoxLayout(center_frame)

        self.image_display = ROISelectableLabel()
        self.image_display.setAlignment(Qt.AlignCenter)
        self.image_display.setStyleSheet("background-color: #333; color: white; border: 1px solid #555;")
        self.image_display.setMinimumSize(400, 400)
        # Conectamos la señal de selección
        #self.image_display.roi_selected.connect(self.extract_and_display_roi)
        self.image_display.roi_selected.connect(self.handle_roi_selection)

        center_layout.addWidget(self.image_display)

        # --- SUBPANELES: ROI y Gráfica de Intensidad ---
        subpanels_frame = QFrame()
        subpanels_layout = QHBoxLayout(subpanels_frame)

        # Panel A: Área de Interés (ROI)
        panel_a_group = QFrame()
        panel_a_layout = QVBoxLayout(panel_a_group)
        panel_a_layout.addWidget(QLabel("### 🔍 Panel A: Área de Interés (ROI)"))

        self.roi_display = QLabel("Seleccione un área en la imagen central")
        self.roi_display.setAlignment(Qt.AlignCenter)
        self.roi_display.setStyleSheet("background-color: #333; color: #AAA; border: 1px solid #555;")
        self.roi_display.setFixedSize(600, 400)  # Tamaño fijo para el ROI

        panel_a_layout.addWidget(self.roi_display)

        # Panel B: Perfil de Intensidad
        panel_b_group = QFrame()
        panel_b_layout = QVBoxLayout(panel_b_group)
        panel_b_layout.addWidget(QLabel("### 📈 Panel B: Perfil de Intensidad"))
        self.intensity_plot = IntensityPlotWidget()
        panel_b_layout.addWidget(self.intensity_plot)

        # Agregar sub-paneles al layout horizontal
        subpanels_layout.addWidget(panel_a_group, 1)  # Proporción 1
        subpanels_layout.addWidget(panel_b_group, 1)  # Proporción 1

        # Agregar subpaneles debajo del panel central
        center_layout.addWidget(subpanels_frame)

        # --- Agregar todo al Layout Principal ---
        # Proporciones: Controles(1) : Imagen y Subpaneles(4)
        main_layout.addWidget(controls_frame, 1)
        main_layout.addWidget(center_frame, 4)

        # Inicializar el estado de los controles
        self.select_source(0) 

    def _create_controls_panel(self):
        """Crea y configura el panel de controles."""
        controls_frame = QFrame()
        controls_frame.setFrameShape(QFrame.StyledPanel)
        controls_layout = QVBoxLayout(controls_frame)

        # --- Selección de Fuente ---
        source_group = QFrame()
        source_group.setLayout(QVBoxLayout())
        source_group.layout().addWidget(QLabel("### 📸 Fuente de la Imagen"))
        
        self.source_combo = QComboBox()
        self.source_combo.addItems(["Archivo (Estático)", "Cámara (Tiempo Real)"])
        self.source_combo.currentIndexChanged.connect(self.select_source)
        source_group.layout().addWidget(self.source_combo)
        
        self.load_button = QPushButton("Cargar Imagen desde Archivo")
        self.load_button.clicked.connect(self.load_image_from_file)
        source_group.layout().addWidget(self.load_button)
        
        controls_layout.addWidget(source_group)
        controls_layout.addWidget(QFrame(frameShape=QFrame.HLine))

        # --- Controles de Iluminación ---
        brightness_group = QFrame()
        brightness_grid = QGridLayout(brightness_group)
        brightness_grid.addWidget(QLabel("### 💡 Iluminación (Brillo)"), 0, 0, 1, 2)
        
        """self.brightness_label = QLabel("Valor: 0")
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(self.update_brightness)
        
        brightness_grid.addWidget(QLabel("Brillo:"), 1, 0)
        brightness_grid.addWidget(self.brightness_slider, 1, 1)
        brightness_grid.addWidget(self.brightness_label, 1, 2)
        
        controls_layout.addWidget(brightness_group)
        controls_layout.addWidget(QFrame(frameShape=QFrame.HLine))"""

        # 1. Brillo (Beta)
        self.brightness_label = QLabel("Valor: 0")
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100) 
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(self.update_brightness)
        
        brightness_grid.addWidget(QLabel("Brillo (Beta):"), 1, 0)
        brightness_grid.addWidget(self.brightness_slider, 1, 1)
        brightness_grid.addWidget(self.brightness_label, 1, 2)

        # 2. Contraste (Alpha)
        self.contrast_label = QLabel("Factor: 1.0x")
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(10, 30) # Rango de 1.0x a 3.0x
        self.contrast_slider.setValue(10)
        self.contrast_slider.valueChanged.connect(self.update_contrast)
        
        brightness_grid.addWidget(QLabel("Contraste (Alpha):"), 2, 0)
        brightness_grid.addWidget(self.contrast_slider, 2, 1)
        brightness_grid.addWidget(self.contrast_label, 2, 2)
        
        controls_layout.addWidget(brightness_group)
        controls_layout.addWidget(QFrame(frameShape=QFrame.HLine))

        # --- NUEVO: Ecualización de Histograma ---
        hist_group = QFrame()
        hist_layout = QVBoxLayout(hist_group)
        hist_layout.addWidget(QLabel("### 📈 Mejora de Contraste"))
        
        self.equalization_checkbox = QCheckBox("Ecualización de Histograma (YUV)")
        self.equalization_checkbox.stateChanged.connect(self.toggle_equalization)
        hist_layout.addWidget(self.equalization_checkbox)
        
        controls_layout.addWidget(hist_group)
        controls_layout.addWidget(QFrame(frameShape=QFrame.HLine))

        # --- NUEVOS: Controles de Cámara (Focus y Zoom) ---
        camera_controls_group = QFrame()
        camera_grid = QGridLayout(camera_controls_group)
        camera_grid.addWidget(QLabel("### ⚙️ Ajustes de Cámara"), 0, 0, 1, 3)

        # 1. Control de Enfoque (Focus)
        self.focus_label = QLabel("Valor: -1")
        self.focus_slider = QSlider(Qt.Horizontal)
        self.focus_slider.setRange(0, 255) # Rango típico para OpenCV
        self.focus_slider.setValue(0) # Valor predeterminado de la cámara
        self.focus_slider.valueChanged.connect(self.update_focus)
        
        camera_grid.addWidget(QLabel("Enfoque:"), 1, 0)
        camera_grid.addWidget(self.focus_slider, 1, 1)
        camera_grid.addWidget(self.focus_label, 1, 2)

        # 2. Control de Zoom (Magnificación) - Usaremos un zoom digital
        self.zoom_label = QLabel("Factor: 1.0x")
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(10, 50) # Rango de 1.0x a 5.0x
        self.zoom_slider.setValue(10) 
        self.zoom_slider.valueChanged.connect(self.update_zoom)
        
        camera_grid.addWidget(QLabel("Zoom (Digital):"), 2, 0)
        camera_grid.addWidget(self.zoom_slider, 2, 1)
        camera_grid.addWidget(self.zoom_label, 2, 2)
        
        controls_layout.addWidget(camera_controls_group)
        controls_layout.addWidget(QFrame(frameShape=QFrame.HLine))

        # --- NUEVO: Control de Umbralización y Morfología ---
        thresh_morph_group = QFrame()
        thresh_morph_layout = QVBoxLayout(thresh_morph_group)
        thresh_morph_layout.addWidget(QLabel("### ⚙️ Umbralización y Morfología"))
        
        # 1. Umbralización (Thresholding)
        thresh_layout = QGridLayout()
        
        self.thresh_checkbox = QCheckBox("Activar Umbralización")
        self.thresh_checkbox.stateChanged.connect(self.toggle_thresholding)
        thresh_layout.addWidget(self.thresh_checkbox, 0, 0, 1, 2)

        self.thresh_label = QLabel("Umbral (0-255): 127")
        self.thresh_slider = QSlider(Qt.Horizontal)
        self.thresh_slider.setRange(0, 255)
        self.thresh_slider.setValue(127)
        self.thresh_slider.valueChanged.connect(self.update_threshold_value)
        self.thresh_slider.setDisabled(True) # Deshabilitado por defecto
        
        thresh_layout.addWidget(self.thresh_slider, 1, 0)
        thresh_layout.addWidget(self.thresh_label, 1, 1)
        
        self.thresh_type_combo = QComboBox()
        self.thresh_type_combo.addItems(["BINARIO", "BINARIO INV."])
        self.thresh_type_combo.currentIndexChanged.connect(self.update_threshold_type)
        self.thresh_type_combo.setDisabled(True) # Deshabilitado por defecto
        
        thresh_layout.addWidget(self.thresh_type_combo, 2, 0, 1, 2)
        
        thresh_morph_layout.addLayout(thresh_layout)
        thresh_morph_layout.addWidget(QFrame(frameShape=QFrame.HLine)) # Separador

        # 2. Erosión (Erode)
        erode_layout = QGridLayout()
        self.erode_label = QLabel("Erosión (Iter.): 0")
        self.erode_slider = QSlider(Qt.Horizontal)
        self.erode_slider.setRange(0, 5) # 0 a 5 iteraciones
        self.erode_slider.setValue(0)
        self.erode_slider.valueChanged.connect(self.update_erode_iterations)
        self.erode_slider.setDisabled(True) # Deshabilitado por defecto
        
        erode_layout.addWidget(QLabel("Erosión (Iter.):"), 0, 0)
        erode_layout.addWidget(self.erode_slider, 0, 1)
        erode_layout.addWidget(self.erode_label, 0, 2)
        
        thresh_morph_layout.addLayout(erode_layout)

        # 3. Dilatación (Dilate)
        dilate_layout = QGridLayout()
        self.dilate_label = QLabel("Dilatación (Iter.): 0")
        self.dilate_slider = QSlider(Qt.Horizontal)
        self.dilate_slider.setRange(0, 5) # 0 a 5 iteraciones
        self.dilate_slider.setValue(0)
        self.dilate_slider.valueChanged.connect(self.update_dilate_iterations)
        self.dilate_slider.setDisabled(True) # Deshabilitado por defecto
        
        dilate_layout.addWidget(QLabel("Dilatación (Iter.):"), 0, 0)
        dilate_layout.addWidget(self.dilate_slider, 0, 1)
        dilate_layout.addWidget(self.dilate_label, 0, 2)
        
        thresh_morph_layout.addLayout(dilate_layout)
        
        controls_layout.addWidget(thresh_morph_group)
        controls_layout.addWidget(QFrame(frameShape=QFrame.HLine))


        # --- Controles de Máscara ---
        mask_group = QFrame()
        mask_layout = QVBoxLayout(mask_group)
        mask_layout.addWidget(QLabel("### 🎭 Máscaras/Filtros"))
        
        self.mask_combo = QComboBox()
        self.mask_combo.addItems([
            "Ninguna", 
            "Escala de Grises", 
            "Filtro Pasa Bajos (Averaging)",  # <- ¡Nuevo!
            "Filtro Pasa Altos (Laplaciano)", # <- ¡Nuevo!
            "Filtro Gaussiano", 
            "Detección de Bordes (Canny)"
        ])
        self.mask_combo.currentIndexChanged.connect(self.update_mask)
        mask_layout.addWidget(self.mask_combo)
        
        controls_layout.addWidget(mask_group)

        controls_layout.addStretch(1) 
        return controls_frame

    def calculate_and_plot_projection(self, roi_image):
        """
        Realiza la proyección horizontal: suma de columnas verticales.
        1. Convierte a Escala de Grises (si es necesario).
        2. Suma los valores a lo largo del eje 0 (vertical).
        3. Envía los datos al widget de ploteo.
        """
        # 1. Convertir a escala de grises para tener intensidad (1 canal)
        if len(roi_image.shape) == 3:
            gray_roi = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
        else:
            gray_roi = roi_image

        # 2. Proyección Horizontal (Suma de columnas)
        # axis=0 colapsa las filas, resultando en un array de longitud = ancho de imagen
        vertical_projection = np.sum(gray_roi, axis=0)
        
        # Opcional: Normalizar los datos para que el gráfico no tenga números gigantes
        # vertical_projection = vertical_projection / np.max(vertical_projection)

        # 3. Actualizar el gráfico
        #self.intensity_plot.update_plot(vertical_projection)

    def extract_and_display_roi(self, rect_screen):
        """
        Recibe el rectángulo en coordenadas de PANTALLA (Label), 
        lo convierte a coordenadas de IMAGEN y muestra el recorte en el Panel A.
        """
        #if self.current_processed_image is None:
        #    return

        if self.current_processed_image is None: return
        pixmap = self.image_display.pixmap()
        if not pixmap: return

        """# 1. Obtener dimensiones
        pixmap = self.image_display.pixmap()
        if not pixmap: return"""
        
        # Dimensiones del QLabel (espacio disponible)
        label_w = self.image_display.width()
        label_h = self.image_display.height()
        
        # Dimensiones del Pixmap (imagen escalada mostrada)
        pix_w = pixmap.width()
        pix_h = pixmap.height()
        
        # Dimensiones de la imagen original real
        orig_h, orig_w = self.current_processed_image.shape[:2]

        # 2. Calcular Offsets (Debido a "KeepAspectRatio", hay barras negras o espacios vacíos)
        # El pixmap se centra en el label
        offset_x = (label_w - pix_w) / 2
        offset_y = (label_h - pix_h) / 2

        # 3. Mapear coordenadas del Mouse -> Coordenadas del Pixmap
        # Restamos el offset para saber dónde cayó el click dentro de la imagen visible
        x_start = rect_screen.x() - offset_x
        y_start = rect_screen.y() - offset_y
        #x_end = x_start + rect_screen.width()
        #y_end = y_start + rect_screen.height()
        scale_x = orig_w / pix_w
        scale_y = orig_h / pix_h

        # Validar que estemos dentro de los límites del pixmap visible
        #x_start = max(0, min(x_start, pix_w))
        #y_start = max(0, min(y_start, pix_h))
        #x_end = max(0, min(x_end, pix_w))
        #y_end = max(0, min(y_end, pix_h))

        #if x_end - x_start < 5 or y_end - y_start < 5:
        #    return # Selección inválida o fuera de imagen

        # 4. Mapear coordenadas del Pixmap -> Coordenadas de Imagen Original
        # Factor de escala (Original / Visible)
        scale_x = orig_w / pix_w
        scale_y = orig_h / pix_h

        #real_x1 = int(x_start * scale_x)
        #real_y1 = int(y_start * scale_y)
        #real_x2 = int(x_end * scale_x)
        #real_y2 = int(y_end * scale_y)

        real_x1 = int(max(0, x_start) * scale_x)
        real_y1 = int(max(0, y_start) * scale_y)
        real_x2 = int(min(pix_w, x_start + rect_screen.width()) * scale_x)
        real_y2 = int(min(pix_h, y_start + rect_screen.height()) * scale_y)

        # 5. Recortar la imagen original
        roi_img = self.current_processed_image[real_y1:real_y2, real_x1:real_x2]

        if roi_img.size > 0:
            # Mostrar en Panel A
            #self._display_roi_image(roi_img)

            # --- NUEVO: Calcular y Mostrar Gráfico en Panel B ---
            #self.calculate_and_plot_projection(roi_img)
            self.analyze_roi_peaks(roi_img)

    def handle_roi_selection(self, rect_screen):
        """
        1. Recibe el rectángulo dibujado por el mouse.
        2. Lo convierte a coordenadas de la imagen REAL.
        3. Guarda esas coordenadas en self.roi_coords.
        """
        if self.current_processed_image is None: return
        pixmap = self.image_display.pixmap()
        if not pixmap: return
        
        # Dimensiones
        label_w = self.image_display.width()
        label_h = self.image_display.height()
        pix_w = pixmap.width()
        pix_h = pixmap.height()
        orig_h, orig_w = self.current_processed_image.shape[:2]

        # Calcular Offsets (centrado de imagen)
        offset_x = (label_w - pix_w) / 2
        offset_y = (label_h - pix_h) / 2

        # Mapear coordenadas Mouse -> Pixmap
        x_start = rect_screen.x() - offset_x
        y_start = rect_screen.y() - offset_y
        
        # Factor de escala
        scale_x = orig_w / pix_w
        scale_y = orig_h / pix_h

        # Calcular coordenadas reales en la imagen original
        real_x1 = int(max(0, x_start) * scale_x)
        real_y1 = int(max(0, y_start) * scale_y)
        real_x2 = int(min(pix_w, x_start + rect_screen.width()) * scale_x)
        real_y2 = int(min(pix_h, y_start + rect_screen.height()) * scale_y)
        
        # Validar tamaño mínimo
        if (real_x2 - real_x1) > 5 and (real_y2 - real_y1) > 5:
            # GUARDAMOS LAS COORDENADAS
            self.roi_coords = (real_x1, real_y1, real_x2, real_y2)
            
            # Forzamos una actualización inmediata
            self.update_roi_panels()

    def update_roi_panels(self):
        """
        Toma la imagen actual y las coordenadas guardadas para recortar y analizar.
        Este método se llamará en CADA FRAME del video.
        """
        if self.current_processed_image is None or self.roi_coords is None:
            return

        x1, y1, x2, y2 = self.roi_coords
        
        # Verificar que las coordenadas sigan siendo válidas (por si cambia el tamaño de imagen)
        h, w = self.current_processed_image.shape[:2]
        if x2 > w or y2 > h:
            self.roi_coords = None # Resetear si la imagen cambió drásticamente
            return

        # Recortar usando las coordenadas guardadas
        roi_img = self.current_processed_image[y1:y2, x1:x2]

        if roi_img.size > 0:
            self.analyze_roi_peaks(roi_img)

    def analyze_roi_peaks(self, roi_img):
        """
        1. Calcula proyección.
        2. Encuentra picos.
        3. Dibuja líneas en la imagen ROI.
        4. Actualiza ambos paneles.
        """
        # A. Preparar datos (Escala de Grises)
        if len(roi_img.shape) == 3:
            gray_roi = cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)
            display_roi = roi_img.copy() # Copia a color para dibujar líneas rojas
        else:
            gray_roi = roi_img
            # Convertir a BGR para poder dibujar líneas rojas sobre gris
            display_roi = cv2.cvtColor(roi_img, cv2.COLOR_GRAY2BGR)

        # B. Proyección Horizontal (Suma de columnas)
        vertical_projection = np.sum(gray_roi, axis=0)
        
        # C. Detección de Picos (Crestas)
        # distance=10: Mínima distancia horizontal entre picos para evitar ruido
        # height=...: Mínimo valor para ser considerado pico (promedio global)
        #import scipy.signal
        #print("Scipy version:", scipy.__version__)
        #print("¿Existe find_peaks?", hasattr(scipy.signal, 'find_peaks'))
        
        peaks, _ = find_peaks(
            vertical_projection, 
            distance=50, 
            height=np.mean(vertical_projection)
        )
        
        # D. Dibujar Líneas en la Imagen del ROI
        h, w = display_roi.shape[:2]
        for x_pos in peaks:
            # Dibujar línea vertical roja
            # (x_pos, 0) es el punto superior, (x_pos, h) es el inferior
            cv2.line(display_roi, (x_pos, 0), (x_pos, h), (0, 0, 255), 1)
            
            # Opcional: Escribir el índice o coordenada pequeña
            # cv2.putText(display_roi, str(x_pos), (x_pos, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0,255,0), 1)

        # E. Mostrar Imagen con Líneas en Panel A
        self._display_roi_image(display_roi)
        
        #print(f'Veritcal projection: {type(vertical_projection)} {len(vertical_projection)}')
        #print(f'peaks: {type(peaks)} {len(peaks)}')

        # F. Mostrar Gráfico con Picos marcados en Panel B
        #self.intensity_plot.update_plot(vertical_projection, peaks)

    def _display_roi_image(self, cv_img):
        """Muestra la imagen recortada en el Panel A."""
        # Convertir BGR a RGB
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        
        qt_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)
        
        # Escalar al tamaño del recuadro del Panel A
        self.roi_display.setPixmap(
            pixmap.scaled(
                self.roi_display.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
        )
    # --- NUEVOS Métodos de Interacción ---

    def update_focus(self, value):
        """Intenta establecer el enfoque de la cámara y actualiza la etiqueta."""
        self.focus_value = value
        self.focus_label.setText(f"Valor: {value}")
        
        # Aplicar el enfoque SÓLO si estamos en modo cámara
        if self.is_camera_mode and self.video_thread and self.video_thread.cap:
            try:
                # Establecer la propiedad CAP_PROP_FOCUS (código 28)
                self.video_thread.cap.set(cv2.CAP_PROP_FOCUS, float(value))
            except Exception as e:
                print(f"Advertencia: El control de enfoque falló para esta cámara. {e}")

    def update_zoom(self, value):
        """Actualiza el factor de zoom digital y reprocesa la imagen."""
        # Mapea el valor del slider (10 a 50) a un factor (1.0 a 5.0)
        self.zoom_factor = value / 10.0
        self.zoom_label.setText(f"Factor: {self.zoom_factor:.1f}x")
        self.process_and_display() # Reprocesar la imagen con el nuevo zoom

    def update_contrast(self, value):
        """Actualiza el factor de contraste y reprocesa."""
        self.contrast_factor = value / 10.0
        self.contrast_label.setText(f"Factor: {self.contrast_factor:.1f}x")
        self.process_and_display()

    def toggle_equalization(self, state):
        """Activa o desactiva la ecualización de histograma y reprocesa."""
        self.equalize_hist = (state == Qt.Checked)
        self.process_and_display()

    def toggle_thresholding(self, state):
        """Activa/Desactiva la umbralización y habilita/deshabilita controles."""
        self.threshold_active = (state == Qt.Checked)
        
        # Habilitar/Deshabilitar controles dependientes
        self.thresh_slider.setEnabled(self.threshold_active)
        self.thresh_type_combo.setEnabled(self.threshold_active)
        self.erode_slider.setEnabled(self.threshold_active)
        self.dilate_slider.setEnabled(self.threshold_active)
        
        self.process_and_display()

    def update_threshold_value(self, value):
        """Actualiza el valor del umbral."""
        self.thresh_value = value
        self.thresh_label.setText(f"Umbral (0-255): {value}")
        self.process_and_display()

    def update_threshold_type(self, index):
        """Actualiza el tipo de umbral (BINARIO o BINARIO_INV)."""
        if index == 0:
            self.thresh_type = cv2.THRESH_BINARY
        else:
            self.thresh_type = cv2.THRESH_BINARY_INV
            
        self.process_and_display()
        
    def update_erode_iterations(self, value):
        """Actualiza el número de iteraciones de erosión."""
        self.erode_iterations = value
        self.erode_label.setText(f"Erosión (Iter.): {value}")
        self.process_and_display()
    
    def update_dilate_iterations(self, value):
        """Actualiza el número de iteraciones de dilatación."""
        self.dilate_iterations = value
        self.dilate_label.setText(f"Dilatación (Iter.): {value}")
        self.process_and_display()
        

    def process_and_display(self):
        """
        Flujo optimizado: 
        1. Zoom Global (Rápido).
        2. Si hay ROI -> Procesamiento Pesado SOLO en ROI.
        3. Si no hay ROI -> Solo muestra imagen con Zoom.
        """
        if self.current_source_image is None:
            return

        # PASO 1: Aplicar Zoom Global a la imagen completa (Base para todo)
        # Usamos una variable temporal 'base_image'
        base_image = apply_digital_zoom(self.current_source_image, self.zoom_factor)
        
        # Esta será la imagen que mostremos en el centro (cruda o con overlay)
        display_main_img = base_image.copy()

        # PASO 2: Verificar si tenemos un ROI seleccionado
        if self.roi_coords is not None:
            x1, y1, x2, y2 = self.roi_coords
            
            # Validar coordenadas (por si el zoom cambió el tamaño o algo falló)
            h, w = base_image.shape[:2]
            # Asegurar límites dentro de la imagen
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            if x2 > x1 and y2 > y1:
                # A. Recortar el ROI CRUDO de la imagen base
                raw_roi = base_image[y1:y2, x1:x2]
                
                # B. Aplicar procesamiento PESADO solo a este pequeño fragmento
                processed_roi = process_roi_heavy(
                    raw_roi,
                    self.brightness_value, 
                    self.contrast_factor,  
                    self.equalize_hist,    
                    self.mask_type,
                    self.threshold_active, 
                    self.thresh_value, 
                    self.thresh_type,
                    self.erode_iterations,
                    self.dilate_iterations
                )
                
                # C. Actualizar paneles laterales con el ROI procesado
                self._display_roi_image(processed_roi) # Panel A
                self.analyze_roi_peaks(processed_roi)  # Panel B (Gráfica)

                # D. Visualización en Panel Central
                # OPCIÓN 1: Solo dibujar recuadro (Máximo rendimiento)
                #cv2.rectangle(display_main_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # OPCIÓN 2: "Pegar" el ROI procesado sobre la imagen original (Mejor UX)
                # Esto permite ver el efecto de la máscara en contexto
                #try:
                #    display_main_img[y1:y2, x1:x2] = processed_roi
                #    cv2.rectangle(display_main_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                #except Exception as e:
                #    print(f"Error al pegar ROI: {e}")
                #    self.roi_coords = None # Resetear si fallan dimensiones

        # Guardamos la imagen base como la "procesada actual" para referencia de coordenadas del mouse
        # NOTA: Guardamos 'base_image' (con zoom pero sin filtros globales) para que el
        # selector de ROI funcione sobre la geometría correcta.
        self.current_processed_image = base_image 

        # Mostrar la imagen central
        self._display_image(display_main_img)    

            
    # --- Métodos de Interacción y Conexión ---

    def select_source(self, index):
        """Maneja la selección entre Archivo y Cámara."""
        # Detener la cámara si está activa
        if self.video_thread and self.video_thread.isRunning():
            self.video_thread.stop()
            self.is_camera_mode = False
        
        if index == 1: # Cámara seleccionada
            self.is_camera_mode = True
            self.video_thread = VideoThread()
            self.video_thread.change_pixmap_signal.connect(self.update_image_from_camera)
            self.video_thread.start()
            self.load_button.setDisabled(True)
            self.video_thread.start()

            self.image_display.setText("Cámara activa...")
        else: # Archivo seleccionado
            self.is_camera_mode = False
            self.load_button.setDisabled(False)
            if self.current_source_image is None:
                self.image_display.setText("Presione 'Cargar Imagen...'")
            else:
                 self.process_and_display() # Reprocesar la imagen estática

    def load_image_from_file(self):
        """Abre un diálogo para seleccionar y cargar una imagen."""
        if self.is_camera_mode: return

        file_name, _ = QFileDialog.getOpenFileName(
            self, "Abrir Imagen", "", 
            "Archivos de Imagen (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_name:
            img = cv2.imread(file_name)
            if img is not None:
                self.current_source_image = img # Almacena la base
                self.process_and_display()
            else:
                self.image_display.setText("Error al cargar la imagen.")

    def update_brightness(self, value):
        """Actualiza el valor de brillo y reprocesa."""
        self.brightness_value = value
        self.brightness_label.setText(f"Valor: {value}")
        self.process_and_display()

    def update_mask(self, index):
        """Actualiza el tipo de máscara/filtro y reprocesa."""
        self.mask_type = self.mask_combo.currentText()
        self.process_and_display()

    def update_image_from_camera(self, cv_img):
        """Recibe un frame del hilo de video y lo establece como la imagen actual."""
        self.current_source_image = cv_img 
        self.process_and_display()
    
    def _display_image(self, cv_img):
        """Convierte una imagen de OpenCV a QPixmap y la muestra en el QLabel."""
        # Convertir BGR (OpenCV) a RGB (Qt)
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        
        convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(convert_to_qt_format)
        
        # Escalar y mostrar
        self.image_display.setPixmap(
            pixmap.scaled(
                self.image_display.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
        )
        self.image_display.setText("") 

    def closeEvent(self, event):
        """Detiene el hilo de video al cerrar la ventana."""
        if self.video_thread and self.video_thread.isRunning():
            self.video_thread.stop()
        event.accept()