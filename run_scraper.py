#!/usr/bin/env python3
"""
総務省報道資料スクレイピング実行スクリプト
使用方法: python run_scraper.py
"""

import sys
import os
from soumu_scraper import main

if __name__ == "__main__":
    print("総務省報道資料スクレイピングを開始します...")
    print("=" * 60)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  スクレイピングが中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("スクレイピング処理が完了しました")
