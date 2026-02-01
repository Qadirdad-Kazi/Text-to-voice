from universal_tts import create_universal_tts
from tts_pipeline import TTSPipeline
from emotion_detector import create_emotion_detector


def test_urdu_phoneme_accuracy_basic():
    engine = create_universal_tts()
    detector = create_emotion_detector(multimodal=False)
    pipeline = TTSPipeline(engine, detector)

    text = "یہ ایک سادہ جملہ ہے۔"
    audio, meta = pipeline.synthesize(text=text, language="Urdu", emotion="neutral")

    assert audio is not None and len(audio) > 1000
    assert meta["normalized_text"]
    assert meta["token_count"] > 0


def test_urdu_pause_timing():
    engine = create_universal_tts()
    pipeline = TTSPipeline(engine, None)

    text = "یہ جملہ، وقفے کے ساتھ ہے۔"
    units = pipeline.debug_units(text=text, language="Urdu", emotion="neutral")

    assert any(u["is_pause"] for u in units)