#!/usr/bin/env python3
"""
総務省報道資料一括スクレイピング実行スクリプト
2009年1月から現在まで全ての月のデータを取得します
使用方法: python run_batch_scraper.py
"""

import sys
import os
from soumu_scraper import main, main_single_month

def show_menu():
    """メニューを表示"""
    print("=" * 60)
    print("総務省報道資料スクレイピングツール")
    print("=" * 60)
    print("1. 一括スクレイピング（2009年1月～現在）")
    print("2. 単一月スクレイピング（2025年1月のみ）")
    print("3. 終了")
    print("-" * 60)

if __name__ == "__main__":
    while True:
        show_menu()
        choice = input("選択してください (1-3): ").strip()
        
        if choice == "1":
            print("\n一括スクレイピングを開始します...")
            print("⚠️  注意: この処理には時間がかかります（約10-20分）")
            confirm = input("続行しますか？ (y/N): ").strip().lower()
            
            if confirm in ['y', 'yes']:
                try:
                    main()
                except KeyboardInterrupt:
                    print("\n\n⚠️  スクレイピングが中断されました")
                except Exception as e:
                    print(f"\n❌ エラーが発生しました: {e}")
            else:
                print("キャンセルしました")
                
        elif choice == "2":
            print("\n単一月スクレイピングを開始します...")
            try:
                main_single_month()
            except KeyboardInterrupt:
                print("\n\n⚠️  スクレイピングが中断されました")
            except Exception as e:
                print(f"\n❌ エラーが発生しました: {e}")
                
        elif choice == "3":
            print("終了します")
            break
            
        else:
            print("無効な選択です。1-3を選択してください。")
        
        input("\nEnterキーを押して続行...")
        print("\n" + "=" * 60)
