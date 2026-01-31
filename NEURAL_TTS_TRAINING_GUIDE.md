# Training a Neural Sindhi TTS Model

## Current Status
- ✅ **Phoneme-based TTS**: Ready now, works without training
- 🔄 **Neural TTS**: Template provided, requires data & GPU

## Option 1: Use Current Phoneme-Based Engine (Recommended for Now)

The `universal_tts.py` engine is:
- **Immediate**: Works right now
- **Self-contained**: No external dependencies
- **Emotion-aware**: Adjusts prosody based on emotion
- **Multilingual**: English, Urdu, Sindhi

### Advantages
- No training needed
- No GPU required
- Small file size
- Deterministic output

### Limitations
- Less natural-sounding than neural models
- Limited prosody variety
- Fixed phoneme inventory

---

## Option 2: Train Neural TTS (Advanced)

### Requirements

#### Data
```
minimum: 10 hours Sindhi speech
optimal: 50+ hours diverse speakers
preferred: 100+ hours with emotion variations
```

#### Hardware
- **GPU**: NVIDIA RTX 3060 or better (8GB+ VRAM)
- **RAM**: 16GB+ system RAM
- **Disk**: 100GB free space
- **Training time**: 24-48 hours

#### Software
```bash
# Core TTS framework
pip install TTS

# PyTorch with GPU support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Audio processing
pip install scipy librosa soundfile

# Optional: Monitoring
pip install tensorboard wandb
```

### Step 1: Collect Data

```
sindhi_dataset/
├── audio/
│   ├── speaker_001/
│   │   ├── 00001.wav
│   │   ├── 00002.wav
│   │   └── ...
│   ├── speaker_002/
│   └── ...
└── metadata.txt
```

**Metadata format** (`metadata.txt`):
```
speaker_001/00001.wav|توهان جو استقبال آهي|speaker_001|happy
speaker_001/00002.wav|مون کو خوشی ٿي آهي|speaker_001|neutral
speaker_002/00001.wav|سنڌ جو نام لوڪ ڪریو|speaker_002|neutral
```

### Step 2: Prepare Dataset

```python
from neural_sindhi_tts import SindhiTTSTrainer

trainer = SindhiTTSTrainer()

# Prepare dataset
dataset_file = trainer.prepare_dataset(
    audio_dir="./sindhi_dataset/audio",
    metadata_file="./sindhi_dataset/metadata.txt",
    output_dir="./processed_dataset"
)

print(f"Dataset prepared: {dataset_file}")
```

### Step 3: Fine-tune Model

```python
from neural_sindhi_tts import SindhiTTSTrainer

trainer = SindhiTTSTrainer()

# Train model
trainer.train(
    dataset_file="./processed_dataset/metadata.json",
    output_model_path="./models/sindhi_tts_finetuned",
    epochs=50,
    batch_size=16,
    learning_rate=1e-4
)
```

### Step 4: Use Trained Model

```python
from neural_sindhi_tts import NeuralSindhiTTS

# Load trained model
tts = NeuralSindhiTTS(
    model_name="./models/sindhi_tts_finetuned"
)

# Synthesize speech
audio = tts.synthesize(
    text="سنڌ جو جاري رکیو",
    language="sd",
    emotion="happy"
)
```

---

## Option 3: Use Pre-trained Multilingual Models

### Coqui XTTS V2 (Recommended)
- Supports 14+ languages including Arabic script
- Can generalize to Sindhi with minimal data
- Supports emotion and speaker control

```python
from TTS.api import TTS

# Zero-shot synthesis (no training needed)
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)

audio = tts.tts(
    text="سنڌي متن",
    language="ur",  # Use Urdu as closest match
    speaker_wav="reference_speaker.wav"  # Optional
)
```

### Meta TTS (Multilingual)
- Multi-language synthesis
- Good generalization to unseen languages
- Smaller model size

```python
from TTS.api import TTS

tts = TTS("tts_models/multilingual/multi-dataset/glow-tts", gpu=False)
audio = tts.tts("سنڌي متن", language="ur")
```

---

## Data Collection Strategy

### If You Have No Data Yet

1. **Use Existing Resources**
   - Radio archives
   - Podcast recordings
   - YouTube Sindhi content
   - Academic recordings

2. **Crowdsource**
   - Hire native speakers on Fiverr/Upwork
   - Record 5-10 minutes per person
   - ~100 people = 500-1000 hours easily

3. **Synthesize Incrementally**
   - Start with phoneme engine
   - Collect user feedback
   - Improve over time

### Data Annotation Process

For each audio file, collect:
- **Text**: Exact Sindhi transcription
- **Speaker ID**: Who recorded it
- **Emotion**: happy, sad, angry, calm, neutral
- **Quality**: Mark noise/issues
- **Duration**: Audio length in seconds

---

## Comparison: Phoneme vs Neural

| Feature | Phoneme | Neural |
|---------|---------|--------|
| Setup Time | Minutes | Days/Weeks |
| Training Data | None | 10+ hours |
| GPU Required | No | Yes (recommended) |
| Sound Quality | Fair | Excellent |
| Latency | 100-500ms | 500-2000ms |
| Customization | Medium | High |
| Deployment Size | <1MB | 200-500MB |
| Maintenance | Low | High |
| Cost | $0 | GPU costs |

---

## Hybrid Approach (Recommended)

1. **Now**: Use phoneme-based TTS
2. **Phase 1**: Collect 10-20 hours of Sindhi speech
3. **Phase 2**: Fine-tune neural model with collected data
4. **Phase 3**: Deploy neural model, keep phoneme as fallback

---

## Resources for Training

### Sindhi Language Resources
- Sindhi Wikipedia articles
- Sindhi literature database
- Sindhi dictionary (Platts/Ferozpur)
- Academic papers on Sindhi phonology

### TTS Training Guides
- [Coqui TTS Documentation](https://github.com/coqui-ai/TTS)
- [TTS Training Guide](https://github.com/coqui-ai/TTS/tree/dev/recipes)
- [FastSpeech2 Training](https://github.com/ming024/FastSpeech2)

### Community
- [Sindhi Language Community](https://www.sindhi.org)
- [TTS Researchers Discord](https://discord.gg/CnyXx66)
- [Audio Processing Forums](https://dsp.stackexchange.com)

---

## Next Steps

### If Using Current System
1. Deploy phoneme-based TTS
2. Gather user feedback
3. Improve phoneme mappings

### If Training Neural Model
1. Collect/source 10+ hours Sindhi speech
2. Annotate with text transcriptions
3. Set up training environment (GPU)
4. Fine-tune base model
5. Evaluate output quality
6. Deploy and iterate

---

## Questions?

- **Quality issues?** Improve phoneme mappings
- **Need more naturalness?** Collect data and train neural model
- **GPU not available?** Use cloud GPU (AWS, Google Colab, Lambda Labs)
- **Limited budget?** Start with phoneme engine, scale gradually

---

**Current Recommendation**: Use the phoneme-based engine in production now, parallelize data collection for future neural model training.
