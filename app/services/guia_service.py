"""Servico de guias, vencimentos e status de obrigacoes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy import select

from app.db.session_manager import get_session
from app.models.apuracao import Apuracao
from app.models.apuracao_item import ApuracaoItem
from app.models.competencia import Competencia
from app.models.empresa import Empresa
from app.models.enums import StatusObrigacao, TributoAlvo
from app.models.obra import Obra
from app.models.obrigacao_vencimento import ObrigacaoVencimento
from app.models.parametro_sistema import ParametroSistema
from app.services.due_date_service import DueDateService
from app.utils.formatters import format_brl, format_date_br


@dataclass(frozen=True)
class GuiaFilter:
    empresa_id: int | None = None
    obra_id: int | None = None
    competencia_id: int | None = None
    tributo: str | None = None
    status: str | None = None


@dataclass(frozen=True)
class GuiaGenerationInput:
    empresa_id: int
    competencia_id: int
    tributo: str
    visao: str  # CONSOLIDADA | POR_OBRA
    obra_id: int | None = None
    observacoes: str | None = None


@dataclass(frozen=True)
class GuiaPortalConfig:
    federal_url: str
    iss_url: str


class GuiaService:
    def __init__(self) -> None:
        self._due_service = DueDateService()

    def list_obrigacoes(self, filtro: GuiaFilter) -> list[ObrigacaoVencimento]:
        with get_session() as session:
            stmt = select(ObrigacaoVencimento).order_by(ObrigacaoVencimento.data_vencimento.asc())
            if filtro.empresa_id:
                stmt = stmt.where(ObrigacaoVencimento.empresa_id == filtro.empresa_id)
            if filtro.obra_id:
                stmt = stmt.where(ObrigacaoVencimento.obra_id == filtro.obra_id)
            if filtro.competencia_id:
                stmt = stmt.where(ObrigacaoVencimento.competencia_id == filtro.competencia_id)
            if filtro.tributo:
                stmt = stmt.where(ObrigacaoVencimento.tributo == TributoAlvo(filtro.tributo))
            if filtro.status:
                stmt = stmt.where(ObrigacaoVencimento.status == StatusObrigacao(filtro.status))
            rows = list(session.execute(stmt).scalars().all())
        return rows

    def update_status(self, obrigacao_id: int, status: str) -> None:
        new_status = StatusObrigacao(status)
        with get_session() as session:
            row = session.get(ObrigacaoVencimento, obrigacao_id)
            if not row:
                return
            row.status = new_status
            if new_status == StatusObrigacao.PAGO:
                row.pago_em = date.today()
            elif new_status in (StatusObrigacao.EM_ABERTO, StatusObrigacao.CANCELADO, StatusObrigacao.NAO_APLICAVEL):
                row.pago_em = None
            session.commit()

    def get_rules_snapshot(self) -> dict[str, dict[str, str]]:
        rules = self._due_service.resolve_rules()
        return {
            tributo.value: {
                "codigo_receita": rule.codigo_receita,
                "dia_vencimento": str(rule.dia_vencimento),
            }
            for tributo, rule in rules.items()
        }

    def save_rules_snapshot(self, values: dict[str, dict[str, str]]) -> None:
        key_map = {
            "PIS": ("COD_RECEITA_PIS", "VENCIMENTO_DIA_PIS_COFINS"),
            "COFINS": ("COD_RECEITA_COFINS", "VENCIMENTO_DIA_PIS_COFINS"),
            "IRPJ": ("COD_RECEITA_IRPJ", "VENCIMENTO_DIA_IRPJ_CSLL"),
            "CSLL": ("COD_RECEITA_CSLL", "VENCIMENTO_DIA_IRPJ_CSLL"),
            "IRPJ_ADICIONAL": ("COD_RECEITA_IRPJ_ADICIONAL", "VENCIMENTO_DIA_IRPJ_CSLL"),
            "ISS": ("COD_RECEITA_ISS", "VENCIMENTO_DIA_ISS_PADRAO"),
        }

        with get_session() as session:
            for tributo, payload in values.items():
                cod_key, day_key = key_map[tributo]
                self._upsert_param(session, cod_key, valor_texto=payload.get("codigo_receita"))
                self._upsert_param(session, day_key, valor_inteiro=int(payload.get("dia_vencimento", "25")))
            session.commit()

    def get_portal_config(self) -> GuiaPortalConfig:
        defaults = {
            "PORTAL_FEDERAL_ARRECADACAO_URL": "https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/pagamentos-e-parcelamentos",
            "PORTAL_ISS_EMISSAO_URL": "https://www.gov.br/empresas-e-negocios/pt-br/empreendedor/tributos",
        }

        with get_session() as session:
            federal = self._get_param_text(session, "PORTAL_FEDERAL_ARRECADACAO_URL", defaults["PORTAL_FEDERAL_ARRECADACAO_URL"])
            iss = self._get_param_text(session, "PORTAL_ISS_EMISSAO_URL", defaults["PORTAL_ISS_EMISSAO_URL"])

        return GuiaPortalConfig(federal_url=federal, iss_url=iss)

    def save_portal_config(self, config: GuiaPortalConfig) -> None:
        with get_session() as session:
            self._upsert_param(
                session,
                "PORTAL_FEDERAL_ARRECADACAO_URL",
                valor_texto=(config.federal_url or "").strip(),
            )
            self._upsert_param(
                session,
                "PORTAL_ISS_EMISSAO_URL",
                valor_texto=(config.iss_url or "").strip(),
            )
            session.commit()

    def build_official_submission_package(self, params: GuiaGenerationInput) -> dict[str, str]:
        payload = self.build_demonstrativo_payload(params)
        tributo = TributoAlvo(params.tributo)
        config = self.get_portal_config()

        if tributo == TributoAlvo.ISS:
            portal_name = "Portal ISS (municipal)"
            base_url = config.iss_url
        else:
            portal_name = "Portal Receita Federal"
            base_url = config.federal_url

        copy_payload = self._build_copy_payload(payload)
        portal_url = self._build_portal_url(base_url, payload)

        return {
            "portal_name": portal_name,
            "portal_url": portal_url,
            "copy_payload": copy_payload,
            "tributo": payload["tributo"],
            "competencia": payload["competencia"],
            "valor": payload["valor"],
            "codigo_receita": payload["codigo_receita"],
            "vencimento": payload["vencimento"],
        }

    def build_demonstrativo_payload(self, params: GuiaGenerationInput) -> dict[str, str]:
        tributo = TributoAlvo(params.tributo)
        rules = self._due_service.resolve_rules()

        with get_session() as session:
            empresa = session.get(Empresa, params.empresa_id)
            comp = session.get(Competencia, params.competencia_id)
            obra = session.get(Obra, params.obra_id) if params.obra_id else None

            ob_stmt = select(ObrigacaoVencimento).where(
                ObrigacaoVencimento.empresa_id == params.empresa_id,
                ObrigacaoVencimento.competencia_id == params.competencia_id,
                ObrigacaoVencimento.tributo == tributo,
            )
            if params.visao == "POR_OBRA":
                ob_stmt = ob_stmt.where(ObrigacaoVencimento.obra_id == params.obra_id)
            else:
                ob_stmt = ob_stmt.where(ObrigacaoVencimento.obra_id.is_(None))
            obg = session.execute(ob_stmt.order_by(ObrigacaoVencimento.id.desc()).limit(1)).scalar_one_or_none()

            ap_stmt = select(Apuracao).where(
                Apuracao.empresa_id == params.empresa_id,
                Apuracao.competencia_id == params.competencia_id,
                Apuracao.apuracao_valida.is_(True),
            )
            if params.visao == "POR_OBRA":
                ap_stmt = ap_stmt.where(Apuracao.obra_id == params.obra_id, Apuracao.consolidada.is_(False))
            else:
                ap_stmt = ap_stmt.where(Apuracao.obra_id.is_(None), Apuracao.consolidada.is_(True))
            ap = session.execute(ap_stmt.order_by(Apuracao.id.desc()).limit(1)).scalar_one_or_none()

            base = Decimal("0.00")
            aliquota = Decimal("0.00")
            valor = Decimal("0.00")
            memoria = ""
            if ap:
                item = session.execute(
                    select(ApuracaoItem)
                    .where(ApuracaoItem.apuracao_id == ap.id, ApuracaoItem.tributo == tributo)
                    .limit(1)
                ).scalar_one_or_none()
                if item:
                    base = Decimal(str(item.base_calculo))
                    aliquota = Decimal(str(item.aliquota))
                    valor = Decimal(str(item.valor_calculado))
                    memoria = item.descricao_passo

        rule = rules[tributo]
        vencimento_txt = format_date_br(obg.data_vencimento) if obg else "-"
        status_txt = obg.status.value if obg else StatusObrigacao.NAO_APLICAVEL.value
        codigo_txt = obg.codigo_receita if obg else rule.codigo_receita

        return {
            "empresa": empresa.razao_social if empresa else "-",
            "obra": obra.nome if obra else "Consolidado",
            "competencia": comp.referencia if comp else "-",
            "tributo": tributo.value,
            "visao": params.visao,
            "codigo_receita": codigo_txt,
            "vencimento": vencimento_txt,
            "status": status_txt,
            "base": format_brl(base),
            "aliquota": f"{str((aliquota * Decimal('100')).quantize(Decimal('0.01'))).replace('.', ',')}%",
            "valor": format_brl(valor),
            "memoria": memoria,
            "observacoes": params.observacoes or "",
            "gerado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        }

    def export_demonstrativo_pdf(self, payload: dict[str, str], output_path: str) -> str:
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
        except ImportError as exc:
            raise RuntimeError("Pacote reportlab nao encontrado. Instale com: pip install reportlab") from exc

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=24, rightMargin=24, topMargin=24, bottomMargin=24)
        styles = getSampleStyleSheet()
        elems = []

        elems.append(Paragraph("Demonstrativo Interno de Recolhimento", styles["Title"]))
        elems.append(Spacer(1, 8))

        data = [
            ["Empresa", payload["empresa"]],
            ["Obra", payload["obra"]],
            ["Competencia", payload["competencia"]],
            ["Tributo", payload["tributo"]],
            ["Visao", payload["visao"]],
            ["Codigo de Receita", payload["codigo_receita"]],
            ["Vencimento", payload["vencimento"]],
            ["Status", payload["status"]],
            ["Base", payload["base"]],
            ["Aliquota", payload["aliquota"]],
            ["Valor", payload["valor"]],
            ["Memoria", payload["memoria"]],
            ["Observacoes", payload["observacoes"]],
            ["Gerado em", payload["gerado_em"]],
        ]
        table = Table(data, colWidths=[160, 360])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e9f1fb")),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#4f6e92")),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ]
            )
        )
        elems.append(table)

        doc.build(elems)
        return str(path)

    @staticmethod
    def _upsert_param(session, chave: str, valor_texto: str | None = None, valor_inteiro: int | None = None) -> None:
        row = session.execute(select(ParametroSistema).where(ParametroSistema.chave == chave)).scalar_one_or_none()
        if row is None:
            row = ParametroSistema(chave=chave, descricao=chave, ativo=True)
            session.add(row)
        if valor_texto is not None:
            row.valor_texto = valor_texto
        if valor_inteiro is not None:
            row.valor_inteiro = int(valor_inteiro)

    @staticmethod
    def _get_param_text(session, chave: str, fallback: str) -> str:
        row = session.execute(select(ParametroSistema).where(ParametroSistema.chave == chave)).scalar_one_or_none()
        if not row:
            return fallback
        value = (row.valor_texto or "").strip()
        return value or fallback

    @staticmethod
    def _build_copy_payload(payload: dict[str, str]) -> str:
        lines = [
            "EMISSAO OFICIAL - DADOS DA GUIA",
            f"Empresa: {payload['empresa']}",
            f"Obra/Visao: {payload['obra']} / {payload['visao']}",
            f"Competencia: {payload['competencia']}",
            f"Tributo: {payload['tributo']}",
            f"Codigo de receita: {payload['codigo_receita']}",
            f"Vencimento: {payload['vencimento']}",
            f"Base: {payload['base']}",
            f"Aliquota: {payload['aliquota']}",
            f"Valor a recolher: {payload['valor']}",
            f"Observacoes: {payload['observacoes']}",
            f"Gerado em: {payload['gerado_em']}",
        ]
        return "\n".join(lines)

    @staticmethod
    def _build_portal_url(base_url: str, payload: dict[str, str]) -> str:
        text = (
            f"Tributo={payload['tributo']}; Competencia={payload['competencia']}; "
            f"Codigo={payload['codigo_receita']}; Vencimento={payload['vencimento']}; Valor={payload['valor']}"
        )
        sep = "&" if "?" in base_url else "?"
        return f"{base_url}{sep}origem=contabase&dados={quote_plus(text)}"
