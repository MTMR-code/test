import streamlit as st
import requests
import csv
from io import StringIO
from datetime import datetime
import jaconv

@st.cache_data
def load_data(url):
    """
    指定されたURLからCSVデータをダウンロードし、ヘッダーとデータを取得する関数。
    """
    try:
        res = requests.get(url, timeout=10)
        res.encoding = 'shift_jis'
        csv_reader = csv.reader(StringIO(res.text))
        
        header = next(csv_reader)
        
        # 2行目から6行目を無視
        for _ in range(5):
            next(csv_reader, None)
        
        data = list(csv_reader)
        return header, data
    except requests.exceptions.RequestException as e:
        st.error(f"データ取得中にエラーが発生しました。URLを確認するか、再度お試しください: {e}")
        return None, None

def main():
    st.title('物価が下落している食材レシピ提案アプリ 🍳')
    st.write("消費者物価指数（CPI）の前年比が下落（マイナス）している食材を基に、お得なレシピを提案します。")

    url = "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000032103842&fileKind=1"
    
    header, data = load_data(url)
    
    if not data:
        st.stop()
    
    # 7行目の年月データを取得し、最も新しいデータを見つける
    if not data or not data[-1]:
        st.error("データ行が見つかりません。")
        st.stop()

    latest_row = data[-1]
    latest_date_str = latest_row[0]

    # 全角数字を半角に変換してからパースを試みる
    try:
        half_width_date_str = jaconv.z2h(latest_date_str, kana=False, ascii=True, digit=True)
        latest_date = datetime.strptime(half_width_date_str, '%Y年%m月')
    except (ValueError, IndexError):
        st.error(f"CSVファイルの1列目の年月データ形式が予期せぬ形式です。例: 2023年01月, 2023年1月")
        st.stop()

    # 1年前のデータ行を検索
    prev_year_date = latest_date.replace(year=latest_date.year - 1)
    prev_year_date_str = prev_year_date.strftime('%Y年%m月')
    
    prev_year_row = None
    for row in data:
        if jaconv.z2h(row[0], kana=False, ascii=True, digit=True) == prev_year_date_str:
            prev_year_row = row
            break
            
    if prev_year_row is None:
        st.error(f"1年前のデータ（{prev_year_date_str}）が見つかりませんでした。")
        st.stop()

    # 物価下落率を計算
    calculated_data = []
    # 総合指数（通常2列目）を除外し、品目ごとのデータを処理
    for i in range(2, len(header)):
        try:
            item = header[i]
            val_latest = float(latest_row[i])
            val_
