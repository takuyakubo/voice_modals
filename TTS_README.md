## Text-to-Speech (TTS) with Phoneme/Viseme Output

このプロジェクトには、**Piper TTS**を使用したテキスト音声合成機能が含まれています。音声合成と同時に、リップシンクアニメーション用の**Phoneme（音素）**と**Viseme（視覚素）**のタイムライン情報を出力できます。

### 特徴

- ✅ **完全ローカル実行** - インターネット接続不要
- ✅ **Phoneme/Visemeタイムライン** - 各音素の開始・終了時刻付き
- ✅ **動画/アニメーション対応** - Unity、Blender等で使用可能
- ✅ **多言語対応** - 英語、日本語など
- ✅ **高速** - リアルタイム処理可能
- ✅ **軽量** - 少ないリソースで動作

## インストール

### 1. Piper TTSのインストール

```bash
# macOSの場合
brew install espeak-ng
uv pip install piper-tts phonemizer

# Linuxの場合
sudo apt-get install espeak-ng
uv pip install piper-tts phonemizer

# Windowsの場合
# eSpeak-ngをダウンロード: https://github.com/espeak-ng/espeak-ng/releases
uv pip install piper-tts phonemizer
```

### 2. 依存関係の更新

```bash
uv sync
```

## 使い方

### 基本的な使用例

```bash
# シンプルなデモ
uv run python demo_tts.py "Hello, world!" -o output.wav

# 日本語
uv run python demo_tts.py "こんにちは、世界" --language ja -o output.wav

# Phoneme/Visemeデータも保存される (output.json)
```

### Pythonコードでの使用

```python
from voice_modals import PiperTTSEngine

# TTS エンジンの初期化
engine = PiperTTSEngine(
    language="en-us",
    use_simplified_visemes=True,  # 簡略化されたVisemeセット
)

# 音声合成
result = engine.synthesize_to_file(
    "Hello, this is a test.",
    "output.wav",
    include_json=True  # JSONファイルも保存
)

# Phoneme/Viseme情報の取得
for event in result.phonemes:
    print(f"{event.start:.2f}s - {event.end:.2f}s: "
          f"Phoneme '{event.phoneme}' → Viseme '{event.viseme}'")
```

## デモスクリプト

### 1. 基本デモ（demo_tts.py）

```bash
uv run python demo_tts.py "Hello, world!" -o output.wav
```

**機能：**
- 音声合成
- Phoneme/Visemeタイムライン表示
- ASCII可視化
- JSONファイル出力

### 2. 基本使用例（examples/tts_basic.py）

```bash
uv run python examples/tts_basic.py
```

**機能：**
- シンプルな使用例
- Phonemeタイムラインの表示

### 3. アニメーションエクスポート（examples/tts_animation_export.py）

```bash
uv run python examples/tts_animation_export.py
```

**機能：**
- Unity形式でエクスポート
- Blender形式でエクスポート
- SRT字幕形式でエクスポート

## 出力フォーマット

### JSON出力例

```json
{
  "text": "Hello, world!",
  "duration": 1.5,
  "sample_rate": 22050,
  "phonemes": [
    {
      "start": 0.0,
      "end": 0.12,
      "phoneme": "h",
      "viseme": "DD"
    },
    {
      "start": 0.12,
      "end": 0.24,
      "phoneme": "ə",
      "viseme": "E"
    },
    ...
  ]
}
```

### Viseme一覧

#### 標準Visemeセット

| Viseme | 説明 | 対応する音 |
|--------|------|-----------|
| `sil` | 沈黙（口を閉じる） | - |
| `aa` | 口を大きく開く | a, ah |
| `E` | 口を中程度に開く | e, eh |
| `I` | 笑顔（歯を見せる） | i, ee |
| `O` | 口を丸める | o, oh |
| `U` | 口をすぼめる | u, oo |
| `PP` | 唇を閉じる | p, b, m |
| `FF` | 下唇を上歯に当てる | f, v |
| `TH` | 舌を歯の間に | th, t, d |
| `SS` | 歯を合わせてシュー | s, z |
| `CH` | 唇を前に出す | sh, ch |
| `RR` | 唇を丸める | r |
| `kk` | 口の奥 | k, g |
| `nn` | 鼻音 | n, ng |

#### 簡略化Visemeセット

`use_simplified_visemes=True`を使用すると、より少ないVisemeセット（14種類）になります。

## アニメーションソフトウェアでの使用

### Unity

```csharp
// Unity C# スクリプト例
using UnityEngine;
using System.Collections.Generic;

[System.Serializable]
public class VisemeFrame {
    public int startFrame;
    public int endFrame;
    public string viseme;
}

public class LipSyncController : MonoBehaviour {
    public SkinnedMeshRenderer faceMesh;
    public AudioSource audioSource;
    public TextAsset phonemeData;  // JSONファイルをアサイン

    private List<VisemeFrame> frames;

    void Start() {
        // JSONを読み込み
        var data = JsonUtility.FromJson<PhonemeData>(phonemeData.text);
        frames = data.visemeFrames;
    }

    void Update() {
        // 現在のフレームに応じてBlendShapeを更新
        float time = audioSource.time;
        int currentFrame = Mathf.FloorToInt(time * 30);

        foreach (var frame in frames) {
            if (currentFrame >= frame.startFrame && currentFrame <= frame.endFrame) {
                SetViseme(frame.viseme);
                break;
            }
        }
    }

    void SetViseme(string viseme) {
        // BlendShapeを設定
        int index = faceMesh.sharedMesh.GetBlendShapeIndex($"viseme_{viseme}");
        if (index >= 0) {
            faceMesh.SetBlendShapeWeight(index, 100);
        }
    }
}
```

### Blender

```python
# Blender Python スクリプト例
import bpy
import json

# JSONファイルを読み込み
with open('animation_demo_blender.json', 'r') as f:
    data = json.load(f)

# オブジェクトを取得
obj = bpy.data.objects['Head']

# Shape keyアニメーションを作成
for shape_key_data in data['shapeKeys']:
    frame_start = shape_key_data['frame_start']
    frame_end = shape_key_data['frame_end']
    key_name = shape_key_data['key_name']
    influence = shape_key_data['influence']

    # Shape keyを設定
    if key_name in obj.data.shape_keys.key_blocks:
        shape_key = obj.data.shape_keys.key_blocks[key_name]

        # キーフレームを設定
        bpy.context.scene.frame_set(frame_start)
        shape_key.value = influence
        shape_key.keyframe_insert(data_path='value')

        bpy.context.scene.frame_set(frame_end)
        shape_key.value = 0
        shape_key.keyframe_insert(data_path='value')
```

## Visemeマッピングのカスタマイズ

独自のVisemeマッピングを作成できます：

```python
from voice_modals import VisemeMapper

# カスタムマッピング
VisemeMapper.PHONEME_TO_VISEME["custom_phoneme"] = "custom_viseme"

# またはクラスを継承
class CustomVisemeMapper(VisemeMapper):
    PHONEME_TO_VISEME = {
        # カスタムマッピング
        "a": "mouth_open",
        "i": "smile",
        # ...
    }
```

## トラブルシューティング

### Piper TTSがインストールされていない

```bash
pip install piper-tts
# または
brew install piper  # macOS
```

### eSpeak-ngが見つからない

```bash
# macOS
brew install espeak-ng

# Linux
sudo apt-get install espeak-ng

# Windows
# https://github.com/espeak-ng/espeak-ng/releases からダウンロード
```

### 日本語が合成できない

日本語モデルをダウンロードする必要があります：

```bash
# Piperの日本語モデルをダウンロード
# https://github.com/rhasspy/piper から適切なモデルを取得
```

## パフォーマンス

### 処理速度

- **リアルタイム係数**: 約0.3x（1秒の音声を0.3秒で生成）
- **レイテンシ**: 100-300ms
- **メモリ使用量**: 約100-300MB

### 推奨環境

- **CPU**: 2コア以上
- **RAM**: 2GB以上
- **ストレージ**: モデルファイル用に100MB-1GB

## 関連リンク

- [Piper TTS GitHub](https://github.com/rhasspy/piper)
- [eSpeak-ng](https://github.com/espeak-ng/espeak-ng)
- [Phonemizer](https://github.com/bootphon/phonemizer)
- [Unity OVR Lip Sync](https://developer.oculus.com/downloads/package/oculus-lipsync-unity/)

## 今後の拡張予定

- [ ] より多くの言語モデルのサポート
- [ ] リアルタイムストリーミング合成
- [ ] 感情表現のサポート
- [ ] 音声クローニング機能
- [ ] WebSocketベースのAPI

## ライセンス

このTTS実装はPiper TTS（MITライセンス）を使用しています。
