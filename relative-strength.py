"""
Relative Strength Calculator - Extended Version
확장된 범위로 RS 계산 및 CSV 생성
"""

import rs_data
import rs_ranking

def main():
    """메인 실행 함수"""
    print("="*80)
    print("🚀 RS Calculator Extended")
    print("   더 많은 종목으로 확장된 Relative Strength 분석")
    print("="*80)
    print()

    # 1단계: 데이터 수집
    print("[1단계] 주식 데이터 수집")
    print("-" * 80)
    rs_data.main()

    print("\n")

    # 2단계: RS 계산 및 순위
    print("[2단계] RS 계산 및 순위 매기기")
    print("-" * 80)
    rs_ranking.main()

    print("\n" + "="*80)
    print("✅ 모든 작업 완료!")
    print("   📁 output/rs_stocks.csv 파일을 확인하세요")
    print("="*80)

if __name__ == "__main__":
    main()
