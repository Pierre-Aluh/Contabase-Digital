"""Dashboard funcional com componentes reais e dados fiscais (com fallback)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy import select

from app.db.session_manager import get_session
from app.models.competencia import Competencia
from app.models.empresa import Empresa
from app.models.enums import StatusObrigacao
from app.models.lancamento_fiscal import LancamentoFiscal
from app.models.obra import Obra
from app.models.obrigacao_vencimento import ObrigacaoVencimento
from app.services import FiscalCalculationService, GuiaFilter, GuiaService
from app.ui.widgets.dashboard_widgets import DonutChartWidget, EvolutionLineChartWidget, KpiCardData, KpiCardWidget
from app.utils.formatters import format_brl, format_date_br


class DashboardPage(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("DashboardPage")
        self._fiscal_service = FiscalCalculationService()
        self._guia_service = GuiaService()

        self._mock = self._default_mock_data()
        self._build_ui()
        self._refresh_dashboard_data()

    def on_filters_changed(self) -> None:
        self._refresh_dashboard_data()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(12)

        self.title_label = QLabel("Dashboard Fiscal")
        self.title_label.setObjectName("DashboardHeroTitle")
        self.subtitle_label = QLabel("Visao executiva de faturamento, apuracao e vencimentos")
        self.subtitle_label.setObjectName("DashboardHeroSubtitle")
        root.addWidget(self.title_label)
        root.addWidget(self.subtitle_label)

        kpi_row = QGridLayout()
        kpi_row.setHorizontalSpacing(10)
        kpi_row.setVerticalSpacing(10)
        self.kpi_cards: list[KpiCardWidget] = []
        for idx in range(4):
            card = KpiCardWidget(
                KpiCardData(
                    titulo="-",
                    valor="R$ 0,00",
                    variacao="0,0%",
                    icone="•",
                    cor_icone="#00d9ff",
                )
            )
            self.kpi_cards.append(card)
            kpi_row.addWidget(card, 0, idx)
            kpi_row.setColumnStretch(idx, 1)
        root.addLayout(kpi_row)

        mid_row = QHBoxLayout()
        mid_row.setSpacing(10)

        line_card = QFrame()
        line_card.setObjectName("DashCard")
        line_layout = QVBoxLayout(line_card)
        line_layout.setContentsMargins(12, 10, 12, 12)
        line_layout.setSpacing(8)
        line_title = QLabel("Faturamento Mensal x Impostos")
        line_title.setObjectName("DashSectionTitle")
        self.line_chart = EvolutionLineChartWidget()
        self.line_legend = QLabel()
        self.line_legend.setObjectName("DashLegend")
        line_layout.addWidget(line_title)
        line_layout.addWidget(self.line_chart, 1)
        line_layout.addWidget(self.line_legend)
        mid_row.addWidget(line_card, 3)

        summary_card = QFrame()
        summary_card.setObjectName("DashCard")
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(12, 10, 12, 12)
        summary_layout.setSpacing(6)
        summary_title = QLabel("Resumo da Apuracao")
        summary_title.setObjectName("DashSectionTitle")
        self.summary_period = QLabel("Periodo: -")
        self.summary_period.setObjectName("DashMuted")
        self.summary_company = QLabel("Empresa: -")
        self.summary_company.setObjectName("DashMuted")
        summary_layout.addWidget(summary_title)
        summary_layout.addWidget(self.summary_period)
        summary_layout.addWidget(self.summary_company)

        self.summary_rows: dict[str, QLabel] = {}
        for tributo in ["PIS", "COFINS", "CSLL", "IRPJ", "IRPJ_ADICIONAL", "ISS"]:
            row = QLabel(f"{tributo}: R$ 0,00")
            row.setObjectName("DashTaxRow")
            self.summary_rows[tributo] = row
            summary_layout.addWidget(row)

        self.summary_tipo_apuracao = QLabel()
        self.summary_tipo_apuracao.setObjectName("DashApuracaoTipo")
        self.summary_total = QLabel("TOTAL: R$ 0,00")
        self.summary_total.setObjectName("DashTotal")
        self.summary_effective = QLabel("Alíquota efetiva: 0,00%")
        self.summary_effective.setObjectName("DashMuted")
        self.summary_status = QLabel("Status: EM ABERTO")
        self.summary_status.setObjectName("DashStatusWarning")
        self.summary_due = QLabel("Próx. vencimento: -")
        self.summary_due.setObjectName("DashMuted")
        summary_layout.addWidget(self.summary_tipo_apuracao)
        summary_layout.addWidget(self.summary_total)
        summary_layout.addWidget(self.summary_effective)
        summary_layout.addWidget(self.summary_status)
        summary_layout.addWidget(self.summary_due)
        summary_layout.addStretch(1)
        mid_row.addWidget(summary_card, 2)
        root.addLayout(mid_row, 2)

        low_row = QHBoxLayout()
        low_row.setSpacing(10)

        table_card = QFrame()
        table_card.setObjectName("DashCard")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(12, 10, 12, 12)
        table_layout.setSpacing(8)
        table_title = QLabel("Composicao dos Tributos - Lucro Presumido")
        table_title.setObjectName("DashSectionTitle")
        self.tributos_table = QTableWidget(0, 4)
        self.tributos_table.setObjectName("DashTributosTable")
        self.tributos_table.setHorizontalHeaderLabels(["Tributo", "Base de Calculo", "Aliquota", "Valor Calculado"])
        self.tributos_table.verticalHeader().setVisible(False)
        self.tributos_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tributos_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.tributos_table.horizontalHeader().setStretchLastSection(True)
        table_layout.addWidget(table_title)
        table_layout.addWidget(self.tributos_table)
        low_row.addWidget(table_card, 3)

        donut_card = QFrame()
        donut_card.setObjectName("DashCard")
        donut_layout = QVBoxLayout(donut_card)
        donut_layout.setContentsMargins(12, 10, 12, 12)
        donut_layout.setSpacing(8)
        donut_title = QLabel("Distribuicao dos Tributos")
        donut_title.setObjectName("DashSectionTitle")
        self.donut_chart = DonutChartWidget()
        self.donut_legend = QLabel()
        self.donut_legend.setObjectName("DashLegend")
        self.donut_legend.setTextFormat(Qt.TextFormat.RichText)
        self.donut_legend.setWordWrap(True)
        donut_layout.addWidget(donut_title)
        donut_layout.addWidget(self.donut_chart, 1)
        donut_layout.addWidget(self.donut_legend)
        low_row.addWidget(donut_card, 2)

        due_card = QFrame()
        due_card.setObjectName("DashCard")
        due_layout = QVBoxLayout(due_card)
        due_layout.setContentsMargins(12, 10, 12, 12)
        due_layout.setSpacing(6)
        due_title = QLabel("Proximos Vencimentos")
        due_title.setObjectName("DashSectionTitle")
        self.due_list = QVBoxLayout()
        self.due_list.setSpacing(6)
        due_layout.addWidget(due_title)
        due_layout.addLayout(self.due_list)
        due_layout.addStretch(1)
        low_row.addWidget(due_card, 2)
        root.addLayout(low_row, 3)

        actions = QFrame()
        actions.setObjectName("DashActionsBar")
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(12, 10, 12, 10)
        actions_layout.setSpacing(10)
        self.btn_gerar_guia = QPushButton("Gerar Guia")
        self.btn_gerar_guia.setObjectName("DashActionPrimary")
        self.btn_exportar = QPushButton("Exportar Relatorio")
        self.btn_exportar.setObjectName("DashActionSecondary")
        self.btn_compartilhar = QPushButton("Compartilhar")
        self.btn_compartilhar.setObjectName("DashActionSecondary")
        actions_layout.addWidget(self.btn_gerar_guia)
        actions_layout.addWidget(self.btn_exportar)
        actions_layout.addWidget(self.btn_compartilhar)
        actions_layout.addStretch(1)
        root.addWidget(actions)

        footer = QFrame()
        footer.setObjectName("DashFooter")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(12, 8, 12, 8)
        footer_layout.setSpacing(8)
        self.footer_label = QLabel("Atualizado agora")
        self.footer_label.setObjectName("DashMuted")
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setObjectName("DashTinyButton")
        self.btn_menu = QPushButton("Menu")
        self.btn_menu.setObjectName("DashTinyButton")
        footer_layout.addWidget(self.footer_label)
        footer_layout.addStretch(1)
        footer_layout.addWidget(self.btn_refresh)
        footer_layout.addWidget(self.btn_menu)
        root.addWidget(footer)

        self.btn_refresh.clicked.connect(self._refresh_dashboard_data)
        self.btn_gerar_guia.clicked.connect(lambda: self._navigate("guias"))
        self.btn_exportar.clicked.connect(lambda: self._navigate("relatorios"))
        self.btn_compartilhar.clicked.connect(self._share_summary)

    def _share_summary(self) -> None:
        text = (
            f"{self.summary_period.text()}\n"
            f"{self.summary_company.text()}\n"
            f"{self.summary_total.text()}\n"
            f"{self.summary_status.text()}"
        )
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(text)
        QMessageBox.information(self, "Compartilhar", "Resumo copiado para a area de transferencia")

    def _navigate(self, page: str) -> None:
        window = self.window()
        if hasattr(window, "navigate_to"):
            window.navigate_to(page)

    def _refresh_dashboard_data(self) -> None:
        data = self._load_real_data_or_fallback()
        self._mock = data
        self._render_data()

    def _load_real_data_or_fallback(self) -> dict:
        try:
            with get_session() as session:
                all_empresas = list(session.execute(select(Empresa).order_by(Empresa.razao_social.asc())).scalars().all())
                if not all_empresas:
                    return self._default_mock_data()

                payload = self._get_filter_payload()
                search_text = str(payload.get("search") or "").strip().lower()

                empresa_id = payload.get("empresa_id")
                obra_id = payload.get("obra_id")
                obra_empresa_id = payload.get("obra_empresa_id")
                obra_ids_filter: set[int] | None = None

                if isinstance(empresa_id, int):
                    empresa_ids = [empresa_id]
                elif isinstance(obra_id, int) and isinstance(obra_empresa_id, int):
                    empresa_ids = [obra_empresa_id]
                else:
                    empresa_ids = [e.id for e in all_empresas]

                if search_text:
                    all_obras = list(session.execute(select(Obra).order_by(Obra.nome.asc())).scalars().all())

                    matched_empresas = {
                        e.id
                        for e in all_empresas
                        if search_text in e.razao_social.lower()
                        or search_text in (e.nome_fantasia or "").lower()
                        or search_text in (e.cnpj or "")
                    }
                    matched_obras = [
                        o
                        for o in all_obras
                        if search_text in o.nome.lower() or search_text in (o.codigo_interno or "").lower()
                    ]
                    matched_empresas.update(o.empresa_id for o in matched_obras)

                    empresa_ids = [eid for eid in empresa_ids if eid in matched_empresas]
                    if not empresa_ids:
                        return self._empty_real_data("Busca sem resultados")

                    if not isinstance(obra_id, int):
                        obra_ids_filter = {o.id for o in matched_obras if o.empresa_id in empresa_ids}

                selected_comp_ids, period_label = self._resolve_period_scope(payload)
                if not selected_comp_ids:
                    return self._empty_real_data("Período sem competências válidas")

                refs = list(
                    session.execute(select(Competencia).where(Competencia.id.in_(selected_comp_ids)))
                    .scalars()
                    .all()
                )
                ref_by_id = {c.id: c for c in refs}

                scopes: list[tuple[int, int | None]] = []
                if isinstance(obra_id, int):
                    for emp_id in empresa_ids:
                        scopes.append((emp_id, obra_id))
                elif obra_ids_filter:
                    obra_to_empresa = {o.id: o.empresa_id for o in session.execute(select(Obra)).scalars().all()}
                    for oid in sorted(obra_ids_filter):
                        emp = obra_to_empresa.get(oid)
                        if emp in empresa_ids:
                            scopes.append((emp, oid))
                else:
                    for emp_id in empresa_ids:
                        scopes.append((emp_id, None))

                if not scopes:
                    return self._empty_real_data("Escopo vazio para os filtros informados")

                tributos_total: dict[str, dict[str, Decimal]] = {
                    "PIS": {"base_final": Decimal("0.00"), "imposto_devido": Decimal("0.00")},
                    "COFINS": {"base_final": Decimal("0.00"), "imposto_devido": Decimal("0.00")},
                    "CSLL": {"base_final": Decimal("0.00"), "imposto_devido": Decimal("0.00")},
                    "IRPJ": {"base_final": Decimal("0.00"), "imposto_devido": Decimal("0.00")},
                    "IRPJ_ADICIONAL": {"base_final": Decimal("0.00"), "imposto_devido": Decimal("0.00")},
                    "ISS": {"base_final": Decimal("0.00"), "imposto_devido": Decimal("0.00")},
                }

                is_fechamento = False
                total = Decimal("0.00")
                receita_atual = Decimal("0.00")
                for emp_id, scope_obra_id in scopes:
                    for comp_id in selected_comp_ids:
                        try:
                            result = self._fiscal_service.calculate_for_scope(
                                empresa_id=emp_id,
                                competencia_id=comp_id,
                                obra_id=scope_obra_id,
                                consolidada=not isinstance(scope_obra_id, int),
                                persist=False,
                            )
                        except Exception:
                            continue
                        if result.fechamento_trimestral:
                            is_fechamento = True
                        receita_atual += self._sum_receita(emp_id, comp_id, scope_obra_id)
                        total += result.total_impostos
                        for tributo, values in result.tributos.items():
                            tributos_total[tributo]["base_final"] += values["base_final"]
                            tributos_total[tributo]["imposto_devido"] += values["imposto_devido"]

                receita_anterior = Decimal("0.00")
                impostos_anteriores = Decimal("0.00")

                preview_comp = ref_by_id.get(selected_comp_ids[-1])
                if preview_comp:
                    prev_comp = session.execute(
                        select(Competencia)
                        .where(
                            (Competencia.ano < preview_comp.ano)
                            | ((Competencia.ano == preview_comp.ano) & (Competencia.mes < preview_comp.mes))
                        )
                        .order_by(Competencia.ano.desc(), Competencia.mes.desc())
                        .limit(1)
                    ).scalar_one_or_none()
                    if prev_comp:
                        for emp_id, scope_obra_id in scopes:
                            receita_anterior += self._sum_receita(
                                emp_id,
                                prev_comp.id,
                                scope_obra_id,
                            )
                            impostos_anteriores += self._sum_impostos(
                                emp_id,
                                prev_comp.id,
                                scope_obra_id,
                            )

                pis = tributos_total["PIS"]["imposto_devido"]
                cofins = tributos_total["COFINS"]["imposto_devido"]
                irpj = tributos_total["IRPJ"]["imposto_devido"]
                csll = tributos_total["CSLL"]["imposto_devido"]
                iss = tributos_total["ISS"]["imposto_devido"]
                base_calculo = tributos_total["IRPJ"]["base_final"] + tributos_total["CSLL"]["base_final"]

                trend = self._build_trend(scopes=scopes)
                due_items = self._build_due_items(
                    empresa_ids=empresa_ids,
                    competencia_ids=selected_comp_ids,
                    obra_id=obra_id if isinstance(obra_id, int) else None,
                    obra_ids=obra_ids_filter,
                )

                if isinstance(empresa_id, int):
                    company_label = next((e.razao_social for e in all_empresas if e.id == empresa_id), "Empresa")
                else:
                    company_label = "Todas as Empresas"

                if isinstance(obra_id, int):
                    company_label = f"{company_label} | Obra selecionada"
                elif obra_ids_filter:
                    company_label = f"{company_label} | Obras filtradas por busca"

                # Determinar status consolidado das obrigações
                status_geral = self._resolve_status_geral(due_items)

                # Indicador projeção vs fechamento
                mode = (payload.get("period") or {}).get("mode", "MES")
                if mode in ("TRIMESTRE", "ANUAL", "PERSONALIZADO"):
                    tipo_apuracao = "CONSOLIDADO MULTI-PERÍODO"
                elif is_fechamento:
                    tipo_apuracao = "FECHAMENTO TRIMESTRAL"
                else:
                    tipo_apuracao = "PROJEÇÃO MENSAL  —  IRPJ/CSLL/Adic. são estimativas até o fechamento trimestral"

                return {"_is_real": True, "_tipo_apuracao": tipo_apuracao, "_is_fechamento": is_fechamento,
                    "kpis": [
                        {
                            "title": "Faturamento Bruto",
                            "value": format_brl(receita_atual),
                            "variation": self._variation(receita_atual, receita_anterior),
                            "icon": "◎",
                        },
                        {
                            "title": "Base de Calculo",
                            "value": format_brl(base_calculo),
                            "variation": self._variation(base_calculo, Decimal("0.00")),
                            "icon": "◉",
                        },
                        {
                            "title": "Total de Impostos",
                            "value": format_brl(total),
                            "variation": self._variation(total, impostos_anteriores),
                            "icon": "◈",
                        },
                        {
                            "title": "Aliquota Efetiva",
                            "value": f"{self._percent(total, receita_atual):.2f}%",
                            "variation": self._variation(total, impostos_anteriores),
                            "icon": "◆",
                        },
                    ],
                    "trend": trend,
                    "summary": {
                        "period": period_label,
                        "company": company_label,
                        "taxes": {
                            "PIS": format_brl(pis),
                            "COFINS": format_brl(cofins),
                            "CSLL": format_brl(csll),
                            "IRPJ": format_brl(irpj),
                            "IRPJ_ADICIONAL": format_brl(tributos_total["IRPJ_ADICIONAL"]["imposto_devido"]),
                            "ISS": format_brl(iss),
                        },
                        "total": format_brl(total),
                        "effective": f"{self._percent(total, receita_atual):.2f}%",
                        "status": status_geral,
                        "next_due": next((d["data"] for d in due_items if d["status_raw"] == "EM_ABERTO"), "-"),
                    },
                    "composition": [
                        {
                            "tributo": "PIS",
                            "base": format_brl(tributos_total["PIS"]["base_final"]),
                            "aliquota": self._fmt_aliquota(pis, tributos_total["PIS"]["base_final"]),
                            "valor": format_brl(pis),
                        },
                        {
                            "tributo": "COFINS",
                            "base": format_brl(tributos_total["COFINS"]["base_final"]),
                            "aliquota": self._fmt_aliquota(cofins, tributos_total["COFINS"]["base_final"]),
                            "valor": format_brl(cofins),
                        },
                        {
                            "tributo": "CSLL" + ("  ⚡" if not is_fechamento else ""),
                            "base": format_brl(tributos_total["CSLL"]["base_final"]),
                            "aliquota": self._fmt_aliquota(csll, tributos_total["CSLL"]["base_final"]),
                            "valor": format_brl(csll),
                        },
                        {
                            "tributo": "IRPJ" + ("  ⚡" if not is_fechamento else ""),
                            "base": format_brl(tributos_total["IRPJ"]["base_final"]),
                            "aliquota": self._fmt_aliquota(irpj, tributos_total["IRPJ"]["base_final"]),
                            "valor": format_brl(irpj),
                        },
                        {
                            "tributo": "IRPJ Adic." + ("  ⚡" if not is_fechamento else ""),
                            "base": format_brl(tributos_total["IRPJ_ADICIONAL"]["base_final"]),
                            "aliquota": self._fmt_aliquota(
                                tributos_total["IRPJ_ADICIONAL"]["imposto_devido"],
                                tributos_total["IRPJ_ADICIONAL"]["base_final"],
                            ),
                            "valor": format_brl(tributos_total["IRPJ_ADICIONAL"]["imposto_devido"]),
                        },
                        {
                            "tributo": "ISS",
                            "base": format_brl(tributos_total["ISS"]["base_final"]),
                            "aliquota": self._fmt_aliquota(iss, tributos_total["ISS"]["base_final"]),
                            "valor": format_brl(iss),
                        },
                    ],
                    "donut": {
                        "center": format_brl(total),
                        "segments": [
                            ("PIS", "#00d9ff", float(pis)),
                            ("COFINS", "#9d4edd", float(cofins)),
                            ("CSLL", "#00a8ff", float(csll)),
                            ("IRPJ", "#4ec7f7", float(irpj)),
                            ("IRPJ AD", "#f59f00", float(tributos_total["IRPJ_ADICIONAL"]["imposto_devido"])),
                            ("ISS", "#1ef886", float(iss)),
                        ],
                        "legend": "PIS  •  COFINS  •  CSLL  •  IRPJ  •  IRPJ AD  •  ISS",
                    },
                    "due_items": due_items,
                }
        except Exception:
            return self._empty_real_data("Falha ao carregar dados reais da dashboard")

    def _get_filter_payload(self) -> dict[str, object | None]:
        window = self.window()
        topbar = getattr(window, "topbar", None)
        if topbar and hasattr(topbar, "get_filter_payload"):
            payload = topbar.get_filter_payload()
            if isinstance(payload, dict):
                return payload
        return {
            "period": {"mode": "MES"},
            "empresa_id": None,
            "obra_id": None,
            "obra_empresa_id": None,
            "search": "",
        }

    def _resolve_period_scope(self, payload: dict[str, object | None]) -> tuple[list[int], str]:
        from datetime import date as _date

        period = payload.get("period") or {}
        mode = period.get("mode", "MES")

        with get_session() as session:
            competencias = list(
                session.execute(select(Competencia).order_by(Competencia.ano.asc(), Competencia.mes.asc()))
                .scalars()
                .all()
            )

        if not competencias:
            return [], "-"

        if mode == "MES":
            year = period.get("year")
            month = period.get("month")
            if year and month:
                comp = next((c for c in competencias if c.ano == year and c.mes == month), None)
                if comp:
                    return [comp.id], comp.referencia

        elif mode == "TRIMESTRE":
            year = period.get("year")
            quarter = period.get("quarter")
            if year and quarter:
                start = ((quarter - 1) * 3) + 1
                ids = [c.id for c in competencias if c.ano == year and start <= c.mes <= start + 2]
                return ids, f"{quarter}\u00ba TRI/{year}"

        elif mode == "ANUAL":
            year = period.get("year")
            if year:
                ids = [c.id for c in competencias if c.ano == year]
                return ids, str(year)

        elif mode == "PERSONALIZADO":
            start_date = period.get("start_date")
            end_date = period.get("end_date")
            if start_date and end_date and start_date <= end_date:
                ids = [
                    c.id for c in competencias
                    if _date(c.ano, c.mes, 1) >= _date(start_date.year, start_date.month, 1)
                    and _date(c.ano, c.mes, 1) <= _date(end_date.year, end_date.month, 1)
                ]
                label = f"{start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}"
                return ids, label
            return [], "-"

        # fallback: competência mais recente
        comp = competencias[-1]
        return [comp.id], comp.referencia

    _STATUS_LABELS: dict[str, tuple[str, str]] = {
        "EM_ABERTO": ("Em aberto", "DueStatusAberto"),
        "PAGO": ("Pago", "DueStatusPago"),
        "VENCIDO": ("Vencido", "DueStatusVencido"),
        "CANCELADO": ("Cancelado", "DueStatusCancelado"),
        "NAO_APLICAVEL": ("Não aplicável", "DueStatusNaoAplicavel"),
    }

    def _build_due_items(
        self,
        empresa_ids: list[int],
        competencia_ids: list[int],
        obra_id: int | None = None,
        obra_ids: set[int] | None = None,
    ) -> list[dict[str, str]]:
        if not empresa_ids or not competencia_ids:
            return []
        today = date.today()
        obrigacoes: list[ObrigacaoVencimento] = []
        for emp_id in empresa_ids:
            for comp_id in competencia_ids:
                obrigacoes.extend(
                    self._guia_service.list_obrigacoes(GuiaFilter(empresa_id=emp_id, competencia_id=comp_id))
                )
        obrigacoes.sort(key=lambda x: x.data_vencimento)
        obrigacoes = obrigacoes[:10]

        if obra_id:
            obrigacoes = [item for item in obrigacoes if item.obra_id == obra_id]
        elif obra_ids:
            obrigacoes = [item for item in obrigacoes if item.obra_id in obra_ids]

        result = []
        for item in obrigacoes:
            raw = item.status.value
            # Auto-upgrade: em aberto com data passada = vencido
            if raw == StatusObrigacao.EM_ABERTO.value and item.data_vencimento < today:
                raw = "VENCIDO"
            label, style = self._STATUS_LABELS.get(raw, (raw, "DueStatusAberto"))
            result.append(
                {
                    "tributo": item.tributo.value.replace("_", " "),
                    "data": item.data_vencimento.strftime("%d/%m/%Y"),
                    "valor": format_brl(item.valor),
                    "status": label,
                    "status_raw": raw,
                    "status_style": style,
                }
            )
        return result

    @staticmethod
    def _resolve_status_geral(due_items: list[dict]) -> str:
        if not due_items:
            return "SEM OBRIGAÇÕES"
        raws = {d["status_raw"] for d in due_items}
        if "VENCIDO" in raws:
            return "VENCIDO"
        if "EM_ABERTO" in raws:
            return "EM ABERTO"
        if all(d["status_raw"] == "PAGO" for d in due_items):
            return "PAGO"
        if all(d["status_raw"] in ("NAO_APLICAVEL", "CANCELADO") for d in due_items):
            return "NÃO APLICÁVEL"
        return "EM ABERTO"

    @staticmethod
    def _fmt_aliquota(imposto: Decimal, base: Decimal) -> str:
        if base <= 0:
            return "-"
        aliq = (imposto / base * Decimal("100")).quantize(Decimal("0.01"))
        return f"{str(aliq).replace('.', ',')}%"

    def _build_trend(self, scopes: list[tuple[int, int | None]]) -> dict:
        with get_session() as session:
            competencias = list(
                session.execute(select(Competencia).order_by(Competencia.ano.desc(), Competencia.mes.desc()).limit(12))
                .scalars()
                .all()
            )
        competencias.reverse()

        labels: list[str] = []
        faturamento: list[float] = []
        impostos: list[float] = []
        for comp in competencias:
            labels.append(comp.referencia[:3].lower())
            receita = Decimal("0.00")
            imposto = Decimal("0.00")
            for empresa_id, obra_id in scopes:
                receita += self._sum_receita(empresa_id, comp.id, obra_id)
                imposto += self._sum_impostos(empresa_id, comp.id, obra_id)
            faturamento.append(float(receita))
            impostos.append(float(imposto))

        return {
            "labels": labels,
            "series": [
                ("Faturamento Bruto", "#00d9ff", faturamento),
                ("Total de Impostos", "#9d4edd", impostos),
            ],
            "legend": "Faturamento Bruto #00d9ff  •  Total de Impostos #9d4edd",
        }

    def _empty_real_data(self, reason: str) -> dict:
        zero = Decimal("0.00")
        trend = self._build_trend(scopes=[])
        return {
            "_is_real": True,
            "_tipo_apuracao": f"SEM DADOS  —  {reason}",
            "_is_fechamento": False,
            "kpis": [
                {"title": "Faturamento Bruto", "value": format_brl(zero), "variation": "+0,0%", "icon": "◎"},
                {"title": "Base de Calculo", "value": format_brl(zero), "variation": "+0,0%", "icon": "◉"},
                {"title": "Total de Impostos", "value": format_brl(zero), "variation": "+0,0%", "icon": "◈"},
                {"title": "Aliquota Efetiva", "value": "0,00%", "variation": "+0,0%", "icon": "◆"},
            ],
            "trend": trend,
            "summary": {
                "period": "-",
                "company": "-",
                "taxes": {
                    "PIS": format_brl(zero),
                    "COFINS": format_brl(zero),
                    "CSLL": format_brl(zero),
                    "IRPJ": format_brl(zero),
                    "IRPJ_ADICIONAL": format_brl(zero),
                    "ISS": format_brl(zero),
                },
                "total": format_brl(zero),
                "effective": "0,00%",
                "status": "SEM OBRIGAÇÕES",
                "next_due": "-",
            },
            "composition": [
                {"tributo": "PIS", "base": format_brl(zero), "aliquota": "-", "valor": format_brl(zero)},
                {"tributo": "COFINS", "base": format_brl(zero), "aliquota": "-", "valor": format_brl(zero)},
                {"tributo": "CSLL", "base": format_brl(zero), "aliquota": "-", "valor": format_brl(zero)},
                {"tributo": "IRPJ", "base": format_brl(zero), "aliquota": "-", "valor": format_brl(zero)},
                {"tributo": "IRPJ Adic.", "base": format_brl(zero), "aliquota": "-", "valor": format_brl(zero)},
                {"tributo": "ISS", "base": format_brl(zero), "aliquota": "-", "valor": format_brl(zero)},
            ],
            "donut": {
                "center": format_brl(zero),
                "segments": [
                    ("PIS", "#00d9ff", 0.0),
                    ("COFINS", "#9d4edd", 0.0),
                    ("CSLL", "#00a8ff", 0.0),
                    ("IRPJ", "#4ec7f7", 0.0),
                    ("IRPJ AD", "#f59f00", 0.0),
                    ("ISS", "#1ef886", 0.0),
                ],
                "legend": "",
            },
            "due_items": [],
        }

    def _sum_receita(self, empresa_id: int, competencia_id: int | None, obra_id: int | None = None) -> Decimal:
        if not competencia_id:
            return Decimal("0.00")
        stmt = select(LancamentoFiscal.receita_bruta).where(
            LancamentoFiscal.empresa_id == empresa_id,
            LancamentoFiscal.competencia_id == competencia_id,
        )
        if obra_id:
            stmt = stmt.where(LancamentoFiscal.obra_id == obra_id)
        with get_session() as session:
            rows = list(
                session.execute(stmt)
                .scalars()
                .all()
            )
        return sum((Decimal(str(v)) for v in rows), start=Decimal("0.00"))

    def _sum_impostos(self, empresa_id: int, competencia_id: int | None, obra_id: int | None = None) -> Decimal:
        if not competencia_id:
            return Decimal("0.00")
        try:
            result = self._fiscal_service.calculate_for_scope(
                empresa_id=empresa_id,
                competencia_id=competencia_id,
                obra_id=obra_id,
                consolidada=not isinstance(obra_id, int),
                persist=False,
            )
            return result.total_impostos
        except Exception:
            return Decimal("0.00")

    @staticmethod
    def _percent(numerator: Decimal, denominator: Decimal) -> Decimal:
        if denominator <= 0:
            return Decimal("0.00")
        return (numerator / denominator) * Decimal("100")

    @staticmethod
    def _variation(current: Decimal, previous: Decimal) -> str:
        if previous <= 0:
            return "+0,0%"
        var = ((current - previous) / previous) * Decimal("100")
        sign = "+" if var >= 0 else ""
        return f"{sign}{var.quantize(Decimal('0.1'))}%"

    @staticmethod
    def _donut_legend_html(segments: list[tuple[str, str, float]]) -> str:
        positive = [(label, color, value) for label, color, value in segments if value > 0]
        total = sum(value for _, _, value in positive)
        if total <= 0:
            return ""

        parts: list[str] = []
        for label, color, value in positive:
            pct = (value / total) * 100
            pct_text = f"{pct:.1f}".replace(".", ",")
            val_text = format_brl(Decimal(str(value)))
            parts.append(
                f"<span style='color:{color};font-weight:700'>■</span> "
                f"<span style='color:#dceaff'>{label}</span> "
                f"<span style='color:#8fb1d6'>({pct_text}% • {val_text})</span>"
            )
        return "&nbsp;&nbsp;".join(parts)

    def _render_data(self) -> None:
        is_real = self._mock.get("_is_real", False)
        tipo_apuracao = self._mock.get("_tipo_apuracao", "DEMONSTRAÇÃO  —  banco vazio, exibindo dados de exemplo")

        kpis = self._mock["kpis"]
        for idx, card in enumerate(self.kpi_cards):
            data = kpis[idx]
            card.layout().itemAt(0).widget().setText(f"{data['icon']}  {data['variation']}")
            card.layout().itemAt(1).widget().setText(data["title"])
            card.layout().itemAt(2).widget().setText(data["value"])

        self.line_chart.set_data(self._mock["trend"]["labels"], self._mock["trend"]["series"])
        self.line_legend.setText(self._mock["trend"]["legend"])

        resumo = self._mock["summary"]
        self.summary_period.setText(f"Período: {resumo['period']}")
        self.summary_company.setText(f"Empresa: {resumo['company']}")

        is_fechamento = self._mock.get("_is_fechamento", False)
        for tributo, valor in resumo["taxes"].items():
            if tributo in self.summary_rows:
                sufixo = "  ⚡" if (not is_fechamento and tributo in ("IRPJ", "CSLL", "IRPJ_ADICIONAL")) else ""
                self.summary_rows[tributo].setText(f"{tributo.replace('_', ' ')}{sufixo}: {valor}")

        self.summary_tipo_apuracao.setText(tipo_apuracao)
        self.summary_total.setText(f"TOTAL: {resumo['total']}")
        self.summary_effective.setText(f"Alíquota efetiva: {resumo['effective']}")

        status = resumo["status"]
        style_map = {
            "VENCIDO": "DashStatusDanger",
            "EM ABERTO": "DashStatusWarning",
            "PAGO": "DashStatusOk",
        }
        self.summary_status.setObjectName(style_map.get(status, "DashStatusWarning"))
        self.summary_status.setStyleSheet("")  # força re-apply do QSS
        self.summary_status.setText(f"Status: {status}")
        self.summary_due.setText(f"Próx. vencimento: {resumo['next_due']}")

        rows = self._mock["composition"]
        self.tributos_table.setRowCount(len(rows))
        for row, item in enumerate(rows):
            self.tributos_table.setItem(row, 0, QTableWidgetItem(item["tributo"]))
            self.tributos_table.setItem(row, 1, QTableWidgetItem(item["base"]))
            self.tributos_table.setItem(row, 2, QTableWidgetItem(item["aliquota"]))
            self.tributos_table.setItem(row, 3, QTableWidgetItem(item["valor"]))
        self.tributos_table.resizeColumnsToContents()

        donut_segments = self._mock["donut"]["segments"]
        self.donut_chart.set_data(self._mock["donut"]["center"], donut_segments)
        self.donut_legend.setText(self._donut_legend_html(donut_segments))

        while self.due_list.count():
            child = self.due_list.takeAt(0)
            widget = child.widget()
            if widget:
                widget.deleteLater()

        for item in self._mock["due_items"]:
            card = QFrame()
            card.setObjectName("DueMiniCard")
            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(8, 6, 8, 6)
            c_layout.setSpacing(2)
            l1 = QLabel(f"{item['tributo']} — {item['data']}")
            l1.setObjectName("DueTitle")
            status_style = item.get("status_style", "DueStatusAberto")
            l2 = QLabel(f"{item['valor']}  |  {item['status']}")
            l2.setObjectName(status_style)
            c_layout.addWidget(l1)
            c_layout.addWidget(l2)
            self.due_list.addWidget(card)

        fonte = "dados reais" if is_real else "dados de demonstração"
        self.footer_label.setText(f"Atualizado em {format_date_br(date.today())}  —  {fonte}")

    @staticmethod
    def _default_mock_data() -> dict:
        """Dados de demonstração exibidos quando o banco está vazio (seed visual)."""
        return {
            "_is_real": False,
            "_tipo_apuracao": "DEMONSTRAÇÃO  —  banco vazio, exibindo dados de exemplo",
            "_is_fechamento": False,
            "kpis": [
                {"title": "Faturamento Bruto", "value": format_brl("785450"), "variation": "+12,4%", "icon": "◎"},
                {"title": "Base de Calculo", "value": format_brl("353452.5"), "variation": "+12,1%", "icon": "◉"},
                {"title": "Total de Impostos", "value": format_brl("68730.21"), "variation": "+9,7%", "icon": "◈"},
                {"title": "Aliquota Efetiva", "value": "8,75%", "variation": "-0,2 p.p.", "icon": "◆"},
            ],
            "trend": {
                "labels": ["mai/25", "jun/25", "jul/25", "ago/25", "set/25", "out/25", "nov/25", "dez/25", "jan/26", "fev/26", "mar/26", "abr/26"],
                "series": [
                    ("Faturamento Bruto", "#1f7bff", [560, 540, 610, 640, 645, 730, 690, 740, 720, 700, 760, 790]),
                    ("Total de Impostos", "#8a49ff", [290, 270, 285, 310, 340, 390, 335, 340, 365, 350, 450, 590]),
                ],
                "legend": "Faturamento Bruto #1f7bff  •  Total de Impostos #8a49ff",
            },
            "summary": {
                "period": "Abr/2026",
                "company": "Empresa Alpha Ltda",
                "taxes": {
                    "PIS": format_brl("5105.43"),
                    "COFINS": format_brl("23563.5"),
                    "CSLL": format_brl("22621.96"),
                    "IRPJ": format_brl("37701.6"),
                    "IRPJ_ADICIONAL": format_brl("12900"),
                    "ISS": format_brl("15444"),
                },
                "total": format_brl("68730.21"),
                "effective": "8,75%",
                "status": "EM ABERTO",
                "next_due": "25/05/2026",
            },
            "composition": [
                {"tributo": "IRPJ", "base": format_brl("251344"), "aliquota": "15,00%", "valor": format_brl("37701.6")},
                {"tributo": "IRPJ Adicional", "base": format_brl("129000"), "aliquota": "10,00%", "valor": format_brl("12900")},
                {"tributo": "CSLL", "base": format_brl("251344"), "aliquota": "9,00%", "valor": format_brl("22621.96")},
                {"tributo": "PIS", "base": format_brl("785450"), "aliquota": "0,65%", "valor": format_brl("5105.43")},
                {"tributo": "COFINS", "base": format_brl("785450"), "aliquota": "3,00%", "valor": format_brl("23563.5")},
                {"tributo": "ISS", "base": format_brl("785450"), "aliquota": "2,00%", "valor": format_brl("15444")},
            ],
            "donut": {
                "center": format_brl("68730.21"),
                "segments": [
                    ("IRPJ", "#1f7bff", 37701.6),
                    ("CSLL", "#12b2aa", 22621.96),
                    ("COFINS", "#7f4dff", 23563.5),
                    ("ISS", "#f59f00", 15444),
                    ("PIS", "#ffbd2e", 5105.43),
                    ("Adic. IRPJ", "#ff73b9", 12900),
                ],
                "legend": "IRPJ  •  CSLL  •  COFINS  •  ISS  •  PIS  •  Adic. IRPJ",
            },
            "due_items": [
                {"tributo": "PIS", "data": "25/05/2026", "valor": "Darf", "status": "Em aberto", "status_raw": "EM_ABERTO", "status_style": "DueStatusAberto"},
                {"tributo": "COFINS", "data": "25/05/2026", "valor": "Darf", "status": "Em aberto", "status_raw": "EM_ABERTO", "status_style": "DueStatusAberto"},
                {"tributo": "ISS", "data": "15/05/2026", "valor": "Guia Municipal", "status": "Em aberto", "status_raw": "EM_ABERTO", "status_style": "DueStatusAberto"},
                {"tributo": "IRPJ e CSLL", "data": "30/05/2026", "valor": "Darf", "status": "Em aberto", "status_raw": "EM_ABERTO", "status_style": "DueStatusAberto"},
            ],
        }
