#!/bin/bash
# .agents/workflows/setup-pre-commit.sh
# KNOWLEDGE.md への教訓自動追記用 Git pre-commit フックのセットアップスクリプト

HOOK_FILE=".git/hooks/pre-commit"

echo "⚙️ AIコンテキスト自動抽出フックの設定を開始します..."

# 既存のフックをバックアップ
if [ -f "$HOOK_FILE" ]; then
  cp "$HOOK_FILE" "$HOOK_FILE.bak"
  echo "既存の pre-commit を .bak としてバックアップしました。"
fi

# pre-commit ファイルの作成
cat << 'EOF' > "$HOOK_FILE"
#!/bin/bash

# ==========================================
# 🧠 AI Context Learner (pre-commit hook)
# ==========================================
# コミット時に差分をClaude/Geminiに解析させ、KNOWLEDGE.mdに有用な教訓を自動追記するスクリプト

# Stageされている変更（Diff）を取得
STAGED_DIFF=$(git diff --cached)

# 変更がない場合はスキップ
if [ -z "$STAGED_DIFF" ]; then
  exit 0
fi

# ==========================================
# 🚦 LLM判定ゲート（事前フィルタ）
# ==========================================
# LLM呼び出しの前にシェルレベルで不要な処理をスキップする

STAGED_FILES=$(git diff --cached --name-only)

# フィルタ1: KNOWLEDGE.md のみの変更ならスキップ（自己参照ループ防止）
NON_KNOWLEDGE_FILES=$(echo "$STAGED_FILES" | grep -v "^KNOWLEDGE.md$")
if [ -z "$NON_KNOWLEDGE_FILES" ]; then
  exit 0
fi

# フィルタ2: ドキュメント/設定ファイルのみの変更ならスキップ
CODE_FILES=$(echo "$STAGED_FILES" | grep -vE '\.(md|txt|json|yaml|yml)$')
if [ -z "$CODE_FILES" ]; then
  exit 0
fi

# フィルタ3: 差分が大きすぎる場合はスキップ（トークン浪費防止）
DIFF_LINES=$(echo "$STAGED_DIFF" | wc -l)
if [ "$DIFF_LINES" -gt 500 ]; then
  echo "⏭️ 差分が大きすぎるため（${DIFF_LINES}行）、自動学習抽出をスキップします。"
  echo "   手動で /record-learnings を実行してください。"
  exit 0
fi

# 対話型セッションであることを宣言（キー入力を受け付けるため）
exec < /dev/tty

echo "🤖 コミットの差分から AI（KNOWLEDGE.md用）の教訓を絞り出しています..."

# AIへのプロンプト定義
PROMPT="あなたは経験豊富なシニアソフトウェアエンジニアです。
以下の git diff を確認し、将来のAI実装（Claude CodeやGemini CLIなど）が絶対に知っておくべき「プロジェクト固有のルール」「陥りやすいバグ」「特殊な設定の振る舞い」などの教訓が1つでもあれば、それを抽出してください。

【ルール】
1. タイポ修正、一般的なリファクタリング、ライブラリ追加など「自明なこと」は絶対に教訓にしないでください。
2. 提案すべき特筆事項が何もない場合は、必ず「NONE」という単語だけを出力してください。
3. 抽出する場合は、絶対に非常に簡潔な日本語で1行〜2行の「箇条書き（ハイフン始まり）」形式で出力してください。
   例: \"- Vite環境でCSS Modulesを使う際、必ず xxx.module.css と命名し、グローバルへの漏洩を防ぐこと。\"

【Git Diff】
$STAGED_DIFF
"

# 利用可能なCLIを判定してAIに問い合わせ
RESULT=""
if command -v claude &> /dev/null; then
  # Claude Code のプロンプト実行
  RESULT=$(claude -p "$PROMPT" 2>/dev/null)
elif command -v gemini &> /dev/null; then
  # Gemini CLI による実行
  RESULT=$(gemini "$PROMPT" 2>/dev/null)
else
  echo "⚠️ 'claude' ツールまたは 'gemini' ツールが見つからないため、学習抽出をスキップします。"
  exit 0
fi

# 結果をパース（ANSIエスケープシーケンスなどを除去し、ハイフンで始まる行のみ抽出）
CLEAN_RESULT=$(echo "$RESULT" | sed -e 's/\x1b\[[0-9;]*m//g' | grep "^- " | head -n 1)

# 有用な教訓が見つかった場合
if [ -n "$CLEAN_RESULT" ] && [ "$CLEAN_RESULT" != "NONE" ] && [[ "$CLEAN_RESULT" == -* ]]; then
  echo ""
  echo -e "\033[1;36m💡 AI がこのコミットから以下の教訓を抽出しました：\033[0m"
  echo -e "\033[1;33m$CLEAN_RESULT\033[0m"
  echo ""
  
  read -p "この教訓を KNOWLEDGE.md の [Gotchas & Learnings] セクションに追記しますか？ (y/N): " -n 1 -r REPLY
  echo ""
  
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    
    # 既存の KNOWLEDGE.md に追記（セクションマーカーを目印にする）
    if [ -f "KNOWLEDGE.md" ]; then
      # Gotchasセクションの下に追記
      echo "$CLEAN_RESULT" >> KNOWLEDGE.md
      git add KNOWLEDGE.md
      echo "✅ KNOWLEDGE.md に追記し、このコミットに含めました。"
    else
      echo "⚠️ KNOWLEDGE.md が見つかりませんでした。"
    fi
  else
     echo "🚫 追記をスキップしました。"
  fi
fi

# コミットを継続
exit 0
EOF

# 実行権限の付与
chmod +x "$HOOK_FILE"

echo "✨ AIコンテキスト自動抽出フックのインストールが完了しました！"
echo "次回以降、git commit する度に Claude Code / Gemini CLI が裏で走り、有用な教訓を KNOWLEDGE.md へ自動提案します。"
