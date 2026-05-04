# url-shortener

学習用の小さな URL 短縮サービス。FastAPI + SQLModel + SQLite で構築。

## 機能

- ランダムまたはカスタムの短縮コードで URL を発行
- 短縮 URL にアクセスすると元 URL へ 307 リダイレクト
- アクセスごとにクリック数をカウント
- リンク情報の取得・全件一覧
- バリデーション (URL 形式 / 重複コード)

## 必要環境

- Python 3.11+
- uv

## セットアップ

```bash
cd apps/url_shortener
uv sync
```

## 起動

```bash
uv run uvicorn url_shortener.main:app --reload
```

または `pyproject.toml` のスクリプト経由:

```bash
uv run url-shortener
```

サーバが `http://127.0.0.1:8000` で起動します。OpenAPI ドキュメントは `/docs` で見られます。

## 使い方

### 短縮 URL を作る (ランダムコード)

```bash
curl -X POST http://127.0.0.1:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/long/path"}'
```

レスポンス:

```json
{
  "code": "Ab3xY9z",
  "short_url": "http://127.0.0.1:8000/Ab3xY9z",
  "target_url": "https://example.com/long/path"
}
```

### カスタムコードを指定

```bash
curl -X POST http://127.0.0.1:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com", "code": "gh"}'
```

### リダイレクト

```bash
curl -i http://127.0.0.1:8000/gh
# HTTP/1.1 307 Temporary Redirect
# location: https://github.com
```

### リンク情報

```bash
curl http://127.0.0.1:8000/api/links/gh
```

```json
{
  "code": "gh",
  "target_url": "https://github.com",
  "clicks": 1,
  "created_at": "2026-05-04T00:00:00Z"
}
```

### 全リンク一覧

```bash
curl http://127.0.0.1:8000/api/links
```

### ヘルスチェック

```bash
curl http://127.0.0.1:8000/healthz
# {"status":"ok"}
```

## エンドポイント一覧

| Method | Path                | 説明                               |
| ------ | ------------------- | ---------------------------------- |
| GET    | `/healthz`          | ヘルスチェック                     |
| POST   | `/shorten`          | 短縮URL作成 (201 / 409 / 422)      |
| GET    | `/{code}`           | 元URLへリダイレクト (307 / 404)    |
| GET    | `/api/links`        | 全リンク一覧                       |
| GET    | `/api/links/{code}` | リンク情報取得 (200 / 404)         |

## テスト

```bash
uv run pytest         # 14 tests
uv run ruff check     # lint
```

テストはインメモリ SQLite (`sqlite:///:memory:`) で実行され、各テストごとに DB が新しく作られます。

## Docker で動かす

```bash
docker build -t url-shortener .
docker run --rm -p 8000:8000 url-shortener
```

## ディレクトリ

```
apps/url_shortener/
├── pyproject.toml
├── Dockerfile
├── README.md
├── src/url_shortener/
│   ├── __init__.py
│   ├── main.py        FastAPI アプリ + ルーティング
│   ├── models.py      SQLModel: Link テーブル
│   ├── schemas.py     リクエスト/レスポンスの Pydantic モデル
│   ├── db.py          エンジン作成・初期化
│   └── shortcode.py   ランダムコード生成
└── tests/
    ├── conftest.py    インメモリ DB の fixture
    ├── test_api.py    API テスト 10件
    └── test_shortcode.py コード生成テスト 4件
```

## 設計メモ

- `create_app(database_url)` で DB を切り替えられるようにし、テストではインメモリを注入
- `:memory:` SQLite では `StaticPool` を使い、リクエストを跨いで同じ接続を共有 (そうしないとテーブルが見えない)
- ランダムコードは衝突したら最大 5 回までリトライ
- カスタムコードの重複は事前に SELECT して 409 を返す
