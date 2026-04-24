"""Widgets visuais reutilizaveis da dashboard."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


@dataclass(frozen=True)
class KpiCardData:
    titulo: str
    valor: str
    variacao: str
    icone: str
    cor_icone: str


class KpiCardWidget(QFrame):
    def __init__(self, data: KpiCardData, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("KpiCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        top_row = QLabel(f"{data.icone}  {data.variacao}")
        top_row.setObjectName("KpiVariation")
        top_row.setProperty("iconColor", data.cor_icone)

        titulo = QLabel(data.titulo)
        titulo.setObjectName("KpiTitle")

        valor = QLabel(data.valor)
        valor.setObjectName("KpiValue")

        layout.addWidget(top_row)
        layout.addWidget(titulo)
        layout.addWidget(valor)
        layout.addStretch(1)


class EvolutionLineChartWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(220)
        self._series: list[tuple[str, QColor, list[float]]] = []
        self._labels: list[str] = []

    def set_data(self, labels: list[str], series: list[tuple[str, str, list[float]]]) -> None:
        self._labels = labels
        self._series = [(name, QColor(color), values) for name, color, values in series]
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#15243a"))

        if not self._series or not self._labels:
            return

        margin_left = 36
        margin_right = 14
        margin_top = 14
        margin_bottom = 30
        chart_w = max(1, self.width() - margin_left - margin_right)
        chart_h = max(1, self.height() - margin_top - margin_bottom)

        max_value = max(max(values) for _, _, values in self._series)
        max_value = max(max_value, 1.0)

        grid_pen = QPen(QColor("#2b4160"))
        grid_pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)
        for i in range(5):
            y = margin_top + (chart_h * i / 4)
            painter.drawLine(margin_left, int(y), margin_left + chart_w, int(y))

        for name, color, values in self._series:
            if len(values) < 2:
                continue
            path = QPainterPath()
            for idx, value in enumerate(values):
                x = margin_left + (chart_w * idx / (len(values) - 1))
                y = margin_top + chart_h - (chart_h * (value / max_value))
                if idx == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)

            pen = QPen(color)
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawPath(path)

            for idx, value in enumerate(values):
                x = margin_left + (chart_w * idx / (len(values) - 1))
                y = margin_top + chart_h - (chart_h * (value / max_value))
                painter.setBrush(color)
                painter.drawEllipse(QPointF(x, y), 2.8, 2.8)

        painter.setPen(QColor("#9fb7d4"))
        font = QFont()
        font.setPointSize(8)
        painter.setFont(font)
        for idx, label in enumerate(self._labels):
            x = margin_left + (chart_w * idx / (len(self._labels) - 1))
            painter.drawText(int(x - 10), self.height() - 10, label)


class DonutChartWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumSize(240, 220)
        self._segments: list[tuple[str, QColor, float]] = []
        self._center_title = "TOTAL"
        self._center_value = "R$ 0,00"

    def set_data(self, center_value: str, segments: list[tuple[str, str, float]]) -> None:
        self._center_value = center_value
        self._segments = [(label, QColor(color), value) for label, color, value in segments]
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#15243a"))

        if not self._segments:
            return

        positive_segments = [(label, color, value) for label, color, value in self._segments if value > 0]
        if not positive_segments:
            return

        total = sum(value for _, _, value in positive_segments)
        total = max(total, 1.0)

        size = min(self.width(), self.height()) - 40
        left = (self.width() - size) / 2
        top = (self.height() - size) / 2

        rect = self.rect().adjusted(int(left), int(top), -int(left), -int(top))
        start_angle = 90 * 16
        total_units = 360 * 16
        consumed_units = 0

        for idx, (_, color, value) in enumerate(positive_segments):
            if idx == len(positive_segments) - 1:
                span_units = total_units - consumed_units
            else:
                span_units = int(round((value / total) * total_units))
                consumed_units += span_units
            span = -span_units
            pen = QPen(color)
            pen.setWidth(18)
            # FlatCap evita superestimar visualmente segmentos pequenos.
            pen.setCapStyle(Qt.PenCapStyle.FlatCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawArc(rect, start_angle, span)
            start_angle += span

        painter.setPen(QColor("#dfeaff"))
        t_font = QFont()
        t_font.setPointSize(8)
        t_font.setBold(True)
        painter.setFont(t_font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter, f"{self._center_title}\n{self._center_value}")
