import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import deque
import time
import math

class JumpAnalyzer:
    def __init__(self):
        # Configuración de MediaPipe
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Variables para análisis
        self.pose_data = []
        self.timestamps = []
        self.frame_count = 0
        self.recording = False
        self.start_time = None
        
        # Buffer para suavizado de datos
        self.position_buffer = deque(maxlen=10)
        self.velocity_buffer = deque(maxlen=5)
        
        # Variables para detección de salto
        self.baseline_hip_y = None
        self.max_height = 0
        self.jump_detected = False
        self.takeoff_time = None
        self.landing_time = None
        self.in_air = False
        
        # Métricas calculadas
        self.metrics = {
            'jump_height': 0,
            'flight_time': 0,
            'takeoff_velocity': 0,
            'knee_angle_takeoff': 0,
            'hip_angle_takeoff': 0,
            'ankle_angle_takeoff': 0,
            'symmetry_index': 0,
            'center_of_mass_displacement': 0
        }
        
    def calculate_angle(self, a, b, c):
        """Calcula el ángulo entre tres puntos"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle
    
    def calculate_distance(self, point1, point2):
        """Calcula la distancia euclidiana entre dos puntos"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def get_center_of_mass(self, landmarks):
        """Estima el centro de masa usando puntos clave de MediaPipe"""
        # Puntos principales para estimar COM
        key_points = [
            self.mp_pose.PoseLandmark.LEFT_SHOULDER,
            self.mp_pose.PoseLandmark.RIGHT_SHOULDER,
            self.mp_pose.PoseLandmark.LEFT_HIP,
            self.mp_pose.PoseLandmark.RIGHT_HIP,
            self.mp_pose.PoseLandmark.LEFT_KNEE,
            self.mp_pose.PoseLandmark.RIGHT_KNEE
        ]
        
        # Pesos aproximados para cada región corporal
        weights = [0.15, 0.15, 0.25, 0.25, 0.1, 0.1]  # Suma = 1.0
        
        com_x = 0
        com_y = 0
        
        for i, point_idx in enumerate(key_points):
            landmark = landmarks[point_idx.value]
            com_x += landmark.x * weights[i]
            com_y += landmark.y * weights[i]
            
        return (com_x, com_y)
    
    def detect_jump_phases(self, com_y, current_time):
        """Detecta las fases del salto basándose en el movimiento del COM"""
        if self.baseline_hip_y is None:
            self.baseline_hip_y = com_y
            return
        
        # Umbral para detección de despegue/aterrizaje (ajustable)
        threshold = 0.02  # 2% de la altura de la imagen
        
        # Detección de despegue
        if not self.in_air and com_y < (self.baseline_hip_y - threshold):
            self.in_air = True
            self.takeoff_time = current_time
            self.jump_detected = True
            print(f"¡Despegue detectado! Tiempo: {current_time:.2f}s")
        
        # Actualizar altura máxima
        if self.in_air and com_y < self.max_height:
            self.max_height = com_y
        
        # Detección de aterrizaje
        if self.in_air and com_y > (self.baseline_hip_y - threshold/2):
            self.in_air = False
            self.landing_time = current_time
            if self.takeoff_time:
                self.metrics['flight_time'] = self.landing_time - self.takeoff_time
                self.metrics['jump_height'] = abs(self.baseline_hip_y - self.max_height) * 100  # Convertir a cm aproximado
                print(f"¡Aterrizaje detectado! Tiempo de vuelo: {self.metrics['flight_time']:.2f}s")
                print(f"Altura estimada: {self.metrics['jump_height']:.1f} cm")
    
    def analyze_pose(self, landmarks, current_time):
        """Analiza la pose y calcula métricas biomecánicas"""
        # Obtener puntos clave
        left_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                   landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
        right_hip = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        left_knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        right_knee = [landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                     landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        left_ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                     landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        right_ankle = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                      landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
        left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        right_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                         landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        
        # Calcular ángulos articulares
        left_knee_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
        right_knee_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
        left_hip_angle = self.calculate_angle(left_shoulder, left_hip, left_knee)
        right_hip_angle = self.calculate_angle(right_shoulder, right_hip, right_knee)
        
        # Calcular centro de masa
        com = self.get_center_of_mass(landmarks)
        
        # Detectar fases del salto
        self.detect_jump_phases(com[1], current_time)
        
        # Calcular índice de simetría
        knee_symmetry = 100 - abs(left_knee_angle - right_knee_angle) / ((left_knee_angle + right_knee_angle) / 2) * 100
        hip_symmetry = 100 - abs(left_hip_angle - right_hip_angle) / ((left_hip_angle + right_hip_angle) / 2) * 100
        
        # Almacenar datos
        pose_data_point = {
            'timestamp': current_time,
            'com_x': com[0],
            'com_y': com[1],
            'left_knee_angle': left_knee_angle,
            'right_knee_angle': right_knee_angle,
            'left_hip_angle': left_hip_angle,
            'right_hip_angle': right_hip_angle,
            'knee_symmetry': knee_symmetry,
            'hip_symmetry': hip_symmetry,
            'in_air': self.in_air
        }
        
        self.pose_data.append(pose_data_point)
        
        # Actualizar métricas en tiempo real
        if self.takeoff_time and current_time == self.takeoff_time:
            self.metrics['knee_angle_takeoff'] = (left_knee_angle + right_knee_angle) / 2
            self.metrics['hip_angle_takeoff'] = (left_hip_angle + right_hip_angle) / 2
            self.metrics['symmetry_index'] = (knee_symmetry + hip_symmetry) / 2
        
        return pose_data_point
    
    def draw_metrics_overlay(self, image, pose_data_point):
        """Dibuja las métricas en tiempo real sobre la imagen"""
        h, w, _ = image.shape
        
        # Información del estado
        cv2.putText(image, f"Recording: {'ON' if self.recording else 'OFF'}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0) if self.recording else (0, 0, 255), 2)
        
        # Métricas en tiempo real
        cv2.putText(image, f"Jump Height: {self.metrics['jump_height']:.1f} cm", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(image, f"Flight Time: {self.metrics['flight_time']:.2f} s", 
                   (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(image, f"Knee Angle: {pose_data_point['left_knee_angle']:.1f}° / {pose_data_point['right_knee_angle']:.1f}°", 
                   (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(image, f"Symmetry: {pose_data_point['knee_symmetry']:.1f}%", 
                   (10, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(image, f"Status: {'IN AIR' if self.in_air else 'ON GROUND'}", 
                   (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255) if self.in_air else (255, 0, 0), 2)
        
        # Instrucciones
        cv2.putText(image, "Press 'r' to start/stop recording, 'q' to quit, 's' to save data", 
                   (10, h-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    def save_data(self):
        """Guarda los datos recolectados en un archivo CSV"""
        if len(self.pose_data) > 0:
            df = pd.DataFrame(self.pose_data)
            filename = f"jump_analysis_{int(time.time())}.csv"
            df.to_csv(filename, index=False)
            print(f"Datos guardados en: {filename}")
            
            # Mostrar resumen de métricas
            self.print_summary()
    
    def print_summary(self):
        """Imprime un resumen de las métricas calculadas"""
        print("\n" + "="*50)
        print("RESUMEN DE ANÁLISIS BIOMECÁNICO")
        print("="*50)
        print(f"Altura de salto estimada: {self.metrics['jump_height']:.1f} cm")
        print(f"Tiempo de vuelo: {self.metrics['flight_time']:.3f} segundos")
        print(f"Ángulo de rodilla en despegue: {self.metrics['knee_angle_takeoff']:.1f}°")
        print(f"Ángulo de cadera en despegue: {self.metrics['hip_angle_takeoff']:.1f}°")
        print(f"Índice de simetría: {self.metrics['symmetry_index']:.1f}%")
        print(f"Total de frames analizados: {len(self.pose_data)}")
        print("="*50)
    
    def run(self):
        """Función principal para ejecutar el análisis"""
        cap = cv2.VideoCapture(0)
        
        # Configurar resolución de cámara
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("Sistema de Análisis Biomecánico Iniciado")
        print("Instrucciones:")
        print("- Presiona 'r' para iniciar/detener grabación")
        print("- Presiona 's' para guardar datos")
        print("- Presiona 'q' para salir")
        print("- Colócate de perfil a la cámara para mejor análisis")
        
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignorando frame vacío de la cámara.")
                continue
            
            # Convertir de BGR a RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            
            # Procesar con MediaPipe
            results = self.pose.process(image_rgb)
            
            # Convertir de vuelta a BGR para OpenCV
            image_rgb.flags.writeable = True
            image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
            
            # Dibujar landmarks
            if results.pose_landmarks:
                self.mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
                
                # Analizar pose si estamos grabando
                if self.recording:
                    current_time = time.time() - self.start_time
                    pose_data_point = self.analyze_pose(results.pose_landmarks.landmark, current_time)
                    self.draw_metrics_overlay(image, pose_data_point)
                else:
                    # Solo mostrar overlay básico
                    cv2.putText(image, "Recording: OFF", (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Mostrar imagen
            cv2.imshow('Análisis Biomecánico - MediaPipe', image)
            
            # Manejo de teclas
            key = cv2.waitKey(5) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                if not self.recording:
                    self.recording = True
                    self.start_time = time.time()
                    self.pose_data = []
                    self.baseline_hip_y = None
                    self.max_height = 0
                    self.jump_detected = False
                    self.takeoff_time = None
                    self.landing_time = None
                    self.in_air = False
                    print("¡Grabación iniciada!")
                else:
                    self.recording = False
                    print("¡Grabación detenida!")
            elif key == ord('s'):
                if len(self.pose_data) > 0:
                    self.save_data()
                else:
                    print("No hay datos para guardar. Inicia una grabación primero.")
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    analyzer = JumpAnalyzer()
    analyzer.run()
