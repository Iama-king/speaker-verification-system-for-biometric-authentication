"""
Self-contained end-to-end test for the speaker-recognition model.
Builds an enrollment gallery from each speaker's enroll.p and identifies each test.p.
Auto-detects GPU (CUDA) and falls back to CPU. Writes nothing except stdout.

Run from the project root:  python run_test.py
"""
import os, sys, pickle, math, statistics
import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model.model import background_resnet

FEAT = os.path.join('feat_logfbank_nfilt40', 'test')  # 13 speakers, each enroll.p + test.p
CKPT = os.path.join('model_saved', 'checkpoint_13.pth')  # lowest EER of all 40 checkpoints, evaluated on a 31-speaker set
TEST_FRAMES = 100
EMB = 128
NCLS = 240

USE_CUDA = torch.cuda.is_available()
print("=" * 60)
print("ENVIRONMENT")
print("  torch version :", torch.__version__)
print("  CUDA available:", USE_CUDA)
if USE_CUDA:
    print("  GPU           :", torch.cuda.get_device_name(0))
    print("  CUDA version  :", torch.version.cuda)
print("  Device in use :", "GPU (cuda)" if USE_CUDA else "CPU")
print("=" * 60)


def read_MFB(fn):
    with open(fn, 'rb') as f:
        d = pickle.load(f)
    feat = d['feat']
    sf = int(0.5 / 0.01)
    ef = len(feat) - int(0.5 / 0.01)
    return feat[sf:ef, :]


def to_tensor(x):
    x = np.expand_dims(x, 0)
    x = np.expand_dims(x, 1)
    return torch.from_numpy(x.transpose((0, 1, 3, 2))).float()


def l2_norm(inp, alpha):
    b = torch.pow(inp, 2)
    n = torch.sum(b, 1).add_(1e-10)
    norm = torch.sqrt(n)
    out = torch.div(inp, norm.view(-1, 1).expand_as(inp)) * alpha
    return out.view(inp.size())


def get_embedding(model, fn):
    feat = read_MFB(fn)
    tot = math.ceil(len(feat) / TEST_FRAMES)
    act = 0
    with torch.no_grad():
        for i in range(tot):
            seg = feat[i * TEST_FRAMES:i * TEST_FRAMES + TEST_FRAMES]
            if len(seg) < 20:
                continue
            ti = to_tensor(seg)
            if USE_CUDA:
                ti = ti.cuda()
            emb, _ = model(ti)
            if emb.dim() == 1:
                emb = emb.unsqueeze(0)
            act = act + torch.sum(emb, dim=0, keepdim=True)
    return l2_norm(act, 1)


def main():
    model = background_resnet(embedding_size=EMB, num_classes=NCLS)
    if USE_CUDA:
        model.cuda()
    ck = torch.load(CKPT, map_location='cuda' if USE_CUDA else 'cpu')
    model.load_state_dict(ck['state_dict'])
    model.eval()
    print("Model loaded OK from", CKPT)

    spks = sorted([d for d in os.listdir(FEAT) if os.path.isdir(os.path.join(FEAT, d))])
    gallery = {}
    for s in spks:
        ep = os.path.join(FEAT, s, 'enroll.p')
        if os.path.exists(ep):
            gallery[s] = get_embedding(model, ep)
    print("Enrolled %d speakers: %s\n" % (len(gallery), list(gallery)))

    correct = 0
    total = 0
    rows = []
    for s in spks:
        tp = os.path.join(FEAT, s, 'test.p')
        if not os.path.exists(tp):
            continue
        te = get_embedding(model, tp)
        best, bs = None, -9.0
        for g, ge in gallery.items():
            sc = F.cosine_similarity(te, ge).item()
            if sc > bs:
                bs, best = sc, g
        ok = (best == s)
        correct += int(ok)
        total += 1
        rows.append((s, best, bs, ok))

    print("=== IDENTIFICATION (gallery = enroll.p, query = test.p) ===")
    for s, best, bs, ok in rows:
        print("  true=%-12s pred=%-12s score=%.4f  %s" % (s, best, bs, "OK" if ok else "X"))
    print("Accuracy: %d/%d = %.1f%%\n" % (correct, total, 100 * correct / max(total, 1)))

    gen, imp = [], []
    for s in spks:
        tp = os.path.join(FEAT, s, 'test.p')
        if not os.path.exists(tp) or s not in gallery:
            continue
        te = get_embedding(model, tp)
        for g, ge in gallery.items():
            sc = F.cosine_similarity(te, ge).item()
            (gen if g == s else imp).append(sc)
    if gen and imp:
        print("=== VERIFICATION score separation ===")
        print("  genuine  mean=%.4f  min=%.4f" % (statistics.mean(gen), min(gen)))
        print("  impostor mean=%.4f  max=%.4f" % (statistics.mean(imp), max(imp)))
        print("  (good models: genuine clearly > impostor)")
    print("\nDONE")


if __name__ == '__main__':
    main()
