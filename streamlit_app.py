import streamlit as st
import pandas as pd

st.title("CPIデータの列名確認アプリ")

csv_url = "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000032103842&fileKind=1"

try:
    df = pd.read_csv(csv_url, encoding="shift_jis")
    st.write("取得したデータの先頭5行:")
    st.dataframe(df.head())

    st.write("列名一覧:")
    st.write(df.columns.tolist())
except Exception as e:
    st.error(f"データ取得エラー: {e}")
