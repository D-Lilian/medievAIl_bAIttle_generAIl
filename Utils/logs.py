import sys
from loguru import logger

CONTEXT_COLORS = {
    "general": "blue",
    "order": "magenta",
    "order-manager": "purple",
    "squad": "yellow",
    "unit_id": "cyan",
}
DEFAULT_CONTEXT_COLOR = "white"

def dynamic_formatter(record):
    """
    Cette fonction construit dynamiquement la ligne de log.
    """
    # Partie fixe du format
    log_format = (
        "<green>{time:HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}:{line}</cyan>"
    )

    if record["extra"]:
        extra_parts = []
        for key, value in record["extra"].items():
            color = CONTEXT_COLORS.get(key, DEFAULT_CONTEXT_COLOR)
            extra_parts.append(f"<{color}>{key}:{value}</{color}>")

        log_format += " | " + " | ".join(extra_parts)

    log_format += " - <level>{message}</level>\n"

    return log_format


def setup_logger(level="INFO", modules=None):
    logger.remove()  # On supprime toute configuration existante

    if not modules:
        logger.disable("__main__")
        return
    logger.enable("__main__")

    def module_filter(record):
        if record["name"] == "__main__":
            return True
        if not modules:
            return True
        return any(record["name"].startswith(mod) for mod in modules)

    logger.add(
        sys.stderr,
        level=level,
        filter=module_filter,
        format=dynamic_formatter,
        colorize=True,
    )


# par defaut on ne log rien, cad aucun module
setup_logger(modules=None)
"""
On uttilisera setup_logger(level=level, modules=[])
avec level le niveau de log désiré, et modules les modules à logguer
"""