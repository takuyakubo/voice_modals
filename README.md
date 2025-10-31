# Voice Modals

ローカルで動作するストリーミングASR（自動音声認識）システムです。OpenAIのWhisperモデルを使用して、リアルタイムで音声をテキストに変換します。

## 特徴

- **リアルタイム音声認識**: マイクからの音声をリアルタイムで文字起こし
- **ローカル実行**: インターネット接続不要、プライバシーを保護
- **複数言語対応**: Whisperの多言語サポートを活用
- **軽量・高速**: faster-whisperを使用した最適化された推論
- **カスタマイズ可能**: モデルサイズ、処理間隔などを調整可能

## システム要件

- Python 3.9以上
- マイク入力が可能なデバイス
- （オプション）GPU: CUDA対応GPUで高速化可能

## インストール

### 1. リポジトリのクローン

```bash
cd voice_modals
```

### 2. 依存関係のインストール

uvを使用している場合:

```bash
uv sync
```

または、pipを使用する場合:

```bash
pip install -e .
```

### 3. PyAudioのインストール

macOSの場合:

```bash
brew install portaudio
uv pip install pyaudio
```

Linuxの場合:

```bash
sudo apt-get install portaudio19-dev
uv pip install pyaudio
```

Windowsの場合:

```bash
uv pip install pyaudio
```

## 使い方

### システムテスト（初回確認推奨）

まず、システムが正常に動作するか10秒間のテストを実行することをお勧めします：

```bash
uv run python test_system.py
```

このテストは：
- tinyモデルを使用（最速）
- 10秒間音声を録音
- 文字起こし結果を表示
- システムの動作確認に最適

### 基本的な使用方法

```bash
uv run python -m voice_modals.cli
```

### モデルサイズの指定

モデルサイズを変更することで、精度と速度のバランスを調整できます:

```bash
# 小さくて速い (tiny)
uv run python -m voice_modals.cli --model tiny

# デフォルト (base)
uv run python -m voice_modals.cli --model base

# 高精度 (small)
uv run python -m voice_modals.cli --model small

# より高精度 (medium)
uv run python -m voice_modals.cli --model medium

# 最高精度 (large)
uv run python -m voice_modals.cli --model large
```

### 言語の指定

特定の言語を指定することで、認識精度が向上します:

```bash
# 日本語
uv run python -m voice_modals.cli --language ja

# 英語
uv run python -m voice_modals.cli --language en

# 中国語
uv run python -m voice_modals.cli --language zh

# 自動検出（デフォルト）
uv run python -m voice_modals.cli
```

### GPU使用

CUDAが利用可能な場合、GPUで高速化できます:

```bash
uv run python -m voice_modals.cli --device cuda --model medium
```

### パラメータの調整

処理パラメータを調整してパフォーマンスを最適化:

```bash
# チャンク期間と処理間隔の調整
uv run python -m voice_modals.cli --chunk-duration 2.0 --process-interval 3.0
```

## コマンドラインオプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `--model` | Whisperモデルサイズ (tiny/base/small/medium/large) | base |
| `--device` | 実行デバイス (cpu/cuda/auto) | cpu |
| `--language` | 言語コード (ja/en/zh等) | 自動検出 |
| `--chunk-duration` | 音声チャンク期間（秒） | 1.0 |
| `--process-interval` | 処理間隔（秒） | 2.0 |

## プログラムでの使用

Pythonコードから直接使用することもできます:

```python
from voice_modals import AudioCapture, StreamingASR

# ASRエンジンの初期化
asr = StreamingASR(
    model_size="base",
    device="cpu",
    language="ja",  # 日本語
)

# 音声キャプチャの初期化
audio = AudioCapture(
    sample_rate=16000,
    chunk_duration=1.0,
)

# コールバック関数の定義
def on_transcription(result):
    print(f"[{result.language}] {result.text}")

asr.set_callback(on_transcription)

# 処理の開始
audio.start()
asr.start_processing_thread(process_interval=2.0)

try:
    # 音声データをASRエンジンにフィード
    while True:
        audio_chunk = audio.get_audio_chunk(timeout=1.0)
        if audio_chunk is not None:
            asr.add_audio(audio_chunk)
except KeyboardInterrupt:
    pass
finally:
    asr.stop_processing_thread()
    audio.stop()
```

## アーキテクチャ

### コンポーネント

1. **AudioCapture** ([audio_capture.py](src/voice_modals/audio_capture.py))
   - PyAudioを使用してマイクから音声を取得
   - リアルタイムで音声データをキューに格納
   - 16kHzサンプリングレート、モノラル音声

2. **StreamingASR** ([streaming_asr.py](src/voice_modals/streaming_asr.py))
   - faster-whisperを使用した音声認識
   - バッファリングされた音声を定期的に処理
   - VAD（Voice Activity Detection）フィルタリング
   - コールバックベースの非同期処理

3. **CLI** ([cli.py](src/voice_modals/cli.py))
   - コマンドラインインターフェース
   - シグナルハンドリング（Ctrl+C）
   - パラメータ設定

### データフロー

```
Microphone → AudioCapture → Audio Queue → StreamingASR → Transcription → Callback
                (PyAudio)                   (Whisper)
```

## パフォーマンスチューニング

### モデルサイズの選択

| モデル | サイズ | 速度 | 精度 | 推奨用途 |
|-------|--------|------|------|---------|
| tiny | 39M | 最速 | 低 | テスト・デモ |
| base | 74M | 速い | 中 | 一般的な用途 |
| small | 244M | 中 | 高 | バランス重視 |
| medium | 769M | 遅い | 高 | 高精度が必要 |
| large | 1550M | 最遅 | 最高 | 最高精度が必要 |

### チャンク期間と処理間隔

- **chunk_duration**: 音声キャプチャのチャンクサイズ
  - 小さい値: レイテンシが低いが、オーバーヘッドが増加
  - 大きい値: レイテンシが高いが、効率的
  - 推奨: 1.0～2.0秒

- **process_interval**: ASR処理の実行間隔
  - 小さい値: リアルタイム性が高いが、CPU負荷増加
  - 大きい値: CPU負荷が低いが、遅延が増加
  - 推奨: 2.0～5.0秒

## トラブルシューティング

### PyAudioのインストールエラー

macOSで`portaudio.h not found`エラーが出る場合:

```bash
brew install portaudio
export CFLAGS="-I/opt/homebrew/include"
export LDFLAGS="-L/opt/homebrew/lib"
uv pip install pyaudio
```

### マイクが認識されない

利用可能なマイクデバイスを確認:

```bash
uv run python check_audio_devices.py
```

または、Pythonコードで確認:

```python
import pyaudio
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(f"{i}: {info['name']}")
```

### GPUが使用されない

CUDAとPyTorchのインストールを確認:

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

## プロジェクト構造

```
voice_modals/
├── src/voice_modals/        # メインパッケージ
│   ├── __init__.py          # パッケージ初期化
│   ├── __main__.py          # エントリーポイント
│   ├── audio_capture.py     # 音声キャプチャモジュール
│   ├── streaming_asr.py     # ASRエンジン
│   └── cli.py               # CLIインターフェース
├── examples/                # サンプルコード
│   ├── basic_usage.py       # 基本的な使用例
│   └── custom_callback.py   # カスタムコールバック例
├── test_system.py           # システムテスト（10秒）
├── check_audio_devices.py   # オーディオデバイス確認
├── README.md                # このファイル
├── QUICKSTART.md            # クイックスタートガイド
├── CONTRIBUTING.md          # 貢献ガイドライン
├── pyproject.toml           # プロジェクト設定（uv用）
└── requirements.txt         # 依存関係（pip用）
```

## 貢献

プロジェクトへの貢献を歓迎します！詳細は[CONTRIBUTING.md](CONTRIBUTING.md)をご覧ください。

## 謝辞

- [OpenAI Whisper](https://github.com/openai/whisper)
- [faster-whisper](https://github.com/guillaumekln/faster-whisper)
- [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/)
