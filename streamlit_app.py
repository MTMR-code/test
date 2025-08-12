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

        # データを読み込み、不要な行をスキップ
        df = pd.read_csv(csv_data, encoding='shift_jis', skiprows=5, header=0)

        # 最初の行（新しいヘッダー）を適切に設定
        df.columns = df.iloc[0]
        df = df.drop(0).reset_index(drop=True)

        # 列名のない最初の列（yyyymm）に'yyyymm'という名前を付ける
        df.rename(columns={df.columns[0]: 'yyyymm'}, inplace=True)
            
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
    columns_to_plot = [col for col in plot_df.columns if col not in ['yyyymm']]
    selected_column = st.selectbox("カテゴリを選択してください", columns_to_plot)

    if selected_column:
        st.subheader(f"CPIの推移: {selected_column}")
        
        # グラフ描画のためのDataFrameを準備
        chart_df = plot_df[[selected_column]].reset_index()
        
        # Altairでグラフを描画
        chart = alt.Chart(chart_df).mark_line(point=True).encode(
            x=alt.X('年月', axis=alt.Axis(title='年月')),
            y=alt.Y(selected_column, axis=alt.Axis(title='指数', type='quantitative')),
            tooltip=['年月', alt.Tooltip(selected_column, title=selected_column)]
        ).interactive()
        
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("グラフを表示するにはカテゴリを選択してください。")

if __name__ == "__main__":
    main()
