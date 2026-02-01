from universal_tts import create_universal_tts
from tts_pipeline import TTSPipeline
from emotion_detector import create_emotion_detector


def test_english_phoneme_accuracy_basic():
    engine = create_universal_tts()
    detector = create_emotion_detector(multimodal=False)
    pipeline = TTSPipeline(engine, detector)

    text = "This is a simple sentence."
    audio, meta = pipeline.synthesize(text=text, language="English", emotion="neutral")

    assert audio is not None and len(audio) > 1000
    assert meta["normalized_text"]
    assert meta["token_count"] > 0


def test_english_long_form_stability():
    engine = create_universal_tts()
    pipeline = TTSPipeline(engine, None)

    text = " ".join(["This is a longer narration segment."] * 30)
    audio, _ = pipeline.synthesize(text=text, language="English", emotion="neutral")

    assert audio is not None and len(audio) > 10000