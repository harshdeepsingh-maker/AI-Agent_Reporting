from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt

def _save_fig(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

def generate_charts(report: Dict, folder: Path) -> Tuple[List[Dict], str]:
    """
    Returns:
      attachments: list of {"path": str, "cid": str}
      html_block : HTML <section> with <img> tags (cid w/ local fallback)
    """
    attachments: List[Dict] = []
    imgs_html: List[str] = []

    # --- marketing by campaign ---
    mkt = (report.get("marketing") or {}).get("data") or {}
    campaigns = mkt.get("campaigns") or []
    names = [c.get("name","") for c in campaigns]
    roas  = [float(c.get("roas") or 0) for c in campaigns]
    conv  = [int(c.get("conversions") or 0) for c in campaigns]
    spend = [float(c.get("spend") or 0) for c in campaigns]
    rev   = [float(c.get("revenue") or 0) for c in campaigns]

    # ROAS by campaign
    if names:
        plt.figure()
        plt.bar(names, roas)
        plt.xticks(rotation=20, ha="right")
        plt.title("ROAS by Campaign")
        plt.ylabel("ROAS")
        p = folder / "chart_roas.png"
        _save_fig(p)
        attachments.append({"path": str(p), "cid": "roas"})
        imgs_html.append(f"<img alt='ROAS' src='cid:roas' onerror=\"this.onerror=null;this.src='chart_roas.png';\" style='max-width:100%;height:auto;'/>")

    # Conversions by campaign
    if names:
        plt.figure()
        plt.bar(names, conv)
        plt.xticks(rotation=20, ha="right")
        plt.title("Conversions by Campaign")
        plt.ylabel("Conversions")
        p = folder / "chart_conversions.png"
        _save_fig(p)
        attachments.append({"path": str(p), "cid": "conversions"})
        imgs_html.append(f"<img alt='Conversions' src='cid:conversions' onerror=\"this.onerror=null;this.src='chart_conversions.png';\" style='max-width:100%;height:auto;'/>")

    # Spend vs Revenue by campaign (grouped)
    if names:
        import numpy as np
        x = np.arange(len(names))
        width = 0.38
        plt.figure()
        plt.bar(x - width/2, spend, width)
        plt.bar(x + width/2, rev,   width)
        plt.xticks(x, names, rotation=20, ha="right")
        plt.title("Spend vs Revenue by Campaign")
        plt.ylabel("Amount")
        plt.legend(["Spend","Revenue"])
        p = folder / "chart_spend_revenue.png"
        _save_fig(p)
        attachments.append({"path": str(p), "cid": "spendrev"})
        imgs_html.append(f"<img alt='Spend vs Revenue' src='cid:spendrev' onerror=\"this.onerror=null;this.src='chart_spend_revenue.png';\" style='max-width:100%;height:auto;'/>")

    # --- sales kpis ---
    sales = (report.get("sales") or {}).get("data") or {}
    orders = int(sales.get("orders") or 0)
    newcust = int(sales.get("new_customers") or 0)

    plt.figure()
    plt.bar(["Orders","New Customers"], [orders, newcust])
    plt.title("Sales KPIs")
    p = folder / "chart_sales_kpis.png"
    _save_fig(p)
    attachments.append({"path": str(p), "cid": "saleskpis"})
    imgs_html.append(f"<img alt='Sales KPIs' src='cid:saleskpis' onerror=\"this.onerror=null;this.src='chart_sales_kpis.png';\" style='max-width:100%;height:auto;'/>")

    html_block = "<h3 style='margin:16px 0 8px;'>Charts</h3>" + "".join(imgs_html)
    return attachments, html_block
