"""Shared KPI metric card component."""

import streamlit as st

KPI_STYLE = """
<style>
.kpi-grid { display: flex; gap: 16px; margin: 16px 0; }
.kpi-card { flex: 1; padding: 20px 24px; border-radius: 12px; border: 1px solid #e0e0e0; background: #fff; }
.kpi-label { font-size: 14px; color: #666; margin-bottom: 6px; }
.kpi-value { font-size: 36px; font-weight: 700; line-height: 1.1; }
.kpi-sub { font-size: 13px; color: #888; margin-top: 4px; }
.kpi-blue  .kpi-value { color: #1565C0; }
.kpi-green .kpi-value { color: #2E7D32; }
.kpi-red   .kpi-value { color: #C62828; }
.kpi-orange .kpi-value { color: #E65100; }
.kpi-teal  .kpi-value { color: #00695C; }
</style>
"""


def render_kpi_cards(cards: list[dict]):
    """
    Render a row of KPI metric cards.

    cards: list of dicts with keys:
        - label (str)
        - value (str|int|float)
        - color (str): one of "blue", "green", "red", "orange", "teal"
        - sub (str, optional): smaller text below the value
    """
    parts = [KPI_STYLE, '<div class="kpi-grid">']
    for c in cards:
        sub_html = f'<div class="kpi-sub">{c["sub"]}</div>' if c.get("sub") else ""
        parts.append(
            f'<div class="kpi-card kpi-{c["color"]}">'
            f'<div class="kpi-label">{c["label"]}</div>'
            f'<div class="kpi-value">{c["value"]}</div>'
            f'{sub_html}'
            f'</div>'
        )
    parts.append("</div>")
    st.html("".join(parts))
