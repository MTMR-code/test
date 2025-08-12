import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# タイトル
st.title("日本の消費者物価指数（CPI）表示アプリ")

# 説明
st.write("このアプリは、e-Stat（政府統計ポータル）から取得した最新のCPIデータを表示します。")

# CPIデータのCSVファイルURL（2020年基準の例）
csv_url = "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000032231210&fileKind=1"

# データの読み込み
try:
    df = pd.read_csv(csv_url, encoding="shift_jis")

    # 表示用の整形
    if "年月" in df.columns and "全国" in df.columns:
        df_filtered = df[["年月", "全国"]].dropna()
        df_filtered["年月"] = pd.to_datetime(df_filtered["年月"], format="%Y年%m月", errors="coerce")
        df_filtered = df_filtered.dropna()

        # 表の表示
        st.subheader("CPIデータ（全国）")
        st.dataframe(df_filtered)

        # グラフの表示
        st.subheader("CPI推移グラフ")
        fig, ax = plt.subplots()
        ax.plot(df_filtered["年月"], df_filtered["全国"], marker="o")
        ax.set_xlabel("年月")
        ax.set_ylabel("CPI（全国）")
        ax.set_title("全国CPIの推移")
        ax.grid(True)
        st.pyplot(fig)
    else:
        st.error("CSVファイルに '年月' または '全国' 列が見つかりませんでした。")
except Exception as e:
    st.error(f"データの取得または解析中にエラーが発生しました: {e}")
