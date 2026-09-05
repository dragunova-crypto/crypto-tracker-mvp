from fastapi import FastAPI
import httpx

app = FastAPI()

@app.get("/prices")
async def get_prices():
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 10,
                "page": 1,
                "sparkline": False
            },
            timeout=10.0
        )
        r.raise_for_status()
        return r.json()
