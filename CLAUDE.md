# CLAUDE.md

Guidance for Claude Code (or any agent) working in this repo. See `README.md` for user-facing docs
and `docs/PROJECT_ANALYSIS.md` for the full pipeline/architecture writeup and known-issue history.

## What this project is

Text-independent speaker verification (1:1) and identification (1:N) from voice, using a
ResNet-18 embedding model. Core pipeline: `DB_wav_reader.py`/`SR_Dataset.py` (features) →
`model/model.py` (`background_resnet`) → `verification.py`/`identification.py` (inference).

## Running things

Use `run_test.py` as the reference smoke test after any change — it's self-contained, rebuilds
the enrollment gallery fresh from `feat_logfbank_nfilt40/test/<spk>/enroll.p`, and auto-detects
GPU vs CPU:

```bash
python run_test.py
```

`identification.py` instead reads precomputed `enroll_embeddings/*.pth` — regenerate those with
`enroll.py` after retraining, or they'll silently go stale.

## Hard constraints — do not violate

- **Don't newly expose personally-identifiable voice data.** `enroll_embeddings/*.pth` (all
  names), `recording.wav`, and `test_wavs/{sanjay,swarna}` are already public on this repo's
  `main` from before this cleanup — see docs/PROJECT_ANALYSIS.md — so this branch matches that
  existing exposure rather than pretending it isn't there. But `feat_logfbank_nfilt40/test/
  {gopika,sanjay,swarna}` and any `website/`-captured `.wav` recordings were **not** already
  exposed and are deliberately excluded (`.gitignore`) — don't add those or any newly-recorded
  real-named speaker's data without checking whether it's already public first. When in doubt,
  ask before committing anything under a real person's name; this is not a settled, low-stakes
  call to make unilaterally.
- **Only one checkpoint ships in `model_saved/`** (`checkpoint_13`, chosen by lowest EER across a
  31-speaker accent-diverse evaluation, not assumed — see `docs/PROJECT_ANALYSIS.md`). This
  codebase has no early stopping; later checkpoints (31-40) are actually broken (model collapse),
  so "newest epoch = best" is false here. If you retrain and swap checkpoints, you **must**
  regenerate `enroll_embeddings/*.pth` with `enroll.py` afterward — embeddings from different
  checkpoints live in different, non-comparable vector spaces, and mixing them silently produces
  garbage cosine-similarity scores (this bit us once already during this cleanup).
- **This model has a known accent/domain-mismatch limitation**, not just a threshold-tuning one:
  it accepts genuine out-of-distribution-accent speakers fine, but is measurably worse at telling
  different speakers *within* that group apart from each other (14% cohort EER vs 0.17% for the
  training-matched dataset speakers). See `docs/PROJECT_ANALYSIS.md` before claiming this works
  well for any population that doesn't resemble the original training data.
- **Don't force-push.** This repo's `main`/`master` is a real, published GitHub repo. Publish
  changes via a branch + PR, not by rewriting history, unless the user explicitly asks otherwise.

## Environment

This project depends on a specific conda env with a working GPU-enabled PyTorch build (see
`docs/PROJECT_ANALYSIS.md` / `CLAUDE_HANDOFF.md` for machine-specific env names/versions found
during setup — don't assume `pip install -r requirements.txt` into a fresh env matches the
validated GPU build; CUDA-enabled torch needs the right wheel for the driver).

## Known non-obvious things

- `train1.py` is a broken, abandoned variant of `train.py` — don't use it as a reference.
- `EER.py` is not runnable as shipped (hardcoded absolute path from the original author's
  machine) — it documents the FAR/FRR/threshold-sweep approach, not a working script.
- `dat.py`, `enp.py`, `sp.py`, `split.py`, `te1.py`, `test.py` are one-off experiments, not part of
  the supported pipeline, and pull in extra deps (`librosa`, `tensorflow`, `pydub`) that the core
  pipeline doesn't need.
- `website/` is a separate Node/Express + Firebase app living inside this Python repo at the
  user's request — treat it as independent (own `package.json`, own `node_modules/`, gitignored).
