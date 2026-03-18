# KNOWLEDGE (Project Context & Rules)

このファイルは、AIエージェント（Antigravity, Claude Code, Cursor, Gemini CLI等）がこのプロジェクトで作業する際の**単一の真実の情報源（Single Source of Truth）**です。
すべてのAIエージェントは、作業を開始する前に必ずこのファイルを読み込み、記載されたルールと文脈に完全に従ってください。
**このファイルへの追記・更新はすべて日本語で行ってください。**

---

## 1. Architecture & Key Files (アーキテクチャと重要なファイル)

中綴じ（サドルステッチ）面付けを行うローカルWebアプリ。Python (Flask) バックエンド + HTML/CSS/JS フロントエンドで構成。

```
A5-A5_mentsuke/
├── app.py                  # Flask バックエンド（API + 面付けロジック）
├── requirements.txt        # Python 依存パッケージ（flask, pypdf）
├── templates/
│   └── index.html          # フロントエンド（シングルHTML、CSS/JS埋め込み）
├── venv/                   # Python 仮想環境
├── KNOWLEDGE.md            # このファイル
└── .agents/
    └── workflows/          # AIワークフロー定義
```

- **面付けロジック**: `app.py` 内の `get_imposition_order()` と `impose()` 関数
- **ファイル選択**: macOS の `osascript` でネイティブファイルダイアログを使用（ブラウザのセキュリティ制限回避のため）
- **元スクリプト**: `/Users/takaya/Projects/A5-A4面付け/saddle_stitch_impose.py` を GUI 化したもの

## 2. Commands (主要なコマンド群)

```bash
# 仮想環境のセットアップ（初回のみ）
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 開発サーバー起動
source venv/bin/activate
python app.py
# → http://localhost:5000 をブラウザで開く
```

## 3. Code Style & Rules (コーディング規約とルール)

- チャットは日本語で回答すること
- Git コミットメッセージも日本語で書くこと
- フロントエンドのスタイリングはダークモードベースのモダンUI（グラスモーフィズム、Inter + Noto Sans JP フォント）

## 4. Environment & Testing (環境変数とテスト方針)

- **Python**: 3.x（macOS システムの Python3）
- **主要ライブラリ**: Flask, pypdf
- **OS依存**: macOS（`osascript` でのファイルダイアログ、`open -R` でのFinder表示）
- テストフレームワークは未導入

## 5. Gotchas & Learnings (過去の失敗と教訓)

- ブラウザの Drag & Drop ではファイルの実パスが取得できない（セキュリティ制限）。ローカル macOS アプリでは `osascript` のネイティブファイルダイアログで実パスを取得する方式が正解。
