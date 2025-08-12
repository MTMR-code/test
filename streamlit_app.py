import streamlit as st
import pandas as pd

# タイトル
st.title("日本の消費者物価指数（CPI）表示アプリ")

# CSVファイルURL（e-Stat）
csv_url = "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000032103842&fileKind=1"

# データの読み込み
try:
    # 最初の行を列名として使用
    df = pd.read_csv(csv_url, encoding="shift_jis", skiprows=6, header=None)
    df.columns = df.iloc[0]
    df = df.drop(index=0).reset_index(drop=True)

    # 転置して年月をインデックスに
    df_transposed = df.T
    df_transposed.columns = df_transposed.iloc[0]
    df_transposed = df_transposed.drop(index=df_transposed.index[0])
    df_transposed.index.name = "年月"

    # 年月を datetime に変換
    df_transposed = df_transposed.reset_index()
    df_transposed["年月"] = pd.to_datetime(df_transposed["年月"], format="%Y%m", errors="coerce")
    df_transposed = df_transposed.dropna(subset=["年月"]).set_index("年月")

    # 総合列を数値に変換
    if "総合" in df_transposed.columns:
        df_transposed["総合"] = pd.to_numeric(df_transposed["総合"], errors="coerce")
        df_transposed = df_transposed.dropna(subset=["総合"])

        # グラフ表示
        st.subheader("CPI（総合）の推移")
        st.line_chart(df_transposed["総合"])
    else:
        st.error("列 '総合' が見つかりませんでした。")
except Exception as e:
    st.error(f"データの取得または解析中にエラーが発生しました: {e}")
