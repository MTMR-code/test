import streamlit as st
import pandas as pd

# タイトル
st.title("日本の消費者物価指数（CPI）表示アプリ")

# CSVファイルURL（e-Stat）
csv_url = "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000032103842&fileKind=1"

# データの読み込み
try:
    df = pd.read_csv(csv_url, encoding="shift_jis", skiprows=6)

    # 列名表示
    st.subheader("列名一覧")
    st.write(df.columns.tolist())

    # 転置して年月をインデックスに
    if df.columns[0] == "類・品目":
        df_transposed = df.set_index("類・品目").T
        df_transposed.index.name = "年月"
        df_transposed.reset_index(inplace=True)

        # 年月を datetime に変換
        df_transposed["年月"] = pd.to_datetime(df_transposed["年月"], format="%Y年%m月", errors="coerce")
        df_transposed = df_transposed.dropna(subset=["年月"])

        # 総合列を数値に変換
        df_transposed["総合"] = pd.to_numeric(df_transposed["総合"], errors="coerce")
        df_transposed = df_transposed.dropna(subset=["総合"])

        df_transposed = df_transposed.set_index("年月")

        # グラフ表示
        st.subheader("CPI（総合）の推移")
        st.line_chart(df_transposed["総合"])
    else:
        st.error("最初の列が '類・品目' ではありません。CSV構造が変更された可能性があります。")
except Exception as e:
    st.error(f"データの取得または解析中にエラーが発生しました: {e}")
