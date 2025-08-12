import streamlit as st
import pandas as pd
import io
import requests
import altair as alt

# データの取得とキャッシュ
@st.cache_data
def get_gdp_data():
    """内閣府からGDPのCSVデータを取得し、整形する関数"""
    url = "https://www.esri.cao.go.jp/jp/sna/data/data_list/sokuhou/files/2025/qe251_2/tables/gaku-jk2512.csv"

    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTPエラーがあれば例外を発生させる
        csv_data = io.BytesIO(response.content)

        # ファイルを読み込む
        # 8行目からヘッダーが始まることを考慮して、skiprowsとheaderを調整
        df = pd.read_csv(csv_data, encoding='shift_jis', header=8, index_col=0)

        # 不要な行・列を削除
        df = df.dropna(how='all')
        df = df.dropna(axis=1, how='all')

        # 最初の列をインデックスとして設定し、名前を'四半期'に変更
        df.index.name = '四半期'

        # 数値データに変換できない値をNaNに変換し、数値型に変換
        df = df.apply(pd.to_numeric, errors='coerce')
        
        return df

    except requests.exceptions.RequestException as e:
        st.error(f"データの取得中にエラーが発生しました: {e}")
        return pd.DataFrame()

# アプリのメイン処理
def main():
    st.title("GDP（国内総生産）グラフ表示アプリ")
    st.markdown("内閣府のGDP統計データ（速報値）を基に、主要項目の推移を可視化します。")
    st.markdown("※本データは実質季節調整系列（前期比）です。")

    df = get_gdp_data()

    if df.empty:
        st.warning("データを取得できませんでした。URLを確認してください。")
        return

    # インデックス（四半期）を整形
    df.reset_index(inplace=True)
    df['四半期'] = df['四半期'].str.replace('/', ' ').str.strip()

    # グラフ表示用のデータフレームを準備
    plot_df = df.set_index('四半期')

    # カテゴリの選択
    # 修正箇所: フィルタリングせずにすべての列を表示
    columns_to_plot = plot_df.columns.tolist()
    selected_column = st.selectbox("カテゴリを選択してください", columns_to_plot)

    if selected_column:
        st.subheader(f"GDPの推移: {selected_column}")
        st.markdown("※グラフは前期比（%）で表示されます。")

        # グラフ描画のためのDataFrameを準備
        chart_df = plot_df[[selected_column]].reset_index()

        # Altairで折れ線グラフを作成
        line_chart = alt.Chart(chart_df).mark_line(point=True).encode(
            x=alt.X('四半期', axis=alt.Axis(title='四半期', labelAngle=-45)),
            y=alt.Y(selected_column, axis=alt.Axis(title='前期比 (%)', titleColor='blue')),
            tooltip=[
                alt.Tooltip('四半期', title='四半期'),
                alt.Tooltip(selected_column, title='前期比 (%)', format='.2f')
            ]
        ).properties(
            title=f"GDP（{selected_column}）の前期比推移"
        )
        
        # ゼロラインを追加
        zero_line = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color='red', strokeDash=[5, 5]).encode(y='y')

        st.altair_chart(line_chart + zero_line, use_container_width=True)

    else:
        st.info("グラフを表示するにはカテゴリを選択してください。")

if __name__ == "__main__":
    main()
