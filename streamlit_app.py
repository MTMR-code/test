import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import requests

# データの取得
@st.cache_data
def get_cpi_data():
    url = "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000032103842&fileKind=1"
    response = requests.get(url)
    csv_data = io.BytesIO(response.content)
    
    # データを読み込み、不要な行をスキップ
    df = pd.read_csv(csv_data, encoding='shift_jis', skiprows=5, header=0)
    
    # 最初の行（新しいヘッダー）を適切に設定
    df.columns = df.iloc[0]
    df = df.drop(0).reset_index(drop=True)
    
    # 'Unnamed: 0'列を削除
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])
    
    return df

# アプリのメイン処理
def main():
    st.title("CPI（消費者物価指数）グラフ表示アプリ")
    
    df = get_cpi_data()

    if df.empty:
        st.error("データの取得に失敗しました。URLを確認してください。")
        return

    # 日付列の整形
    df['年月'] = df['全国']
    df['年月'] = df['年月'].apply(lambda x: f"{str(x)[:4]}年{str(x)[4:6]}月" if pd.notna(x) else None)
    df = df.rename(columns={'全国': 'yyyymm'})

    # グラフ表示用のデータフレームを準備
    plot_df = df.drop(columns=['yyyymm'])
    plot_df = plot_df.set_index('年月')
    
    # カテゴリの選択
    # 選択肢から'年月'列を除外
    columns_to_plot = [col for col in plot_df.columns if col not in ['年月']]
    selected_column = st.selectbox("カテゴリを選択してください", columns_to_plot)

    if selected_column:
        st.header(f"カテゴリ: {selected_column}")
        
        # グラフの描画
        st.subheader("CPI推移グラフ")
        plt.figure(figsize=(12, 6))
        plt.plot(plot_df.index, plot_df[selected_column], marker='o')
        plt.xticks(rotation=45)
        plt.title(f"CPI（{selected_column}）の推移")
        plt.xlabel("年月")
        plt.ylabel("指数")
        plt.grid(True)
        st.pyplot(plt)
    else:
        st.info("グラフ表示にはカテゴリを選択してください。")

if __name__ == "__main__":
    main()
