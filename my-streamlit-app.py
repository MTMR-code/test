import streamlit as st
import pandas as pd
import io

st.title("📊 総務省報道資料分析アプリ")
st.write("CSVファイルをアップロードして報道資料を分析できます")

# CSVファイルのアップロード
uploaded_file = st.file_uploader(
    "CSVファイルをアップロードしてください",
    type=['csv'],
    help="総務省報道資料のCSVファイルをアップロードしてください"
)

if uploaded_file is not None:
    try:
        # CSVファイルを読み込み
        df = pd.read_csv(uploaded_file, encoding='utf-8')
        
        st.success("✅ CSVファイルが正常に読み込まれました！")
        
        # データの基本情報を表示
        st.subheader("📈 データ概要")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("総件数", len(df))
        
        with col2:
            st.metric("部局数", df['部局'].nunique())
        
        with col3:
            st.metric("期間", f"{df['発表日'].min()} ～ {df['発表日'].max()}")
        
        # 検索機能
        st.subheader("🔍 検索機能")
        search_term = st.text_input("キーワードで検索", placeholder="例: 電波法、放送、統計")
        
        if search_term:
            # 内容と部局で検索
            mask = (df['内容'].str.contains(search_term, case=False, na=False) | 
                   df['部局'].str.contains(search_term, case=False, na=False))
            filtered_df = df[mask]
            st.write(f"検索結果: {len(filtered_df)}件")
        else:
            filtered_df = df
        
        # データテーブル表示
        st.subheader("📋 報道資料一覧")
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )
        
        # 部局別集計
        st.subheader("📊 部局別集計")
        dept_counts = df['部局'].value_counts()
        st.bar_chart(dept_counts)
        
        # 日付別集計
        st.subheader("📅 日付別集計")
        df['発表日'] = pd.to_datetime(df['発表日'])
        daily_counts = df.groupby(df['発表日'].dt.date).size()
        st.line_chart(daily_counts)
        
        # ダウンロード機能
        st.subheader("💾 データダウンロード")
        csv_data = filtered_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="検索結果をCSVでダウンロード",
            data=csv_data,
            file_name=f"filtered_press_releases_{search_term or 'all'}.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"❌ ファイルの読み込み中にエラーが発生しました: {str(e)}")
        st.write("CSVファイルの形式を確認してください。以下の列が必要です：")
        st.write("- 発表日")
        st.write("- 内容") 
        st.write("- 部局")

else:
    st.info("👆 CSVファイルをアップロードしてください")
    st.write("### 使用例")
    st.write("1. 総務省報道資料のCSVファイルをアップロード")
    st.write("2. キーワードで検索")
    st.write("3. 部局別・日付別の集計を確認")
    st.write("4. 検索結果をダウンロード")
    