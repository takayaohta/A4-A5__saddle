# 中綴じ面付け GUIアプリ

A5 単ページ PDF を A4 横の面付け済み PDF に変換する、macOS 向けローカル Web アプリです。

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-green)

## 特徴

- 📄 **macOS ネイティブファイル選択** — Finder のダイアログでPDFを選択
- 📋 **ページ数バリデーション** — 4の倍数でなければエラー表示
- 📖 **面付け順プレビュー** — 各用紙の表裏に配置されるページ番号を一覧表示
- 🖨️ **ワンクリック面付け** — `元ファイル名_imposed.pdf` として同じディレクトリに出力
- 📂 **Finder で表示** — 処理完了後に出力ファイルをFinderで開くボタン

## セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/takayaohta/A5-A5_mentsuke.git
cd A5-A5_mentsuke

# 仮想環境を作成して依存パッケージをインストール
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 起動方法

```bash
source venv/bin/activate
python app.py
```

ブラウザで **http://localhost:5000** を開いてください。

## 使い方

1. 画面中央のエリアをクリック → macOS のファイル選択ダイアログが開く
2. 面付けしたい A5 単ページ PDF を選択
3. ページ数・サイズが表示され、面付け順のプレビューを確認
4. 「🖨️ 面付け実行」ボタンをクリック
5. 元ファイルと同じディレクトリに `_imposed.pdf` が生成される
6. 「📂 Finder で表示」ボタンで出力ファイルを確認

## 面付けの仕組み

中綴じ（サドルステッチ）製本用のページ配置を自動計算します。

例: 8ページの冊子の場合

| 用紙 | 面 | 左 | 右 |
|------|------|-----|-----|
| 1枚目 | おもて | 8 | 1 |
| 1枚目 | うら | 2 | 7 |
| 2枚目 | おもて | 6 | 3 |
| 2枚目 | うら | 4 | 5 |

## 技術スタック

- **バックエンド**: Python / Flask
- **PDF処理**: pypdf
- **フロントエンド**: HTML / CSS / JavaScript（シングルHTML）
- **ファイル選択**: macOS `osascript`（ネイティブダイアログ）

## ライセンス

MIT
