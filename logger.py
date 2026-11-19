# logger.py
import logging


def configurar_logger(nombre_archivo="sistema_fj.log"):
    """Configura un logger que guarda eventos y errores en un archivo de texto."""
    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formato = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        archivo_handler = logging.FileHandler(nombre_archivo, encoding="utf-8")
        archivo_handler.setFormatter(formato)
        logger.addHandler(archivo_handler)

        consola_handler = logging.StreamHandler()
        consola_handler.setFormatter(formato)
        logger.addHandler(consola_handler)

    return logger