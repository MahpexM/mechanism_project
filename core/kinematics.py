# core/kinematics.py
import numpy as np

def solve_B(A, O1, LAB, LO1B, config=1):
    """
    Решает положение точки B для четырёхзвенника.
    config=1 – правая сборка, config=0 – левая сборка.
    """
    xA, yA = A
    xO1, yO1 = O1
    u = xA - xO1
    v = yA - yO1
    d_sq = u**2 + v**2
    d = np.sqrt(d_sq)

    if d > LAB + LO1B or d + min(LAB, LO1B) < max(LAB, LO1B):
        raise ValueError(f"Невозможно собрать механизм: d={d}, LAB={LAB}, LO1B={LO1B}")

    cos_alpha = (d_sq + LAB**2 - LO1B**2) / (2 * d * LAB)
    cos_alpha = np.clip(cos_alpha, -1.0, 1.0)
    alpha = np.arccos(cos_alpha)
    theta = np.arctan2(v, u)

    if config == 1:
        beta = theta + alpha
    else:
        beta = theta - alpha

    xB = xO1 + LO1B * np.cos(beta)
    yB = yO1 + LO1B * np.sin(beta)
    return np.array([xB, yB])

def step_model(fi1_rad, LOA, LAB, LO1B, xO1, yO1, config=1, LCF=0.4):
    """Полный шаг модели – возвращает координаты и параметры для заданного fi1 (радианы)."""
    xA = LOA * np.cos(fi1_rad)
    yA = LOA * np.sin(fi1_rad)
    A = np.array([xA, yA])
    O1 = np.array([xO1, yO1])

    B = solve_B(A, O1, LAB, LO1B, config)

    # Середина AB
    xC = (xA + B[0]) / 2
    yC = (yA + B[1]) / 2

    # Вектор AB
    AB_x = B[0] - xA
    AB_y = B[1] - yA
    len_AB = np.hypot(AB_x, AB_y)

    # Перпендикуляр (поворот на +90°)
    perp_x = -AB_y / len_AB
    perp_y = AB_x / len_AB

    xF = xC + perp_x * LCF
    yF = yC + perp_y * LCF

    # Углы звеньев
    fi2 = np.arctan2(B[1] - yA, B[0] - xA)
    fi3 = np.arctan2(B[1] - yO1, B[0] - xO1)

    return {
        'fi1': fi1_rad,
        'xA': xA, 'yA': yA,
        'xB': B[0], 'yB': B[1],
        'xC': xC, 'yC': yC,
        'xF': xF, 'yF': yF,
        'LAB_calc': len_AB,
        'LO1B_calc': np.linalg.norm(B - O1),
        'fi2': fi2,
        'fi3': fi3,
    }

def step_model_deg(fi1_deg, LOA, LAB, LO1B, xO1, yO1, config=1, LCF=0.4):
    """Обёртка для step_model, принимающая угол в градусах."""
    fi1_rad = np.radians(fi1_deg)
    return step_model(fi1_rad, LOA, LAB, LO1B, xO1, yO1, config, LCF)
