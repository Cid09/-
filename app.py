import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(layout="wide")  # 전체 화면 레이아웃 사용

st.title("📊 생필품 가격 변동 분석 & 비교 대시보드")

# CSV 불러오기
df = pd.read_csv("products.csv")

# 레이아웃: 좌우 컬럼 분리
left_col, right_col = st.columns([1, 2])

with left_col:
    st.header("필터 & 선택")

    categories = df["Category"].unique()
    selected_categories = st.multiselect("카테고리를 선택하세요:", categories, default=list(categories))

    filtered_df = df[df["Category"].isin(selected_categories)]

    search_input = st.text_input("상품명을 검색하세요 (부분 입력 가능)").strip()
    products = filtered_df["Product"].unique()
    if search_input:
        filtered_products = [p for p in products if search_input in p]
    else:
        filtered_products = list(products)

    selected_products = st.multiselect("비교할 상품을 선택하세요 (최대 3개)", filtered_products, max_selections=3)

with right_col:
    if selected_products:
        # 탭으로 그래프와 분석 나누기
        tabs = st.tabs(["가격 변동 비교 그래프", "상승률 그래프", "경제학적 분석", "데이터 다운로드"])

        # 1. 가격 변동 비교 그래프
        with tabs[0]:
            fig, ax = plt.subplots()
            for product in selected_products:
                product_df = filtered_df[filtered_df["Product"] == product].sort_values("Year")
                ax.plot(product_df["Year"], product_df["Price"], marker="o", label=product)
            ax.set_title("선택한 상품 가격 변동 비교 (2020~2025)", fontsize=14)
            ax.set_xlabel("연도")
            ax.set_ylabel("가격 (원)")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)

        # 2. 상승률 그래프 (첫 번째 선택한 상품 기준)
        with tabs[1]:
            main_product = selected_products[0]
            main_df = filtered_df[filtered_df["Product"] == main_product].sort_values("Year")
            main_df["pct_change"] = main_df["Price"].pct_change() * 100

            fig2, ax2 = plt.subplots()
            ax2.bar(main_df["Year"][1:], main_df["pct_change"][1:], color="salmon")
            ax2.set_title(f"{main_product} 연도별 가격 상승률 (%)", fontsize=14)
            ax2.set_xlabel("연도")
            ax2.set_ylabel("상승률 (%)")
            ax2.grid(axis="y")
            st.pyplot(fig2)

        # 3. 경제학적 분석
        with tabs[2]:
            st.markdown("### 📈 경제학적 분석")
            price_change = main_df["Price"].iloc[-1] - main_df["Price"].iloc[0]
            if price_change > 0:
                st.success(f"{main_product} 가격이 총 {price_change}원 상승했습니다. 인플레이션이나 원자재 가격 상승 영향을 받을 수 있습니다.")
            elif price_change < 0:
                st.info(f"{main_product} 가격이 총 {abs(price_change)}원 하락했습니다. 공급 증가나 수요 감소가 원인일 수 있습니다.")
            else:
                st.warning(f"{main_product} 가격이 변화하지 않아 안정적인 시장 상태를 나타냅니다.")

        # 4. 데이터 다운로드
        with tabs[3]:
            download_df = filtered_df[filtered_df["Product"].isin(selected_products)]
            csv_bytes = download_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="선택한 상품 데이터 CSV 다운로드",
                data=csv_bytes,
                file_name="selected_product_price.csv",
                mime="text/csv"
            )
    else:
        st.info("비교할 상품을 최소 1개 이상 선택해 주세요.")
