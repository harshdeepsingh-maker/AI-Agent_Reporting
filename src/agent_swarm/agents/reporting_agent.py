from __future__ import annotations
import os, datetime as dt, html
from pathlib import Path
from typing import Any, Dict
from ..eventbus import (
    EventBus,
    TOPIC_SALES_REQ, TOPIC_SALES_RES,
    TOPIC_MARKETING_REQ, TOPIC_MARKETING_RES,
)
from ..logging_utils import info, warn
from ..email_utils import send_email
from agent_swarm.charts import generate_charts

TZ = os.getenv("REPORT_TIMEZONE", "Asia/Kolkata")

def _safe(val, default="—"):
    return default if val is None else val

def _render_html(today: str, sales: dict, campaigns: list[dict]) -> str:
    ts = dt.datetime.now(dt.timezone.utc).isoformat()
    total_sales = _safe(sales.get("total_sales"))
    currency    = _safe(sales.get("currency"))
    orders      = _safe(sales.get("orders"))
    new_cust    = _safe(sales.get("new_customers"))
    aov         = _safe(sales.get("avg_order_value"))

    rows = []
    for c in campaigns:
        rows.append(f"""
            <tr>
              <td style="padding:8px;border-bottom:1px solid #eee;">{html.escape(str(c.get('name','')))}</td>
              <td style="padding:8px;border-bottom:1px solid #eee;text-align:right;">{_safe(c.get('click_rate'))}%</td>
              <td style="padding:8px;border-bottom:1px solid #eee;text-align:right;">{_safe(c.get('conversions'))}</td>
              <td style="padding:8px;border-bottom:1px solid #eee;text-align:right;">{_safe(c.get('spend'))}</td>
              <td style="padding:8px;border-bottom:1px solid #eee;text-align:right;">{_safe(c.get('revenue'))}</td>
              <td style="padding:8px;border-bottom:1px solid #eee;text-align:right;">{_safe(c.get('roas'))}</td>
            </tr>
        """)

    campaign_rows = "\n".join(rows) if rows else """
        <tr><td colspan="6" style="padding:12px;text-align:center;color:#777;">No campaigns</td></tr>
    """

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Daily Company Report — {today}</title>
</head>
<body style="font-family:Segoe UI,Arial,Helvetica,sans-serif;background:#f6f8fa;margin:0;padding:24px;">
  <div style="max-width:860px;margin:0 auto;background:#ffffff;border:1px solid #eaecef;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,0.04);overflow:hidden;">
    <div style="padding:20px 24px;border-bottom:1px solid #f0f1f2;background:#fafbfc;">
      <h1 style="margin:0;font-size:20px;">Daily Company Report — {today} <span style="font-weight:400;color:#6a737d">({TZ})</span></h1>
      <div style="margin-top:4px;color:#6a737d;font-size:12px;">Generated: {ts}</div>
    </div>

    <div style="padding:20px 24px;">
      <h2 style="margin:0 0 12px 0;font-size:16px;color:#24292e;">Sales</h2>
      <table style="width:100%;border-collapse:collapse;background:#fff;border:1px solid #eee;border-radius:10px;overflow:hidden;">
        <tr style="background:#f6f8fa;">
          <th style="text-align:left;padding:10px;">Total Sales</th>
          <th style="text-align:left;padding:10px;">Currency</th>
          <th style="text-align:left;padding:10px;">Orders</th>
          <th style="text-align:left;padding:10px;">New Customers</th>
          <th style="text-align:left;padding:10px;">Avg Order Value</th>
        </tr>
        <tr>
          <td style="padding:10px;">{total_sales}</td>
          <td style="padding:10px;">{currency}</td>
          <td style="padding:10px;">{orders}</td>
          <td style="padding:10px;">{new_cust}</td>
          <td style="padding:10px;">{aov}</td>
        </tr>
      </table>
    </div>

    <div style="padding:0 24px 24px 24px;">
      <h2 style="margin:12px 0;font-size:16px;color:#24292e;">Marketing</h2>
      <table style="width:100%;border-collapse:collapse;background:#fff;border:1px solid #eee;border-radius:10px;overflow:hidden;">
        <tr style="background:#f6f8fa;">
          <th style="text-align:left;padding:10px;">Campaign</th>
          <th style="text-align:right;padding:10px;">CTR</th>
          <th style="text-align:right;padding:10px;">Conversions</th>
          <th style="text-align:right;padding:10px;">Spend</th>
          <th style="text-align:right;padding:10px;">Revenue</th>
          <th style="text-align:right;padding:10px;">ROAS</th>
        </tr>
        {campaign_rows}
      </table>
    </div>

    <div style="padding:14px 24px;background:#fafbfc;border-top:1px solid #f0f1f2;color:#6a737d;font-size:12px;">
      <a href="." style="color:#0366d6;text-decoration:none;">Open in folder</a>
    </div>
  </div>
</body>
</html>"""

class ReportingAgent:
    def __init__(self, bus: EventBus):
        self.bus = bus

    async def run_once(self) -> Dict[str, Any]:
        # Trigger data collection
        self.bus.publish(TOPIC_SALES_REQ, {"reason": "report"})
        self.bus.publish(TOPIC_MARKETING_REQ, {"reason": "report"})

        # Wait for results
        sales_res = await self.bus.request(TOPIC_SALES_RES, timeout=10.0)
        mkt_res   = await self.bus.request(TOPIC_MARKETING_RES, timeout=10.0)

        sales = (sales_res or {}).get("data", {}) if (sales_res or {}).get("status") == "success" else {}
        campaigns = (mkt_res or {}).get("data", {}).get("campaigns", []) if (mkt_res or {}).get("status") == "success" else []

        today = dt.date.today().isoformat()
        html_doc = _render_html(today, sales, campaigns)

        # Save HTML file
        folder = Path("reports") / today
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "email.html").write_text(html_doc, encoding="utf-8")

        # Generate charts
        from agent_swarm.charts import generate_charts
        chart_attachments, charts_html = generate_charts(
            {"sales": sales_res, "marketing": mkt_res}, folder
        )
        if "</body>" in html_doc:
            html_doc = html_doc.replace("</body>", charts_html + "</body>")
        else:
            html_doc += charts_html
        (folder / "email.html").write_text(html_doc, encoding="utf-8")

        # Send email
        try:
            send_email(
                subject=f"Daily Company Report — {today}",
                html=html_doc,
                attachments=chart_attachments,
            )
            info("email_sent_or_written")
        except Exception as e:
            warn(f"email_send_failed: {e!r}")

        return {"status": "ok", "date": today, "path": str(folder / "email.html")}
