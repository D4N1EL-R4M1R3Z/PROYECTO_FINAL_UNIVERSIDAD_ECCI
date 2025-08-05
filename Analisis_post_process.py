import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import signal
from scipy.stats import pearsonr
import os
import glob

class JumpDataAnalyzer:
    def __init__(self, csv_file=None):
        """
        Inicializa el analizador de datos
        Args:
            csv_file: Ruta al archivo CSV. Si es None, busca el más reciente.
        """
        if csv_file is None:
            # Buscar el archivo CSV más reciente
            csv_files = glob.glob("jump_analysis_*.csv")
            if not csv_files:
                raise FileNotFoundError("No se encontraron archivos de análisis")
            csv_file = max(csv_files, key=os.path.getctime)
            print(f"Usando archivo: {csv_file}")
        
        self.data = pd.read_csv(csv_file)
        self.filename = csv_file
        
        # Configurar estilo de gráficos
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def filter_data(self, cutoff_freq=10, sampling_rate=30):
        """
        Aplica filtro pasa-bajas para suavizar los datos
        Args:
            cutoff_freq: Frecuencia de corte en Hz
            sampling_rate: Frecuencia de muestreo en Hz
        """
        nyquist = sampling_rate / 2
        normal_cutoff = cutoff_freq / nyquist
        b, a = signal.butter(2, normal_cutoff, btype='low', analog=False)
        
        # Filtrar posición del centro de masa
        self.data['com_y_filtered'] = signal.filtfilt(b, a, self.data['com_y'])
        self.data['com_x_filtered'] = signal.filtfilt(b, a, self.data['com_x'])
        
        # Calcular velocidad vertical (derivada numérica)
        dt = np.diff(self.data['timestamp'].values)
        dt = np.append(dt, dt[-1])  # Mantener la misma longitud
        
        self.data['vertical_velocity'] = np.gradient(self.data['com_y_filtered'], 
                                                   self.data['timestamp'])
        
        print("Datos filtrados exitosamente")
    
    def detect_jump_events(self, velocity_threshold=0.05):
        """
        Detecta eventos de salto con mayor precisión
        Args:
            velocity_threshold: Umbral de velocidad para detectar despegue
        """
        if 'vertical_velocity' not in self.data.columns:
            self.filter_data()
        
        # Detectar despegue (velocidad hacia arriba significativa)
        takeoff_candidates = self.data[self.data['vertical_velocity'] < -velocity_threshold]
        
        # Detectar aterrizaje (regreso a velocidad baja después del vuelo)
        landing_candidates = self.data[
            (self.data['vertical_velocity'].abs() < velocity_threshold/2) & 
            (self.data.index > takeoff_candidates.index.min() if len(takeoff_candidates) > 0 else 0)
        ]
        
        if len(takeoff_candidates) > 0 and len(landing_candidates) > 0:
            takeoff_idx = takeoff_candidates.index[0]
            landing_idx = landing_candidates.index[0]
            
            # Calcular métricas mejoradas
            flight_time = self.data.iloc[landing_idx]['timestamp'] - self.data.iloc[takeoff_idx]['timestamp']
            
            # Altura basada en la máxima elevación del COM
            flight_data = self.data.iloc[takeoff_idx:landing_idx]
            if len(flight_data) > 0:
                baseline_height = self.data.iloc[:takeoff_idx]['com_y_filtered'].mean()
                max_height = flight_data['com_y_filtered'].min()  # Menor Y = mayor altura
                jump_height = abs(baseline_height - max_height) * 200  # Factor de escala estimado
                
                return {
                    'takeoff_time': self.data.iloc[takeoff_idx]['timestamp'],
                    'landing_time': self.data.iloc[landing_idx]['timestamp'],
                    'flight_time': flight_time,
                    'jump_height_cm': jump_height,
                    'takeoff_velocity': abs(self.data.iloc[takeoff_idx]['vertical_velocity']),
                    'takeoff_idx': takeoff_idx,
                    'landing_idx': landing_idx
                }
        
        return None
    
    def calculate_advanced_metrics(self):
        """Calcula métricas biomecánicas avanzadas"""
        jump_events = self.detect_jump_events()
        
        if jump_events is None:
            print("No se detectaron eventos de salto claros")
            return None
        
        # Análisis durante el despegue
        takeoff_idx = jump_events['takeoff_idx']
        takeoff_window = slice(max(0, takeoff_idx-5), takeoff_idx+1)
        
        takeoff_data = self.data.iloc[takeoff_window]
        
        metrics = {
            **jump_events,
            'avg_knee_angle_takeoff': takeoff_data[['left_knee_angle', 'right_knee_angle']].mean().mean(),
            'avg_hip_angle_takeoff': takeoff_data[['left_hip_angle', 'right_hip_angle']].mean().mean(),
            'knee_asymmetry': abs(takeoff_data['left_knee_angle'].mean() - 
                                takeoff_data['right_knee_angle'].mean()),
            'hip_asymmetry': abs(takeoff_data['left_hip_angle'].mean() - 
                               takeoff_data['right_hip_angle'].mean()),
            'overall_symmetry': takeoff_data[['knee_symmetry', 'hip_symmetry']].mean().mean(),
            'power_estimate': self.estimate_power(jump_events['jump_height_cm'], 
                                                jump_events['flight_time'])
        }
        
        return metrics
    
    def estimate_power(self, height_cm, flight_time, body_mass_kg=70):
        """
        Estima la potencia usando la fórmula de Sayers
        Args:
            height_cm: Altura del salto en cm
            flight_time: Tiempo de vuelo en segundos
            body_mass_kg: Masa corporal estimada
        """
        if height_cm > 0:
            # Fórmula de Sayers: P = (60.7 × height_cm) + (45.3 × body_mass) - 2055
            power_sayers = (60.7 * height_cm) + (45.3 * body_mass_kg) - 2055
            
            # Fórmula alternativa basada en tiempo de vuelo
            # P = (m × g × h) / t_contact (asumiendo t_contact ≈ flight_time)
            if flight_time > 0:
                power_physics = (body_mass_kg * 9.81 * (height_cm/100)) / flight_time
                return max(power_sayers, power_physics * 0.8)  # Tomar el más conservador
        
        return 0
    
    def create_comprehensive_report(self):
        """Genera un reporte visual completo del análisis"""
        metrics = self.calculate_advanced_metrics()
        
        if metrics is None:
            print("No se pueden generar gráficos sin datos de salto válidos")
            return
        
        # Crear figura con subplots
        fig = plt.figure(figsize=(16, 12))
        
        # 1. Trayectoria del centro de masa
        ax1 = plt.subplot(2, 3, 1)
        plt.plot(self.data['timestamp'], self.data['com_y'], alpha=0.5, label='COM Y (raw)')
        if 'com_y_filtered' in self.data.columns:
            plt.plot(self.data['timestamp'], self.data['com_y_filtered'], 
                    label='COM Y (filtered)', linewidth=2)
        
        # Marcar eventos de salto
        if metrics['takeoff_idx'] and metrics['landing_idx']:
            plt.axvline(x=metrics['takeoff_time'], color='green', 
                       linestyle='--', label='Takeoff')
            plt.axvline(x=metrics['landing_time'], color='red', 
                       linestyle='--', label='Landing')
        
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Posición Y (normalizada)')
        plt.title('Trayectoria Vertical del Centro de Masa')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 2. Velocidad vertical
        ax2 = plt.subplot(2, 3, 2)
        if 'vertical_velocity' in self.data.columns:
            plt.plot(self.data['timestamp'], self.data['vertical_velocity'], 
                    color='orange', linewidth=2)
            plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            plt.xlabel('Tiempo (s)')
            plt.ylabel('Velocidad Vertical')
            plt.title('Velocidad Vertical del COM')
            plt.grid(True, alpha=0.3)
        
        # 3. Ángulos articulares
        ax3 = plt.subplot(2, 3, 3)
        plt.plot(self.data['timestamp'], self.data['left_knee_angle'], 
                label='Rodilla Izq', linewidth=2)
        plt.plot(self.data['timestamp'], self.data['right_knee_angle'], 
                label='Rodilla Der', linewidth=2)
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Ángulo (grados)')
        plt.title('Ángulos de Rodilla')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 4. Índice de simetría
        ax4 = plt.subplot(2, 3, 4)
        plt.plot(self.data['timestamp'], self.data['knee_symmetry'], 
                label='Simetría Rodillas', linewidth=2, color='purple')
        plt.plot(self.data['timestamp'], self.data['hip_symmetry'], 
                label='Simetría Caderas', linewidth=2, color='brown')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Índice de Simetría (%)')
        plt.title('Análisis de Simetría Bilateral')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 5. Resumen de métricas
        ax5 = plt.subplot(2, 3, 5)
        ax5.axis('off')
        
        # Crear tabla de métricas
        metrics_text = f"""
        MÉTRICAS BIOMECÁNICAS
        
        Altura de Salto: {metrics['jump_height_cm']:.1f} cm
        Tiempo de Vuelo: {metrics['flight_time']:.3f} s
        Velocidad de Despegue: {metrics['takeoff_velocity']:.3f} m/s
        
        Ángulos en Despegue:
        • Rodillas: {metrics['avg_knee_angle_takeoff']:.1f}°
        • Caderas: {metrics['avg_hip_angle_takeoff']:.1f}°
        
        Asimetría:
        • Rodillas: {metrics['knee_asymmetry']:.1f}°
        • Caderas: {metrics['hip_asymmetry']:.1f}°
        
        Simetría General: {metrics['overall_symmetry']:.1f}%
        Potencia Estimada: {metrics['power_estimate']:.0f} W
        """
        
        ax5.text(0.1, 0.9, metrics_text, transform=ax5.transAxes, 
                fontsize=11, verticalalignment='top', 
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
        
        # 6. Distribución de ángulos
        ax6 = plt.subplot(2, 3, 6)
        
        # Boxplot de ángulos durante diferentes fases
        angles_data = [
            self.data['left_knee_angle'].values,
            self.data['right_knee_angle'].values,
            self.data['left_hip_angle'].values,
            self.data['right_hip_angle'].values
        ]
        
        labels = ['Rodilla Izq', 'Rodilla Der', 'Cadera Izq', 'Cadera Der']
        
        plt.boxplot(angles_data, labels=labels)
        plt.ylabel('Ángulo (grados)')
        plt.title('Distribución de Ángulos Articulares')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Guardar el reporte
        report_filename = f"jump_report_{int(pd.Timestamp.now().timestamp())}.png"
        plt.savefig(report_filename, dpi=300, bbox_inches='tight')
        print(f"Reporte guardado como: {report_filename}")
        plt.show()
        
        return metrics
    
    def export_summary_csv(self, metrics):
        """Exporta un resumen de métricas en formato CSV"""
        if metrics is None:
            print("No hay métricas para exportar")
            return
        
        summary_data = {
            'timestamp': [pd.Timestamp.now()],
            'archivo_origen': [self.filename],
            'altura_salto_cm': [metrics['jump_height_cm']],
            'tiempo_vuelo_s': [metrics['flight_time']],
            'velocidad_despegue_ms': [metrics['takeoff_velocity']],
            'angulo_rodillas_despegue': [metrics['avg_knee_angle_takeoff']],
            'angulo_caderas_despegue': [metrics['avg_hip_angle_takeoff']],
            'asimetria_rodillas': [metrics['knee_asymmetry']],
            'asimetria_caderas': [metrics['hip_asymmetry']],
            'simetria_general_pct': [metrics['overall_symmetry']],
            'potencia_estimada_w': [metrics['power_estimate']]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_filename = f"jump_summary_{int(pd.Timestamp.now().timestamp())}.csv"
        summary_df.to_csv(summary_filename, index=False)
        print(f"Resumen exportado como: {summary_filename}")
    
    def compare_multiple_jumps(self, csv_files_list):
        """
        Compara múltiples saltos para análisis de progresión
        Args:
            csv_files_list: Lista de archivos CSV para comparar
        """
        all_metrics = []
        
        for file in csv_files_list:
            try:
                temp_analyzer = JumpDataAnalyzer(file)
                metrics = temp_analyzer.calculate_advanced_metrics()
                if metrics:
                    metrics['filename'] = file
                    all_metrics.append(metrics)
            except Exception as e:
                print(f"Error procesando {file}: {e}")
        
        if len(all_metrics) < 2:
            print("Se necesitan al menos 2 archivos válidos para comparación")
            return
        
        # Crear DataFrame para comparación
        comparison_df = pd.DataFrame(all_metrics)
        
        # Gráfico de comparación
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Altura de salto
        axes[0,0].bar(range(len(comparison_df)), comparison_df['jump_height_cm'])
        axes[0,0].set_title('Altura de Salto por Sesión')
        axes[0,0].set_ylabel('Altura (cm)')
        axes[0,0].set_xlabel('Sesión')
        
        # Tiempo de vuelo
        axes[0,1].bar(range(len(comparison_df)), comparison_df['flight_time'])
        axes[0,1].set_title('Tiempo de Vuelo por Sesión')
        axes[0,1].set_ylabel('Tiempo (s)')
        axes[0,1].set_xlabel('Sesión')
        
        # Simetría
        axes[1,0].bar(range(len(comparison_df)), comparison_df['overall_symmetry'])
        axes[1,0].set_title('Simetría General por Sesión')
        axes[1,0].set_ylabel('Simetría (%)')
        axes[1,0].set_xlabel('Sesión')
        
        # Potencia estimada
        axes[1,1].bar(range(len(comparison_df)), comparison_df['power_estimate'])
        axes[1,1].set_title('Potencia Estimada por Sesión')
        axes[1,1].set_ylabel('Potencia (W)')
        axes[1,1].set_xlabel('Sesión')
        
        plt.tight_layout()
        
        # Guardar comparación
        comparison_filename = f"jump_comparison_{int(pd.Timestamp.now().timestamp())}.png"
        plt.savefig(comparison_filename, dpi=300, bbox_inches='tight')
        print(f"Comparación guardada como: {comparison_filename}")
        plt.show()
        
        # Exportar datos de comparación
        comparison_csv = f"jump_comparison_{int(pd.Timestamp.now().timestamp())}.csv"
        comparison_df.to_csv(comparison_csv, index=False)
        print(f"Datos de comparación exportados como: {comparison_csv}")
        
        return comparison_df
    
    def analyze_technique_classification(self):
        """
        Clasifica el tipo de salto basándose en patrones de movimiento
        """
        metrics = self.calculate_advanced_metrics()
        
        if metrics is None:
            return "No se pudo clasificar - datos insuficientes"
        
        # Reglas heurísticas para clasificación
        knee_angle = metrics['avg_knee_angle_takeoff']
        flight_time = metrics['flight_time']
        symmetry = metrics['overall_symmetry']
        
        # Clasificación basada en patrones típicos
        if knee_angle < 90 and flight_time > 0.3:
            jump_type = "Countermovement Jump (CMJ)"
            confidence = "Alta" if symmetry > 85 else "Media"
        elif knee_angle > 90 and knee_angle < 120:
            jump_type = "Half Squat Jump"
            confidence = "Media"
        elif knee_angle >= 120:
            jump_type = "Deep Squat Jump"
            confidence = "Media"
        else:
            jump_type = "Jump técnico indefinido"
            confidence = "Baja"
        
        # Evaluación de la técnica
        if symmetry > 90:
            technique_quality = "Excelente simetría"
        elif symmetry > 80:
            technique_quality = "Buena simetría"
        elif symmetry > 70:
            technique_quality = "Simetría moderada"
        else:
            technique_quality = "Asimetría significativa - revisar técnica"
        
        classification_result = {
            'tipo_salto': jump_type,
            'confianza_clasificacion': confidence,
            'calidad_tecnica': technique_quality,
            'recomendaciones': self.generate_recommendations(metrics)
        }
        
        return classification_result
    
    def generate_recommendations(self, metrics):
        """Genera recomendaciones basadas en las métricas analizadas"""
        recommendations = []
        
        # Análisis de altura
        if metrics['jump_height_cm'] < 20:
            recommendations.append("• Trabajar en fuerza explosiva de piernas")
            recommendations.append("• Practicar técnica de contra-movimiento")
        
        # Análisis de simetría
        if metrics['overall_symmetry'] < 80:
            recommendations.append("• Enfocarse en ejercicios de simetría bilateral")
            recommendations.append("• Evaluar posibles descompensaciones musculares")
        
        # Análisis de ángulos
        if metrics['avg_knee_angle_takeoff'] > 140:
            recommendations.append("• Trabajar en mayor flexión de rodillas durante preparación")
        elif metrics['avg_knee_angle_takeoff'] < 70:
            recommendations.append("• Evitar flexión excesiva - optimizar ángulo de despegue")
        
        # Análisis de tiempo de vuelo
        if metrics['flight_time'] < 0.25:
            recommendations.append("• Incrementar velocidad de extensión en despegue")
            recommendations.append("• Trabajar coordinación de brazos para mayor impulso")
        
        return recommendations
    
    def run_complete_analysis(self):
        """Ejecuta un análisis completo y genera todos los reportes"""
        print("="*60)
        print("ANÁLISIS BIOMECÁNICO COMPLETO DE SALTO")
        print("="*60)
        
        # Filtrar datos
        self.filter_data()
        
        # Calcular métricas
        metrics = self.calculate_advanced_metrics()
        
        if metrics is None:
            print("❌ No se detectaron saltos válidos en los datos")
            return
        
        # Clasificar técnica
        classification = self.analyze_technique_classification()
        
        # Mostrar resultados
        print(f"\n📊 MÉTRICAS PRINCIPALES:")
        print(f"   Altura de salto: {metrics['jump_height_cm']:.1f} cm")
        print(f"   Tiempo de vuelo: {metrics['flight_time']:.3f} segundos")
        print(f"   Potencia estimada: {metrics['power_estimate']:.0f} W")
        print(f"   Simetría general: {metrics['overall_symmetry']:.1f}%")
        
        print(f"\n🎯 CLASIFICACIÓN:")
        print(f"   Tipo de salto: {classification['tipo_salto']}")
        print(f"   Confianza: {classification['confianza_clasificacion']}")
        print(f"   Calidad técnica: {classification['calidad_tecnica']}")
        
        print(f"\n💡 RECOMENDACIONES:")
        for rec in classification['recomendaciones']:
            print(f"   {rec}")
        
        # Generar reportes
        print(f"\n📈 Generando reportes visuales...")
        self.create_comprehensive_report()
        self.export_summary_csv(metrics)
        
        print(f"\n✅ Análisis completado exitosamente!")
        
        return metrics, classification

# Función principal para ejecutar el análisis
def main():
    """Función principal para ejecutar el análisis de datos"""
    print("Sistema de Análisis Post-Procesamiento de Saltos")
    print("=" * 50)
    
    try:
        # Crear analizador (busca automáticamente el archivo más reciente)
        analyzer = JumpDataAnalyzer()
        
        # Ejecutar análisis completo
        results = analyzer.run_complete_analysis()
        
        # Preguntar si desea comparar con otros archivos
        response = input("\n¿Desea comparar con otros archivos de salto? (s/n): ")
        if response.lower() == 's':
            import glob
            csv_files = glob.glob("jump_analysis_*.csv")
            if len(csv_files) > 1:
                print(f"Archivos disponibles: {csv_files}")
                analyzer.compare_multiple_jumps(csv_files)
            else:
                print("Solo hay un archivo disponible para análisis")
    
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Asegúrate de haber ejecutado primero el sistema de captura")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()
