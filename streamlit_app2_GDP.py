import streamlit as st
import pandas as pd
import io
import requests
import altair as alt
import re

# ヘッダー処理関数
def process_gdp_header(csv_data, skiprows, nrows):
    """
    CSVデータのヘッダーを読み込み、列名を生成する関数
    """
    header_df = pd.read_csv(io.BytesIO(csv_data), encoding='shift_jis', header=None, skiprows=skiprows, nrows=nrows, dtype=str)
    new_columns = []
    for col in header_df.columns:
        first_non_na = header_df[col].dropna()
        if not first_non_na.empty:
            new_columns.append(first_non_na.iloc[0].strip())
        else:
            new_columns.append(f'Unnamed_Col_{col}')
    return new_columns

# データの取得とキャッシュ
@st.cache_data
def get_gdp_data():
    """内閣府からGDPの実額と前期比のCSVデータを取得し、整形する関数"""
    url_gaku = "https://www.esri.cao.go.jp/jp/sna/data/data_list/sokuhou/files/2025/qe251_2/tables/gaku-jk2512.csv"
    url_ritu = "https://www.esri.cao.go.jp/jp/sna/data/data_list/sokuhou/files/2025/qe251_2/tables/ritu-jk2512.csv"

    gaku_df = pd.DataFrame()
    ritu_df = pd.DataFrame()

    try:
        # 実額データの取得と整形
        response_gaku = requests.get(url_gaku)
        response_gaku.raise_for_status()
        csv_data_gaku = response_gaku.content
        new_columns_gaku = process_gdp_header(csv_data_gaku, skiprows=2, nrows=4)
        gaku_df = pd.read_csv(io.BytesIO(csv_data_gaku), encoding='shift_jis', header=None, skiprows=8)
        gaku_df.columns = new_columns_gaku
        gaku_df = gaku_df.set_index(gaku_df.columns[0])
        gaku_df.index.name = '四半期'
        gaku_df = gaku_df.dropna(axis=1, how='all')
        
        # 数値変換前にカンマを削除
        gaku_df = gaku_df.replace({',': ''}, regex=True)
        gaku_df = gaku_df.apply(pd.to_numeric, errors='coerce')

        # 前期比データの取得と整形
        response_ritu = requests.get(url_ritu)
        response_ritu.raise_for_status()
        csv_data_ritu = response_ritu.content
        new_columns_ritu = process_gdp_header(csv_data_ritu, skiprows=2, nrows=4)
        ritu_df = pd.read_csv(io.BytesIO(csv_data_ritu), encoding='shift_jis', header=None, skiprows=8)
        ritu_df.columns = new_columns_ritu
        ritu_df = ritu_df.set_index(ritu_df.columns[0])
        ritu_df.index.name = '四半期'
        ritu_df = ritu_df.dropna(axis=1, how='all')
        
        # 数値変換前にカンマを削除
        ritu_df = ritu_df.replace({',': ''}, regex=True)
        ritu_df = ritu_df.apply(pd.to_numeric, errors='coerce')

        return gaku_df, ritu_df

    except requests.exceptions.RequestException as e:
        st.error(f"データの取得中にエラーが発生しました: {e}")
        return pd.DataFrame(), pd.DataFrame()

# アプリのメイン処理
def main():
    st.title("GDP（国内総生産）グラフ表示アプリ")
    
    gaku_df, ritu_df = get_gdp_data()
    
    if st.checkbox("Show raw dataframes for debugging"):
        st.subheader("Gaku DataFrame (実額)")
        st.dataframe(gaku_df)
        st.subheader("Ritu DataFrame (前期比)")
        st.dataframe(ritu_df)

    if gaku_df.empty or ritu_df.empty:
        st.warning("データを取得できませんでした。URLを確認してください。")
        return

    # 表示方法の選択
    view_type = st.radio(
        "表示方法を選択してください",
        ("実額", "前期比")
    )
    
    # 選択された表示方法に応じてデータフレームを切り替え
    if view_type == "実額":
        df = gaku_df.copy()
        y_axis_title = '実額 (10億円)'
        title_suffix = 'の実額推移'
    else: # 前期比
        df = ritu_df.copy()
        y_axis_title = '前期比 (%)'
        title_suffix = 'の前期比推移'

    # インデックス（四半期）を整形
    df.reset_index(inplace=True)
    
    # 四半期列を文字列に変換し、整形
    df['四半期'] = df['四半期'].astype(str).str.strip().str.replace('.', '')

    # 年を補足するロジックを修正
    current_year = None
    new_quarter_list = []

    for i, row in df.iterrows():
        quarter_str = row['四半期']
        match = re.search(r'(\d{4})/(.*)', quarter_str)
        
        if match:
            current_year = match.group(1)
            quarter_text = match.group(2).strip()
            new_quarter_list.append(f"{current_year}年{quarter_text}月期")
        elif current_year:
            quarter_text = quarter_str.strip()
            new_quarter_list.append(f"{current_year}年{quarter_text}月期")
        else:
            new_quarter_list.append(quarter_str)
            
    df['四半期'] = new_quarter_list
            
    # グラフ表示用のデータフレームを準備
    plot_df = df.set_index('四半期')

    # カテゴリの選択
    columns_to_plot = plot_df.columns.tolist()
    selected_column = st.selectbox("カテゴリを選択してください", columns_to_plot)

    if selected_column:
        st.subheader(f"GDPの推移: {selected_column}")
        
        # グラフ描画のためのDataFrameを準備
        chart_df = plot_df[[selected_column]].reset_index()

        # Altairで折れ線グラフを作成
        line_chart = alt.Chart(chart_df).mark_line(point=True).encode(
            x=alt.X('四半期', axis=alt.Axis(title='四半期', labelAngle=-45)),
            y=alt.Y(selected_column, axis=alt.Axis(title=y_axis_title, titleColor='blue')),
            tooltip=[
                alt.Tooltip('四半期', title='四半期'),
                alt.Tooltip(selected_column, title=y_axis_title, format='.2f')
            ]
        ).properties(
            title=f"GDP（{selected_column}）{title_suffix}"
        )
        
        # 前期比の場合のみゼロラインを追加
        if view_type == "前期比":
            zero_line = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color='red', strokeDash=[5, 5]).encode(y='y')
            st.altair_chart(line_chart + zero_line, use_container_width=True)
        else:
            st.altair_chart(line_chart, use_container_width=True)

    else:
        st.info("グラフを表示するにはカテゴリを選択してください。")

if __name__ == "__main__":
    main()
