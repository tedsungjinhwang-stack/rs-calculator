"""
RS Ranking Calculation Module
Relative Strength 계산 및 순위 매기기
"""

import json
import pandas as pd
import numpy as np
import yaml
import os

def load_config():
    """설정 파일 로드"""
    with open('config.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_stock_data(filename='data/stock_data.json'):
    """저장된 주식 데이터 로드"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def quarters_perf(prices, days_per_quarter=63):
    """
    분기별 수익률 계산
    days_per_quarter: 거래일 기준 약 3개월 (63일)
    """
    if len(prices) < days_per_quarter * 4:
        return None

    # 최근 4분기 시작점 인덱스
    indices = [
        len(prices) - 1,                          # 현재
        len(prices) - days_per_quarter - 1,       # 1분기 전
        len(prices) - days_per_quarter * 2 - 1,   # 2분기 전
        len(prices) - days_per_quarter * 3 - 1,   # 3분기 전
        len(prices) - days_per_quarter * 4 - 1    # 4분기 전
    ]

    # 인덱스 유효성 검사
    if any(idx < 0 for idx in indices):
        return None

    # 각 분기 수익률 계산
    perfs = []
    for i in range(4):
        start_price = prices[indices[i+1]]
        end_price = prices[indices[i]]
        if start_price > 0:
            perf = (end_price / start_price - 1) * 100
            perfs.append(perf)
        else:
            return None

    return perfs

def strength(quarters):
    """
    연간 성과 계산 (최근 분기는 2배 가중치)
    quarters: [Q1, Q2, Q3, Q4] (Q1이 최근)
    """
    if quarters is None or len(quarters) != 4:
        return None

    # 가중치: 최근 분기 40%, 나머지 각 20%
    weights = [0.4, 0.2, 0.2, 0.2]
    weighted_sum = sum(q * w for q, w in zip(quarters, weights))

    return weighted_sum

def relative_strength(stock_strength, reference_strength):
    """
    상대 강도 계산
    RS = (종목 성과 / 기준지수 성과) * 100
    """
    if stock_strength is None or reference_strength is None:
        return None

    if reference_strength == 0:
        return None

    rs = (stock_strength / reference_strength) * 100

    return rs

def calculate_rs_for_all(stock_data, reference_ticker='SPY'):
    """모든 종목의 RS 계산"""
    print(f"\n📊 RS 계산 시작 (기준: {reference_ticker})...\n")

    # 1. 기준 지수(SPY) 데이터 찾기
    reference_data = None
    for stock in stock_data:
        if stock['ticker'] == reference_ticker:
            reference_data = stock
            break

    if not reference_data:
        raise ValueError(f"기준 지수 {reference_ticker} 데이터가 없습니다!")

    # 2. 기준 지수의 성과 계산
    ref_prices = [p['close'] for p in reference_data['prices']]
    ref_quarters = quarters_perf(ref_prices)
    ref_strength = strength(ref_quarters)

    if ref_strength is None:
        raise ValueError(f"기준 지수 {reference_ticker}의 성과 계산 실패!")

    print(f"✅ {reference_ticker} 성과: {ref_strength:.2f}%")
    print(f"\n개별 종목 RS 계산 중...\n")

    # 3. 각 종목의 RS 계산
    rs_results = []

    for idx, stock in enumerate(stock_data, 1):
        ticker = stock['ticker']

        # 기준 지수는 스킵
        if ticker == reference_ticker:
            continue

        try:
            # 가격 데이터 추출
            prices = [p['close'] for p in stock['prices']]

            # 분기별 수익률
            qtrs = quarters_perf(prices)
            if qtrs is None:
                continue

            # 종목 성과
            stock_str = strength(qtrs)
            if stock_str is None:
                continue

            # RS 계산
            rs = relative_strength(stock_str, ref_strength)
            if rs is None:
                continue

            # 결과 저장
            rs_results.append({
                'ticker': ticker,
                'sector': stock['sector'],
                'industry': stock['industry'],
                'market_cap': stock['market_cap'],
                'exchange': stock['exchange'],
                'rs': rs,
                'stock_strength': stock_str
            })

            if idx % 100 == 0:
                print(f"  처리 중: {idx}/{len(stock_data)} 종목...")

        except Exception as e:
            continue

    print(f"\n✅ RS 계산 완료: {len(rs_results)}개 종목")

    return rs_results

def calculate_percentiles(rs_results):
    """RS 백분위 계산"""
    df = pd.DataFrame(rs_results)

    # RS 기준 오름차순 순위 (작은 값이 낮은 순위)
    df['rank'] = df['rs'].rank(method='min', ascending=True)

    # 백분위 계산 (0~100)
    df['percentile'] = ((df['rank'] - 1) / (len(df) - 1) * 100).round(0).astype(int)

    # RS 기준 내림차순 정렬
    df = df.sort_values('rs', ascending=False).reset_index(drop=True)

    # 최종 순위 (1위부터)
    df['rank'] = range(1, len(df) + 1)

    return df

def save_results(df, config):
    """결과를 CSV로 저장"""
    output_dir = config.get('OUTPUT_DIR', 'output')
    os.makedirs(output_dir, exist_ok=True)

    filename = f'{output_dir}/rs_stocks.csv'

    # 시가총액을 억 달러 단위로 변환
    df['market_cap_b'] = (df['market_cap'] / 1e9).round(2)

    # 저장할 컬럼 선택 및 순서 지정
    output_df = df[[
        'rank', 'ticker', 'sector', 'industry', 'exchange',
        'rs', 'percentile', 'market_cap_b', 'stock_strength'
    ]]

    # 컬럼명 변경
    output_df.columns = [
        'Rank', 'Ticker', 'Sector', 'Industry', 'Exchange',
        'Relative Strength', 'Percentile', 'Market Cap ($B)', 'Stock Strength (%)'
    ]

    # CSV 저장
    output_df.to_csv(filename, index=False, encoding='utf-8')
    print(f"💾 결과 저장: {filename}")

    return output_df

def main():
    """메인 실행 함수"""
    print("="*80)
    print("🚀 RS Ranking Calculation")
    print("="*80)
    print()

    # 설정 로드
    config = load_config()

    # 데이터 로드
    print("📂 주식 데이터 로드 중...")
    stock_data = load_stock_data()
    print(f"✅ {len(stock_data)}개 종목 데이터 로드")

    # RS 계산
    rs_results = calculate_rs_for_all(stock_data, config['REFERENCE_TICKER'])

    # 백분위 계산
    print("\n📊 백분위 계산 중...")
    df = calculate_percentiles(rs_results)

    # 최소 백분위 필터링
    min_percentile = config.get('MIN_PERCENTILE', 70)
    df_filtered = df[df['percentile'] >= min_percentile]
    print(f"✅ {min_percentile}% 이상: {len(df_filtered)}개 종목")

    # 결과 저장
    save_results(df_filtered, config)

    # 상위 20개 출력
    print("\n" + "="*80)
    print("🏆 상위 20개 종목")
    print("="*80)
    for idx, row in df_filtered.head(20).iterrows():
        print(f"{row['rank']:3d}. {row['ticker']:6s} | "
              f"RS: {row['rs']:7.2f} | "
              f"Percentile: {row['percentile']:3d} | "
              f"{row['sector']}")

    print("\n✅ 모든 작업 완료!")

if __name__ == "__main__":
    main()
