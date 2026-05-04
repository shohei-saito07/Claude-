# Project: todo-cli

学習用の小さな TODO CLI。AI駆動開発（TDDループ）を体験するためのテンプレートとして育てる。

## スタック

- Python 3.11+
- uv（パッケージ管理）
- pytest（テスト）
- ruff（lint + format）

## ディレクトリ

```
src/todo_cli/   実装コード
tests/          pytest テスト
pyproject.toml  プロジェクト設定
```

## 開発フロー（TDDループ）

1. `tests/` に失敗するテストを追加（Red）
2. `src/todo_cli/` に最小実装を入れて通す（Green）
3. 重複・命名・構造を整える（Refactor）
4. コミット → 次の機能へ

## よく使うコマンド

```
uv sync                # 依存インストール
uv run pytest          # テスト実行
uv run ruff check      # lint
uv run ruff format     # 整形
uv run todo            # CLI 実行（実装後）
```

## 設計メモ

- `TaskStore` がタスクの追加/一覧/完了を担当（インメモリ）
- 永続化（JSON ファイル等）は後の段階で追加する
- CLI レイヤ（`cli.py`）は `TaskStore` を呼び出すだけの薄い層に保つ

## AI への指示（このリポジトリで作業するとき）

- 新機能は **必ず先にテストから書く**
- パブリック API を変えたら関連テストも更新する
- `ruff check` と `pytest` を変更後に実行し、両方グリーンになるまで完了としない
- 仕様を勝手に拡張しない。質問して合意を得てから進める
