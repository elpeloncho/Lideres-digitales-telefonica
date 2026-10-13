DEMO_DISTRICT_CENTERS: tuple[tuple[str, float, float], ...] = (
    ("Centro", 36.721, -4.421),
    ("Este", 36.718, -4.401),
    ("Ciudad Jardín", 36.746, -4.426),
    ("Bailén-Miraflores", 36.735, -4.438),
    ("Palma-Palmilla", 36.741, -4.432),
    ("Cruz de Humilladero", 36.711, -4.452),
    ("Carretera de Cádiz", 36.684, -4.438),
    ("Churriana", 36.665, -4.493),
    ("Campanillas", 36.674, -4.528),
    ("Puerto de la Torre", 36.741, -4.474),
    ("Teatinos-Universidad", 36.716, -4.483),
)


def classify_demo_district(latitude: float, longitude: float) -> str:
    """Assign an approximate demo district using its representative center."""
    return min(
        DEMO_DISTRICT_CENTERS,
        key=lambda center: (latitude - center[1]) ** 2 + (longitude - center[2]) ** 2,
    )[0]
