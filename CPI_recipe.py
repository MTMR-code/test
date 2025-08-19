import streamlit as st
import requests
import csv
from io import StringIO
import re

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
    
    # 動的なヘッダーインデックスの特定
    try:
        item_index = header.index('類・品目')
        
        # '令和'で始まる列を正規表現で検索し、直近2年分を取得
        year_columns = [col for col in header if re.match(r'令和\d+年', col)]
        if len(year_columns) < 2:
            raise ValueError("年を表す列が2つ以上見つかりませんでした。")
        
        # 最新の2年分を抽出
        latest_year_columns = sorted(year_columns, key=lambda x: int(re.search(r'\d+', x).group()), reverse=True)[:2]
        
        y2023_index = header.index(latest_year_columns[0])
        y2022_index = header.index(latest_year_columns[1])
        
    except (ValueError, IndexError):
        st.error("CSVファイルのヘッダーに必要な列が見つかりません。データ形式が大幅に変更された可能性があります。")
        st.stop()
    
    calculated_data = []
    for row in data:
        try:
            item = row[item_index]
            if '類' in item and len(item) < 4:
                continue
            
            val_2022 = float(row[y2022_index])
            val_2023 = float(row[y2023_index])
            
            if val_2022 != 0:
                growth_rate = (val_2023 / val_2022 - 1) * 100
                if growth_rate < 0:
                    calculated_data.append({'品目': item, '前年比': f'{growth_rate:.2f}%'})
        except (ValueError, IndexError):
            continue

    falling_foods = sorted(calculated_data, key=lambda x: float(x['前年比'].strip('%')))[:10]

    st.subheader('物価が下落している食材リスト')
    st.table(falling_foods)

    selected_food = st.selectbox(
        'レシピを知りたい食材を選択してください：',
        [food['品目'] for food in falling_foods]
    )

    recipes = {
        '豆腐': {'ジャンル': '和食', 'レシピ名': '簡単麻婆豆腐', '材料': '豆腐、ひき肉、長ねぎ、にんにく、しょうが、豆板醤', '作り方': 'ひき肉と香味野菜を炒め、調味料と水を加えて煮立てる。豆腐を加えて温める。'},
        '食パン': {'ジャンル': '洋食', 'レシピ名': 'カリカリチーズトースト', '材料': '食パン、とろけるチーズ', '作り方': '食パンにチーズを乗せ、オーブントースターで焼き色がつくまで焼く。'},
        '鶏卵': {'ジャンル': '和食', 'レシピ名': 'だし巻き卵', '材料': '鶏卵、だし汁、砂糖、醤油', '作り方': '卵を溶き、調味料と混ぜて焼く。'},
        '牛乳': {'ジャンル': '洋食', 'レシピ名': '牛乳たっぷりホワイトシチュー', '材料': '牛乳、鶏肉、じゃがいも、にんじん、玉ねぎ', '作り方': '野菜と鶏肉を炒め、水を加えて煮込む。火が通ったら牛乳を加え、シチュールウでとろみをつける。'},
        '豚肉': {'ジャンル': '中華', 'レシピ名': '豚肉とピーマンの細切り炒め', '材料': '豚肉、ピーマン、筍、オイスターソース', '作り方': '細切りにした豚肉と野菜を炒め、調味料で味を調える。'},
        '牛肉（国産品）': {'ジャンル': '和食', 'レシピ名': '牛肉のしぐれ煮', '材料': '牛肉、しょうが、醤油、みりん、砂糖', '作り方': '鍋に調味料を煮立たせ、細切りにした牛肉としょうがを加えて炒り煮にする。'}
    }

    if selected_food in recipes:
        st.subheader(f'「{selected_food}」を使ったレシピ')
        st.write(f"**ジャンル:** {recipes[selected_food]['ジャンル']}")
        st.write(f"**レシピ名:** {recipes[selected_food]['レシピ名']}")
        st.write(f"**材料:** {recipes[selected_food]['材料']}")
        st.write(f"**作り方:** {recipes[selected_food]['作り方']}")
    else:
        st.info("選択された食材のレシピは現在準備中です。別の食材をお試しください。")

if __name__ == '__main__':
    main()
    
