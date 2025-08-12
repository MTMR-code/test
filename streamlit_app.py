import streamlit as st
import pandas as pd

# タイトル
st.title("日本の消費者物価指数（CPI）表示アプリ")

# e-StatのCSVファイルURL
csv_url = "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000032103842&fileKind=1"

try:
    # 1行目をヘッダー、2〜6行目をスキップ
    df = pd.read_csv(csv_url, encoding="shift_jis", skiprows=6, header=None)
    df.columns = df.iloc[0]  # 1行目を列名に
    df = df.drop(index=0).reset_index(drop=True)

    # 1列目（年月）を datetime に変換し、表示用に整形
    date_column = df.columns[0]
    df[date_column] = pd.to_datetime(df[date_column], format="%Y%m", errors="coerce")
    df = df.dropna(subset=[date_column])
    df["表示年月"] = df[date_column].dt.strftime("%Y年%m月")

    # 表示
    st.subheader("CPIデータ（年月変換済み）")
    st.dataframe(df[["表示年月"] + df.columns[1:].tolist()])

except Exception as e:
    st.error(f"データの取得または解析中にエラーが発生しました: {e}")
