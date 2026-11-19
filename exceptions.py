# exceptions.py
# Excepciones personalizadas para el sistema de Software FJ

class ErrorSistemaFJ(Exception):
    """Clase base para todos los errores del sistema Software FJ."""
    pass


class DatosInvalidosError(ErrorSistemaFJ):
    """Se lanza cuando un dato tiene formato incorrecto o un valor no permitido."""
    pass


class ParametrosFaltantesError(ErrorSistemaFJ):
    """Se lanza cuando falta información obligatoria."""
    pass


class OperacionNoPermitidaError(ErrorSistemaFJ):
    """Se lanza cuando se intenta hacer una acción que no corresponde al estado actual."""
    pass


class ReservaInvalidaError(ErrorSistemaFJ):
    """Se lanza cuando hay un problema al crear, confirmar o procesar una reserva."""
    pass


class ServicioNoDisponibleError(ErrorSistemaFJ):
    """Se lanza cuando un servicio no está disponible."""
    pass


class CalculoInconsistenteError(ErrorSistemaFJ):
    """Se lanza cuando el cálculo de un costo da un resultado inválido."""
    pass