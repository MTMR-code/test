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
