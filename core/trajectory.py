# core/trajectory.py
import numpy as np
from .kinematics import step_model_deg

def compute_trajectory(LOA, LAB, LO1B, xO1, yO1, config, LCF, n_points=360):
    """
    Возвращает массив точек траектории F (x,y) для полного оборота кривошипа.
    n_points – количество точек на 360°.
    """
    angles_deg = np.linspace(0, 360, n_points, endpoint=False)
    traj = []
    for deg in angles_deg:
        res = step_model_deg(deg, LOA, LAB, LO1B, xO1, yO1, config, LCF)
        traj.append([res['xF'], res['yF']])
    return np.array(traj)

def compute_arc_length(points, start_deg, end_deg, n_points_total=360):
    """
    Вычисляет длину дуги траектории между углами start_deg и end_deg (градусы).
    points – массив точек, соответствующих равномерной разбивке 0..360 (n_points_total).
    Если start_deg > end_deg, обход идёт через 360°.
    Возвращает длину и кортеж (индексы начала, конца, массив точек подсвечиваемого участка).
    """
    N = len(points)
    # Нормализация углов в [0, 360)
    start = start_deg % 360.0
    end = end_deg % 360.0

    # Индексы с учётом дискретности
    idx_start = int(round(start / 360.0 * (N - 1)))
    idx_end = int(round(end / 360.0 * (N - 1)))

    if start <= end:
        indices = list(range(idx_start, idx_end + 1))
    else:
        indices = list(range(idx_start, N)) + list(range(0, idx_end + 1))

    # Сборка массива выделяемых точек
    subset = points[indices] if isinstance(indices, slice) else points[indices]

    # Длина через сумму евклидовых расстояний
    length = 0.0
    for i in range(len(indices) - 1):
        p1 = points[indices[i]]
        p2 = points[indices[i+1]]
        length += np.hypot(p2[0] - p1[0], p2[1] - p1[1])

    return length, (indices[0], indices[-1], subset)
