# modelos.py
from abc import ABC, abstractmethod
from exceptions import (
    DatosInvalidosError,
    ParametrosFaltantesError,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
    CalculoInconsistenteError,
)


class EntidadSistema(ABC):
    """Clase abstracta base para entidades generales del sistema Software FJ."""

    def __init__(self, id_entidad: str):
        if not id_entidad or not str(id_entidad).strip():
            raise ParametrosFaltantesError("El ID de la entidad es obligatorio.")
        self._id_entidad = str(id_entidad).strip()

    @property
    def id_entidad(self) -> str:
        return self._id_entidad

    @abstractmethod
    def obtener_resumen(self) -> str:
        """Devuelve un resumen legible de la entidad."""
        pass


class Cliente(EntidadSistema):
    """Representa un cliente con datos personales encapsulados y validados."""

    def __init__(self, id_cliente: str, nombre: str, correo: str, telefono: str):
        super().__init__(id_cliente)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not valor.strip():
            raise ParametrosFaltantesError("El nombre del cliente es obligatorio.")
        if len(valor.strip()) < 3:
            raise DatosInvalidosError("El nombre del cliente debe tener al menos 3 caracteres.")
        self.__nombre = valor.strip()

    @property
    def correo(self) -> str:
        return self.__correo

    @correo.setter
    def correo(self, valor: str):
        if not valor or not valor.strip():
            raise ParametrosFaltantesError("El correo del cliente es obligatorio.")
        correo_limpio = valor.strip()
        if "@" not in correo_limpio or "." not in correo_limpio.split("@")[-1]:
            raise DatosInvalidosError(f"Correo electrónico inválido: '{correo_limpio}'.")
        self.__correo = correo_limpio

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str):
        if not valor or not str(valor).strip():
            raise ParametrosFaltantesError("El teléfono del cliente es obligatorio.")
        tel_limpio = "".join(ch for ch in str(valor) if ch.isdigit())
        if len(tel_limpio) < 7:
            raise DatosInvalidosError(f"Teléfono inválido: '{valor}'. Debe tener al menos 7 dígitos.")
        self.__telefono = tel_limpio

    def obtener_resumen(self) -> str:
        return f"Cliente [{self.id_entidad}] - {self.__nombre} | Correo: {self.__correo} | Tel: {self.__telefono}"


class Servicio(EntidadSistema, ABC):
    """Clase abstracta base para los servicios ofrecidos por Software FJ."""

    def __init__(self, codigo: str, nombre: str, tarifa_base: float, disponible: bool = True):
        super().__init__(codigo)
        if not nombre or not nombre.strip():
            raise ParametrosFaltantesError("El nombre del servicio es obligatorio.")
        try:
            tarifa_num = float(tarifa_base)
        except (TypeError, ValueError) as exc:
            raise DatosInvalidosError("La tarifa base debe ser un valor numérico.") from exc

        if tarifa_num <= 0:
            raise DatosInvalidosError("La tarifa base del servicio debe ser mayor que cero.")

        self.nombre = nombre.strip()
        self.tarifa_base = tarifa_num
        self.disponible = bool(disponible)

    @abstractmethod
    def validar_parametros(self, **kwargs) -> bool:
        """Valida parámetros específicos del servicio."""
        pass

    @abstractmethod
    def describir_servicio(self) -> str:
        """Describe las características del servicio."""
        pass

    @abstractmethod
    def _calcular_subtotal_base(self, duracion: float, **kwargs) -> float:
        """Calcula el subtotal antes de descuentos e impuestos según el tipo de servicio."""
        pass

    def calcular_costo(
        self,
        duracion: float,
        descuento: float = 0.0,
        impuesto: float = 0.19,
        recargo_adicional: float = 0.0,
        **kwargs,
    ) -> float:
        """Calcula el costo total con argumentos opcionales de descuento, impuesto y recargo."""
        try:
            duracion_num = float(duracion)
            descuento_num = float(descuento)
            impuesto_num = float(impuesto)
            recargo_num = float(recargo_adicional)
        except (TypeError, ValueError) as exc:
            raise CalculoInconsistenteError("Parámetros numéricos inválidos en el cálculo de costo.") from exc

        if duracion_num <= 0:
            raise CalculoInconsistenteError("La duración debe ser mayor que cero.")
        if not (0.0 <= descuento_num < 1.0):
            raise CalculoInconsistenteError("El descuento debe estar entre 0.0 (0%) y menor a 1.0 (100%).")
        if impuesto_num < 0 or recargo_num < 0:
            raise CalculoInconsistenteError("Impuestos y recargos no pueden ser negativos.")

        subtotal = self._calcular_subtotal_base(duracion_num, **kwargs) + recargo_num
        con_descuento = subtotal * (1 - descuento_num)
        total = con_descuento * (1 + impuesto_num)

        if total <= 0 or subtotal < 0:
            raise CalculoInconsistenteError("El resultado del cálculo de costo es inconsistente.")

        return round(total, 2)

    def obtener_resumen(self) -> str:
        estado_disp = "Disponible" if self.disponible else "No disponible"
        return f"Servicio [{self.id_entidad}] - {self.nombre} (${self.tarifa_base:,.2f}) | {estado_disp}"


class ReservaSala(Servicio):
    """Servicio especializado para reserva de salas."""

    def __init__(self, codigo: str, nombre: str, tarifa_base: float, capacidad: int, disponible: bool = True):
        super().__init__(codigo, nombre, tarifa_base, disponible)
        self.validar_parametros(capacidad=capacidad)
        self.capacidad = int(capacidad)

    def validar_parametros(self, **kwargs) -> bool:
        if "capacidad" not in kwargs or kwargs["capacidad"] is None:
            raise ParametrosFaltantesError("Debe indicarse la capacidad de personas de la sala.")
        try:
            cap = int(kwargs["capacidad"])
        except (TypeError, ValueError) as exc:
            raise DatosInvalidosError("La capacidad de la sala debe ser un número entero.") from exc
        if cap <= 0:
            raise DatosInvalidosError("La capacidad de la sala debe ser mayor que cero.")
        return True

    def _calcular_subtotal_base(self, duracion: float, **kwargs) -> float:
        recargo_sala_grande = 15000.0 if self.capacidad >= 20 else 0.0
        return (self.tarifa_base * duracion) + recargo_sala_grande

    def describir_servicio(self) -> str:
        return f"Reserva de Sala '{self.nombre}' para hasta {self.capacidad} personas."


class AlquilerEquipo(Servicio):
    """Servicio especializado para alquiler de equipos."""

    def __init__(self, codigo: str, nombre: str, tarifa_base: float, tipo_equipo: str, cantidad: int, disponible: bool = True):
        super().__init__(codigo, nombre, tarifa_base, disponible)
        self.validar_parametros(tipo_equipo=tipo_equipo, cantidad=cantidad)
        self.tipo_equipo = tipo_equipo.strip()
        self.cantidad = int(cantidad)

    def validar_parametros(self, **kwargs) -> bool:
        tipo = kwargs.get("tipo_equipo")
        cantidad = kwargs.get("cantidad")
        if not tipo or not str(tipo).strip():
            raise ParametrosFaltantesError("El tipo de equipo es obligatorio.")
        if cantidad is None:
            raise ParametrosFaltantesError("La cantidad de equipos es obligatoria.")
        try:
            cant = int(cantidad)
        except (TypeError, ValueError) as exc:
            raise DatosInvalidosError("La cantidad de equipos debe ser un número entero.") from exc
        if cant <= 0:
            raise DatosInvalidosError("La cantidad de equipos debe ser mayor que cero.")
        return True

    def _calcular_subtotal_base(self, duracion: float, **kwargs) -> float:
        return self.tarifa_base * self.cantidad * duracion

    def describir_servicio(self) -> str:
        return f"Alquiler de Equipo '{self.nombre}' ({self.tipo_equipo}), cantidad: {self.cantidad}."


class AsesoriaEspecializada(Servicio):
    """Servicio especializado para asesorías técnicas/profesionales."""

    MODALIDADES_VALIDAS = {"VIRTUAL", "PRESENCIAL"}

    def __init__(self, codigo: str, nombre: str, tarifa_base: float, especialidad: str, modalidad: str, disponible: bool = True):
        super().__init__(codigo, nombre, tarifa_base, disponible)
        self.validar_parametros(especialidad=especialidad, modalidad=modalidad)
        self.especialidad = especialidad.strip()
        self.modalidad = modalidad.strip().upper()

    def validar_parametros(self, **kwargs) -> bool:
        especialidad = kwargs.get("especialidad")
        modalidad = kwargs.get("modalidad")
        if not especialidad or not str(especialidad).strip():
            raise ParametrosFaltantesError("La especialidad de la asesoría es obligatoria.")
        if not modalidad or not str(modalidad).strip():
            raise ParametrosFaltantesError("La modalidad de la asesoría es obligatoria.")
        if str(modalidad).strip().upper() not in self.MODALIDADES_VALIDAS:
            raise DatosInvalidosError("Modalidad inválida. Use 'VIRTUAL' o 'PRESENCIAL'.")
        return True

    def _calcular_subtotal_base(self, duracion: float, **kwargs) -> float:
        factor_modalidad = 1.2 if self.modalidad == "PRESENCIAL" else 1.0
        return self.tarifa_base * duracion * factor_modalidad

    def describir_servicio(self) -> str:
        return f"Asesoría Especializada en {self.especialidad} ({self.modalidad}) - {self.nombre}."


class Reserva(EntidadSistema):
    """Integra un cliente, un servicio, duración y estado con control de transiciones."""

    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, duracion: float):
        super().__init__(id_reserva)
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un objeto Cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un objeto Servicio válido.")
        try:
            dur = float(duracion)
        except (TypeError, ValueError) as exc:
            raise ReservaInvalidaError("La duración de la reserva debe ser numérica.") from exc
        if dur <= 0:
            raise ReservaInvalidaError("La duración de la reserva debe ser mayor que cero.")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{servicio.nombre}' no está disponible para reservar.")

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = dur
        self.estado = "PENDIENTE"
        self.costo_calculado = None

    def confirmar(self, descuento: float = 0.0, impuesto: float = 0.19):
        if self.estado == "CANCELADA":
            raise OperacionNoPermitidaError("No se puede confirmar una reserva cancelada.")
        if self.estado == "PROCESADA":
            raise OperacionNoPermitidaError("No se puede confirmar una reserva ya procesada.")
        if not self.servicio.disponible:
            raise ServicioNoDisponibleError("El servicio ya no está disponible para confirmar.")

        self.costo_calculado = self.servicio.calcular_costo(
            duracion=self.duracion,
            descuento=descuento,
            impuesto=impuesto,
        )
        self.estado = "CONFIRMADA"

    def cancelar(self, motivo: str = ""):
        if self.estado == "PROCESADA":
            raise OperacionNoPermitidaError("No se puede cancelar una reserva ya procesada.")
        self.estado = "CANCELADA"

    def procesar(self, descuento: float = 0.0, impuesto: float = 0.19):
        if self.estado == "CANCELADA":
            raise OperacionNoPermitidaError("No se puede procesar una reserva cancelada.")
        if self.estado != "CONFIRMADA":
            self.confirmar(descuento=descuento, impuesto=impuesto)
        self.estado = "PROCESADA"

    def obtener_resumen(self) -> str:
        costo_texto = f"${self.costo_calculado:,.2f}" if self.costo_calculado is not None else "Pendiente de cálculo"
        return (
            f"Reserva [{self.id_entidad}] | Estado: {self.estado} | "
            f"Cliente: {self.cliente.nombre} | Servicio: {self.servicio.nombre} | "
            f"Duración: {self.duracion}h | Costo: {costo_texto}"
        )