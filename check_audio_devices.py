"""Check available audio input devices."""

import pyaudio

def list_audio_devices():
    """List all available audio devices."""
    p = pyaudio.PyAudio()

    print("=" * 80)
    print("Available Audio Devices")
    print("=" * 80)

    input_devices = []

    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)

        # Only show input devices
        if info['maxInputChannels'] > 0:
            input_devices.append((i, info))
            print(f"\n[Device {i}]")
            print(f"  Name: {info['name']}")
            print(f"  Input Channels: {info['maxInputChannels']}")
            print(f"  Default Sample Rate: {int(info['defaultSampleRate'])} Hz")
            if i == p.get_default_input_device_info()['index']:
                print("  *** DEFAULT INPUT DEVICE ***")

    print("\n" + "=" * 80)
    print(f"Found {len(input_devices)} input device(s)")
    print("=" * 80)

    p.terminate()

    return input_devices

if __name__ == "__main__":
    list_audio_devices()
