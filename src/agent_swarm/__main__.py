
import asyncio, typer, uvicorn
from .eventbus import EventBus
from .agents.sales_agent import SalesAgent
from .agents.marketing_agent import MarketingAgent
from .agents.reporting_agent import ReportingAgent

app = typer.Typer()

@app.command()
def run_once():
    asyncio.run(_run())

async def _run():
    bus=EventBus(); s=SalesAgent(bus); m=MarketingAgent(bus); r=ReportingAgent(bus)
    ag1=asyncio.create_task(s.run()); ag2=asyncio.create_task(m.run())
    await asyncio.sleep(0.05)
    try:
        res=await r.run_once(); print(res)
    finally:
        ag1.cancel(); ag2.cancel()

@app.command()
def mock_api(host: str = "127.0.0.1", port: int = 8000):
    uvicorn.run("agent_swarm.mock_api:app", host=host, port=port, log_level="warning")

if __name__ == "__main__":
    app()

import asyncio, typer
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from .agents.reporting_agent import ReportingAgent
from .eventbus import EventBus
from .agents.sales_agent import SalesAgent
from .agents.marketing_agent import MarketingAgent
from .settings import SETTINGS

app = typer.Typer(add_completion=False) if 'app' not in globals() else app

@app.command()
def run_daily():
    async def _loop():
        tz = ZoneInfo(SETTINGS.REPORT_TIMEZONE)
        bus = EventBus()
        s = SalesAgent(bus); m = MarketingAgent(bus); r = ReportingAgent(bus)
        ag1 = asyncio.create_task(s.run())
        ag2 = asyncio.create_task(m.run())
        try:
            while True:
                now = datetime.now(tz)
                target = now.replace(hour=9, minute=0, second=0, microsecond=0)
                if now >= target:
                    target = target + timedelta(days=1)
                wait_s = (target - now).total_seconds()
                await asyncio.sleep(wait_s)
                try:
                    await r.run_once()
                except Exception as e:
                    # simple log to stderr; you can improve logging as needed
                    print(f"[daily] error: {e}", file=sys.stderr)
        finally:
            ag1.cancel(); ag2.cancel()

    asyncio.run(_loop())

