import base64

from universal_tts import create_universal_tts
from tts_pipeline import TTSPipeline
from emotion_detector import create_emotion_detector


def test_sindhi_phoneme_accuracy_basic():
    engine = create_universal_tts()
    detector = create_emotion_detector(multimodal=False)
    pipeline = TTSPipeline(engine, detector)

    text = "سنڌي ٻولي خوبصورت آهي."
    audio, meta = pipeline.synthesize(text=text, language="Sindhi", emotion="neutral")

    assert audio is not None and len(audio) > 1000
    assert meta["normalized_text"]
    assert meta["token_count"] > 0


def test_sindhi_emotion_serious():
    engine = create_universal_tts()
    detector = create_emotion_detector(multimodal=False)
    pipeline = TTSPipeline(engine, detector)

    text = "هي هڪ سنجيده اعلان آهي."
    audio, meta = pipeline.synthesize(text=text, language="Sindhi", emotion="serious")

    assert audio is not None and len(audio) > 1000
    assert meta["emotion"] == "serious"