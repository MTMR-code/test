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

        # skiprows=6で正しいヘッダー行を読み込む
        # usecols=[0, 1, ..., 70] のように必要な列のみを指定して読み込む
        # `zmi2020s.csv`のヘッダーは71列目まで日本語のカテゴリ名が続いている
        df = pd.read_csv(csv_data, encoding='shift_jis', skiprows=6, usecols=range(71))

        # 最初の列名が自動で設定されないため、手動で変更
        df.rename(columns={df.columns[0]: 'yyyymm'}, inplace=True)
        
        # 不要な列を削除する (この段階では必要に応じてコメントアウト/調整)
        # 例えば、列名にNaNが含まれる列や、特定の文字列を含む列を削除
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
    # カテゴリのリストから、数値以外の要素（yyyymmなど）を除外
    columns_to_plot = [col for col in plot_df.columns if pd.api.types.is_numeric_dtype(plot_df[col])]
    selected_column = st.selectbox("カテゴリを選択してください", columns_to_plot)

    if selected_column:
        st.subheader(f"CPIの推移: {selected_column}")
        
        # グラフ描画のためのDataFrameを準備
        chart_df = plot_df[[selected_column]].reset_index()
        
        # Altairでグラフを描画
        chart = alt.Chart(chart_df).mark_line(point=True).encode(
            x=alt.X('年月', axis=alt.Axis(title='年月')),
            y=alt.Y(selected_column, axis=alt.Axis(title='指数')),
            tooltip=['年月', alt.Tooltip(selected_column, title=selected_column)]
        ).interactive()
        
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("グラフを表示するにはカテゴリを選択してください。")

if __name__ == "__main__":
    main()
