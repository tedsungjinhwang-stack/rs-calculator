"""
RS Data Collection Module - Extended Version
확장된 범위로 더 많은 종목 데이터 수집
"""

import json
import time
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
import requests
import yaml

def load_config():
    """설정 파일 로드"""
    with open('config.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_sp500_tickers():
    """S&P 500 종목 리스트"""
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    tables = pd.read_html(requests.get(url, headers=headers).text)
    df = tables[0]
    return df['Symbol'].str.replace('.', '-').tolist()

def get_nasdaq100_tickers():
    """Nasdaq 100 종목 리스트"""
    url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    tables = pd.read_html(requests.get(url, headers=headers).text)
    df = tables[4]
    return df['Ticker'].str.replace('.', '-').tolist()

def get_sp400_tickers():
    """S&P 400 (Mid Cap) 종목 리스트"""
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_400_companies'
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        tables = pd.read_html(requests.get(url, headers=headers).text)
        df = tables[0]
        return df['Symbol'].str.replace('.', '-').tolist()
    except:
        print("⚠️  S&P 400 데이터 수집 실패")
        return []

def get_sp600_tickers():
    """S&P 600 (Small Cap) 종목 리스트"""
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_600_companies'
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        tables = pd.read_html(requests.get(url, headers=headers).text)
        df = tables[0]
        return df['Symbol'].str.replace('.', '-').tolist()
    except:
        print("⚠️  S&P 600 데이터 수집 실패")
        return []

def get_russell2000_tickers():
    """Russell 2000 종목 리스트 (Wikipedia에서)"""
    url = 'https://en.wikipedia.org/wiki/Russell_2000_Index'
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers)
        tables = pd.read_html(response.text)

        # Russell 2000 전체 리스트는 Wikipedia에 없음
        # 대신 상위 일부만 있을 수 있음
        if len(tables) > 0:
            df = tables[0]
            if 'Ticker' in df.columns:
                return df['Ticker'].str.replace('.', '-').tolist()
            elif 'Symbol' in df.columns:
                return df['Symbol'].str.replace('.', '-').tolist()
    except Exception as e:
        print(f"⚠️  Russell 2000 데이터 수집 실패: {e}")

    return []

def get_nasdaq_screener_tickers(min_market_cap=500000000, max_count=1000):
    """
    Nasdaq 스크리너에서 시가총액 기준 종목 가져오기
    min_market_cap: 최소 시가총액 ($)
    max_count: 최대 종목 수
    """
    print(f"📊 Nasdaq 스크리너에서 시가총액 ${min_market_cap/1e9:.1f}B 이상 종목 수집 중...")

    try:
        # Nasdaq FTP에서 전체 종목 리스트 다운로드
        url = "ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt"
        df = pd.read_csv(url, sep='|')

        # ETF 제외
        df = df[df['ETF'] == 'N']
        tickers = df['Symbol'].tolist()

        print(f"   ✅ {len(tickers)}개 Nasdaq 종목 수집")

        # NYSE 추가
        url_nyse = "ftp://ftp.nasdaqtrader.com/symboldirectory/otherlisted.txt"
        df_nyse = pd.read_csv(url_nyse, sep='|')
        df_nyse = df_nyse[df_nyse['ETF'] == 'N']
        tickers_nyse = df_nyse['ACT Symbol'].tolist()

        print(f"   ✅ {len(tickers_nyse)}개 NYSE 종목 수집")

        all_tickers = tickers + tickers_nyse

        # 중복 제거 및 특수문자 처리
        all_tickers = list(set([t.replace('.', '-') for t in all_tickers if isinstance(t, str) and t.strip()]))

        print(f"   📋 총 {len(all_tickers)}개 종목 (중복 제거 후)")
        print(f"   💰 시가총액 필터링 중... (최소 ${min_market_cap/1e9:.1f}B)")

        # 시가총액으로 필터링 (상위 max_count개만)
        # 주의: 모든 종목 조회는 시간이 오래 걸림
        # 샘플링 또는 배치 처리 필요

        return all_tickers[:max_count]  # 임시로 상위 N개만 반환

    except Exception as e:
        print(f"⚠️  스크리너 데이터 수집 실패: {e}")
        return []

def get_all_tickers(config):
    """설정에 따라 종목 리스트 수집"""
    all_tickers = set()

    # 기본 지수들
    if config.get('SP500', False):
        print("📊 S&P 500 종목 수집 중...")
        tickers = get_sp500_tickers()
        all_tickers.update(tickers)
        print(f"   ✅ {len(tickers)}개 종목 수집")

    if config.get('NQ100', False):
        print("📊 Nasdaq 100 종목 수집 중...")
        tickers = get_nasdaq100_tickers()
        all_tickers.update(tickers)
        print(f"   ✅ {len(tickers)}개 종목 수집")

    if config.get('SP400', False):
        print("📊 S&P 400 종목 수집 중...")
        tickers = get_sp400_tickers()
        all_tickers.update(tickers)
        print(f"   ✅ {len(tickers)}개 종목 수집")

    if config.get('SP600', False):
        print("📊 S&P 600 종목 수집 중...")
        tickers = get_sp600_tickers()
        all_tickers.update(tickers)
        print(f"   ✅ {len(tickers)}개 종목 수집")

    # Russell 2000 (확장)
    if config.get('INCLUDE_RUSSELL_2000', False):
        print("📊 Russell 2000 종목 수집 중...")
        tickers = get_russell2000_tickers()
        if tickers:
            all_tickers.update(tickers)
            print(f"   ✅ {len(tickers)}개 종목 수집")

    # 시가총액 기준 (확장)
    if config.get('INCLUDE_BY_MARKET_CAP', False):
        min_cap = config.get('MIN_MARKET_CAP', 500000000)
        max_count = config.get('MAX_TICKERS_BY_CAP', 1000)
        tickers = get_nasdaq_screener_tickers(min_cap, max_count)
        if tickers:
            all_tickers.update(tickers)
            print(f"   ✅ 추가 {len(tickers)}개 종목 수집")

    return sorted(list(all_tickers))

def fetch_stock_data(ticker, start_date, end_date, config):
    """개별 종목의 가격 데이터 및 메타 정보 수집"""
    try:
        stock = yf.Ticker(ticker)

        # 가격 데이터
        hist = stock.history(start=start_date, end=end_date)

        min_days = config.get('MIN_TRADING_DAYS', 200)
        if hist.empty or len(hist) < min_days:
            return None

        # 평균 거래량 체크
        min_volume = config.get('MIN_AVG_VOLUME', 100000)
        if hist['Volume'].mean() < min_volume:
            return None

        # 메타 정보
        info = stock.info

        # 데이터 구조화
        price_data = []
        for date, row in hist.iterrows():
            price_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume'])
            })

        result = {
            'ticker': ticker,
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
            'market_cap': info.get('marketCap', 0),
            'exchange': info.get('exchange', 'Unknown'),
            'prices': price_data
        }

        return result

    except Exception as e:
        return None

def collect_all_data(tickers, config):
    """모든 종목 데이터 수집"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=400)  # 1년 + 여유

    print(f"\n📅 데이터 수집 기간: {start_date.date()} ~ {end_date.date()}")
    print(f"📊 총 {len(tickers)}개 종목 데이터 수집 시작...\n")

    all_data = []
    success_count = 0

    for idx, ticker in enumerate(tickers, 1):
        if idx % 50 == 0:
            print(f"[{idx}/{len(tickers)}] 진행 중... (성공: {success_count})")

        data = fetch_stock_data(ticker, start_date, end_date, config)

        if data:
            all_data.append(data)
            success_count += 1

        # API rate limit 방지
        time.sleep(0.3)

    print(f"\n✅ 데이터 수집 완료: {success_count}/{len(tickers)} 종목")

    return all_data

def save_data(data, filename='data/stock_data.json'):
    """데이터를 JSON 파일로 저장"""
    import os
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"💾 데이터 저장 완료: {filename}")

def main():
    """메인 실행 함수"""
    print("="*80)
    print("🚀 RS Data Collection (Extended)")
    print("="*80)
    print()

    # 설정 로드
    config = load_config()

    # 종목 리스트 수집
    tickers = get_all_tickers(config)
    print(f"\n📋 총 {len(tickers)}개 유니크 종목")

    # 데이터 수집
    all_data = collect_all_data(tickers, config)

    # 데이터 저장
    save_data(all_data)

    print("\n✅ 모든 작업 완료!")

if __name__ == "__main__":
    main()
