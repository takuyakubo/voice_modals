# Contributing to Voice Modals

このプロジェクトへの貢献を検討いただきありがとうございます！

## 開発環境のセットアップ

### 1. リポジトリのフォークとクローン

```bash
git clone https://github.com/YOUR_USERNAME/voice_modals.git
cd voice_modals
```

### 2. 依存関係のインストール

```bash
uv sync
```

macOSの場合、portaudioのインストールも必要です：

```bash
brew install portaudio
export CFLAGS="-I/opt/homebrew/include"
export LDFLAGS="-L/opt/homebrew/lib"
uv sync
```

### 3. 動作確認

```bash
uv run python test_system.py
```

## コーディング規約

- Python 3.9以上に対応
- コードフォーマット: Black（line-length=100）
- Linter: Ruff
- 型ヒントの使用を推奨

### フォーマット実行

```bash
uv run black src/
uv run ruff check src/
```

## プルリクエストのガイドライン

1. **機能追加の場合**
   - 新機能の目的と利点を説明
   - サンプルコードや使用例を含める
   - 必要に応じてドキュメントを更新

2. **バグ修正の場合**
   - 問題の詳細な説明
   - 再現手順
   - 修正内容の説明

3. **ドキュメント改善**
   - 誤字脱字の修正
   - わかりにくい説明の改善
   - サンプルコードの追加

## テスト

新機能を追加する場合は、動作確認のためのテストコードを含めてください。

```bash
# システムテスト
uv run python test_system.py

# サンプルの実行
uv run python examples/basic_usage.py
uv run python examples/custom_callback.py
```

## イシューの報告

バグや改善提案がある場合は、GitHubのIssuesで報告してください：

- **バグ報告**: 再現手順、期待される動作、実際の動作を記載
- **機能リクエスト**: 機能の説明、ユースケース、実装案を記載

## コミットメッセージ

わかりやすいコミットメッセージを心がけてください：

```
Add feature: Support for custom audio devices

- Add device_index parameter to AudioCapture
- Update documentation with device selection examples
```

## 質問・相談

不明点があれば、遠慮なくIssueで質問してください。

## 行動規範

- 敬意を持った対応を心がける
- 建設的なフィードバックを提供する
- 異なる意見や視点を尊重する

ご協力ありがとうございます！
