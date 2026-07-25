# Should the original 240 speakers stay in the retraining set?

Opus analysis pass, 2026-07-25, answering a question raised while scoping `docs/RETRAIN_PLAN.md`:
given the original 240 training speakers, the 21 Indian speakers on hand, and prospective new
corpora (Common Voice ~1,000 Indian-accent speakers, IndicVoices sample, VoxCeleb2 ~6,112 speakers)
are wildly different sizes, does combining them skew the retrained model? Should the original 240
(domain-different from the target Indian-accented-English population) be excluded?

**Recommendation up front: keep them, and fix the one imbalance mechanism that is actually real
with a five-line sampler change. Dropping them would cost real supervision to solve a problem that
mostly doesn't exist in the form suspected — and would leave the mechanism actually at play
completely unaddressed.**

Note: the 240 original training speakers' actual nationality/accent/language was never
conclusively determined — anonymized-code speakers (e.g. "103F3021") from what looks like a
Korean-tutorial-derived corpus. Only confirmed: a different acoustic/recording domain from the 21
Indian-accented speakers (studio read speech vs. phone-recorded), not their actual
ethnicity/accent. "The 240" means "the original training-matched population, domain-different from
the target," not a confirmed-foreign-nationality claim.

---

## 1. "Skew" is three different things here. Only one is real, and it isn't group size.

### (a) Class-count imbalance across domains — 240 vs ~1,000 vs ~6,000. Not a real mechanism.

The model isn't asked to predict "domain" — it predicts *which of N speakers this is*, one class
per speaker. The 240 aren't a group the model can bias toward; they're 240 individual classes
alongside 1,000 other individual classes in a flat N-way problem. There's no label meaning
"original corpus." The classic imbalance pathology ("80% of data is class A, model just predicts
A") requires a majority *label*; there isn't one here.

What class count actually does is set discrimination-task difficulty, which forces a
well-conditioned embedding space — one of the better-established results in the field (the
VoxCeleb1→VoxCeleb2 progression, 1,211→5,994 training speakers, is the canonical demonstration that
speaker *count* is the dominant scaling axis for embedding quality, holding even when extra
speakers come from a different language/nationality/recording condition than the test set).
`RETRAIN_PLAN.md` §4 already says this: "Speaker count dominates hours-per-speaker for this
objective." The 240 aren't a competing population diluting a signal — they're +240 classes of free
supervision on data already extracted, already validated, already on disk. Marginal cost of
including them: approximately zero.

### (b) Per-class utterance-count imbalance — 100/speaker vs ~15-25/speaker. Real, and live in the current code.

`DvectorDataset.__getitem__` indexes a flat utterance-level DataFrame; `train.py`'s `DataLoader`
uses `shuffle=True` over it — uniform sampling over *utterances*, not *speakers*. Each speaker's
gradient-update share is proportional to their utterance count. Post-merge: 240 speakers at 100
chunks each vs. a Common Voice speaker at ~15-25 chunks (after a >=60s filter) — a 4-6x gradient-
share advantage per speaker for the original corpus, and since there are 24,000 of those
utterances, the original domain would supply roughly half of all gradient steps in a Phase-1 merge
despite being ~19% of the classes.

Two consequences: (1) on the classifier head, under-sampled classes get their prototype vector
updated less often while weight decay shrinks it every step regardless — weight norms end up
correlated with class frequency, and since plain-softmax logits are norm-sensitive, rare classes
get systematically smaller logits (long-tailed recognition literature, e.g. Kang et al.,
*Decoupling Representation and Classifier*, 2020). (2) on the backbone, it sees studio-channel
audio in roughly half of all steps, feeding into (c).

Fix cost: ~5 lines (see §4). This is the only mechanism in the original question that requires
action — fixed by changing *how you sample*, not *who's included*.

### (c) Embedding-geometry distortion from domain-correlated shortcuts. Real — and likely what the original instinct was actually detecting.

Even with perfect per-speaker sampling, a classification loss uses the cheapest features that
separate classes. If channel correlates with speaker identity, channel *is* a valid speaker feature
to the loss. Cross-domain pairs (studio vs. phone) become trivially separable, and the model spends
angular budget on a domain axis rather than voice axes. Everything on the phone side of that axis
gets packed into a narrow cone — matching the measured symptom exactly: genuine 0.99, within-cohort
impostor mean 0.795, cohort EER 14.29%. High similarity everywhere inside the Indian-accented
group, both genuine and impostor. The model resolves "which side of the domain axis" well and
"which person within the cone" poorly.

**Dropping the 240 does not fix this.** It removes one domain boundary and leaves the mechanism
intact: Common Voice is crowd-sourced (one contributor = one device = one room, typically one or a
few sittings) — within CV, channel is *nearly perfectly confounded with speaker identity*, a
stronger version of the same trap at finer granularity. IndicVoices and VoxCeleb2 are their own
separate domains too. Homogenizing the training set by deletion isn't achievable — you'd just
choose a different set of domains.

The actual fix for (c): make channel uninformative via MUSAN noise / RIR reverb / codec-bandwidth
simulation applied across *all* sources including the 240, so every speaker appears under many
channels and the shortcut stops paying. Already Phase 2 of `RETRAIN_PLAN.md` — this analysis raises
its priority. Orthogonal to the include/exclude question.

## 2. Does excluding non-target-domain speakers improve Indian-accent discrimination? No.

Negative transfer from adding more speakers of a different domain isn't a supported phenomenon in
speaker verification. The field's consistent finding runs the other way: VoxCeleb-trained encoders
(English, YouTube-sourced, heavily Western-skewed) are routinely deployed as general-purpose
speaker encoders across languages and accents, and work — because "what makes two voices
different" is largely accent-invariant vocal-tract/prosodic structure. The documented failure mode
is narrow training data → domain shift at test time, not extra domains contaminating a target
domain.

Risk asymmetry:

| | Include the 240 | Exclude them |
|---|---|---|
| Upside | +240 classes; +24k utts of dense per-speaker phonetic coverage; a second domain that makes channel-invariance learnable; the repo's own regression gate stays meaningful | Removes a gradient-share imbalance already fixable for free with a sampler |
| Downside | Gradient-share imbalance — fully fixable, ~5 lines, zero data cost | Fewer classes; more homogeneous training set; loses the only non-crowd-sourced domain; breaks the shipped demo |
| Evidence base | Well-established (scaling with speaker count) | Speculative |

Concrete cost specific to this repo: `run_test.py` and the shipped `enroll_embeddings/*.pth` are
ten of the 240 anonymized speakers, and `RETRAIN_PLAN.md` §5 makes "dataset-cohort EER must stay
<1%" a hard gate. Train without the 240 and that cohort becomes out-of-domain by construction —
near-certain to trip the gate, with no way to distinguish "the domain gap moved" from "the domain
gap closed" — the exact diagnostic that gate exists to provide.

Honest scoping: not much either way. The 240 are ~19% of classes in a Phase-1 pool (~1,240) and
~3% in a Phase-3 pool with VoxCeleb2 (~7,350). The load-bearing decisions are AAM-softmax, total
speaker count, and augmentation — not this. What makes the call easy isn't that the benefit is
large; it's that the cost is zero. The features exist, in the right format, verified. Include them.

## 3. Does AAM-softmax change the answer? Yes — removes most of the imbalance concern by construction.

What AAM fixes structurally: L2-normalizes both class prototype and feature, so every logit is
`s*cos(theta)` — eliminates the weight-norm-vs-frequency coupling entirely (the dominant long-tail
pathology in plain softmax can't occur when prototype norms are constrained to 1; normalized/cosine
classifiers are a standard long-tailed-recognition prescription for exactly this). The margin `m`
applies identically regardless of class frequency, so a 15-utterance speaker is held to the same
angular-separation standard as a 100-utterance one (plain softmax only demands correct ranking,
settling for a razor-thin margin on rare classes). It also optimizes cosine geometry — the metric
actually scored at inference, strictly stronger than plain softmax's linear separability.

What AAM does *not* fix, and may worsen: backbone gradient share still follows utterance counts
(still need the sampler), and it does nothing about the domain shortcut in (c) — worse, AAM applies
*stronger* separation pressure, and the cheapest way to open an angular margin between a studio and
phone speaker is the channel axis. **AAM can amplify shortcut learning when a shortcut is
available**, raising (not lowering) the value of Phase 2 augmentation.

Net: AAM neutralizes the classifier-side half of the concern; sampling handles the backbone-side
half; augmentation handles the geometry. Which speakers are included isn't the lever for any of the
three.

### A finding not currently in RETRAIN_PLAN.md §3

`model/model.py` returns `spk_embedding` (raw `fc0` output) as the voiceprint (`enroll.py:54` uses
exactly that). But the classifier consumes a *different* vector:

```python
spk_embedding = self.fc0(out)
out = F.relu(self.bn0(spk_embedding))   # <-- classifier sees this
out = self.last(out)
```

Two consequences of bolting AAM onto `self.last` as-is: (1) the angular margin is imposed in the
post-BN/post-ReLU space, not the space cosine-scored at inference — a substantial fraction of AAM's
benefit leaks away through that mismatch. (2) The ReLU confines the classifier's feature space to
the **non-negative orthant**, where every pairwise cosine is >= 0 and the maximum achievable angle
between any two embeddings is 90 degrees, not 180. A hard cap on angular spread and a plausible
structural contributor to "impostor scores run too high" — the symptom being fixed.

For the retrain: remove the ReLU (BN-only, or nothing) and apply the AAM head to the same vector
exported as the embedding. Small change, disproportionate value, independent of every data question
here.

## 4. The mitigation to actually implement (two things, not a menu)

**1. Speaker-balanced sampling — do this.** In `train.py`, replace `shuffle=True` with a
`WeightedRandomSampler` where each utterance's weight is `1 / n_utts(its speaker)`,
`replacement=True`, `num_samples ~= n_speakers * 25`. Every speaker then contributes an equal
expected number of gradient updates per epoch regardless of source corpus, and all 24,000 original
utterances stay reachable across epochs. Five lines, no `DvectorDataset` change, no loss change,
works for any future corpus mix.

*Simpler alternative:* cap utterances per speaker at ~25 when building the manifest in
`tools/prepare_features.py`. Zero training-loop changes, cuts epoch time (bottleneck is I/O per
plan §4) — cost is permanently discarding 75% of the original corpus's content diversity instead of
resampling different subsets each epoch. The sampler is better.

**2. Per-domain metrics during training — do this.** Log training accuracy and dev EER *split by
source corpus*, not just pooled. Turns "is this skewing?" from a theoretical worry into a number
readable off a chart at epoch 5.

**Explicitly do not do:**
- **Class-weighted loss** — mathematically similar to resampling but much higher gradient variance
  on rare classes, interacts badly with AAM's fixed-margin geometry. With ~1,240-7,000 classes and
  only ~5x imbalance, resampling is strictly better behaved, and AAM already closed the pathway
  class weighting would correct.
- **Sub-sampling the 240 *speakers* down to match corpus scale** — never delete classes to fix
  imbalance in metric learning; classes *are* the supervision. Cap utterances, never speakers.
- **Explicit domain-balanced batching** — unnecessary. Once per-speaker sampling is uniform over a
  pooled class label set, batch domain proportions automatically track class proportions, the
  correct target. Don't add machinery.

## 5. The bill if excluded anyway

- **-240 classes**: ~19% of a Phase-1 pool, ~3% of a Phase-3 pool with VoxCeleb2. Meaningful in
  Phase 1, marginal in Phase 3.
- **-24,000 utterances / ~27h**, likely *more than half* of Phase-1 training volume before
  VoxCeleb2 lands.
- **The densest per-speaker content coverage in the entire planned pool**: each of the 240 has
  exactly 100 pickles, 100 *distinct read prompts* (`SNR084F2MIC102051_ch01` ... `...102150_ch01`,
  sequential). Common Voice at >=60s/speaker gives maybe 15-25 chunks of far less linguistic
  variety. Since the model is *text-independent* verification, 100 different sentences per speaker
  is exactly the "same voice, different words" signal — the scarcest thing in the rest of the plan.
- **The only non-crowd-sourced domain**, and therefore what makes channel-invariance learnable
  rather than just hoped-for.
- **The regression gate and shipped 10-speaker demo** (`run_test.py`, `enroll_embeddings/`) go
  out-of-domain.

**Premise correction** (cuts against an initial assumption): expected the 240's `MIC..._ch01`
filenames to indicate multi-mic/multi-session capture per speaker. They don't — every file for a
given speaker shares one MIC prefix and `_ch01`. So the 240 provide **content diversity, not
channel diversity**; per-speaker channel is as confounded there as in Common Voice. Strengthens the
augmentation argument (§1c), weakens any claim the 240 supply channel robustness on their own.
(Inference from filenames, not verified, and moot since only features survive locally, not raw
audio.)

## 6. Final recommendation

**Include the original 240. Add a `WeightedRandomSampler` weighted by `1/n_utts_per_speaker`. Keep
AAM-softmax. Keep Phase 2 augmentation, treated as higher priority than before this analysis.**

Plain terms: the instinct that something can go wrong with mismatched groups is correct, but the
thing that goes wrong isn't group *size* — it's that the model hears one group 5x more often per
speaker, and recordings from one group all share a microphone. Both are fixed by changing *how the
data is fed*, not by deleting data. Deleting the 240 throws away a fifth of the training classes
and the densest per-speaker speech, and doesn't touch either actual problem.

For certainty rather than argument: the ablation is cheap. Phase 1 trains two models identical
except for the presence of the 240, compared on the speaker-disjoint dev split and Svarah — never
on the 21, per plan §5. One extra overnight run on the 3060. Predicted: a small edge for including
them, larger in Phase 1 than Phase 3 — but that's a prediction, and the run costs one night.

Scope note restated: none of this touches the 21 on-hand speakers. They stay frozen as the
acceptance set under every branch of this recommendation.

## Top uncertainties

1. **The accent-vs-channel confound is still unresolved and dominates this analysis.** If Phase 0
   shows the gap is channel rather than accent, augmentation is the entire fix, the Indian-corpus
   sourcing effort is largely wasted, and this include/exclude question becomes nearly irrelevant —
   retraining on the original data plus augmentation would capture most of the win. Run Phase 0
   before spending on data.
2. **Common Voice's actual per-speaker yield after a >=60s filter is unverified**, and it sets how
   much the 240 matter proportionally. If CV yields 300 usable Indian speakers rather than 1,000,
   the 240 become ~44% of a Phase-1 class pool rather than ~19%, and excluding them would go from
   "mildly harmful" to "clearly harmful." The recommendation doesn't flip either way, but the stakes
   rise sharply if CV under-delivers.

## Critical files for implementation

- `train.py` — sampler change (`shuffle=True` -> `WeightedRandomSampler`), per-domain metric
  logging, LR schedule
- `model/model.py` — AAM head; remove the `F.relu(self.bn0(...))` before the classifier so the
  margin applies to the exported embedding
- `SR_Dataset.py` — `DvectorDataset` is where per-speaker counts must be exposed to build sampler
  weights
- `DB_wav_reader.py` — `read_feats_structure` builds the flat utterance manifest; the
  `source`/`speaker_id` columns needed for balancing and per-domain reporting originate here
- `docs/RETRAIN_PLAN.md` — §3 (training approach) and §7 Phase 1/2 priority ordering should be
  updated to reflect the sampler and the raised priority of augmentation
