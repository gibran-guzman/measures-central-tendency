"""
Pruebas de Corridas Arriba y Debajo de la Media
Implementación basada en principios SOLID y Clean Code
"""

from pyscript import document
import math
import random


# ============================================================================
# MODELOS DE DATOS (Data Classes)
# ============================================================================

class RunsTestResult:
    """Encapsula los resultados de la prueba de corridas"""
    
    def __init__(self, sequence, c0, n0, n1, n, mu_c0, variance, sigma_c0, 
                 z0, z_critical, is_independent, alpha, confidence):
        self.sequence = sequence
        self.c0 = c0
        self.n0 = n0
        self.n1 = n1
        self.n = n
        self.mu_c0 = mu_c0
        self.variance = variance
        self.sigma_c0 = sigma_c0
        self.z0 = z0
        self.z_critical = z_critical
        self.is_independent = is_independent
        self.alpha = alpha
        self.confidence = confidence


# ============================================================================
# SERVICIOS (Single Responsibility Principle)
# ============================================================================

class SequenceGenerator:
    """Responsable de generar secuencias binarias"""
    
    THRESHOLD = 0.5
    
    @staticmethod
    def generate(data):
        """
        Genera una secuencia de 0s y 1s comparando cada valor con el umbral.
        
        Args:
            data: Lista de números a convertir
            
        Returns:
            Lista de 0s y 1s según la comparación
        """
        return [0 if value < SequenceGenerator.THRESHOLD else 1 for value in data]


class RunsCounter:
    """Responsable de contar corridas en una secuencia"""
    
    @staticmethod
    def count(sequence):
        """
        Cuenta el número de corridas en la secuencia.
        Una corrida es una secuencia de valores idénticos consecutivos.
        
        Args:
            sequence: Secuencia binaria
            
        Returns:
            Número de corridas
        """
        if not sequence:
            return 0
        
        runs = 1
        for i in range(1, len(sequence)):
            if sequence[i] != sequence[i - 1]:
                runs += 1
        
        return runs
    
    @staticmethod
    def count_values(sequence):
        """
        Cuenta la cantidad de 0s y 1s en la secuencia.
        
        Args:
            sequence: Secuencia binaria
            
        Returns:
            Tupla (cantidad de 0s, cantidad de 1s)
        """
        n0 = sequence.count(0)
        n1 = sequence.count(1)
        return n0, n1


class StatisticsCalculator:
    """Responsable de realizar cálculos estadísticos"""
    
    @staticmethod
    def calculate_expected_runs(n0, n1, n):
        """
        Calcula el valor esperado del número de corridas (μ_C0).
        Formula: μ_C0 = (2*n0*n1)/n + 1/2
        """
        return (2 * n0 * n1) / n + 0.5
    
    @staticmethod
    def calculate_variance(n0, n1, n):
        """
        Calcula la varianza del número de corridas (σ²_C0).
        Formula: σ²_C0 = [2*n0*n1 * (2*n0*n1 - n)] / [n² * (n-1)]
        """
        if n <= 1:
            return 0
        
        numerator = 2 * n0 * n1 * (2 * n0 * n1 - n)
        denominator = n * n * (n - 1)
        
        return numerator / denominator if denominator != 0 else 0
    
    @staticmethod
    def calculate_z_statistic(c0, mu_c0, variance):
        """
        Calcula el estadístico Z0.
        Formula: Z0 = (C0 - μ_C0) / σ_C0
        """
        if variance <= 0:
            return 0
        
        sigma_c0 = math.sqrt(variance)
        return (c0 - mu_c0) / sigma_c0


class CriticalValueProvider:
    """Responsable de proveer valores críticos de la distribución Z"""
    
    Z_TABLE = {
        0.01: 2.576,  # 99% confianza
        0.05: 1.96,   # 95% confianza
        0.10: 1.645   # 90% confianza
    }
    
    DEFAULT_ALPHA = 0.05
    
    @classmethod
    def get_critical_value(cls, alpha):
        """
        Obtiene el valor crítico Z para un nivel de significancia dado.
        
        Args:
            alpha: Nivel de significancia
            
        Returns:
            Valor crítico Z_α/2
        """
        return cls.Z_TABLE.get(alpha, cls.Z_TABLE[cls.DEFAULT_ALPHA])


class HypothesisValidator:
    """Responsable de validar la hipótesis de independencia"""
    
    @staticmethod
    def validate(z0, z_critical):
        """
        Valida si se puede rechazar la hipótesis nula.
        
        Args:
            z0: Estadístico calculado
            z_critical: Valor crítico
            
        Returns:
            True si no se puede rechazar (números son independientes)
        """
        return abs(z0) <= z_critical


# ============================================================================
# SERVICIO PRINCIPAL (Facade Pattern)
# ============================================================================

class RunsTestService:
    """
    Servicio principal que coordina la prueba de corridas.
    Implementa el patrón Facade para simplificar la interfaz.
    """
    
    def __init__(self):
        self.sequence_generator = SequenceGenerator()
        self.runs_counter = RunsCounter()
        self.stats_calculator = StatisticsCalculator()
        self.critical_value_provider = CriticalValueProvider()
        self.hypothesis_validator = HypothesisValidator()
    
    def execute(self, data, alpha=0.05):
        """
        Ejecuta la prueba completa de corridas.
        
        Args:
            data: Lista de números a analizar
            alpha: Nivel de significancia
            
        Returns:
            Objeto RunsTestResult con todos los resultados
        """
        # Generar secuencia
        sequence = self.sequence_generator.generate(data)
        
        # Contar corridas y valores
        c0 = self.runs_counter.count(sequence)
        n0, n1 = self.runs_counter.count_values(sequence)
        n = len(data)
        
        # Calcular estadísticos
        mu_c0 = self.stats_calculator.calculate_expected_runs(n0, n1, n)
        variance = self.stats_calculator.calculate_variance(n0, n1, n)
        sigma_c0 = math.sqrt(variance) if variance > 0 else 0
        z0 = self.stats_calculator.calculate_z_statistic(c0, mu_c0, variance)
        
        # Obtener valor crítico
        z_critical = self.critical_value_provider.get_critical_value(alpha)
        
        # Validar hipótesis
        is_independent = self.hypothesis_validator.validate(z0, z_critical)
        
        return RunsTestResult(
            sequence=sequence,
            c0=c0,
            n0=n0,
            n1=n1,
            n=n,
            mu_c0=mu_c0,
            variance=variance,
            sigma_c0=sigma_c0,
            z0=z0,
            z_critical=z_critical,
            is_independent=is_independent,
            alpha=alpha,
            confidence=(1 - alpha) * 100
        )


# ============================================================================
# CAPA DE PRESENTACIÓN (Separation of Concerns)
# ============================================================================

class ResultsPresenter:
    """Responsable de presentar los resultados en la interfaz HTML"""
    
    @staticmethod
    def show_results_section():
        """Muestra la sección de resultados"""
        results_section = document.querySelector("#results")
        results_section.classList.add("show")
    
    @staticmethod
    def display_input_data(data):
        """Muestra los datos de entrada en una tabla"""
        input_table = document.querySelector("#input-table")
        html = "<thead><tr><th>Índice</th><th>Valor</th></tr></thead><tbody>"
        
        for i, value in enumerate(data, 1):
            html += f"<tr><td>{i}</td><td>{value:.3f}</td></tr>"
        
        html += "</tbody>"
        input_table.innerHTML = html
    
    @staticmethod
    def display_sequence(sequence):
        """Muestra la secuencia binaria"""
        sequence_div = document.querySelector("#sequence")
        sequence_str = "{" + ",".join(map(str, sequence)) + "}"
        sequence_div.innerHTML = f"S = {sequence_str}"
    
    @staticmethod
    def display_statistics_table(result):
        """Muestra la tabla con los estadísticos calculados"""
        results_body = document.querySelector("#results-body")
        
        rows_data = [
            ("n (Tamaño de muestra)", 
             "Cantidad total de números en el conjunto", 
             result.n),
            ("n₀ (Cantidad de ceros)", 
             "Números menores que 0.5 en la secuencia", 
             result.n0),
            ("n₁ (Cantidad de unos)", 
             "Números mayores o iguales a 0.5 en la secuencia", 
             result.n1),
            ("C₀ (Número de corridas)", 
             "Cantidad de secuencias de 0s o 1s consecutivos", 
             result.c0),
            ("μ_C₀ (Valor esperado)", 
             "Valor esperado del número de corridas", 
             f"{result.mu_c0:.4f}"),
            ("σ²_C₀ (Varianza)", 
             "Varianza del número de corridas", 
             f"{result.variance:.6f}"),
            ("σ_C₀ (Desviación estándar)", 
             "Raíz cuadrada de la varianza", 
             f"{result.sigma_c0:.6f}"),
            ("Z₀ (Estadístico)", 
             "Estadístico calculado para la prueba", 
             f"{result.z0:.4f}"),
            ("±Z_α/2 (Valor crítico)", 
             f"Valor crítico para α={result.alpha} ({result.confidence:.0f}% confianza)", 
             f"±{result.z_critical}")
        ]
        
        html = ""
        for criterion, description, value in rows_data:
            html += f"<tr><td><strong>{criterion}</strong></td><td>{description}</td><td>{value}</td></tr>"
        
        results_body.innerHTML = html
    
    @staticmethod
    def display_validation(result):
        """Muestra el resultado de la validación"""
        validation_div = document.querySelector("#validation")
        
        if result.is_independent:
            validation_div.className = "validation pass"
            validation_div.innerHTML = f"""
                ✅ <strong>PRUEBA APROBADA</strong><br>
                Como {result.z0:.4f} está dentro del intervalo 
                [{-result.z_critical}, {result.z_critical}],<br>
                <strong>NO se puede rechazar</strong> que los números del conjunto 
                r<sub>i</sub> son independientes<br>
                con un nivel de confianza del {result.confidence:.0f}%.
            """
        else:
            validation_div.className = "validation fail"
            validation_div.innerHTML = f"""
                ❌ <strong>PRUEBA RECHAZADA</strong><br>
                Como {result.z0:.4f} está fuera del intervalo 
                [{-result.z_critical}, {result.z_critical}],<br>
                <strong>SE RECHAZA</strong> que los números del conjunto 
                r<sub>i</sub> son independientes<br>
                con un nivel de confianza del {result.confidence:.0f}%.
            """
    
    @classmethod
    def present_all(cls, result, data):
        """Presenta todos los resultados"""
        cls.show_results_section()
        cls.display_input_data(data)
        cls.display_sequence(result.sequence)
        cls.display_statistics_table(result)
        cls.display_validation(result)


# ============================================================================
# UTILIDADES
# ============================================================================

class DataParser:
    """Responsable de parsear los datos de entrada"""
    
    @staticmethod
    def parse(data_input):
        """
        Convierte una cadena de texto en una lista de números flotantes.
        
        Args:
            data_input: Cadena con números separados por comas o espacios
            
        Returns:
            Lista de números flotantes
            
        Raises:
            ValueError: Si los datos no son válidos
        """
        data_str = data_input.replace(',', ' ').split()
        data = [float(x) for x in data_str if x.strip()]
        
        if not data:
            raise ValueError("No se encontraron números válidos en la entrada")
        
        return data


class UIController:
    """Controlador principal de la interfaz de usuario"""
    
    def __init__(self):
        self.test_service = RunsTestService()
        self.presenter = ResultsPresenter()
        self.parser = DataParser()
        self._rng = random.Random()
    
    def handle_test_execution(self, event):
        """
        Maneja el evento de ejecución de la prueba.
        
        Args:
            event: Evento del botón
        """
        try:
            # Obtener datos de entrada
            data_input = document.querySelector("#data-input").value
            # Acepta coma o punto como separador decimal para alpha
            alpha_raw = document.querySelector("#alpha-input").value
            alpha_input = float(alpha_raw.replace(',', '.')) if alpha_raw else 0.05
            
            # Validar alpha
            if not (0 < alpha_input < 1):
                self._show_error("El nivel de significancia debe estar entre 0 y 1")
                return
            
            # Parsear datos
            data = self.parser.parse(data_input)
            
            # Ejecutar prueba
            result = self.test_service.execute(data, alpha_input)
            
            # Presentar resultados
            self.presenter.present_all(result, data)
            
        except ValueError as e:
            self._show_error(f"Error en los datos: {str(e)}")
        except Exception as e:
            self._show_error(f"Error inesperado: {str(e)}")
    
    def _show_error(self, message):
        """Muestra un mensaje de error al usuario"""
        # En PyScript, usamos la función alert del navegador
        try:
            from js import alert
            alert(message)
        except:
            print(f"Error: {message}")

    # -----------------------------
    # Generación de datos aleatorios
    # -----------------------------
    def handle_generate_random(self, event):
        """Genera números aleatorios U(0,1) y llena el textarea"""
        try:
            count_el = document.querySelector("#count-input")
            decimals_el = document.querySelector("#decimals-input")
            n = int(count_el.value) if count_el and count_el.value else 50
            decimals = int(decimals_el.value) if decimals_el and decimals_el.value else 3
            if n <= 0:
                self._show_error("La cantidad debe ser mayor que 0")
                return
            if decimals < 0 or decimals > 10:
                self._show_error("Los decimales deben estar entre 0 y 10")
                return
            values = [self._rng.random() for _ in range(n)]
            text = ", ".join(f"{v:.{decimals}f}" for v in values)
            document.querySelector("#data-input").value = text
        except Exception as e:
            self._show_error(f"No se pudieron generar los datos: {str(e)}")

    def handle_clear_fields(self, event):
        """Limpia el textarea y oculta/borrar resultados"""
        try:
            # Limpiar datos de entrada
            data_area = document.querySelector("#data-input")
            if data_area:
                data_area.value = ""

            # Ocultar y limpiar resultados
            res_section = document.querySelector("#results")
            if res_section:
                res_section.classList.remove("show")

            tbl_input = document.querySelector("#input-table")
            seq_div = document.querySelector("#sequence")
            tbl_body = document.querySelector("#results-body")
            validation = document.querySelector("#validation")
            if tbl_input: tbl_input.innerHTML = ""
            if seq_div: seq_div.innerHTML = ""
            if tbl_body: tbl_body.innerHTML = ""
            if validation:
                validation.className = "validation"
                validation.innerHTML = ""
        except Exception as e:
            self._show_error(f"No se pudo limpiar: {str(e)}")


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

# Instancia global del controlador
_controller = UIController()

# Función expuesta para el evento del botón (debe estar en el scope global)
def run_runs_test(event):
    """Función de entrada para la ejecución de la prueba"""
    _controller.handle_test_execution(event)

# Función expuesta para generar datos aleatorios
def generate_random_data(event):
    _controller.handle_generate_random(event)

# Función expuesta para limpiar
def clear_fields(event):
    _controller.handle_clear_fields(event)

