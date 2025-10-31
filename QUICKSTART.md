# クイックスタートガイド

## セットアップ完了！

依存関係のインストールが完了しました。システムを使用する準備ができています。

## 🎤 すぐに始める

### 1. システムテスト（10秒間）

まず、システムが正常に動作することを確認します：

```bash
uv run python test_system.py
```

このテストは10秒間実行され、マイクから音声を取得して文字起こしを行います。

### 2. 基本的な使用

最もシンプルな使い方：

```bash
uv run python -m voice_modals.cli
```

これでストリーミングASRが起動します。マイクに向かって話すと、リアルタイムで文字起こしされます。

終了するには `Ctrl+C` を押してください。

### 3. 日本語に最適化

日本語の認識精度を上げるには：

```bash
uv run python -m voice_modals.cli --language ja --model base
```

### 4. より高精度なモデル

より高精度な文字起こしが必要な場合：

```bash
uv run python -m voice_modals.cli --language ja --model small
```

**モデルサイズと特徴：**
- `tiny`: 最速だが精度低（テスト用）
- `base`: 速度と精度のバランスが良い（推奨）
- `small`: 高精度で実用的な速度
- `medium`: より高精度だが遅い
- `large`: 最高精度だが非常に遅い

## 📝 サンプルコード

### 基本的な使用例

```bash
uv run python examples/basic_usage.py
```

### ファイルに保存する例

```bash
uv run python examples/custom_callback.py
```

このスクリプトは、文字起こし結果をタイムスタンプ付きでファイルに保存します。

## 🔧 よく使うコマンド

### オーディオデバイスの確認

```bash
uv run python check_audio_devices.py
```

### パラメータのカスタマイズ

```bash
# チャンク期間と処理間隔を調整
uv run python -m voice_modals.cli \
  --language ja \
  --model base \
  --chunk-duration 1.5 \
  --process-interval 2.5
```

**パラメータの意味：**
- `--chunk-duration`: 音声キャプチャのチャンクサイズ（秒）
  - 小さい値: レスポンス速いがCPU負荷高
  - 大きい値: CPU負荷低いが遅延増加
  - 推奨: 1.0〜2.0秒

- `--process-interval`: ASR処理の実行間隔（秒）
  - 小さい値: リアルタイム性高いがCPU負荷高
  - 大きい値: CPU負荷低いが遅延増加
  - 推奨: 2.0〜5.0秒

## 🐛 トラブルシューティング

### マイクが使えない

macOSの場合、システム環境設定でマイクのアクセス許可を確認してください：
「システム設定」→「プライバシーとセキュリティ」→「マイク」

### 音声が認識されない

1. マイクに近づいて大きめの声で話す
2. オーディオデバイスが正しく選択されているか確認：
   ```bash
   uv run python check_audio_devices.py
   ```

### Whisperモデルのダウンロード

初回実行時、Whisperモデルが自動的にダウンロードされます。
インターネット接続が必要です（初回のみ）。

モデルサイズ：
- tiny: 約39MB
- base: 約74MB
- small: 約244MB
- medium: 約769MB
- large: 約1550MB

## 📚 次のステップ

- [README.md](README.md) - 詳細なドキュメント
- [examples/](examples/) - より多くのサンプルコード
- カスタムコールバックを作成して、文字起こし結果を独自の方法で処理

## 🎯 使用例

### 会議の文字起こし

```bash
uv run python examples/custom_callback.py
```

会議中に実行すると、発言内容がファイルに記録されます。

### リアルタイム字幕

```bash
uv run python -m voice_modals.cli --language ja --process-interval 1.5
```

処理間隔を短くすることで、よりリアルタイムに近い表示が可能です。

### 多言語対応

```bash
# 英語
uv run python -m voice_modals.cli --language en

# 中国語
uv run python -m voice_modals.cli --language zh

# 自動検出
uv run python -m voice_modals.cli
```

## 💡 Tips

1. **初めて使う場合はtinyモデルで試す**
   ```bash
   uv run python test_system.py
   ```

2. **日常使いはbaseモデルがおすすめ**
   速度と精度のバランスが最適です。

3. **重要な会議はsmallモデル以上**
   より正確な文字起こしが必要な場合。

4. **GPU があれば活用**
   ```bash
   uv run python -m voice_modals.cli --device cuda --model medium
   ```

5. **静かな環境で使用**
   背景ノイズが少ないほど認識精度が向上します。
