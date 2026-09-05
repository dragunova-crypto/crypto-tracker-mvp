import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Крипто Трекер", page_icon="💹", layout="wide")
st.title("💹 Крипто Трекер — Топ 10")

# Запрос к CoinGecko API
url = "https://api.coingecko.com/api/v3/coins/markets"
params = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 10,
    "page": 1,
    "sparkline": False
}

try:
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
except Exception as e:
    st.error(f"Не удалось получить данные: {e}")
    st.stop()

# Подготовка DataFrame
df = pd.DataFrame(data)
df = df[["name", "current_price", "market_cap", "total_volume", "price_change_percentage_24h"]]
df.columns = ["Монета", "Цена (USD)", "Капитализация", "Объём 24ч", "Изменение 24ч (%)"]

# Форматирование чисел
def fmt_money(x):
    if pd.isna(x): return "-"
    if x >= 1e12: return f"\${x/1e12:.2f} трлн"
    if x >= 1e9: return f"\${x/1e9:.2f} млрд"
    if x >= 1e6: return f"\${x/1e6:.2f} млн"
    return f"\${x:,.2f}"

def fmt_pct(x):
    if pd.isna(x): return "-"
    sign = "▼" if x < 0 else "▲"
    return f"{sign}{abs(x):.2f}%"

df["Капитализация"] = df["Капитализация"].apply(fmt_money)
df["Объём 24ч"] = df["Объём 24ч"].apply(fmt_money)
df["Изменение 24ч (%)"] = df["Изменение 24ч (%)"].apply(fmt_pct)

# Карточки с метриками
col1, col2, col3, col4 = st.columns(4)
total_market_cap = sum(item.get("market_cap") or 0 for item in data)
total_volume = sum(item.get("total_volume") or 0 for item in data)
dominance_btc = next((item.get("market_cap_change_percentage_24h_in_currency") or 0 for item in data if item.get("symbol") == "btc"), 0)

col1.metric("Капитализация рынка", fmt_money(total_market_cap))
col2.metric("Объём 24ч", fmt_money(total_volume))
col3.metric("BTC доминирование", f"{dominance_btc:.1f}%")
col4.metric("Обновлено", pd.Timestamp.now().strftime("%H:%M:%S"))

# Таблица
st.subheader("Топ 10 криптовалют")
st.dataframe(df, use_container_width=True, hide_index=True)

# График изменения цен
st.subheader("Динамика изменения за 24 часа")
fig = px.bar(
    df,
    x="Монета",
    y="Изменение 24ч (%)",
    title="Изменение цены за 24 часа (%)",
    color="Изменение 24ч (%)",
    color_continuous_scale=["red", "white", "green"],
    text="Изменение 24ч (%)"
)
fig.update_layout(xaxis_title="", yaxis_title="Изменение (%)", showlegend=False)
st.plotly_chart(fig, use_container_width=True)
