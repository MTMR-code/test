import streamlit as st
import pandas as pd

# タイトル
st.title("日本の消費者物価指数（CPI）表示アプリ")

# 説明
st.write("このアプリは、e-Stat（政府統計ポータル）から取得した最新のCPIデータを表示します。")

# 正しいCSVファイルURL（2025年6月時点）
csv_url = "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000032103842&fileKind=1"

# データの読み込み
try:
    df = pd.read_csv(csv_url, encoding="shift_jis")

    # 表示用の整形
    if "年月" in df.columns and "全国" in df.columns:
        df_filtered = df[["年月", "全国"]].dropna()
        df_filtered["年月"] = pd.to_datetime(df_filtered["年月"], format="%Y年%m月", errors="coerce")
        df_filtered = df_filtered.dropna()
        df_filtered = df_filtered.set_index("年月")

        # 表の表示
        st.subheader("CPIデータ（全国）")
        st.dataframe(df_filtered)

        # グラフの表示（Streamlit標準）
        st.subheader("CPI推移グラフ")
        st.line_chart(df_filtered)
    else:
        st.error("CSVファイルに '年月' または '全国' 列が見つかりませんでした。")
except Exception as e:
    st.error(f"データの取得または解析中にエラーが発生しました: {e}")
