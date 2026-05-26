# gui/analysis_window.py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from core.trajectory import compute_arc_length

def open_analysis_window(trajectory, config, LOA, LAB, LO1B, LCF, xO1, yO1):
    fig = plt.figure(figsize=(14, 9))
    fig.canvas.manager.set_window_title('Анализ шатунной кривой')
    
    ax = plt.axes([0.04, 0.12, 0.50, 0.80])
    ax.set_title("Траектория точки F")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(True, alpha=0.3)
    ax.axis('equal')
    
    traj = np.array(trajectory, copy=True)
    n_points_full = len(traj)   # обычно 360
    
    start_deg = 0.0
    end_deg = 90.0
    n_used = n_points_full       # точность (количество используемых точек)
    
    # ---- Элементы управления (только слайдеры и кнопка) ----
    left = 0.65
    w_slider = 0.28
    
    start_deg = 180
    end_deg = 270
    
    ax_start_slider = plt.axes([left, 0.80, w_slider, 0.04])
    slider_start = Slider(ax_start_slider, "Нач. угол, °", 0, 360, valinit=start_deg, valfmt="%.1f°")
    
    ax_end_slider = plt.axes([left, 0.68, w_slider, 0.04])
    slider_end = Slider(ax_end_slider, "Кон. угол, °", 0, 360, valinit=end_deg, valfmt="%.1f°")
    
    # Ползунок точности
    ax_quality = plt.axes([left, 0.56, w_slider, 0.04])
    quality_slider = Slider(ax_quality, "Точность (точек)", 30, n_points_full, valinit=n_points_full, valfmt="%d")
    
    # Информационные поля (просто текст)
    ax_start_info = plt.axes([left, 0.74, 0.15, 0.04])
    ax_start_info.axis('off')
    start_info = ax_start_info.text(0, 0.5, f"Нач. угол: {start_deg:.1f}°", fontsize=10)
    
    ax_end_info = plt.axes([left, 0.62, 0.15, 0.04])
    ax_end_info.axis('off')
    end_info = ax_end_info.text(0, 0.5, f"Кон. угол: {end_deg:.1f}°", fontsize=10)
    
    # Кнопка "Рассчитать" (пересчёт длины)
    ax_calc = plt.axes([left, 0.46, 0.18, 0.06])
    btn_calc = Button(ax_calc, "Рассчитать", color='lightgreen')
    
    # Поле результата
    ax_result = plt.axes([left, 0.15, 0.28, 0.20])
    result_text = ax_result.text(0.05, 0.6, "Длина = 0.00000", fontsize=14)
    ax_result.axis('off')
    
    # ---- Графика ----
    ax.plot(traj[:, 0], traj[:, 1], 'c-', lw=1.2, alpha=0.5, label='Вся траектория')
    highlight_line, = ax.plot([], [], 'r-', lw=2.5, label='Выбранный участок')
    ax.legend(loc='upper left')
    
    # ---- Функции ----
    def get_indices_for_angles(start, end, n_points):
        """Индексы точек для диапазона углов при заданной дискретизации."""
        if n_points <= 1:
            return [0]
        step = 360.0 / (n_points - 1)
        start_idx = int(round(start / step))
        end_idx = int(round(end / step))
        if start <= end:
            return list(range(start_idx, end_idx + 1))
        else:
            return list(range(start_idx, n_points)) + list(range(0, end_idx + 1))
    
    def update_highlight():
        """Быстрое обновление красной линии (без пересчёта длины)."""
        # Прореживаем траекторию до n_used точек
        step_full = (n_points_full - 1) / (n_used - 1) if n_used > 1 else 0
        idx_used = np.round(np.linspace(0, n_points_full - 1, n_used)).astype(int)
        traj_used = traj[idx_used]
        indices = get_indices_for_angles(start_deg, end_deg, n_used)
        if len(indices) > 1:
            highlight_line.set_data(traj_used[indices, 0], traj_used[indices, 1])
        else:
            highlight_line.set_data([], [])
        start_info.set_text(f"Нач. угол: {start_deg:.1f}°")
        end_info.set_text(f"Кон. угол: {end_deg:.1f}°")
        fig.canvas.draw_idle()
    
    def compute_length():
        """Полный расчёт длины с текущей точностью."""
        step_full = (n_points_full - 1) / (n_used - 1) if n_used > 1 else 0
        idx_used = np.round(np.linspace(0, n_points_full - 1, n_used)).astype(int)
        traj_used = traj[idx_used]
        length, _ = compute_arc_length(traj_used, start_deg, end_deg, n_used)
        result_text.set_text(f"Длина дуги = {length:.5f}")
        fig.canvas.draw_idle()
    
    # ---- Обработчики событий ----
    def on_start(val):
        nonlocal start_deg
        start_deg = val
        update_highlight()
    
    def on_end(val):
        nonlocal end_deg
        end_deg = val
        update_highlight()
    
    def on_quality(val):
        nonlocal n_used
        n_used = int(val)
        update_highlight()
        # Можно сразу пересчитать длину, но лучше по кнопке
        # compute_length()
    
    def on_calc(event):
        compute_length()
    
    slider_start.on_changed(on_start)
    slider_end.on_changed(on_end)
    quality_slider.on_changed(on_quality)
    btn_calc.on_clicked(on_calc)
    
    # Инициализация
    update_highlight()
    # Начальный расчёт длины
    compute_length()
    plt.show()
