---
title: "AI が作ったファイルが手元にない！ - git pull で気づいた『同期』の正体"
emoji: "🔄"
type: "tech"
topics: ["git", "github", "claude", "claudecode", "beginner"]
published: false
---

## はじめに

Claude Code を使って AI に開発を進めてもらっていたとき、こんな出来事がありました。

> 私「ローカルで `apps/url_shortener` を動かしたい」
>
> AI「`cd apps/url_shortener` してください」
>
> 私「**そのフォルダが手元にないです**」

「あれ？確かに AI は作ったって言ってたのに……」と一瞬パニックになったのですが、原因はとてもシンプルで、**ローカルに最新のコードが届いていなかった** だけでした。

この記事は、Git をなんとなく使い始めた人がよくぶつかる「**push と pull の同期感覚**」を、AI駆動開発の文脈で図解しながら整理した記録です。同じところで詰まる人の助けになれば嬉しいです。

## 何が起きていたか

私は Claude Code on Web を使っていました。AI はクラウド上のサンドボックス（仮想マシン）で作業していて、そこで作ったファイルを GitHub にプッシュしてくれます。

ところが手元の PC には、その変更は **自動では反映されません**。図にするとこういう状態でした。

```
GitHubサーバ                  あなたのPC
┌──────────────────┐          ┌──────────────────┐
│ ecbea87 ★最新    │          │ 古い状態         │
│  └ apps/         │ ◀────    │                  │
│     url_shortener│ 未同期   │ apps/ がない     │
│ 063aff4          │          │ 063aff4          │
│ f9d1d0a          │          │ f9d1d0a          │
└──────────────────┘          └──────────────────┘
```

GitHub には最新コミット `ecbea87`（`apps/url_shortener` を含む）が乗っているけれど、ローカルにはまだ届いていない、というわけです。

「AI が `git push` した」というのは「GitHub までは届いた」という意味であって、「あなたの手元のフォルダに現れた」という意味ではありません。ここを取り違えると、迷子になります。

## 解決方法：`git pull`

ローカルに最新を取り込むには、こちらから取りに行く必要があります。

```bash
cd /path/to/Claude-
git fetch origin
git checkout claude/check-code-O9eOf
git pull origin claude/check-code-O9eOf
```

これを実行したら、`apps/url_shortener/` が手元に現れました。

```
GitHubサーバ                  あなたのPC
┌──────────────────┐ git pull ┌──────────────────┐
│ ecbea87 ★最新    │ ────▶   │ ecbea87 届いた!  │
│  └ apps/         │          │  └ apps/         │
│     url_shortener│          │     url_shortener│
└──────────────────┘          └──────────────────┘
```

各コマンドの役割は次の通りです。

| コマンド | やっていること |
| --- | --- |
| `git fetch origin` | GitHub の最新情報を取得（ファイルはまだ更新しない） |
| `git checkout <branch>` | 該当ブランチに切り替え |
| `git pull origin <branch>` | リモートの最新コミットをローカルに反映 |

`git pull` は内部的には「`fetch` + `merge`」とほぼ同じで、**ダウンロードして合流させる** ところまでをまとめてやってくれます。

## Git は「双方の橋渡しをする集合場所」

実は Git/GitHub は、人間と AI（あるいは複数の人間）が、コードを安全に共有するための **集合場所** として機能しています。

```
あなた push ──▶ GitHub ──▶ 私が pull
                  ↕
AI が push  ──▶ GitHub ──▶ あなたが pull
```

ポイントは、**push と pull は別々の操作で、片方が動いただけでは反対側に何も届かない** ことです。

| 動作 | 誰が誰に渡すか | きっかけ |
| --- | --- | --- |
| `git push` | ローカル → GitHub | 自分が叩いたとき |
| `git pull` | GitHub → ローカル | 自分が叩いたとき |

「自動で同期されている」ように感じることがあっても、それは IDE や CI が裏で `git pull` 相当を実行してくれているだけで、**Git そのものは何もしません**。手元のフォルダが自動更新されるのは、誰かが pull を発火させた瞬間だけです。

## AI 駆動開発で特に起きやすい理由

AI 駆動開発では、AI が高速に複数のコミットを積んで GitHub に push します。一方、人間は手元で別のことをしていることが多く、**push のたびにローカルが置いていかれる** 状況になりがちです。

私の体験でも、こんな順番で起きていました。

```
1. AI が apps/url_shortener を作って push
2. 私が「動かしたい」と言う
3. AI が「cd apps/url_shortener で動きます」と言う
4. 私「そのフォルダがない！」
5. AI「git pull すれば現れます」
6. 解決
```

ここで覚えておくと便利な習慣はひとつだけです。

> **AI が「push しました」と言ったら、自分は `git pull` する。**

これさえ習慣にしておけば、迷子になる頻度が一気に下がります。

## つまずきポイントのチェックリスト

似たような場面で詰まったとき、私が確認したポイントをまとめておきます。

```
[ ] 自分は Claude- リポジトリのルートにいるか? (pwd で確認)
[ ] git branch --show-current で正しいブランチにいるか?
[ ] git log --oneline -5 で最新コミットがローカルに来ているか?
[ ] git fetch origin で取得したあと、git pull したか?
[ ] そもそも別ブランチ (main など) にいて未マージではないか?
```

特に最後の「**ブランチ違い**」は気づきにくいです。AI が新しいブランチ（例: `claude/check-code-O9eOf`）に push しているのに、自分は `main` を見ていた、というケース。`git branch --show-current` で必ず確認しましょう。

## 学んだこと

- **`git push` ≠ ローカルに反映される** という当たり前の事実を、改めて体に叩き込んだ。
- Git は **同期の仕組みを自動でやってはくれない**。人間（あるいは AI）が明示的に push/pull したときだけ動く。
- AI 駆動開発では「AI が push → 自分が pull」のリズムが基本動作になる。
- 詰まったときは、まず **`pwd`** と **`git log --oneline`** で「自分の現在地」と「履歴の到達点」を確認するのが近道。

## おわりに

シンプルなトラブルでしたが、Git の挙動を「集合場所モデル」で理解し直す良いきっかけになりました。AI が高速にコードを生成する時代だからこそ、**push/pull の感覚** は AI 駆動開発で生き残るための基礎体力だと感じます。

同じところで詰まった人、これから AI 駆動開発を始める人の参考になれば幸いです。

## 参考リンク

- [Git 公式ドキュメント](https://git-scm.com/doc)
- [GitHub Docs - Pulling changes from a remote](https://docs.github.com/en/get-started/using-git/getting-changes-from-a-remote-repository)
- [Claude Code](https://docs.claude.com/claude-code)
