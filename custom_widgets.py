from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtGui import QPainter, QPen, QColor

# --- Importaciones para Matplotlib ---
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class ROISelectableLabel(QLabel):

    """
    QLabel personalizado que permite seleccionar un área rectangular (ROI) con el mouse.
    Emite una señal 'roi_selected' con las coordenadas del rectángulo seleccionado.
    """
    # Señal que envía el rectángulo seleccionado (x, y, ancho, alto)
    roi_selected = pyqtSignal(QRect)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_point = None
        self.end_point = None
        self.is_drawing = False
        
        # Cursor en cruz para indicar selección
        self.setCursor(Qt.CrossCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            self.end_point = event.pos()
            self.is_drawing = True
            self.update()  # Fuerza el repintado para mostrar el cuadro

    def mouseMoveEvent(self, event):
        if self.is_drawing:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_drawing:
            self.end_point = event.pos()
            self.is_drawing = False

            # Calcular el rectángulo normalizado (para permitir arrastrar en cualquier dirección)
            self.current_rect = QRect(self.start_point, self.end_point).normalized()

            # Solo emitir si el área tiene un tamaño razonable
            if self.current_rect.width() > 5 and self.current_rect.height() > 5:
                self.roi_selected.emit(self.current_rect)

            self.update()

    def paintEvent(self, event):
        # 1. Dibujar la imagen base (comportamiento estándar)
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setPen(QPen(QColor(255, 0, 0), 2, Qt.SolidLine))  # Rojo, grosor 2
        painter.setBrush(QColor(255, 0, 0, 50))  # Rojo semitransparente

        # 2. Dibujar el rectángulo actual si existe
        if hasattr(self, 'current_rect') and self.current_rect:
            painter.drawRect(self.current_rect)

        # 3. Dibujar el rectángulo de selección mientras se dibuja
        if self.is_drawing and self.start_point and self.end_point:
            temp_rect = QRect(self.start_point, self.end_point).normalized()
            painter.drawRect(temp_rect)

# --- Widget 2: Gráfico de Intensidad (NUEVO) ---
class IntensityPlotWidget(QWidget):
    """
    Widget que contiene un gráfico de Matplotlib para mostrar perfiles de intensidad.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Crear Figura y Canvas
        # facecolor='#2a2a2a' coincide con el fondo oscuro de tu app
        self.figure = Figure(figsize=(5, 3), facecolor='#2a2a2a')
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        
        # Configurar ejes iniciales
        self.ax = self.figure.add_subplot(111)
        self.setup_plot_style()

    def setup_plot_style(self):
        """Configura colores y estilos para tema oscuro."""
        self.ax.set_facecolor('#2a2a2a') # Fondo del gráfico
        self.ax.tick_params(colors='white', which='both') # Color de números
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('#444') 
        self.ax.spines['left'].set_color('white')
        self.ax.spines['right'].set_color('#444')
        self.ax.set_title("Proyección Horizontal (Suma de Columnas)", color='white', fontsize=10)
        self.ax.set_xlabel("Eje X (Píxeles)", color='gray', fontsize=8)
        self.ax.set_ylabel("Intensidad Acumulada", color='gray', fontsize=8)
        self.figure.tight_layout()

    def update_plot(self, data, peaks):
        """
        Recibe los datos de proyección y opcionalmente los índices de los picos.
        """
        pass
        #self.ax.clear() 
        #self.setup_plot_style()
        
        # 1. Graficar la curva
        #self.ax.plot(data, color='#00ff00', linewidth=1.5, label='Intensidad')
        #self.ax.fill_between(range(len(data)), data, color='#00ff00', alpha=0.1)
        
        # 2. Graficar los picos (si existen)
        #if peaks is not None and len(peaks) > 0:
            # data[peaks] obtiene los valores de altura en esos índices
        #    self.ax.plot(peaks, data[peaks], "x", color='red', markersize=8, label='Crestas')
        #    self.ax.legend(loc='upper right', fontsize=8)

        #self.canvas.draw()

