import streamlit as st
import pandas as pd
import io
import requests
import altair as alt

# データの取得とキャッシュ
@st.cache_data
def get_cpi_data():
    """e-StatからCPIのCSVデータを取得し、整形する関数"""
    url = "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000032103842&fileKind=1"

    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTPエラーがあれば例外を発生させる
        csv_data = io.BytesIO(response.content)

        # 1行目をヘッダーとして読み込み、2行目から6行目をスキップ
        df = pd.read_csv(csv_data, encoding='shift_jis', header=0, skiprows=list(range(1, 7)))

        # 最初の列名が「類・品目」となるので、yyyymmに変更
        df.rename(columns={'類・品目': 'yyyymm'}, inplace=True)

        # 不要な列を削除 (データがすべて欠損値の列)
        df = df.dropna(axis=1, how='all')

        # yyyymm以外の列を数値型に変換
        numeric_cols = [col for col in df.columns if col != 'yyyymm']
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

        return df

    except requests.exceptions.RequestException as e:
        st.error(f"データの取得中にエラーが発生しました: {e}")
        return pd.DataFrame()

# アプリのメイン処理
def main():
    st.title("CPI（消費者物価指数）グラフ表示アプリ")

    df = get_cpi_data()

    if df.empty:
        st.warning("データを取得できませんでした。")
        return

    # 日付列の整形
    df['年月'] = df['yyyymm'].astype(str).str.slice(0, 6)
    df['年月'] = df['年月'].apply(lambda x: f"{x[:4]}年{x[4:6]}月" if len(x) == 6 else None)

    # グラフ表示用のデータフレームを準備
    plot_df = df.set_index('年月')

    # カテゴリの選択
    columns_to_plot = [col for col in plot_df.columns if col != 'yyyymm']
    selected_column = st.selectbox("カテゴリを選択してください", columns_to_plot)

    if selected_column:
        st.subheader(f"CPIの推移: {selected_column}")

        # グラフ描画のためのDataFrameを準備
        chart_df = plot_df[[selected_column]].reset_index()

        # 前年比の計算
        chart_df['yyyymm_int'] = chart_df['年月'].str[:4].astype(int) * 100 + chart_df['年月'].str[5:7].astype(int)
        chart_df['yyyymm_prev'] = chart_df['yyyymm_int'] - 100

        # 前年同月のデータを結合
        chart_df = pd.merge(chart_df, chart_df[['yyyymm_int', selected_column]],
                            left_on='yyyymm_prev', right_on='yyyymm_int',
                            suffixes=('', '_prev'))

        # ★修正箇所★ 正しい構文に修正
        chart_df['前年比'] = ((chart_df[selected_column] / chart_df[selected_column + '_prev']) - 1) * 100

        # Altairで折れ線グラフ（CPI）を作成
        line_chart = alt.Chart(chart_df).mark_line(point=True, color='blue').encode(
            x=alt.X('年月', axis=alt.Axis(title='年月', titleColor='black', labelColor='black')),
            y=alt.Y(selected_column, axis=alt.Axis(title='指数', titleColor='black', labelColor='black'))
        )

        # Altairで棒グラフ（前年比）を作成
        bar_chart = alt.Chart(chart_df).mark_bar(color='red', opacity=0.4).encode(
            x='年月',
            y=alt.Y('前年比', axis=alt.Axis(title='前年比 (%)', titleColor='red'))
        )

        # ツールチップの定義
        tooltip = [
            alt.Tooltip('年月', title='年月'),
            alt.Tooltip(selected_column, title='指数', format='.2f'),
            alt.Tooltip('前年比', title='前年比', format='.2f')
        ]

        # 折れ線グラフと棒グラフを重ね合わせ
        combined_chart = alt.layer(
            line_chart.encode(tooltip=tooltip),
            bar_chart.encode(tooltip=tooltip)
        ).resolve_scale(
            y='independent'  # 独立したY軸を右側に表示
        ).properties(
            title=f"CPI（{selected_column}）の推移と前年比"
        )

        st.altair_chart(combined_chart, use_container_width=True)

    else:
        st.info("グラフを表示するにはカテゴリを選択してください。")

if __name__ == "__main__":
    main()
