# VN30 Futures Tracker

Bản chỉ tracking phái sinh VN30.

## Có gì

- VN30 / VNINDEX trạng thái xu hướng
- VN30F1M, VN30F2M, VN30F1Q, VN30F2Q
- Basis và Basis %
- MA10 / MA20 / MA50
- RSI14
- MACD
- Volume ratio
- Bias: CANH LONG / CANH SHORT / THEO DÕI / NO TRADE
- Levels: hỗ trợ, kháng cự, breakout, short trigger
- Kế hoạch Long/Short, stop, target, position sizing

## File

```txt
index.html
data.json
update_data.py
requirements.txt
.github/workflows/update-data.yml
```

## Lưu ý

Daily data chỉ dùng để xác định bias chính. Vào lệnh phái sinh bắt buộc xác nhận bằng chart intraday 5m/15m, có stop-loss và không gồng lỗ.
