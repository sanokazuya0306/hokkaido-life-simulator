#!/usr/bin/env python3
"""
セットアップ確認スクリプト
必要なライブラリとデータファイルの存在を確認します
"""

import sys
from pathlib import Path

def check_python_version():
    """Pythonバージョンの確認"""
    version = sys.version_info
    print(f"🐍 Python バージョン: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8以上が必要です")
        return False
    else:
        print("✅ Pythonバージョン: OK")
        return True

def check_libraries():
    """必要なライブラリの確認"""
    print("\n📚 ライブラリの確認:")
    
    libraries = {
        "pandas": "pandas",
        "requests": "requests",
        "openpyxl": "openpyxl",
        "streamlit": "streamlit",
        "plotly": "plotly"
    }
    
    all_ok = True
    for lib_name, import_name in libraries.items():
        try:
            __import__(import_name)
            print(f"  ✅ {lib_name}: インストール済み")
        except ImportError:
            print(f"  ❌ {lib_name}: 未インストール")
            all_ok = False
    
    return all_ok

def check_data_files():
    """データファイルの確認"""
    print("\n📁 データファイルの確認:")
    
    script_dir = Path(__file__).parent
    data_dir = script_dir / "data"
    
    if not data_dir.exists():
        print("  ❌ dataディレクトリが見つかりません")
        return False
    
    required_files = [
        "birth_by_city.csv",
        "high_school_rate.csv",
        "university_rate.csv",
        "hokkaido_university_destinations.csv",
        "workers_by_industry.csv",
        "retirement_age.csv",
        "death_by_age.csv",
        "death_by_cause.csv"
    ]
    
    all_ok = True
    for filename in required_files:
        filepath = data_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"  ✅ {filename} ({size:,} bytes)")
        else:
            print(f"  ⚠️  {filename}: 見つかりません（サンプルデータを使用します）")
            # データファイルがなくてもサンプルデータで動作するのでエラーにはしない
    
    return all_ok

def check_simulator():
    """シミュレーターの動作確認"""
    print("\n🧪 シミュレーターの動作確認:")
    
    try:
        from hokkaido_life_simulator import HokkaidoLifeSimulator
        print("  ✅ モジュールのインポート: OK")
        
        simulator = HokkaidoLifeSimulator()
        print("  ✅ シミュレーターの初期化: OK")
        
        life = simulator.generate_life()
        print("  ✅ 人生の生成: OK")
        
        formatted = simulator.format_life(life)
        print("  ✅ 人生のフォーマット: OK")
        
        return True
    except Exception as e:
        print(f"  ❌ エラー: {e}")
        return False

def main():
    print("=" * 60)
    print("🌏 北海道人生シミュレーター - セットアップ確認")
    print("=" * 60)
    print()
    
    results = {
        "Python": check_python_version(),
        "ライブラリ": check_libraries(),
        "データファイル": check_data_files(),
        "シミュレーター": check_simulator()
    }
    
    print("\n" + "=" * 60)
    print("📊 確認結果サマリー")
    print("=" * 60)
    
    for item, result in results.items():
        status = "✅ OK" if result else "❌ NG"
        print(f"{item}: {status}")
    
    print()
    
    if all(results.values()):
        print("🎉 すべての確認が完了しました！")
        print("\n起動方法:")
        print("  シンプル版: ./start.sh または streamlit run app.py")
        print("  拡張版:     ./start_advanced.sh または streamlit run app_advanced.py")
    else:
        print("⚠️  いくつかの項目で問題が見つかりました。")
        print("\n解決方法:")
        
        if not results["Python"]:
            print("  - Python 3.8以上をインストールしてください")
        
        if not results["ライブラリ"]:
            print("  - 必要なライブラリをインストール: pip3 install -r requirements.txt")
        
        if not results["データファイル"]:
            print("  - データファイルが一部不足していますが、サンプルデータで動作可能です")
        
        if not results["シミュレーター"]:
            print("  - 上記の問題を解決してから再度確認してください")
    
    print()

if __name__ == "__main__":
    main()

