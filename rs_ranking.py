"""
RS Ranking Calculation Module - Multi-Period Support
여러 기간의 Relative Strength 계산 및 순위 매기기
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

def calculate_rs_at_offset(prices, offset=0):
    """
    특정 시점(offset)에서의 RS 계산
    offset: 0=현재, 5=1주일전, 21=1개월전, etc.
    """
    # offset 적용 (과거 데이터만 사용)
    if offset > 0:
        if len(prices) <= offset:
            return None
        prices = prices[:-offset]

    # 분기별 성과 계산
    qtrs = quarters_perf(prices)
    if qtrs is None:
        return None

    # 종목 성과
    stock_str = strength(qtrs)

    return stock_str

def calculate_rs_multi_period(stock_data, reference_ticker='SPY'):
    """여러 기간의 RS 계산"""

    # 기간 정의 (거래일 기준)
    periods = {
        'current': 0,
        '1w_ago': 5,      # 1주일 = 5거래일
        '1m_ago': 21,     # 1개월 = 21거래일
        '3m_ago': 63,     # 3개월 = 63거래일
        '6m_ago': 126,    # 6개월 = 126거래일
        '1y_ago': 252     # 1년 = 252거래일
    }

    print(f"\n📊 멀티 기간 RS 계산 시작 (기준: {reference_ticker})...")
    print(f"   계산 기간: {', '.join(periods.keys())}\n")

    # 1. 기준 지수(SPY) 데이터 찾기
    reference_data = None
    for stock in stock_data:
        if stock['ticker'] == reference_ticker:
            reference_data = stock
            break

    if not reference_data:
        raise ValueError(f"기준 지수 {reference_ticker} 데이터가 없습니다!")

    # 2. 각 기간별로 기준 지수의 성과 계산
    ref_prices = [p['close'] for p in reference_data['prices']]

    ref_strengths = {}
    for period_name, offset in periods.items():
        ref_str = calculate_rs_at_offset(ref_prices, offset)
        if ref_str is None:
            print(f"⚠️  기준 지수 {period_name} 성과 계산 실패")
            continue
        ref_strengths[period_name] = ref_str
        print(f"✅ {reference_ticker} {period_name}: {ref_str:.2f}%")

    if not ref_strengths:
        raise ValueError(f"기준 지수 {reference_ticker}의 성과 계산 실패!")

    print(f"\n개별 종목 멀티 기간 RS 계산 중...\n")

    # 3. 각 종목의 멀티 기간 RS 계산
    rs_results = []

    for idx, stock in enumerate(stock_data, 1):
        ticker = stock['ticker']

        # 기준 지수는 스킵
        if ticker == reference_ticker:
            continue

        try:
            # 가격 데이터 추출
            prices = [p['close'] for p in stock['prices']]

            # 각 기간별 RS 계산
            rs_dict = {
                'ticker': ticker,
                'sector': stock['sector'],
                'industry': stock['industry'],
                'market_cap': stock['market_cap'],
                'exchange': stock['exchange']
            }

            # 모든 기간에 대해 RS 계산
            valid_periods = 0
            for period_name, offset in periods.items():
                if period_name not in ref_strengths:
                    rs_dict[f'rs_{period_name}'] = None
                    continue

                stock_str = calculate_rs_at_offset(prices, offset)
                if stock_str is None:
                    rs_dict[f'rs_{period_name}'] = None
                    continue

                # RS 계산
                rs = relative_strength(stock_str, ref_strengths[period_name])
                rs_dict[f'rs_{period_name}'] = rs
                valid_periods += 1

            # 현재 RS가 없으면 제외
            if rs_dict.get('rs_current') is None or valid_periods < 3:
                continue

            rs_results.append(rs_dict)

            if idx % 100 == 0:
                print(f"  처리 중: {idx}/{len(stock_data)} 종목... (성공: {len(rs_results)})")

        except Exception as e:
            continue

    print(f"\n✅ 멀티 기간 RS 계산 완료: {len(rs_results)}개 종목")

    return rs_results, periods

def calculate_percentiles_multi_period(rs_results, periods):
    """여러 기간의 RS 백분위 계산"""
    print("\n📊 멀티 기간 백분위 계산 중...")

    df = pd.DataFrame(rs_results)

    # 각 기간별로 백분위 계산
    for period_name in periods.keys():
        rs_col = f'rs_{period_name}'
        percentile_col = f'percentile_{period_name}'

        if rs_col not in df.columns:
            continue

        # 유효한 RS 값만 선택
        valid_mask = df[rs_col].notna()

        if valid_mask.sum() > 0:
            # 백분위 계산 (0~100)
            df.loc[valid_mask, 'rank_temp'] = df.loc[valid_mask, rs_col].rank(method='min', ascending=True)
            max_rank = df.loc[valid_mask, 'rank_temp'].max()
            df.loc[valid_mask, percentile_col] = ((df.loc[valid_mask, 'rank_temp'] - 1) / (max_rank - 1) * 100).round(0).astype(int)
            df = df.drop('rank_temp', axis=1)
        else:
            df[percentile_col] = None

    # 현재 RS 기준으로 정렬
    df = df.sort_values('rs_current', ascending=False, na_position='last').reset_index(drop=True)

    # 최종 순위 (1위부터)
    df['rank'] = range(1, len(df) + 1)

    print(f"✅ 백분위 계산 완료")

    return df

def save_results(df, config, periods):
    """결과를 CSV로 저장"""
    output_dir = config.get('OUTPUT_DIR', 'output')
    os.makedirs(output_dir, exist_ok=True)

    filename = f'{output_dir}/rs_stocks.csv'

    # 시가총액을 억 달러 단위로 변환
    df['market_cap_b'] = (df['market_cap'] / 1e9).round(2)

    # 저장할 컬럼 선택
    columns = ['rank', 'ticker', 'sector', 'industry', 'exchange', 'market_cap_b']

    # RS 값 추가
    for period_name in periods.keys():
        rs_col = f'rs_{period_name}'
        if rs_col in df.columns:
            columns.append(rs_col)

    # Percentile 값 추가
    for period_name in periods.keys():
        percentile_col = f'percentile_{period_name}'
        if percentile_col in df.columns:
            columns.append(percentile_col)

    output_df = df[columns].copy()

    # 컬럼명 변경
    column_names = {
        'rank': 'Rank',
        'ticker': 'Ticker',
        'sector': 'Sector',
        'industry': 'Industry',
        'exchange': 'Exchange',
        'market_cap_b': 'Market Cap ($B)',
        'rs_current': 'RS_Current',
        'rs_1w_ago': 'RS_1W_Ago',
        'rs_1m_ago': 'RS_1M_Ago',
        'rs_3m_ago': 'RS_3M_Ago',
        'rs_6m_ago': 'RS_6M_Ago',
        'rs_1y_ago': 'RS_1Y_Ago',
        'percentile_current': 'Percentile_Current',
        'percentile_1w_ago': 'Percentile_1W',
        'percentile_1m_ago': 'Percentile_1M',
        'percentile_3m_ago': 'Percentile_3M',
        'percentile_6m_ago': 'Percentile_6M',
        'percentile_1y_ago': 'Percentile_1Y'
    }

    output_df = output_df.rename(columns=column_names)

    # CSV 저장
    output_df.to_csv(filename, index=False, encoding='utf-8')
    print(f"💾 결과 저장: {filename}")

    return output_df

def main():
    """메인 실행 함수"""
    print("="*80)
    print("🚀 RS Ranking Calculation (Multi-Period)")
    print("="*80)
    print()

    # 설정 로드
    config = load_config()

    # 데이터 로드
    print("📂 주식 데이터 로드 중...")
    stock_data = load_stock_data()
    print(f"✅ {len(stock_data)}개 종목 데이터 로드")

    # 멀티 기간 RS 계산
    rs_results, periods = calculate_rs_multi_period(stock_data, config['REFERENCE_TICKER'])

    # 멀티 기간 백분위 계산
    df = calculate_percentiles_multi_period(rs_results, periods)

    # 최소 백분위 필터링 (현재 기준)
    min_percentile = config.get('MIN_PERCENTILE', 70)
    df_filtered = df[df['percentile_current'] >= min_percentile]
    print(f"✅ 현재 {min_percentile}% 이상: {len(df_filtered)}개 종목")

    # 결과 저장
    save_results(df_filtered, config, periods)

    # 상위 20개 출력
    print("\n" + "="*80)
    print("🏆 상위 20개 종목 (멀티 기간 RS)")
    print("="*80)
    print(f"{'Rank':>4} {'Ticker':<6} {'RS_Now':>7} {'RS_1W':>7} {'RS_1M':>7} {'RS_3M':>7} {'RS_6M':>7} {'RS_1Y':>7} {'Sector':<25}")
    print("-"*80)

    for idx, row in df_filtered.head(20).iterrows():
        print(f"{row['rank']:4d} {row['ticker']:<6} "
              f"{row.get('rs_current', 0):7.1f} "
              f"{row.get('rs_1w_ago', 0):7.1f} "
              f"{row.get('rs_1m_ago', 0):7.1f} "
              f"{row.get('rs_3m_ago', 0):7.1f} "
              f"{row.get('rs_6m_ago', 0):7.1f} "
              f"{row.get('rs_1y_ago', 0):7.1f} "
              f"{row['sector']:<25}")

    print("\n✅ 모든 작업 완료!")

if __name__ == "__main__":
    main()
