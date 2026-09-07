# Phase 3 dataset intake

The current Phase 3 data is insufficient: it contains only three REAL and three SYNTHETIC source recordings. Do not alter the old artifact or its metadata. Add a new consented dataset using this layout:

```text
data/raw/
  real/
    <source_dataset>/
      <language>/
        <speaker_id>/
          <unique_recording>.wav
  fake/
    <generator_or_source_dataset>/
      <language>/
        <claimed_or_source_speaker_id>/
          <unique_recording>.wav
```

For example, `data/raw/real/common_voice/indian_english/spk_0001/rec_001.wav` and `data/raw/fake/tts_system_a/indian_english/spk_0001/clone_001.wav` are mapped to labels `0=REAL` and `1=SYNTHETIC`. The scanner now preserves the three folder values as `source_dataset`, `language`, and `speaker_id` in the generated metadata.

Minimum gate before training:

- At least 100 independent REAL source recordings and 100 independent SYNTHETIC source recordings in the training split.
- At least 400 labelled recordings overall after preserving train/validation/test source separation.
- At least two documented real sources and two documented synthetic generator/source families.
- Both labels in each split, with no speaker, source file, or identical-audio hash crossing splits.
- WAV/FLAC audio that the preprocessing pipeline can convert to 16 kHz mono WAV. Originals remain untouched.

Use many speakers, channels, and synthesis methods. Add Hindi, Indian English, Marathi, Tamil, Telugu, Bengali, Gujarati, Kannada, Malayalam, and Punjabi only when each group has enough held-out examples to evaluate; otherwise it remains `NOT TESTED`.

After adding data, run:

```powershell
python scripts/preprocess_dataset.py
python scripts/phase3_dataset_readiness.py
python scripts/train.py --config configs/training_v4.yaml
python scripts/evaluate.py --config configs/training_v4.yaml --model models/phase3_v4_trained
python scripts/register_model.py --type synthetic_detector --path models/phase3_v4_trained --version v4-trained
```

Do not run the last three commands until the readiness report is `READY`. The registration command prints a model ID. Promote that candidate to staging only after reviewing its real evaluation with `python scripts/promote_model.py --type synthetic_detector --model-id <MODEL_ID> --validation-approved`; the second promotion requires each named governance approval flag. The new artifact path must be configured in `configs/realtime.yaml` only after registration, hash validation, evaluation, and governance promotion succeed.
