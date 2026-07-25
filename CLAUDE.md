# CLAUDE.md

Agent guidance for this repo. `README.md` = user docs. `docs/PROJECT_ANALYSIS.md` = full
pipeline/architecture/known-issues writeup. `docs/RETRAIN_PLAN.md` = staged plan for the
accent-mismatch fix (local-only, not committed).

## What this is

Text-independent speaker verification (1:1) / identification (1:N) from voice, ResNet-18
embedding model. Pipeline: `DB_wav_reader.py`/`SR_Dataset.py` (features) → `model/model.py`
(`background_resnet`) → `verification.py`/`identification.py` (inference).

## Running things

Smoke test after any change: `python run_test.py` — self-contained, rebuilds gallery fresh from
`feat_logfbank_nfilt40/test/<spk>/enroll.p`, auto GPU/CPU.

`identification.py` reads precomputed `enroll_embeddings/*.pth` instead — regenerate w/ `enroll.py`
after retraining or they go stale silently.

## Hard constraints

- **No new PII exposure.** `enroll_embeddings/*.pth` (all names), `recording.wav`,
  `test_wavs/{sanjay,swarna}` already public on `main` pre-cleanup (see PROJECT_ANALYSIS.md) —
  matched, not hidden. `feat_logfbank_nfilt40/test/{gopika,sanjay,swarna}` + `website/` `.wav`
  recordings were **not** exposed, stay excluded (`.gitignore`). New real-named speaker data:
  check exposure first, ask before committing — not a unilateral call.
- **One checkpoint ships**: `checkpoint_13`, lowest EER across 31-speaker accent-diverse eval, not
  assumed (see PROJECT_ANALYSIS.md). No early stopping; checkpoints 31-40 are broken (collapsed) —
  "newer = better" false here. Swap checkpoint → **must** regenerate `enroll_embeddings/*.pth` w/
  `enroll.py` — cross-checkpoint embeddings are non-comparable, garbage scores otherwise (bit us
  once already).
- **Known accent/domain-mismatch limitation**, not just threshold tuning: accepts
  out-of-distribution speakers fine, worse at discriminating *within* that group (14% cohort EER
  vs 0.17% training-matched). See PROJECT_ANALYSIS.md before claiming this works for populations
  unlike training data.
- **No force-push.** `main`/`master` = real published repo. Branch + PR, not history rewrite,
  unless explicitly asked otherwise.

## Environment

Needs a conda env w/ working GPU PyTorch build (see PROJECT_ANALYSIS.md / CLAUDE_HANDOFF.md for
machine-specific env/versions found during setup). Fresh `pip install -r requirements.txt` may not
match the validated GPU build — CUDA torch needs the right wheel for the driver.

## Known non-obvious things

- `train1.py`: broken/abandoned `train.py` variant, don't reference.
- `EER.py`: not runnable as shipped (hardcoded original-author path), documents the FAR/FRR sweep
  approach only.
- `dat.py`, `enp.py`, `split.py`, `te1.py`, `test.py`: one-off experiments, not core pipeline,
  extra deps (`librosa`, `tensorflow`, `pydub`) not otherwise needed.
- `sp.py`: feature-extraction helper used by `gui.py`/`gui_enroll.py` (`sp.main()`), so it's
  semi-core, not purely peripheral. Two dead imports (`tensorflow`, `IPython.display`, unused
  anywhere in the file) removed. Paths now come from `configure.py`
  (`GUI_TEST_RAW_DIR`/`GUI_ENROLL_RAW_DIR`/`TEST_FEAT_DIR`), not hardcoded. Output filename fixed
  to `enroll.p`/`test.p` (was writing `<name>.p`, which `enroll.py`'s file classifier — matches on
  `'enroll.p'`/`'test.p'` substrings — silently never picked up; this is why `gui_enroll.py` looked
  like it enrolled someone but didn't).
- `gui.py`/`gui_enroll.py`: paths are now repo-relative like the rest of the pipeline. Recordings
  land in `gui_recordings/{test,enroll}/<name>/` — real voices, gitignored, never commit.
- `website/`: separate Node/Express+Firebase app in this Python repo at user's request —
  independent (own `package.json`/`node_modules/`, gitignored).
