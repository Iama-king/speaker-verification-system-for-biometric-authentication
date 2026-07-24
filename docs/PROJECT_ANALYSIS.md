# Project Analysis — Speaker Recognition (fix/reproducibility)

## What this is

A text-independent speaker recognition system: verify a claimed identity (1:1) or identify a
speaker from an enrolled gallery (1:N) from a short utterance. Built on the tutorial by
[jymsuper](https://github.com/jymsuper/SpeakerRecognition_tutorial); this fork made it runnable
outside the original author's machine (hardcoded `D:/audio/...` paths, forced CUDA, a stale
`librosa` import that crashed CPU-only runs, a verification threshold that rejected real users)
and removed personally-identifiable voice data before publishing.

## Pipeline

```
wav (16kHz)
  → log-mel filterbank features, 40 filters   (DB_wav_reader.py, SR_Dataset.py)
  → ResNet-18 backbone                        (model/resnet.py)
  → adaptive avg-pool → 128-d FC               (model/model.py: background_resnet)
  → L2-normalized speaker embedding
  → cosine similarity vs. enrolled embedding(s)
  → accept/reject (verification) or best-match speaker (identification)
```

`background_resnet` trains with a classification head (`num_classes=240`) predicting speaker
identity; the 128-d penultimate layer (`spk_embedding`, before the classification head) is what
gets used at inference time as the voiceprint.

## Core entry points

| File | Role |
|---|---|
| `train.py` | Trains the ResNet-18 background model from `feat_logfbank_nfilt40/train`. |
| `enroll.py` / `gui_enroll.py` | Extracts an embedding for a speaker and saves it to `enroll_embeddings/<name>.pth`. |
| `verification.py` / `gui.py` | 1:1 — compares a test utterance against one claimed enrolled speaker. |
| `identification.py` | 1:N — compares a test utterance against every embedding in `enroll_embeddings/`. |
| `run_test.py` | Self-contained smoke test: rebuilds the gallery fresh from `feat_logfbank_nfilt40/test/<spk>/enroll.p` (doesn't depend on possibly-stale `enroll_embeddings/*.pth`), scores every `test.p`. **Use this as the source of truth for "does the model still work."** |
| `EER.py` | Equal-error-rate / FAR-FRR threshold sweep. Currently hardcoded to a `D:/audio/rsp/test` path from the original author's machine — not runnable as-is; kept for reference on how to derive a threshold from your own data. |

## Peripheral / experimental scripts (not part of the core pipeline)

`dat.py`, `enp.py`, `sp.py`, `split.py`, `te1.py`, `test.py` are one-off feature-extraction/audio-
splitting experiments. They depend on packages the core pipeline doesn't need (`librosa`,
`python_speech_features`, `pydub`, `tensorflow`) and several hardcode `D:/audio/...` paths. They
aren't required to train, enroll, verify, or identify — left in place for reference, not treated as
supported entry points. `train1.py` is an abandoned variant of `train.py` (its `train_val_split()`
is an empty stub — a syntax error if actually run).

## Known issues and how this branch addresses them

1. **Hardcoded paths / forced CUDA** (`identification.py`, `verification.py`) — fixed: paths are
   now repo-relative via `configure.py`, and `use_cuda = torch.cuda.is_available()` so it runs on
   CPU-only machines too.
2. **`librosa` crashed CPU/GPU runs that don't need it** (`DB_wav_reader.py`) — fixed: lazy import,
   only pulled in when raw-wav feature extraction is actually used.
3. **Verification threshold too strict, then re-derived properly** — the original threshold was
   `0.98`, but genuine scores on the bundled data dip well below that, which would reject
   legitimate users. Set to `0.96`, the measured EER point on a 31-speaker (accent-diverse)
   evaluation — see "Checkpoint choice, EER, and threshold" below. Not a fixed value forever:
   re-derive from your own enrollment data before production use.
4. **`enroll_embeddings/` gallery pollution** — the gallery had accumulated embeddings from ~22
   people recorded at different times/checkpoints alongside the 10 speakers from the bundled
   dataset, and `identification.py` (unlike `run_test.py`) reads that gallery directly. This caused
   a real misidentification (a query for one enrolled speaker matched a different, stale entry).
   Two causes, both addressed: (a) the public gallery now only contains the 10 anonymized dataset
   speakers (see PHI section below), removing the stale/inconsistent entries; (b) `enroll.py` had
   the same hardcoded-CUDA/hardcoded-path bugs as `identification.py`/`verification.py` and its
   embeddings weren't regenerated when the checkpoint changed — fixed the same way, and
   `enroll_embeddings/*.pth` for the 10 shipped speakers were regenerated against the checkpoint
   actually in use (checkpoint_13). Mixing embeddings computed under different checkpoints gives
   meaningless cosine-similarity scores, since each checkpoint's embedding space isn't comparable to
   another's — this is a sharp edge worth remembering if you ever swap checkpoints again:
   regenerate the gallery, don't just swap the `.pth` file.
5. **`identification.py` returned the wrong confidence score** — `perform_identification()` printed
   and returned whatever speaker's score happened to be last in the loop, not the actual best match
   (`max_score`). The identification result itself was correct (computed from `max_score`
   internally), but the reported confidence number was misleading. Fixed to return `max_score`.
6. **No requirements.txt / run instructions** — added `requirements.txt` and a proper `README.md`.

## Personally-identifiable data

This repo's working tree has voice biometric data (embeddings and/or raw `.wav`) for real, named
individuals — friends/classmates who'd been recorded to test enrollment/identification, alongside
the 10 speakers from the original anonymized-code tutorial dataset (`103F3021`, `207F2088`,
`213F5100`, `217F3038`, `225M4062`, `229M2031`, `230M4087`, `233F4013`, `236M3043`, `240M3063`).

During this cleanup it turned out that `enroll_embeddings/*.pth` (all 32 names), `recording.wav`,
and `test_wavs/{sanjay,swarna}` were **already public** on this repo's `main` branch from before —
so excluding them from this branch would not have actually protected anyone, only made this
particular branch inconsistent with what's already live. Given that, this branch matches that
existing exposure (regenerating the embeddings against the checkpoint actually in use, so they're
at least functionally correct — see below) rather than pretending it isn't there. Two things were
**not** already exposed and are deliberately kept that way (excluded via `.gitignore`, not added
here): `feat_logfbank_nfilt40/test/{gopika,sanjay,swarna}` (extracted features) and raw `.wav`
recordings captured through `website/`'s enroll/validation flow — no reason to create *new*
exposure beyond what already exists.

**This is not the same as saying the exposure is fine.** Voiceprints are biometric identifiers,
and this data appears to have been published without the recorded individuals' consent. If you
want this actually fixed rather than just not made worse, the real remedy is rewriting `main`'s
git history to strip these files from every commit (not just removing them going forward — a
later commit that deletes a file doesn't remove it from earlier commits), and being aware that if
the repo has ever been cloned or forked by anyone else, they may still have a copy regardless of
what happens to this repository. This was explicitly deferred, not solved, during this session.

## model_saved/ checkpoint choice, EER, and threshold

40 training checkpoints existed locally (287MB). Rather than assume the checkpoint referenced in
upstream docs (`checkpoint_24`) was actually best, every checkpoint was evaluated for identification
accuracy and equal-error-rate (EER) — see `docs/eer_plot.png`.

- **Checkpoints 31-40 are broken.** The model collapsed: 7.7-15.4% identification accuracy,
  impostor scores up to 1.0 (i.e. it started outputting near-identical embeddings for everyone).
  Never use these, regardless of what a "later epoch = better" assumption would suggest.
- **Checkpoints 1-30 all pass** on the bundled 10-speaker set, but their real-world EER differs
  meaningfully once tested against a larger, accent-diverse population (see below). **checkpoint_13**
  had the lowest EER and is the one shipped; only it is tracked in `model_saved/` (see `.gitignore`
  for how the rest are excluded).
- A first pass sized the eval set at only 3 extra speakers and picked a different checkpoint;
  re-running against a proper-sized population changed the answer (see "Known limitation" below) —
  a reminder that small eval sets pick winners by noise, not signal.
- **Verification threshold: 0.96**, set at the measured EER point (EER ≈ 13%) on a 31-speaker set —
  not the ~0.89 threshold you'd get from the bundled 10 speakers alone, which understates real-world
  error. Re-derive for your own enrolled population before relying on this in production.

## Known limitation: accent/domain mismatch, not just a threshold problem

Testing against a larger, accent-diverse population (beyond what's bundled in this repo) surfaced a
real limitation: this model accepts genuine speakers outside its training distribution just fine —
genuine-match scores for that group were, if anything, *higher* on average than for the
training-matched bundled speakers. The actual problem is **discrimination between individuals**
within an out-of-distribution accent group: impostor (wrong-speaker) scores run substantially higher
in that group, meaning the model is less able to tell different speakers apart when their accent
doesn't match what it was trained on. This is consistent with embeddings clustering more tightly for
an unfamiliar domain — the model can tell "this is roughly the right kind of speaker" but has less
resolving power between individuals within that group.

Practical implications:
- A higher verification threshold (0.96, above) partly compensates by trading false accepts for
  more false rejects — appropriate for authentication, but not a full fix.
- **A threshold alone can't fix an embedding space that doesn't separate speakers well.** If you
  need reliable identification/verification for a population whose accent differs from the
  original training data, the real fix is fine-tuning or retraining on representative data.
- This also explains, more fundamentally than "stale embeddings," why the original
  `identification.py` gallery-pollution bug happened: even with a consistent, non-stale gallery,
  this class of confusion between out-of-distribution speakers is a real model limitation.

## Repo hygiene notes for future work

- `feat_logfbank_nfilt40/` (extracted features for the 10 anonymized speakers) and `model_saved/`
  (one checkpoint) are the only large-ish tracked assets; both are necessary for `run_test.py` to
  be self-contained.
- `website/` is a separate Node/Express + Firebase front-end kept in-repo at the user's request;
  its `node_modules/` is gitignored.
- If this project grows real (consented) enrollment data again, keep it out of git entirely (a
  gitignored local directory or a separate private data store), not just out of the default branch.
