# main.py
from logger import configurar_logger
from exceptions import (
    ErrorSistemaFJ,
    DatosInvalidosError,
    ParametrosFaltantesError,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
    CalculoInconsistenteError,
)
from modelos import (
    Cliente,
    ReservaSala,
    AlquilerEquipo,
    AsesoriaEspecializada,
    Reserva,
)


class SistemaSoftwareFJ:
    """Gestiona clientes, servicios y reservas en memoria (sin base de datos)."""

    def __init__(self):
        self.logger = configurar_logger("sistema_fj.log")
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, id_cliente: str, nombre: str, correo: str, telefono: str):
        try:
            cliente = Cliente(id_cliente, nombre, correo, telefono)
        except ErrorSistemaFJ as err:
            self.logger.error(f"[CLIENTE FALLIDO] ID={id_cliente} -> {type(err).__name__}: {err}")
            return None
        else:
            self.clientes.append(cliente)
            self.logger.info(f"[CLIENTE REGISTRADO] {cliente.obtener_resumen()}")
            return cliente
        finally:
            self.logger.info(f"Intento de registro de cliente finalizado (ID={id_cliente}).")

    def registrar_servicio(self, servicio_fn, codigo: str):
        try:
            servicio = servicio_fn()
        except ErrorSistemaFJ as err:
            self.logger.error(f"[SERVICIO FALLIDO] Código={codigo} -> {type(err).__name__}: {err}")
            return None
        else:
            self.servicios.append(servicio)
            self.logger.info(f"[SERVICIO CREADO] {servicio.obtener_resumen()} | {servicio.describir_servicio()}")
            return servicio
        finally:
            self.logger.info(f"Intento de creación de servicio finalizado (Código={codigo}).")

    def crear_y_procesar_reserva(
        self,
        id_reserva: str,
        cliente,
        servicio,
        duracion: float,
        descuento: float = 0.0,
        impuesto: float = 0.19,
        accion: str = "PROCESAR",
    ):
        try:
            try:
                reserva = Reserva(id_reserva, cliente, servicio, duracion)
            except (ServicioNoDisponibleError, DatosInvalidosError, ParametrosFaltantesError) as err_origen:
                # Encadenamiento de excepciones
                raise ReservaInvalidaError(
                    f"No fue posible inicializar la reserva '{id_reserva}'."
                ) from err_origen

            if accion == "CONFIRMAR":
                reserva.confirmar(descuento=descuento, impuesto=impuesto)
            elif accion == "PROCESAR":
                reserva.procesar(descuento=descuento, impuesto=impuesto)
            elif accion == "CANCELAR":
                reserva.cancelar("Cancelada por solicitud del cliente")
            elif accion == "ERROR_ESTADO":
                reserva.cancelar("Cancelación previa")
                reserva.confirmar()  # Provoca OperacionNoPermitidaError

        except ErrorSistemaFJ as err:
            causa = f" | Causa original: {type(err.__cause__).__name__}: {err.__cause__}" if err.__cause__ else ""
            self.logger.error(
                f"[RESERVA FALLIDA] ID={id_reserva} -> {type(err).__name__}: {err}{causa}"
            )
            return None
        else:
            self.reservas.append(reserva)
            self.logger.info(f"[RESERVA EXITOSA] {reserva.obtener_resumen()}")
            return reserva
        finally:
            self.logger.info(f"Flujo de reserva finalizado (ID={id_reserva}).")


def ejecutar_simulacion():
    sistema = SistemaSoftwareFJ()
    sistema.logger.info("=== INICIO DE SIMULACIÓN SOFTWARE FJ (13 OPERACIONES) ===")

    # 1. Registro válido de cliente 1
    c1 = sistema.registrar_cliente("C001", "Laura Gómez", "laura.gomez@correo.com", "3104567890")

    # 2. Registro válido de cliente 2
    c2 = sistema.registrar_cliente("C002", "Carlos Pérez", "carlos.perez@empresa.co", "3209876543")

    # 3. Registro inválido de cliente (correo sin @)
    sistema.registrar_cliente("C003", "Andrés Ruiz", "andres.ruiz.correo.com", "3001112233")

    # 4. Registro inválido de cliente (nombre vacío - parámetro faltante)
    sistema.registrar_cliente("C004", "", "sin.nombre@correo.com", "3004445566")

    # 5. Creación válida de ReservaSala
    s1 = sistema.registrar_servicio(
        lambda: ReservaSala("S001", "Sala Ejecutiva Norte", 80000, capacidad=25, disponible=True),
        "S001",
    )

    # 6. Creación válida de AlquilerEquipo
    s2 = sistema.registrar_servicio(
        lambda: AlquilerEquipo("S002", "Kit Portátiles Desarrollo", 35000, tipo_equipo="Laptop Core i7", cantidad=3, disponible=True),
        "S002",
    )

    # 7. Creación válida de AsesoriaEspecializada (no disponible para probar fallo luego)
    s3 = sistema.registrar_servicio(
        lambda: AsesoriaEspecializada("S003", "Arquitectura Cloud", 120000, especialidad="Nube AWS", modalidad="PRESENCIAL", disponible=False),
        "S003",
    )

    # 8. Creación incorrecta de servicio (tarifa negativa)
    sistema.registrar_servicio(
        lambda: ReservaSala("S004", "Sala Inválida", -50000, capacidad=10),
        "S004",
    )

    # 9. Creación incorrecta de servicio (modalidad inválida en asesoría)
    sistema.registrar_servicio(
        lambda: AsesoriaEspecializada("S005", "Seguridad Informática", 95000, especialidad="Ciberseguridad", modalidad="HIBRIDA"),
        "S005",
    )

    # 10. Reserva exitosa y procesada (sin descuento, impuesto estándar)
    sistema.crear_y_procesar_reserva("R001", c1, s1, duracion=3, accion="PROCESAR")

    # 11. Reserva exitosa con cálculo sobrecargado (10% descuento + 19% IVA)
    sistema.crear_y_procesar_reserva("R002", c2, s2, duracion=4, descuento=0.10, impuesto=0.19, accion="CONFIRMAR")

    # 12. Reserva fallida por servicio no disponible (encadenamiento de excepciones)
    sistema.crear_y_procesar_reserva("R003", c1, s3, duracion=2, accion="PROCESAR")

    # 13. Reserva fallida por intento de confirmar una reserva cancelada
    sistema.crear_y_procesar_reserva("R004", c2, s1, duracion=2, accion="ERROR_ESTADO")

    sistema.logger.info("=== RESUMEN FINAL EN MEMORIA ===")
    sistema.logger.info(f"Total clientes válidos: {len(sistema.clientes)}")
    sistema.logger.info(f"Total servicios válidos: {len(sistema.servicios)}")
    sistema.logger.info(f"Total reservas registradas: {len(sistema.reservas)}")
    sistema.logger.info("=== FIN DE SIMULACIÓN SIN INTERRUPCIONES ===")


if __name__ == "__main__":
    ejecutar_simulacion()