# utils/validators.py
def validate_angle_deg(value):
    """Преобразует входное значение в число в диапазоне [0, 360). Выбрасывает ValueError."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        raise ValueError("Угол должен быть числом")
    v = v % 360.0
    return v

def validate_positive_int(value, min_val=1, max_val=10000):
    """Валидация целого положительного числа, например количества точек."""
    try:
        v = int(float(value))
    except (TypeError, ValueError):
        raise ValueError("Должно быть целое число")
    if v < min_val or v > max_val:
        raise ValueError(f"Значение должно быть между {min_val} и {max_val}")
    return v
