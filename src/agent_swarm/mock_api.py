from __future__ import annotations
import os, random, datetime as dt
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

def _today() -> dt.date:
    forced = os.getenv("MOCK_DATE")
    if forced:
        return dt.date.fromisoformat(forced)
    return dt.date.today()

def _rng_for(date: dt.date) -> random.Random:
    seed = int(date.strftime("%Y%m%d"))  # deterministic per day
    return random.Random(seed)

def create_app() -> FastAPI:
    app = FastAPI(title="Agent Swarm Mock API")

    @app.get("/")
    def root():
        return RedirectResponse(url="/docs")

    @app.get("/health")
    def health():
        d = _today()
        return {"status": "ok", "date": d.isoformat()}

    @app.get("/sales")
    def sales():
        d = _today()
        rng = _rng_for(d)
        base_total = rng.randint(900_000, 1_800_000)
        orders = rng.randint(90, 180)
        new_customers = rng.randint(10, 40)
        aov = round(base_total / max(orders, 1), 2)
        return {
            "date": d.isoformat(),
            "currency": "INR",
            "total_sales": float(base_total),
            "new_customers": new_customers,
            "orders": orders,
            "avg_order_value": float(aov),
        }

    @app.get("/marketing")
    def marketing():
        d = _today()
        rng = _rng_for(d)
        names = [
            "Email - Independence Offer",
            "Google Ads - Branded",
            "Meta - Prospecting",
            "YouTube - Remarketing",
        ]
        campaigns = []
        for name in names:
            ctr = round(rng.uniform(0.8, 13.5), 1)
            conv = rng.randint(3, 25)
            spend = round(rng.uniform(3000, 20000), 0)
            rev   = round(spend * rng.uniform(2.5, 9.0), 0)
            roas  = round(rev / spend, 2) if spend else None
            campaigns.append({
                "name": name,
                "click_rate": ctr,
                "conversions": conv,
                "spend": float(spend),
                "revenue": float(rev),
                "roas": roas,
            })
        return {"date": d.isoformat(), "campaigns": campaigns}

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8000")))
