#UNAD
# Fase 4 - Componente practico
# Curso: Programacion 213023
# Sistema: Clientes, servicios y reservas para Software FJ
# Autor: CARLOS ENRIQUE DOUAT RICAURTE
# Grupo: 213023_255


from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logging.basicConfig(
    filename="eventos.log",
    filemode="w",
    level=logging.INFO,
    format="%(levelname)s :: %(asctime)s :: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)

auditoria = logging.getLogger("software_fj")

class SistemaFJError(Exception):
    """Error general controlado del sistema Software FJ."""
    pass

class ErrorDeValidacion(SistemaFJError):
    """Error producido por datos incompletos o no validos."""
    pass

class ErrorDeServicio(SistemaFJError):
    """Error relacionado con reglas propias de los servicios."""
    pass

class ErrorDeReserva(SistemaFJError):
    """Error relacionado con el proceso de reservas."""
    pass

class ModeloSoftwareFJ(ABC):
    def __init__(self, codigo):
        codigo_limpio = str(codigo).strip()
        if codigo_limpio == "":
            raise ErrorDeValidacion("El codigo no puede estar vacio.")
        self._codigo = codigo_limpio

    @property
    def codigo(self):
        return self._codigo

    @abstractmethod
    def resumen(self):
        pass

class Cliente(ModeloSoftwareFJ):
    def __init__(self, codigo, nombre, documento, ciudad, correo):
        super().__init__(codigo)
        self.__nombre = ""
        self.__documento = ""
        self.__ciudad = ""
        self.__correo = ""
        self.nombre = nombre
        self.documento = documento
        self.ciudad = ciudad
        self.correo = correo

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        valor = str(valor).strip()
        if len(valor) < 5:
            raise ErrorDeValidacion("El nombre del cliente debe tener minimo 5 caracteres.")
        self.__nombre = valor.title()

    @property
    def documento(self):
        return self.__documento

    @documento.setter
    def documento(self, valor):
        valor = str(valor).strip()
        if not valor.isdigit():
            raise ErrorDeValidacion("El documento del cliente debe contener solo numeros.")
        if len(valor) < 7:
            raise ErrorDeValidacion("El documento del cliente debe tener minimo 7 digitos.")
        self.__documento = valor

    @property
    def ciudad(self):
        return self.__ciudad

    @ciudad.setter
    def ciudad(self, valor):
        valor = str(valor).strip()
        if len(valor) < 3:
            raise ErrorDeValidacion("La ciudad del cliente no es valida.")
        self.__ciudad = valor.title()

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        valor = str(valor).strip().lower()
        if "@" not in valor or "." not in valor:
            raise ErrorDeValidacion("El correo del cliente no tiene un formato valido.")
        self.__correo = valor

    def resumen(self):
        return f"{self.codigo} | {self.__nombre} | Doc: {self.__documento} | {self.__ciudad} | {self.__correo}"

class Servicio(ModeloSoftwareFJ):
    def __init__(self, codigo, nombre, tarifa, activo=True):
        super().__init__(codigo)
        nombre = str(nombre).strip()
        if len(nombre) < 6:
            raise ErrorDeServicio("El nombre del servicio es demasiado corto.")
        if tarifa <= 0:
            raise ErrorDeServicio("La tarifa del servicio debe ser mayor que cero.")
        self._nombre = nombre.title()
        self._tarifa = float(tarifa)
        self.__activo = bool(activo)

    @property
    def nombre(self):
        return self._nombre

    @property
    def activo(self):
        return self.__activo

    def bloquear(self):
        self.__activo = False
        auditoria.warning(f"CONTROL_SERVICIO | {self.codigo} | servicio bloqueado")

    def habilitar(self):
        self.__activo = True
        auditoria.info(f"CONTROL_SERVICIO | {self.codigo} | servicio habilitado")

    @abstractmethod
    def validar_tiempo(self, tiempo):
        pass

    @abstractmethod
    def calcular_total(self, tiempo, impuesto=0.19, descuento=0, recargo=0):
        pass

    @abstractmethod
    def descripcion(self):
        pass

    def resumen(self):
        estado = "activo" if self.__activo else "bloqueado"
        return f"{self.codigo} | {self._nombre} | tarifa base ${self._tarifa:,.0f} | {estado}"

class SalaEjecutiva(Servicio):
    def __init__(self, codigo, nombre, tarifa, capacidad, activo=True):
        super().__init__(codigo, nombre, tarifa, activo)
        if capacidad < 2:
            raise ErrorDeServicio("La sala debe tener capacidad minima para 2 personas.")
        self.capacidad = capacidad

    def validar_tiempo(self, tiempo):
        if tiempo <= 0:
            raise ErrorDeServicio("Las horas de sala deben ser mayores que cero.")
        if tiempo > 9:
            raise ErrorDeServicio("La sala ejecutiva solo se reserva hasta por 9 horas.")

    def calcular_total(self, tiempo, impuesto=0.19, descuento=0, recargo=0):
        self.validar_tiempo(tiempo)
        subtotal = self._tarifa * tiempo
        subtotal = subtotal - (subtotal * descuento)
        subtotal = subtotal + recargo
        return subtotal * (1 + impuesto)

    def descripcion(self):
        return f"Sala ejecutiva para reuniones. Capacidad: {self.capacidad} personas."

class KitTecnologico(Servicio):
    def __init__(self, codigo, nombre, tarifa, elementos, activo=True):
        super().__init__(codigo, nombre, tarifa, activo)
        if not elementos:
            raise ErrorDeServicio("Debe registrar al menos un elemento del kit tecnologico.")
        self.elementos = elementos

    def validar_tiempo(self, tiempo):
        if tiempo <= 0:
            raise ErrorDeServicio("Los dias de alquiler deben ser mayores que cero.")
        if tiempo > 12:
            raise ErrorDeServicio("El kit tecnologico no se alquila por mas de 12 dias.")

    def calcular_total(self, tiempo, impuesto=0.19, descuento=0, recargo=0):
        self.validar_tiempo(tiempo)
        subtotal = self._tarifa * tiempo
        if len(self.elementos) > 3:
            subtotal = subtotal + 25000
        subtotal = subtotal + recargo
        subtotal = subtotal - (subtotal * descuento)
        return subtotal + (subtotal * impuesto)

    def descripcion(self):
        listado = ", ".join(self.elementos)
        return f"Kit tecnologico compuesto por: {listado}."

class AcompanamientoProfesional(Servicio):
    def __init__(self, codigo, nombre, tarifa, linea_atencion, activo=True):
        super().__init__(codigo, nombre, tarifa, activo)
        linea_atencion = str(linea_atencion).strip()
        if len(linea_atencion) < 4:
            raise ErrorDeServicio("La linea de atencion no es valida.")
        self.linea_atencion = linea_atencion.title()

    def validar_tiempo(self, tiempo):
        if tiempo <= 0:
            raise ErrorDeServicio("Las horas de acompanamiento deben ser mayores que cero.")
        if tiempo > 4:
            raise ErrorDeServicio("El acompanamiento profesional solo permite maximo 4 horas.")

    def calcular_total(self, tiempo, impuesto=0.19, descuento=0, recargo=0):
        self.validar_tiempo(tiempo)
        valor = self._tarifa * tiempo
        valor = valor + recargo
        valor = valor - (valor * descuento)
        return valor * (1 + impuesto)

    def descripcion(self):
        return f"Acompanamiento profesional en la linea: {self.linea_atencion}."

class EstadoReserva(Enum):
    REGISTRADA = "Registrada"
    CONFIRMADA = "Confirmada"
    PAGADA = "Pagada"
    CANCELADA = "Cancelada"

class Reserva(ModeloSoftwareFJ):
    def __init__(self, codigo, cliente, servicio, tiempo):
        super().__init__(codigo)
        if not isinstance(cliente, Cliente):
            raise ErrorDeReserva("La reserva necesita un cliente valido.")
        if not isinstance(servicio, Servicio):
            raise ErrorDeReserva("La reserva necesita un servicio valido.")
        if tiempo <= 0:
            raise ErrorDeReserva("El tiempo de la reserva debe ser mayor que cero.")
        self.cliente = cliente
        self.servicio = servicio
        self.tiempo = tiempo
        self.estado = EstadoReserva.REGISTRADA
        self.creada_en = datetime.now()
        self.total = 0
        auditoria.info(f"RESERVA_NUEVA | codigo={self.codigo} | cliente={cliente.codigo} | servicio={servicio.codigo}")

    def confirmar(self):
        try:
            if not self.servicio.activo:
                raise ErrorDeServicio("El servicio seleccionado se encuentra bloqueado.")
            self.servicio.validar_tiempo(self.tiempo)
            self.estado = EstadoReserva.CONFIRMADA
        except ErrorDeServicio as error:
            auditoria.error(f"RESERVA_NO_CONFIRMADA | codigo={self.codigo} | detalle={error}")
            raise ErrorDeReserva("No se pudo confirmar la reserva por una condicion del servicio.") from error
        else:
            auditoria.info(f"RESERVA_CONFIRMADA | codigo={self.codigo}")
            return "Reserva confirmada sin novedades."
        finally:
            auditoria.info(f"FIN_CONFIRMACION | codigo={self.codigo} | estado={self.estado.value}")

    def cobrar(self, impuesto=0.19, descuento=0, recargo=0):
        try:
            if self.estado != EstadoReserva.CONFIRMADA:
                raise ErrorDeReserva("Para cobrar, la reserva primero debe estar confirmada.")
            self.total = self.servicio.calcular_total(self.tiempo, impuesto, descuento, recargo)
            self.estado = EstadoReserva.PAGADA
        except SistemaFJError as error:
            auditoria.error(f"COBRO_RECHAZADO | codigo={self.codigo} | detalle={error}")
            return f"No fue posible cobrar la reserva: {error}"
        else:
            auditoria.info(f"COBRO_APROBADO | codigo={self.codigo} | total={self.total:.2f}")
            return f"Cobro aprobado. Valor total: ${self.total:,.2f}"
        finally:
            auditoria.info(f"FIN_COBRO | codigo={self.codigo} | estado={self.estado.value}")

    def cancelar(self):
        if self.estado == EstadoReserva.PAGADA:
            raise ErrorDeReserva("Una reserva pagada no se puede cancelar desde este modulo.")
        if self.estado == EstadoReserva.CANCELADA:
            raise ErrorDeReserva("La reserva ya se encontraba cancelada.")
        self.estado = EstadoReserva.CANCELADA
        auditoria.warning(f"RESERVA_CANCELADA | codigo={self.codigo}")
        return "Reserva cancelada correctamente."

    def resumen(self):
        fecha = self.creada_en.strftime("%d/%m/%Y %H:%M")
        return (
            f"{self.codigo} | Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} | Tiempo: {self.tiempo} | "
            f"Estado: {self.estado.value} | Fecha: {fecha}"
        )

@dataclass
class CasoDePrueba:
    numero: int
    nombre: str
    accion: object

class CentroOperativoFJ:
    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def guardar_cliente(self, cliente):
        self.clientes.append(cliente)
        auditoria.info(f"CLIENTE_OK | codigo={cliente.codigo} | nombre={cliente.nombre}")
        return f"Cliente guardado: {cliente.resumen()}"

    def guardar_servicio(self, servicio):
        self.servicios.append(servicio)
        auditoria.info(f"SERVICIO_OK | codigo={servicio.codigo} | nombre={servicio.nombre}")
        return f"Servicio guardado: {servicio.resumen()}\n{servicio.descripcion()}"

    def guardar_reserva(self, reserva):
        self.reservas.append(reserva)
        auditoria.info(f"RESERVA_OK | codigo={reserva.codigo}")
        return reserva

    def cliente(self, posicion):
        try:
            return self.clientes[posicion]
        except IndexError as error:
            auditoria.error(f"CLIENTE_NO_EXISTE | posicion={posicion}")
            raise ErrorDeReserva("No se encontro el cliente solicitado en la lista interna.") from error

    def servicio(self, posicion):
        try:
            return self.servicios[posicion]
        except IndexError as error:
            auditoria.error(f"SERVICIO_NO_EXISTE | posicion={posicion}")
            raise ErrorDeReserva("No se encontro el servicio solicitado en la lista interna.") from error

centro = CentroOperativoFJ()

def caso_01():
    return centro.guardar_cliente(Cliente("C-501", "Valentina Rojas", "1098765432", "Bucaramanga", "valentina.rojas@mail.com"))

def caso_02():
    return centro.guardar_cliente(Cliente("C-502", "Esteban Moreno", "74382910", "Tunja", "esteban.moreno@mail.com"))

def caso_03():
    return centro.guardar_cliente(Cliente("C-503", "Isa", "987654321", "Cali", "isa@mail.com"))

def caso_04():
    return centro.guardar_cliente(Cliente("C-504", "Camilo Parra", "DOC789", "Neiva", "camilo.parra@mail.com"))

def caso_05():
    return centro.guardar_servicio(SalaEjecutiva("S-801", "Sala Directiva Premium", 58000, 18))

def caso_06():
    return centro.guardar_servicio(KitTecnologico("S-802", "Kit Audiovisual Movil", 42000, ["video beam", "parlante", "microfono", "pantalla"]))

def caso_07():
    return centro.guardar_servicio(AcompanamientoProfesional("S-803", "Asesoria De Procesos", 88000, "Procesos internos"))

def caso_08():
    return centro.guardar_servicio(KitTecnologico("S-804", "Kit Sin Tarifa", -35000, ["portatil"]))

def caso_09():
    reserva = Reserva("R-901", centro.cliente(0), centro.servicio(0), 3)
    centro.guardar_reserva(reserva)
    texto = reserva.confirmar()
    pago = reserva.cobrar(impuesto=0.19, descuento=0.06, recargo=10000)
    return reserva.resumen() + "\n" + texto + "\n" + pago

def caso_10():
    reserva = Reserva("R-902", centro.cliente(1), centro.servicio(2), 7)
    centro.guardar_reserva(reserva)
    return reserva.confirmar()

def caso_11():
    servicio = centro.servicio(1)
    servicio.bloquear()
    reserva = Reserva("R-903", centro.cliente(0), servicio, 2)
    centro.guardar_reserva(reserva)
    return reserva.confirmar()

def caso_12():
    reserva = Reserva("R-904", centro.cliente(1), centro.servicio(0), 2)
    centro.guardar_reserva(reserva)
    return reserva.cobrar()

def caso_13():
    reserva = Reserva("R-905", centro.cliente(1), centro.servicio(2), 2)
    centro.guardar_reserva(reserva)
    reserva.confirmar()
    texto_cancelacion = reserva.cancelar()
    return reserva.resumen() + "\n" + texto_cancelacion

def caso_14():
    reserva = Reserva("R-906", centro.cliente(15), centro.servicio(0), 1)
    centro.guardar_reserva(reserva)
    return reserva.resumen()

def ejecutar(caso):
    print("\n" + "#" * 76)
    print(f"CASO {caso.numero}: {caso.nombre}")
    print("#" * 76)
    try:
        salida = caso.accion()
    except SistemaFJError as error:
        print(f"Fallo controlado: {error}")
        auditoria.error(f"CASO_CONTROLADO | numero={caso.numero} | error={error}")
    except Exception as error:
        print(f"Fallo inesperado controlado: {error}")
        auditoria.exception(f"CASO_INESPERADO | numero={caso.numero}")
    else:
        print(salida)
        auditoria.info(f"CASO_COMPLETO | numero={caso.numero}")
    finally:
        print("Cierre del caso: el programa sigue ejecutandose.")

if __name__ == "__main__":
    print("SOFTWARE FJ - MODULO DE CLIENTES, SERVICIOS Y RESERVAS")
    print("Pruebas simuladas de programacion orientada a objetos")
    print("Revise eventos.log al finalizar la ejecucion.\n")
    auditoria.info("ARRANQUE_APLICACION | Software FJ | Fase 4")
    plan_de_pruebas = [
        CasoDePrueba(1, "Cliente valido registrado en Bucaramanga", caso_01),
        CasoDePrueba(2, "Cliente valido registrado en Tunja", caso_02),
        CasoDePrueba(3, "Cliente invalido por nombre demasiado corto", caso_03),
        CasoDePrueba(4, "Cliente invalido por documento alfanumerico", caso_04),
        CasoDePrueba(5, "Servicio valido de sala ejecutiva", caso_05),
        CasoDePrueba(6, "Servicio valido de kit audiovisual", caso_06),
        CasoDePrueba(7, "Servicio valido de acompanamiento profesional", caso_07),
        CasoDePrueba(8, "Servicio invalido por tarifa negativa", caso_08),
        CasoDePrueba(9, "Reserva confirmada y cobrada", caso_09),
        CasoDePrueba(10, "Reserva rechazada por tiempo excesivo", caso_10),
        CasoDePrueba(11, "Reserva rechazada por servicio bloqueado", caso_11),
        CasoDePrueba(12, "Cobro rechazado porque falta confirmacion", caso_12),
        CasoDePrueba(13, "Cancelacion de reserva confirmada", caso_13),
        CasoDePrueba(14, "Busqueda de cliente inexistente", caso_14),
    ]
    for caso in plan_de_pruebas:
        ejecutar(caso)
    auditoria.info("CIERRE_APLICACION | Software FJ | Fase 4")
    print("\n" + "=" * 76)
    print("SIMULACION TERMINADA")
    print("El sistema ejecuto operaciones validas e invalidas sin detenerse.")
    print("=" * 76)
