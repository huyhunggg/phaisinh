[README.md](https://github.com/user-attachments/files/28334659/README.md)
# VN Technical Market Scanner

Bản build theo brief tracking tín hiệu kỹ thuật.

## Có gì

- MA5/10/20/50/100/200
- RSI14
- MACD / Signal / Histogram
- Volume MA20 / Volume Ratio
- High/Low 20 và 50 phiên
- Relative Strength 20/60/120 so với VNINDEX/VN30
- Distance MA20
- ATR14
- Breakout / False breakout / Breakdown
- Accumulation / Pullback / Reclaim MA / Overextended / Avoid
- Rating A+ đến D
- Hỗ trợ / kháng cự gần
- Alert message

## File

```txt
index.html
data.json
update_data.py
requirements.txt
.github/workflows/update-data.yml
```

## Cách dùng

Upload đè vào repo hiện tại, giữ `VNSTOCK_API_KEY`, chạy:

```txt
Actions → Update technical scanner → Run workflow
```
