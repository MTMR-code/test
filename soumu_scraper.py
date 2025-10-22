import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime, date
import time
import urllib.parse
from dateutil.relativedelta import relativedelta

def generate_date_urls(start_year=2009, end_year=None):
    """
    2009年1月から指定年まで（または現在まで）のURLを生成する
    """
    if end_year is None:
        end_year = datetime.now().year
    
    urls = []
    current_date = date(start_year, 1, 1)
    end_date = date(end_year, 12, 31)
    
    while current_date <= end_date:
        # URL形式: YYMMm.html (例: 2501m.html = 2025年1月)
        # ただし2023年10月のみ2310.html（mなし）
        year_short = str(current_date.year)[2:]  # 下2桁
        month = f"{current_date.month:02d}"
        
        # 2023年10月の特別処理
        if current_date.year == 2023 and current_date.month == 10:
            url_suffix = f"{year_short}{month}.html"
        else:
            url_suffix = f"{year_short}{month}m.html"
        
        url = f"https://www.soumu.go.jp/menu_news/s-news/{url_suffix}"
        
        urls.append({
            'url': url,
            'year': current_date.year,
            'month': current_date.month,
            'period': f"{current_date.year}年{current_date.month}月"
        })
        
        # 次の月へ
        current_date = current_date + relativedelta(months=1)
    
    return urls

def scrape_soumu_press_releases(url, period_info=None):
    """
    総務省の報道資料一覧ページをスクレイピングする
    """
    if period_info:
        print(f"スクレイピング開始: {period_info['period']} ({url})")
    else:
        print(f"スクレイピング開始: {url}")
    
    try:
        # ページの取得
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 文字エンコーディングを自動検出
        if response.encoding == 'ISO-8859-1':
            # 総務省のページはShift_JISの可能性が高い
            response.encoding = 'shift_jis'
        elif response.encoding == 'utf-8':
            # UTF-8の場合はそのまま
            pass
        else:
            # その他の場合はShift_JISを試す
            response.encoding = 'shift_jis'
        
        # HTMLの解析
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 報道資料のテーブルを探す
        press_releases = []
        
        # テーブル内の行を取得
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')
            
            for row in rows[1:]:  # ヘッダー行をスキップ
                cells = row.find_all('td')
                if len(cells) >= 3:
                    # 日付の抽出
                    date_cell = cells[0].get_text(strip=True)
                    
                    # 内容の抽出（リンクテキスト）
                    content_cell = cells[1]
                    content_link = content_cell.find('a')
                    if content_link:
                        content = content_link.get_text(strip=True)
                        # リンクURLも取得
                        link_url = content_link.get('href', '')
                        if link_url and not link_url.startswith('http'):
                            link_url = urllib.parse.urljoin(url, link_url)
                    else:
                        content = content_cell.get_text(strip=True)
                        link_url = ''
                    
                    # 部局の抽出
                    department = cells[2].get_text(strip=True)
                    
                    # データの前処理（文字化け対策）
                    def clean_text(text):
                        if not text:
                            return text
                        # 文字列を正規化
                        text = str(text).strip()
                        # 不要な空白文字を除去
                        text = ' '.join(text.split())
                        return text
                    
                    # データの追加
                    press_releases.append({
                        '発表日': clean_text(date_cell),
                        '内容': clean_text(content),
                        '部局': clean_text(department),
                        'リンクURL': clean_text(link_url),
                        '対象期間': clean_text(period_info['period'] if period_info else '')
                    })
        
        print(f"取得した報道資料数: {len(press_releases)}件")
        
        # DataFrameに変換
        df = pd.DataFrame(press_releases)
        
        if not df.empty:
            # 日付の正規化
            df['発表日'] = df['発表日'].apply(normalize_date)
            
            return df
        else:
            print("報道資料が見つかりませんでした")
            return pd.DataFrame()
            
    except requests.RequestException as e:
        print(f"HTTPリクエストエラー: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"スクレイピングエラー: {e}")
        return pd.DataFrame()

def scrape_all_months(start_year=2009, end_year=None):
    """
    指定期間の全ての月の報道資料をスクレイピングする
    """
    print(f"=== 総務省報道資料一括スクレイピング ===")
    print(f"期間: {start_year}年1月 ～ {end_year or datetime.now().year}年{datetime.now().month}月")
    print("-" * 60)
    
    # URLリストを生成
    urls = generate_date_urls(start_year, end_year)
    print(f"対象URL数: {len(urls)}件")
    
    all_data = []
    successful_count = 0
    failed_count = 0
    
    for i, url_info in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] 処理中...")
        
        # スクレイピング実行
        df = scrape_soumu_press_releases(url_info['url'], url_info)
        
        if not df.empty:
            all_data.append(df)
            successful_count += 1
            print(f"✅ 成功: {len(df)}件取得")
        else:
            failed_count += 1
            print(f"❌ 失敗: データなし")
        
        # リクエスト間隔を空ける（サーバー負荷軽減）
        time.sleep(0.1)
    
    # 全データを結合
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        # データの並び替え（日付順）
        combined_df = combined_df.sort_values('発表日', ascending=False)
        
        print(f"\n=== スクレイピング結果 ===")
        print(f"成功: {successful_count}件")
        print(f"失敗: {failed_count}件")
        print(f"総取得件数: {len(combined_df)}件")
        
        return combined_df
    else:
        print("❌ データが取得できませんでした")
        return pd.DataFrame()

def normalize_date(date_str):
    """
    日付文字列を正規化する
    """
    try:
        # 日付の形式を統一
        if '年' in date_str and '月' in date_str and '日' in date_str:
            # 既に正しい形式の場合
            return date_str
        else:
            # その他の形式の場合はそのまま返す
            return date_str
    except:
        return date_str

def save_to_csv(df, filename):
    """
    DataFrameをCSVファイルに保存
    - 文字化けを完全に防ぐための複数エンコーディング対応
    """
    try:
        # データの前処理（文字化け対策強化）
        df_clean = df.copy()
        for col in df_clean.columns:
            if df_clean[col].dtype == 'object':
                # 文字列の正規化
                df_clean[col] = df_clean[col].astype(str)
                # 改行文字を除去
                df_clean[col] = df_clean[col].str.replace('\n', ' ').str.replace('\r', ' ')
                # タブ文字を除去
                df_clean[col] = df_clean[col].str.replace('\t', ' ')
                # 連続する空白を単一の空白に
                df_clean[col] = df_clean[col].str.replace(r'\s+', ' ', regex=True)
                # 前後の空白を除去
                df_clean[col] = df_clean[col].str.strip()

        # 1. UTF-8 with BOM（Mac/最新Excel向け）
        utf8_path = filename
        df_clean.to_csv(utf8_path, index=False, encoding='utf-8-sig')
        print(f"CSVファイルを保存しました(UTF-8 BOM): {utf8_path}")

        # 2. Shift_JIS（Windows Excel用 - 最も確実）
        if utf8_path.lower().endswith('.csv'):
            shift_jis_path = utf8_path[:-4] + '_shift_jis.csv'
        else:
            shift_jis_path = utf8_path + '_shift_jis.csv'
        
        # Shift_JISで保存（エラーは無視）
        df_clean.to_csv(shift_jis_path, index=False, encoding='shift_jis', errors='ignore')
        print(f"CSVファイルを保存しました(Shift_JIS): {shift_jis_path}")

        # 3. CP932（Windows Excel用）
        if utf8_path.lower().endswith('.csv'):
            cp932_path = utf8_path[:-4] + '_cp932.csv'
        else:
            cp932_path = utf8_path + '_cp932.csv'
        df_clean.to_csv(cp932_path, index=False, encoding='cp932', errors='ignore')
        print(f"CSVファイルを保存しました(CP932): {cp932_path}")

        # 4. Excel専用（手動でBOM付きShift_JIS）
        if utf8_path.lower().endswith('.csv'):
            excel_path = utf8_path[:-4] + '_excel.csv'
        else:
            excel_path = utf8_path + '_excel.csv'
        
        # 手動でBOM付きShift_JISで保存
        with open(excel_path, 'w', encoding='utf-8-sig', newline='') as f:
            # まずUTF-8で書き込み
            df_clean.to_csv(f, index=False, encoding='utf-8')
        
        # ファイルを読み込んでShift_JISで再保存
        with open(excel_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(excel_path, 'w', encoding='shift_jis', newline='') as f:
            f.write(content)
        
        print(f"CSVファイルを保存しました(Excel専用): {excel_path}")

        # 5. テキストファイル（確実に読める形式）
        if utf8_path.lower().endswith('.csv'):
            txt_path = utf8_path[:-4] + '_text.txt'
        else:
            txt_path = utf8_path + '_text.txt'
        
        with open(txt_path, 'w', encoding='utf-8', newline='') as f:
            f.write("発表日\t内容\t部局\tリンクURL\t対象期間\n")
            for _, row in df_clean.iterrows():
                f.write(f"{row['発表日']}\t{row['内容']}\t{row['部局']}\t{row['リンクURL']}\t{row['対象期間']}\n")
        print(f"テキストファイルを保存しました(TSV形式): {txt_path}")

        print("\n📁 保存されたファイル（文字化け対策済み）:")
        print(f"  - {excel_path} (Excel専用 - 最も推奨)")
        print(f"  - {shift_jis_path} (Shift_JIS - Windows Excel用)")
        print(f"  - {cp932_path} (CP932 - Windows Excel用)")
        print(f"  - {utf8_path} (UTF-8 BOM - Mac/Googleスプレッドシート用)")
        print(f"  - {txt_path} (テキスト形式 - 確実に読める)")

        return True
    except Exception as e:
        print(f"CSV保存エラー: {e}")
        return False

def main():
    """
    メイン処理
    """
    print("=== 総務省報道資料一括スクレイピング ===")
    print("2009年1月から現在まで全ての月のデータを取得します")
    print("-" * 60)
    
    # 一括スクレイピング実行
    df = scrape_all_months(start_year=2009)
    
    if not df.empty:
        # 結果の表示
        print("\n=== 詳細統計 ===")
        print(f"総取得件数: {len(df)}件")
        
        print("\n部局別集計:")
        dept_counts = df['部局'].value_counts()
        for dept, count in dept_counts.head(10).items():  # 上位10件のみ表示
            print(f"  {dept}: {count}件")
        
        print("\n年別集計:")
        df['年'] = df['発表日'].str.extract(r'(\d{4})年')
        year_counts = df['年'].value_counts().sort_index()
        for year, count in year_counts.items():
            print(f"  {year}年: {count}件")
        
        print("\n月別集計（直近12ヶ月）:")
        df['月'] = df['発表日'].str.extract(r'(\d{1,2})月')
        recent_data = df.head(100)  # 直近100件で月別集計
        month_counts = recent_data['月'].value_counts().sort_index()
        for month, count in month_counts.items():
            print(f"  {month}月: {count}件")
        
        # CSVファイルに保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"soumu_press_releases_all_{timestamp}.csv"
        
        if save_to_csv(df, filename):
            print(f"\n✅ スクレイピング完了！")
            print(f"📁 保存ファイル: {filename}")
            print(f"📊 データ件数: {len(df)}件")
            print(f"📅 期間: 2009年1月 ～ 現在")
            
            # サンプルデータの表示
            print("\n=== サンプルデータ（最新5件）===")
            print(df.head().to_string(index=False))
        else:
            print("❌ CSVファイルの保存に失敗しました")
    else:
        print("❌ スクレイピングに失敗しました")

def main_single_month():
    """
    単一月のスクレイピング（従来の機能）
    """
    url = "https://www.soumu.go.jp/menu_news/s-news/2501m.html"
    
    print("=== 総務省報道資料スクレイピング（単一月） ===")
    print(f"対象URL: {url}")
    print("-" * 50)
    
    df = scrape_soumu_press_releases(url)
    
    if not df.empty:
        print(f"\n取得件数: {len(df)}件")
        
        # CSVファイルに保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"soumu_press_releases_single_{timestamp}.csv"
        
        if save_to_csv(df, filename):
            print(f"✅ 保存完了: {filename}")
        else:
            print("❌ 保存失敗")
    else:
        print("❌ データ取得失敗")

if __name__ == "__main__":
    main()
