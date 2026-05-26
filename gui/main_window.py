# gui/main_window.py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider, CheckButtons
from matplotlib import rcParams

from config import *
from core import step_model_deg, compute_trajectory
from gui.analysis_window import open_analysis_window

rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'SimHei']
rcParams['axes.unicode_minus'] = False


class MechanismApp:
    def __init__(self):
        self.state = {
            'fi1_deg': 0.0,
            'anim_running': False,
            'direction': 1,
            'config': 1,
            'show_labels': True,
            'speed_rpm': DEFAULT_SPEED_RPM,
            'trajectory_F': None,      # будет пересчитано при инициализации и смене сборки
        }
        self._create_figure()
        self._init_widgets()
        self._update_trajectory()
        self._redraw_plot()
        plt.show()

    def _create_figure(self):
        self.fig = plt.figure(figsize=(15, 9))
        self.fig.suptitle("Четырёхзвенный механизм", fontsize=16, fontweight='bold')

        self.ax_plot = plt.axes([0.05, 0.1, 0.55, 0.8])
        self.ax_slider = plt.axes([0.1, 0.03, 0.45, 0.03])
        self.slider_fi1 = Slider(self.ax_slider, r"$\phi_1$ [°]", 0.0, 360.0,
                                 valinit=0.0, valfmt="%.1f°")

        # Правая панель
        self.ax_panel = plt.axes([0.65, 0.1, 0.3, 0.8])
        self.ax_panel.set_xlim(0, 1)
        self.ax_panel.set_ylim(0, 1)
        self.ax_panel.axis('off')

        # Текстовая информация
        self.ax_info = plt.axes([0.68, 0.1, 0.27, 0.38])
        self.ax_info.axis('off')

        # Надпись "СКОРОСТЬ"
        ax_speed_label = plt.axes([0.68, 0.63, 0.12, 0.03])
        ax_speed_label.axis('off')
        ax_speed_label.text(0.5, 0.5, "СКОРОСТЬ (об/мин)", ha='center', va='center',
                            fontsize=9, fontweight='bold')

        # Кнопки
        ax_play = plt.axes([0.68, 0.82, 0.12, 0.06])
        self.button_play = Button(ax_play, "ПУСК", color='lightgreen', hovercolor='green')

        ax_dir = plt.axes([0.68, 0.74, 0.12, 0.06])
        self.button_dir = Button(ax_dir, "НАПР.", color='lightblue', hovercolor='blue')

        ax_config = plt.axes([0.68, 0.66, 0.12, 0.06])
        self.button_config = Button(ax_config, "СБОРКА", color='yellow', hovercolor='orange')

        ax_speed_up = plt.axes([0.68, 0.58, 0.06, 0.05])
        self.button_speed_up = Button(ax_speed_up, "+", color='lightgray', hovercolor='gray')
        ax_speed_down = plt.axes([0.74, 0.58, 0.06, 0.05])
        self.button_speed_down = Button(ax_speed_down, "-", color='lightgray', hovercolor='gray')

        ax_check = plt.axes([0.68, 0.50, 0.15, 0.05])
        self.check_labels = CheckButtons(ax_check, ['Подписи'], [True])

        # Кнопка анализа шатунной кривой
        ax_analyze = plt.axes([0.86, 0.42, 0.12, 0.05])
        self.button_analyze = Button(ax_analyze, "АНАЛИЗ", color='lightyellow', hovercolor='orange')

        # Привязка событий
        self.slider_fi1.on_changed(self._on_slider)
        self.button_play.on_clicked(self._on_play)
        self.button_dir.on_clicked(self._on_dir)
        self.button_config.on_clicked(self._on_config)
        self.button_speed_up.on_clicked(self._on_speed_up)
        self.button_speed_down.on_clicked(self._on_speed_down)
        self.check_labels.on_clicked(self._on_labels)
        self.button_analyze.on_clicked(self._on_analyze)

    def _init_widgets(self):
        pass

    def _update_trajectory(self, n_points=360):
        """Пересчитывает траекторию F для текущей сборки."""
        self.state['trajectory_F'] = compute_trajectory(
            LOA, LAB, LO1B, xO1, yO1,
            config=self.state['config'],
            LCF=LCF,
            n_points=n_points
        )

    def _redraw_plot(self):
        res = step_model_deg(self.state['fi1_deg'], LOA, LAB, LO1B, xO1, yO1,
                             self.state['config'], LCF)

        self.ax_plot.clear()
        self.ax_plot.grid(True, linestyle='--', alpha=0.3)
        self.ax_plot.axis('equal')
        self.ax_plot.set_xlim(*X_LIM)
        self.ax_plot.set_ylim(*Y_LIM)
        self.ax_plot.set_xlabel("X", fontsize=11)
        self.ax_plot.set_ylabel("Y", fontsize=11)

        # траектория F
        if self.state['trajectory_F'] is not None and len(self.state['trajectory_F']) > 0:
            self.ax_plot.plot(self.state['trajectory_F'][:, 0],
                              self.state['trajectory_F'][:, 1],
                              'c--', linewidth=1, alpha=0.6, label='Траектория F')

        # звенья
        self.ax_plot.plot([0, res['xA']], [0, res['yA']], 'b-', lw=3, label='OA')
        self.ax_plot.plot([res['xA'], res['xB']], [res['yA'], res['yB']], 'r-', lw=3, label='AB')
        self.ax_plot.plot([xO1, res['xB']], [yO1, res['yB']], 'g-', lw=3, label='O1B')
        self.ax_plot.plot([res['xC'], res['xF']], [res['yC'], res['yF']], 'm-', lw=2, label='CF')

        # точки
        self.ax_plot.plot(0, 0, 'ko', ms=10, zorder=5)
        self.ax_plot.plot(xO1, yO1, 'ks', ms=10, zorder=5)
        self.ax_plot.plot(res['xA'], res['yA'], 'bo', ms=8, zorder=5)
        self.ax_plot.plot(res['xB'], res['yB'], 'ro', ms=8, zorder=5)
        self.ax_plot.plot(res['xC'], res['yC'], 'mo', ms=6, zorder=5)
        self.ax_plot.plot(res['xF'], res['yF'], 'co', ms=8, zorder=5)

        if self.state['show_labels']:
            self.ax_plot.annotate('O', (0, 0), xytext=(-15, -15), textcoords='offset points',
                                  fontsize=11, fontweight='bold')
            self.ax_plot.annotate('O1', (xO1, yO1), xytext=(5, -15), textcoords='offset points',
                                  fontsize=11, fontweight='bold')
            self.ax_plot.annotate('A', (res['xA'], res['yA']), xytext=(5, 5),
                                  textcoords='offset points', fontsize=11)
            self.ax_plot.annotate('B', (res['xB'], res['yB']), xytext=(5, 5),
                                  textcoords='offset points', fontsize=11)
            self.ax_plot.annotate('C', (res['xC'], res['yC']), xytext=(5, -10),
                                  textcoords='offset points', fontsize=11)
            self.ax_plot.annotate('F', (res['xF'], res['yF']), xytext=(5, 5),
                                  textcoords='offset points', fontsize=11, color='c')

        self.ax_plot.legend(loc='upper left', fontsize=9)

        # Информационная панель
        self.ax_info.clear()
        self.ax_info.axis('off')
        info_text = (
            f"ПАРАМЕТРЫ\n{'-' * 20}\n"
            f"OA = {LOA}\nAB = {LAB}\nO₁B = {LO1B}\nCF = {LCF}\n\n"
            f"ТЕКУЩИЕ ЗНАЧЕНИЯ\n{'-' * 20}\n"
            f"φ₁ = {self.state['fi1_deg']:.1f}°\n"
            f"φ₂ = {np.degrees(res['fi2']):.1f}°\n"
            f"φ₃ = {np.degrees(res['fi3']):.1f}°\n\n"
            f"AB факт = {res['LAB_calc']:.3f}\n"
            f"O₁B факт = {res['LO1B_calc']:.3f}\n\n"
            f"F = ({res['xF']:.3f}, {res['yF']:.3f})\n\n"
            f"СБОРКА: {self.state['config']}\n"
            f"СКОРОСТЬ: {self.state['speed_rpm']:.0f} об/мин"
        )
        self.ax_info.text(0.05, 0.95, info_text, fontsize=10,
                          verticalalignment='top', family='monospace')
        self.fig.canvas.draw_idle()

    def _animate_step(self):
        if not self.state['anim_running']:
            return
        deg_per_frame = self.state['speed_rpm'] * 360 / 60 / (1000 / FRAME_TIME_MS)
        new_deg = (self.state['fi1_deg'] + deg_per_frame * self.state['direction']) % 360.0
        self.state['fi1_deg'] = new_deg
        self.slider_fi1.set_val(new_deg)
        self._redraw_plot()
        self.fig.canvas.flush_events()
        plt.pause(0.02)                        # задержка
        if self.state['anim_running']:
            self._animate_step()               # рекурсивный вызов (не стекобоязнь, т.к. пауза)

    # ---- Обработчики событий ----
    def _on_slider(self, val):
        if not self.state['anim_running']:
            self.state['fi1_deg'] = val
            self._redraw_plot()

    def _on_play(self, event):
        self.state['anim_running'] = not self.state['anim_running']
        if self.state['anim_running']:
            self.button_play.label.set_text("СТОП")
            self.button_play.color = 'lightcoral'
            self.button_play.hovercolor = 'red'
            self._animate_step()
        else:
            self.button_play.label.set_text("ПУСК")
            self.button_play.color = 'lightgreen'
            self.button_play.hovercolor = 'green'

    def _on_dir(self, event):
        self.state['direction'] *= -1

    def _on_config(self, event):
        self.state['config'] = 1 - self.state['config']
        self._update_trajectory()
        self._redraw_plot()
        # При смене сборки закроем окно анализа, если оно открыто (просто предупреждение)
        try:
            plt.close('analysis')
        except:
            pass

    def _on_speed_up(self, event):
        self.state['speed_rpm'] = min(self.state['speed_rpm'] + 10.0, 120.0)
        self._redraw_plot()

    def _on_speed_down(self, event):
        self.state['speed_rpm'] = max(self.state['speed_rpm'] - 10.0, 10.0)
        self._redraw_plot()

    def _on_labels(self, event):
        self.state['show_labels'] = not self.state['show_labels']
        self._redraw_plot()

    def _on_analyze(self, event):
        # Открыть окно анализа, передав текущую траекторию и параметры
        if self.state['trajectory_F'] is None:
            return
        open_analysis_window(
            trajectory=self.state['trajectory_F'],
            config=self.state['config'],
            LOA=LOA, LAB=LAB, LO1B=LO1B, LCF=LCF, xO1=xO1, yO1=yO1
        )
