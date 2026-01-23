#!/usr/bin/env python3
"""
インポートテスト

Reflexアプリの主要モジュールが正しくインポートできるか確認
"""

import sys
from pathlib import Path

# パス設定（reflex_app/ ディレクトリを参照）
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_core_imports():
    """コアモジュールのインポートテスト"""
    print("Testing core imports...")
    try:
        from core import GachaService, LifeResult
        print("  ✓ core.GachaService, LifeResult")
        
        # サービスのインスタンス化テスト
        service = GachaService(region="hokkaido", data_dir=str(project_root / "data"))
        print("  ✓ GachaService instantiation (hokkaido)")
        
        service_tokyo = GachaService(region="tokyo", data_dir=str(project_root / "data"))
        print("  ✓ GachaService instantiation (tokyo)")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_reflex_state():
    """Reflex状態モジュールのインポートテスト"""
    print("Testing reflex_app.state imports...")
    try:
        import reflex as rx
    except ImportError:
        print("  ⚠ Reflex not installed (run: pip install reflex)")
        print("  → Skipping Reflex-specific tests")
        return True  # スキップとして成功扱い
    
    try:
        # reflex_appディレクトリをパスに追加
        reflex_app_path = Path(__file__).parent
        sys.path.insert(0, str(reflex_app_path))
        
        from reflex_app.state import GachaState, get_service
        print("  ✓ reflex_app.state.GachaState, get_service")
        
        # サービス取得テスト
        service = get_service("hokkaido")
        print("  ✓ get_service('hokkaido')")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """メインテスト"""
    print("=" * 50)
    print("Reflex App Import Test")
    print("=" * 50)
    print()
    
    results = []
    
    results.append(("Core Imports", test_core_imports()))
    print()
    
    results.append(("Reflex State", test_reflex_state()))
    print()
    
    # 結果サマリー
    print("=" * 50)
    print("Results:")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("All tests passed! ✓")
        return 0
    else:
        print("Some tests failed. ✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
