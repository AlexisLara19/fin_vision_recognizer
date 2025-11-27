import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

class VideoThread(QThread):
    """Clase de Hilo para manejar la captura de video de la cámara."""
    
    # Señal que emitirá un frame (matriz numpy) a la ventana principal
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._run_flag = False
        self.cap = None

    def run(self):
        """Método de ejecución del hilo: inicia la captura y emite frames."""
        self._run_flag = True
        # Abre la cámara por defecto (índice 0)
        self.cap = cv2.VideoCapture(1)
        
        if not self.cap.isOpened():
            print("Error: No se puede abrir la cámara.")
            self._run_flag = False
            return

        while self._run_flag:
            ret, cv_img = self.cap.read()
            if ret:
                # Emitir el frame capturado
                self.change_pixmap_signal.emit(cv_img)
            # Pequeña pausa para controlar la velocidad de captura (ej. ~30 FPS)
            self.msleep(30)

        # Liberar la cámara al detener el hilo
        if self.cap:
            self.cap.release()
            
    def stop(self):
        """Método para detener el hilo de forma segura."""
        self._run_flag = False
        self.wait() # Espera a que el hilo termine la ejecución