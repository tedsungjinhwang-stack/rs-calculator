# RS Calculator Extended 🚀

IBD 스타일의 Relative Strength (상대 강도) 계산기 - 확장 버전

**기존 대비 개선사항:**
- ✅ S&P 500 + Nasdaq 100 + S&P 400/600 (기본)
- ✅ Russell 2000 소형주 지수 포함
- ✅ 시가총액 $500M 이상 전체 종목 커버
- ✅ **약 2,500-3,000 종목 분석** (기존 1,336개 → 2배 이상)
- ✅ OKLO 같은 신규 상장주 포함!
- ✅ GitHub Actions 자동화 (매일 업데이트)

---

## 📊 RS (Relative Strength)란?

IBD(Investor's Business Daily) 방식의 상대 강도 지표:
- **최근 12개월** 성과를 분석 (최근 3개월은 2배 가중치)
- SPY 대비 상대적 성과로 계산
- 0-100 백분위로 표시 (99 = 상위 1%)

---

## 🎯 주요 기능

### 1. 확장된 종목 범위
```yaml
# config.yaml
NQ100: true           # Nasdaq 100
SP500: true           # S&P 500
SP400: true           # S&P MidCap 400
SP600: true           # S&P SmallCap 600
INCLUDE_RUSSELL_2000: true    # Russell 2000 추가
INCLUDE_BY_MARKET_CAP: true   # 시총 기준 추가
```

### 2. 시가총액 필터링
```yaml
MIN_MARKET_CAP: 500000000     # $500M 이상
MAX_TICKERS_BY_CAP: 1000      # 상위 1000개
```

### 3. 데이터 품질 필터
```yaml
MIN_TRADING_DAYS: 200         # 최소 200일 거래 기록
MIN_AVG_VOLUME: 100000        # 최소 평균 거래량
```

---

## 🚀 빠른 시작

### 로컬 실행

```bash
# 1. 저장소 클론
git clone https://github.com/YOUR_USERNAME/rs-calculator-extended.git
cd rs-calculator-extended

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 실행
python relative-strength.py
```

**예상 실행 시간:** 약 30-60분 (2,500+ 종목)

### 결과 확인

```bash
# RS 순위 CSV 파일
cat output/rs_stocks.csv
```

---

## ⚙️ GitHub Actions 설정

### 1. GitHub에 저장소 생성

```bash
# GitHub에서 새 저장소 생성 후
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/rs-calculator-extended.git
git push -u origin main
```

### 2. GitHub Actions 자동 실행 설정

`.github/workflows/calculate-rs.yml` 파일이 이미 포함되어 있습니다!

**자동 실행 일정:**
- **매일 새벽 2시 UTC** (한국 시간 오전 11시)
- 결과는 자동으로 commit & push

**수동 실행:**
1. GitHub 저장소 페이지 이동
2. `Actions` 탭 클릭
3. `Calculate RS` workflow 선택
4. `Run workflow` 버튼 클릭

### 3. 결과 확인

- **최신 CSV**: `output/rs_stocks.csv`
- **Raw URL**: `https://raw.githubusercontent.com/YOUR_USERNAME/rs-calculator-extended/main/output/rs_stocks.csv`

---

## 📁 프로젝트 구조

```
rs-calculator-extended/
├── .github/
│   └── workflows/
│       └── calculate-rs.yml    # GitHub Actions 워크플로우
├── config.yaml                 # 설정 파일
├── requirements.txt            # Python 패키지
├── relative-strength.py        # 메인 실행 파일
├── rs_data.py                  # 데이터 수집 모듈
├── rs_ranking.py               # RS 계산 모듈
├── data/
│   └── stock_data.json         # 수집된 가격 데이터
└── output/
    └── rs_stocks.csv           # 최종 RS 순위
```

---

## 🔧 설정 옵션

### config.yaml

```yaml
# 기본 지수
NQ100: true
SP500: true
SP400: true
SP600: true

# 확장 옵션
INCLUDE_RUSSELL_2000: true      # Russell 2000 포함 여부
INCLUDE_BY_MARKET_CAP: true     # 시총 기준 추가 여부

# 시가총액 필터
MIN_MARKET_CAP: 500000000       # 최소 시가총액 ($500M)
MAX_TICKERS_BY_CAP: 1000        # 최대 종목 수

# 데이터 필터
MIN_TRADING_DAYS: 200           # 최소 거래일
MIN_AVG_VOLUME: 100000          # 최소 평균 거래량

# RS 필터
MIN_PERCENTILE: 70              # 70 이상만 출력
REFERENCE_TICKER: SPY           # 기준 지수
```

---

## 💡 사용 예시

### 다른 프로젝트에서 활용

```python
# 최신 RS 데이터 가져오기
import pandas as pd
import requests
from io import StringIO

url = "https://raw.githubusercontent.com/YOUR_USERNAME/rs-calculator-extended/main/output/rs_stocks.csv"
response = requests.get(url)
df = pd.read_csv(StringIO(response.text))

# 대형주 상위 10개
large_cap = df[df['Market Cap ($B)'] >= 10].head(10)
print(large_cap)

# 성장 섹터 상위 10개
growth = df[df['Sector'].isin(['Technology', 'Healthcare'])].head(10)
print(growth)
```

---

## 📊 출력 예시

```
================================================================================
🏆 상위 20개 종목
================================================================================
  1. KC     | RS:  574.15 | Percentile:  99 | Technology
  2. RCAT   | RS:  513.61 | Percentile:  99 | Technology
  3. APP    | RS:  476.83 | Percentile:  99 | Technology
  4. VNET   | RS:  475.39 | Percentile:  99 | Technology
  5. ASTS   | RS:  475.37 | Percentile:  99 | Communication Services
  ...
```

---

## 🤝 기여

이슈 및 PR 환영합니다!

---

## 📝 라이센스

MIT License

---

## 🙏 크레딧

원본 프로젝트: [skyte/relative-strength](https://github.com/skyte/relative-strength)

확장 버전: 더 많은 종목 커버 + GitHub Actions 자동화
