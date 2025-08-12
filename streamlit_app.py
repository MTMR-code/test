import streamlit as st
import pandas as pd

# タイトル
st.title("日本の消費者物価指数（CPI）表示アプリ")

# CSVファイルURL（e-Stat）
csv_url = "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000032103842&fileKind=1"

# データの読み込み
try:
    df = pd.read_csv(csv_url, encoding="shift_jis")

    # 先頭表示
    st.subheader("取得したデータの先頭5行")
    st.dataframe(df.head())

    # 列名表示
    st.subheader("列名一覧")
    st.write(df.columns.tolist())

    # 日付列とCPI列の指定
    date_column = df.columns[0]  # 例: "類・品目"
    value_column = "総合"

    if date_column in df.columns and value_column in df.columns:
        df_plot = df[[date_column, value_column]].dropna()
        df_plot[date_column] = pd.to_datetime(df_plot[date_column], format="%Y年%m月", errors="coerce")
        df_plot = df_plot.dropna()
        df_plot = df_plot.set_index(date_column)

        # グラフ表示
        st.subheader("CPI（総合）の推移")
        st.line_chart(df_plot)
    else:
        st.error(f"列 '{date_column}' または '{value_column}' が見つかりませんでした。")
except Exception as e:
    st.error(f"データの取得または解析中にエラーが発生しました: {e}")
