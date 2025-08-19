import streamlit as st
import requests
import csv
from io import StringIO

@st.cache_data
def load_data(url):
    """
    指定されたURLからCSVデータをダウンロードし、パースする関数。
    """
    try:
        res = requests.get(url, timeout=10)
        res.encoding = 'shift_jis'
        
        # StringIOを使ってテキストデータをファイルのように読み込む
        csv_reader = csv.reader(StringIO(res.text))
        
        # ヘッダーとデータを分離
        header = next(csv_reader)
        data = list(csv_reader)
        
        return header, data
    except requests.exceptions.RequestException as e:
        st.error(f"データ取得中にエラーが発生しました。URLを確認するか、再度お試しください: {e}")
        return None, None

def main():
    st.title('物価が安定した食材レシピ提案アプリ 🍳')
    st.write("消費者物価指数（CPI）の前年比が小さい、価格の変動が安定している食材を基にレシピを提案します。")

    url = "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000032103842&fileKind=1"
    
    header, data = load_data(url)
    
    if not data:
        st.stop()
    
    # CSVファイルのヘッダー名に合わせてインデックスを特定
    try:
        item_index = header.index('類・品目')
        y2022_index = header.index('令和4年')
        y2023_index = header.index('令和5年')
    except ValueError:
        st.error("CSVファイルのヘッダーに必要な列が見つかりません。データ形式が変更された可能性があります。")
        st.stop()

    # 各品目の前年比を計算
    calculated_data = []
    for row in data:
        try:
            item = row[item_index]
            # 「類」のデータを除外
            if '類' in item and len(item) < 4:
                continue
            
            val_2022 = float(row[y2022_index])
            val_2023 = float(row[y2023_index])
            
            if val_2022 != 0:
                growth_rate = (val_2023 / val_2022 - 1) * 100
                calculated_data.append({'品目': item, '前年比': f'{growth_rate:.2f}%'})
        except (ValueError, IndexError):
            continue

    # 前年比の小さい順にソートして上位10件を取得
    stable_foods = sorted(calculated_data, key=lambda x: float(x['前年比'].strip('%')))[:10]

    st.subheader('価格が安定している食材リスト')
    st.table(stable_foods)

    # ユーザーが食材を選択
    selected_food = st.selectbox(
        'レシピを知りたい食材を選択してください：',
        [food['品目'] for food in stable_foods]
    )

    # ダミーのレシピデータ
    recipes = {
        '豆腐': {'ジャンル': '和食', 'レシピ名': '簡単麻婆豆腐', '材料': '豆腐、ひき肉、長ねぎ、にんにく、しょうが、豆板醤', '作り方': 'ひき
