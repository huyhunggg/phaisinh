from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

import pandas as pd

VN_TZ = timezone(timedelta(hours=7))
VNSTOCK_API_KEY = os.getenv("VNSTOCK_API_KEY", "").strip()

if VNSTOCK_API_KEY:
    os.environ["VNSTOCK_API_KEY"] = VNSTOCK_API_KEY
    os.environ["VNSTOCK_TOKEN"] = VNSTOCK_API_KEY
    os.environ["VNSTOCK_KEY"] = VNSTOCK_API_KEY
    os.environ["VNSTOCK_INTERACTIVE"] = "0"
    os.environ["VNSTOCK_LANGUAGE"] = "2"

CONTRACTS = ["VN30F1M", "VN30F2M", "VN30F1Q", "VN30F2Q"]
INDEX_SYMBOLS = ["VN30", "VN30INDEX", "VNINDEX"]

END_DATE = datetime.now(VN_TZ).strftime("%Y-%m-%d")
START_DATE = (datetime.now(VN_TZ) - timedelta(days=260)).strftime("%Y-%m-%d")

def safe_float(x: Any, ndigits: int = 2):
    try:
        if x is None or pd.isna(x):
            return None
        return round(float(x), ndigits)
    except Exception:
        return None

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    lower = {str(c).lower().strip(): c for c in df.columns}
    aliases = {
        "time": ["time", "date", "tradingdate", "trading_date"],
        "open": ["open", "openprice"],
        "high": ["high", "highestprice"],
        "low": ["low", "lowestprice"],
        "close": ["close", "closeprice", "matchprice", "price"],
        "volume": ["volume", "nmvolume", "total_volume", "matchingvolume"],
        "open_interest": ["open_interest", "openinterest", "oi"],
    }
    rename = {}
    for target, keys in aliases.items():
        for k in keys:
            if k in lower:
                rename[lower[k]] = target
                break
    df = df.rename(columns=rename)
    if "time" not in df.columns:
        df["time"] = range(len(df))
    if "close" not in df.columns:
        raise ValueError(f"Missing close column. Columns={list(df.columns)}")
    for col in ["open", "high", "low"]:
        if col not in df.columns:
            df[col] = df["close"]
    if "volume" not in df.columns:
        df["volume"] = 0
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["volume"] = df["volume"].fillna(0)
    df = df.dropna(subset=["close"]).reset_index(drop=True)
    return df

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, pd.NA)
    return 100 - (100 / (1 + rs))

def macd(series: pd.Series):
    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()
    line = ema12 - ema26
    signal = line.ewm(span=9, adjust=False).mean()
    hist = line - signal
    return line, signal, hist

def fetch_history(symbol: str):
    attempts: list[tuple[str, Callable[[], pd.DataFrame]]] = []

    # Chỉ dùng ít nguồn để tránh rate limit. Nếu VCI lỗi, mới thử KBS.
    try:
        from vnstock import Quote
        for src in ["VCI", "KBS"]:
            attempts.append(
                (
                    f"Quote/{src}",
                    lambda src=src: Quote(symbol=symbol, source=src).history(
                        start=START_DATE,
                        end=END_DATE,
                        interval="1D",
                    ),
                )
            )
    except Exception:
        pass

    try:
        from vnstock import Vnstock
        for src in ["VCI", "KBS"]:
            attempts.append(
                (
                    f"Vnstock/{src}",
                    lambda src=src: Vnstock()
                    .stock(symbol=symbol, source=src)
                    .quote.history(
                        start=START_DATE,
                        end=END_DATE,
                        interval="1D",
                    ),
                )
            )
    except Exception:
        pass

    errors = []
    for name, fn in attempts:
        try:
            df = normalize_columns(fn())
            if len(df) >= 30:
                return df, name
            errors.append(f"{name}: too few rows {len(df)}")
        except Exception as exc:
            errors.append(f"{name}: {type(exc).__name__}: {exc}")

    raise RuntimeError(" | ".join(errors[:6]) or "No fetch method available")

def add_indicators(df: pd.DataFrame):
    close = df["close"]
    for p in [5, 10, 20, 50, 100, 200]:
        df[f"ma{p}"] = close.rolling(p).mean()
    df["rsi14"] = rsi(close)
    df["macd"], df["macd_signal"], df["macd_hist"] = macd(close)
    df["vol_ma20"] = df["volume"].rolling(20).mean()
    df["vol_ratio"] = df["volume"] / df["vol_ma20"]
    df["high20_prev"] = df["high"].rolling(20).max().shift(1)
    df["low20_prev"] = df["low"].rolling(20).min().shift(1)
    df["high50_prev"] = df["high"].rolling(50).max().shift(1)
    df["low50_prev"] = df["low"].rolling(50).min().shift(1)
    return df

def detect_levels(df: pd.DataFrame, close: float):
    recent = df.tail(80)
    support_near = float(recent["low"].tail(20).min())
    support_key = float(recent["low"].tail(50).min())
    resistance_near = float(recent["high"].tail(20).max())
    breakout_level = resistance_near
    short_trigger = support_near
    return {
        "support_near": safe_float(support_near, 2),
        "support_key": safe_float(support_key, 2),
        "resistance_near": safe_float(resistance_near, 2),
        "breakout_level": safe_float(breakout_level, 2),
        "short_trigger": safe_float(short_trigger, 2),
    }

def analyze_index(symbol: str, df: pd.DataFrame):
    df = add_indicators(df)
    last = df.iloc[-1]
    c = float(last["close"])
    trend = (
        "STRONG_UPTREND"
        if last["close"] > last["ma20"] > last["ma50"]
        and last["rsi14"] > 55
        and last["macd"] > last["macd_signal"]
        else "UPTREND"
        if last["close"] > last["ma20"]
        else "DOWNTREND"
        if last["close"] < last["ma20"] and last["rsi14"] < 45
        else "SIDEWAY"
    )
    return {
        "symbol": symbol,
        "close": safe_float(c, 2),
        "trendState": trend,
        "rsi14": safe_float(last.get("rsi14")),
        "macdState": "MACD+" if last["macd"] > last["macd_signal"] else "MACD-",
        "ma20": safe_float(last.get("ma20")),
        "ma50": safe_float(last.get("ma50")),
        "ret5": safe_float((c / df.iloc[-6]["close"] - 1) * 100, 2) if len(df) > 6 else None,
        "ret20": safe_float((c / df.iloc[-21]["close"] - 1) * 100, 2) if len(df) > 21 else None,
    }

def analyze_contract(symbol: str, df: pd.DataFrame, vn30_state: dict | None):
    df = add_indicators(df)
    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else last
    c = float(last["close"])
    vn30_close = vn30_state.get("close") if vn30_state else None

    basis = safe_float(c - vn30_close, 2) if vn30_close else None
    basis_pct = safe_float(basis / vn30_close * 100, 2) if basis is not None and vn30_close else None
    vol_ratio = safe_float(last.get("vol_ratio"), 2) or 1
    rsi14 = safe_float(last.get("rsi14"), 2)
    day_change = safe_float((c / float(prev["close"]) - 1) * 100, 2) if float(prev["close"]) else 0

    above_ma20 = bool(last["close"] > last["ma20"]) if pd.notna(last.get("ma20")) else False
    above_ma50 = bool(last["close"] > last["ma50"]) if pd.notna(last.get("ma50")) else False
    macd_positive = bool(last["macd"] > last["macd_signal"]) if pd.notna(last.get("macd")) else False
    basis_positive = bool(basis is not None and basis > 0)
    basis_overheated = bool(basis is not None and basis > 10)

    trend_score = 0
    if last["close"] > last["ma10"]: trend_score += 7
    if above_ma20: trend_score += 8
    if above_ma50: trend_score += 7

    momentum_score = 0
    if rsi14 and 52 <= rsi14 <= 65: momentum_score += 8
    elif rsi14 and 45 <= rsi14 <= 70: momentum_score += 5
    if macd_positive: momentum_score += 8
    if day_change and day_change > 0: momentum_score += 2
    momentum_score = max(0, min(20, momentum_score))

    basis_score = 10
    if basis is not None:
        if -3 <= basis <= 6:
            basis_score += 4
        elif basis > 10:
            basis_score -= 5
        elif basis < -10:
            basis_score -= 3
    basis_score = max(0, min(15, basis_score))

    volume_score = 8
    if vol_ratio >= 1.5:
        volume_score += 7
    elif vol_ratio >= 1.2:
        volume_score += 4
    volume_score = max(0, min(15, volume_score))

    risk_score = 15
    if rsi14 and rsi14 > 72:
        risk_score -= 5
    if basis is not None and abs(basis) > 12:
        risk_score -= 4
    if last.get("ma20") and pd.notna(last["ma20"]):
        distance_ma20 = abs((c / float(last["ma20"]) - 1) * 100)
        if distance_ma20 > 2.5:
            risk_score -= 3
    risk_score = max(0, min(15, risk_score))

    score = round(min(95, trend_score + momentum_score + basis_score + volume_score + risk_score), 1)

    vn30_ok = vn30_state and vn30_state.get("trendState") in ["STRONG_UPTREND", "UPTREND"]
    vn30_weak = vn30_state and vn30_state.get("trendState") == "DOWNTREND"

    long_setup = bool(
        score >= 72
        and above_ma20
        and macd_positive
        and vn30_ok
        and (rsi14 is None or rsi14 < 70)
        and not basis_overheated
    )
    short_setup = bool(
        (score <= 45 or (not above_ma20 and not macd_positive))
        and (vn30_weak or basis is not None)
        and not (basis is not None and basis < -12)
    )
    no_trade = not long_setup and not short_setup and score < 65

    if long_setup:
        bias = "CANH LONG"
        rating = "A" if score < 85 else "A+"
        trend_state = "UPTREND"
        action_tag = "Long ưu thế, ưu tiên retest hoặc breakout có xác nhận"
    elif short_setup:
        bias = "CANH SHORT"
        rating = "D" if score < 45 else "C"
        trend_state = "DOWNTREND"
        action_tag = "Short ưu thế nếu VN30 mất hỗ trợ"
    elif score >= 60:
        bias = "THEO DÕI"
        rating = "B"
        trend_state = "SIDEWAY"
        action_tag = "Có tín hiệu nhưng chưa đủ đẹp"
    else:
        bias = "NO TRADE"
        rating = "C"
        trend_state = "NO_TRADE"
        action_tag = "Không có lợi thế rõ"

    alerts = []
    if long_setup:
        alerts.append(f"[LONG WATCH] {symbol} trên MA20, MACD tích cực, VN30 đồng thuận.")
    if short_setup:
        alerts.append(f"[SHORT WATCH] {symbol} suy yếu, cần xác nhận thủng hỗ trợ intraday.")
    if basis_overheated:
        alerts.append(f"[RISK] Basis {basis} điểm, không Long đuổi khi basis quá dương.")
    if rsi14 and rsi14 > 70:
        alerts.append(f"[RISK] RSI {rsi14}, tránh FOMO.")
    if no_trade:
        alerts.append(f"[NO TRADE] {symbol} chưa có lợi thế rõ.")

    lv = detect_levels(df, c)

    comment = (
        f"{symbol}: {bias}, score {score}. Basis {basis if basis is not None else '-'} điểm. "
        "Daily chỉ dùng xác định hướng chính; điểm vào cần chart 5m/15m."
    )

    return {
        "symbol": symbol,
        "contractName": f"{symbol} - Hợp đồng tương lai VN30",
        "close": safe_float(c, 2),
        "basis": basis,
        "basisPct": basis_pct,
        "score": score,
        "bias": bias,
        "rating": rating,
        "trendState": trend_state,
        "actionTag": action_tag,
        "signals": {
            "above_ma20": above_ma20,
            "above_ma50": above_ma50,
            "rsi14": rsi14,
            "macd_positive": macd_positive,
            "volume_ratio": vol_ratio,
            "basis_positive": basis_positive,
            "basis_overheated": basis_overheated,
            "long_setup": long_setup,
            "short_setup": short_setup,
            "no_trade": no_trade,
        },
        "subscores": {
            "trend": trend_score,
            "momentum": momentum_score,
            "basis": basis_score,
            "volume": volume_score,
            "risk": risk_score,
        },
        "levels": lv,
        "alerts": alerts,
        "tradingPlan": {
            "longSetup": "Long khi F1M giữ trên MA20/MA10, MACD tích cực, VN30 không mất hỗ trợ và basis không quá dương.",
            "shortSetup": "Short khi F1M thủng hỗ trợ/MA20, MACD cắt xuống và VN30 suy yếu đồng thuận.",
            "entry": "Chỉ vào sau xác nhận intraday 5m/15m; tránh vùng nhiễu hoặc basis quá rộng.",
            "stopLoss": "3–5 điểm hoặc khi mất vùng xác nhận; tuyệt đối không gồng lỗ.",
            "takeProfit": "TP1 6–8 điểm; TP2 10–15 điểm; đạt TP1 kéo stop về hòa vốn.",
            "positionSizing": "Lệnh thăm dò 20–30%; chỉ tăng khi đúng hướng và VN30 xác nhận.",
        },
        "comment": comment,
    }

def fallback(errors: dict):
    return {
        "meta": {
            "updated_at": datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M:%S VN"),
            "source": "fallback sample",
            "success": 0,
            "note": "Không lấy được dữ liệu phái sinh từ Vnstock. Xem meta.errors.",
            "errors": errors,
        },
        "market": {
            "vn30": {
                "symbol": "VN30",
                "close": 1285.4,
                "trendState": "UPTREND",
                "rsi14": 58.2,
                "macdState": "MACD+",
                "ma20": 1276.2,
                "ma50": 1258.8,
                "ret5": 1.4,
                "ret20": 3.6,
            },
            "vnindex": {
                "symbol": "VNINDEX",
                "close": 1320.8,
                "trendState": "UPTREND",
                "rsi14": 57.1,
            },
        },
        "contracts": [],
    }

def main():
    errors = {}

    vn30_state = None
    vnindex_state = None

    for idx_symbol in INDEX_SYMBOLS:
        try:
            time.sleep(1.2)
            df, src = fetch_history(idx_symbol)
            state = analyze_index(idx_symbol, df)
            if idx_symbol in ["VN30", "VN30INDEX"] and vn30_state is None:
                vn30_state = state
            if idx_symbol == "VNINDEX":
                vnindex_state = state
            print("INDEX OK", idx_symbol, src, state["trendState"])
        except Exception as exc:
            errors[idx_symbol] = str(exc)
            print("INDEX ERR", idx_symbol, exc)

    contracts = []
    for symbol in CONTRACTS:
        try:
            time.sleep(1.2)
            df, src = fetch_history(symbol)
            item = analyze_contract(symbol, df, vn30_state)
            contracts.append(item)
            print("OK", symbol, item["bias"], item["score"], src)
        except Exception as exc:
            errors[symbol] = str(exc)
            print("ERR", symbol, exc)

    if contracts and vn30_state:
        data = {
            "meta": {
                "updated_at": datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M:%S VN"),
                "source": "Vnstock VN30 Futures Tracker",
                "success": len(contracts),
                "note": "Tracking phái sinh VN30 only. Daily bias, cần xác nhận intraday 5m/15m.",
                "errors": errors,
            },
            "market": {
                "vn30": vn30_state,
                "vnindex": vnindex_state,
            },
            "contracts": sorted(contracts, key=lambda x: x.get("score", 0), reverse=True),
        }
    else:
        data = fallback(errors)

    Path("data.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("Wrote data.json", len(data.get("contracts", [])))

if __name__ == "__main__":
    main()
