"""The persona network: attention layers conditioned on engagement, and the
encrypted offline fine-tuning that trains them (claims 22 and 26).

Every reply a profile speaks — chat, a room turn, a letter, a check-in, a
seat in a company, the Studio Agent answering its owner — is prompted by
``persona.build_system_prompt``, and that prompt now carries a block computed
by a small transformer that QRME owns end to end. Nothing about it is
borrowed from the model that writes the words: the weights live in this
database, encrypted; the forward and backward passes are written out below
in numpy; the training data never leaves the host.

What it does, in one paragraph. The recent turns of the person being spoken
to are a sequence. Each turn is embedded from plain, auditable features (how
long it was, whether it asked, whether it pushed, how it felt, and — the
part the claim turns on — the **degree of engagement** at that turn, replayed
as the same moving average the engagement module keeps). Two attention
layers read the sequence. The attention logits carry a learned bias
proportional to each turn's engagement (``gamma`` per layer), and the softmax
temperature is set by the *current* engagement, so an engaged person gets
sharp attention on the turns that matter and a drifting one gets a wide,
even look. The last position is read out through two heads: the engagement
the next turn is expected to carry, and four emphases the reply should
weight — shared history, warmth, depth, reassurance. The attention row and
the emphases are rendered into the prompt as plain sentences, with the
attended turns quoted, and the same numbers are recorded in
``persona_conditioning`` so a reply can be shown to have been conditioned.

Fine-tuning (``train``) is the offline pass: every interactor's stored
history is replayed into (window → next turn) pairs and the network is fitted
to them by Adam on hand-written gradients. Loss before and after are kept,
the weights are sealed under AES-GCM with a key derived for this deployment
(``QRME_MODEL_KEY``, else the same derivation the watermark key uses), and
the artifact goes to the PDI vault when the account has one. No network
calls, no external model, nothing transmitted.

Deliberately small: d_model 16, two heads, two layers, twelve turns. The
point is not scale; it is that the attention is *ours*, its conditioning on
engagement is a number that can be printed, and its training is a thing the
owner can run with the cable pulled out.
"""

from __future__ import annotations

import hashlib
import json
import os
import re

import numpy as np

from . import db

# -- configuration -----------------------------------------------------------

CONFIG = {"d_in": 8, "d_model": 16, "heads": 2, "layers": 2, "d_ff": 32,
          "window": 12}
EMPHASES = ("shared history", "warmth", "depth", "reassurance")
WEIGHTS_VERSION = 1      # the layout of the sealed artifact, not the training
_ALPHA = 0.3             # engagement replay — the same step engagement.py uses
_LR = 0.01
_ADAM_B1, _ADAM_B2, _ADAM_EPS = 0.9, 0.999, 1e-8
_MAX_SAMPLES = 400
_QUOTE_CHARS = 48

_WORD = re.compile(r"[a-z']+")
_POSITIVE = {"love", "great", "wonderful", "happy", "thanks", "thank", "glad",
             "good", "lovely", "beautiful", "fun", "enjoy", "enjoyed", "nice",
             "perfect", "yes", "excited", "proud"}
_NEGATIVE = {"sad", "scared", "afraid", "worried", "anxious", "tired", "hurt",
             "angry", "alone", "lonely", "lost", "pain", "sick", "hard",
             "can't", "cannot", "help", "sorry", "stress", "stressed",
             "overwhelmed", "no"}
_SELF = {"i", "me", "my", "mine", "myself", "i'm", "i've", "i'd"}
_WARMTH = {"family": 0.9, "grandchild": 0.95, "romantic_partner": 0.9,
           "friend": 0.7, "professional": 0.4, "fan": 0.5, "stranger": 0.2}


# -- features ----------------------------------------------------------------

def engagement_signal(text: str) -> float:
    """The per-turn degree of engagement, exactly as engagement.py scores a
    message — kept identical so the network is conditioned on the number the
    product already shows."""
    words = len((text or "").split())
    return max(0.1, min(1.0, words / 40))


def replay_engagement(texts: list[str]) -> list[float]:
    """The engagement moving average as it stood after each turn."""
    out, score = [], None
    for text in texts:
        signal = engagement_signal(text)
        score = signal if score is None else (1 - _ALPHA) * score + _ALPHA * signal
        out.append(score)
    return out


def _lexicon_rate(words: list[str], lexicon: set[str]) -> float:
    if not words:
        return 0.0
    return min(1.0, sum(w in lexicon for w in words) / max(3, len(words)) * 4)


def features(texts: list[str], engagements: list[float]) -> np.ndarray:
    """One row per turn, every column a number a person can check by hand:
    length, asked, pushed, warm words, hard words, first person, recency,
    and the degree of engagement at that turn."""
    T = len(texts)
    rows = np.zeros((T, CONFIG["d_in"]))
    for i, (text, eng) in enumerate(zip(texts, engagements)):
        words = _WORD.findall((text or "").lower())
        rows[i] = (
            engagement_signal(text),
            1.0 if "?" in (text or "") else 0.0,
            1.0 if "!" in (text or "") else 0.0,
            _lexicon_rate(words, _POSITIVE),
            _lexicon_rate(words, _NEGATIVE),
            _lexicon_rate(words, _SELF),
            (i + 1) / T,
            float(eng),
        )
    return rows


def temperature(engagement: float) -> float:
    """Softmax temperature from the current degree of engagement: engaged
    people get sharp attention, drifting ones a wide, even look."""
    e = min(1.0, max(0.0, float(engagement)))
    return round(1.5 - e, 4)          # 1.5 at 0 … 0.5 at 1


# -- parameters --------------------------------------------------------------

def _seed(profile_id: str) -> int:
    return int.from_bytes(hashlib.sha256(profile_id.encode()).digest()[:4], "big")


def init_params(seed: int, config: dict = CONFIG) -> dict:
    """Fresh weights, deterministic per profile so an untrained profile still
    conditions the same way twice."""
    rng = np.random.default_rng(seed)
    d, dff, din, L = (config["d_model"], config["d_ff"], config["d_in"],
                      config["layers"])

    def w(*shape, scale=None):
        scale = scale or 1 / np.sqrt(shape[0])
        return rng.normal(0, scale, shape)

    p = {"W_in": w(din, d), "b_in": np.zeros(d),
         "P": w(config["window"], d, scale=0.1),
         "w_eng": w(d, 1), "b_eng": np.zeros(1),
         "W_emph": w(d, len(EMPHASES)), "b_emph": np.zeros(len(EMPHASES))}
    for l in range(L):
        p[f"Wq{l}"], p[f"Wk{l}"], p[f"Wv{l}"], p[f"Wo{l}"] = (
            w(d, d), w(d, d), w(d, d), w(d, d))
        p[f"W1{l}"], p[f"b1{l}"] = w(d, dff), np.zeros(dff)
        p[f"W2{l}"], p[f"b2{l}"] = w(dff, d), np.zeros(d)
        p[f"gamma{l}"] = np.array([1.0])   # engagement bias on the logits
    return p


def _softmax(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=-1, keepdims=True)


def _sigmoid(z: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-z))


# -- forward -----------------------------------------------------------------

def forward(p: dict, X: np.ndarray, eng: np.ndarray, tau: float,
            config: dict = CONFIG) -> dict:
    """Run the sequence through the layers. Returns every intermediate the
    backward pass needs, plus the readouts."""
    T = X.shape[0]
    H_heads, d = config["heads"], config["d_model"]
    dk = d // H_heads
    cache = {"X": X, "eng": eng, "tau": tau, "layers": []}
    H = X @ p["W_in"] + p["b_in"] + p["P"][:T]
    for l in range(config["layers"]):
        Q, K, V = H @ p[f"Wq{l}"], H @ p[f"Wk{l}"], H @ p[f"Wv{l}"]
        Qh = Q.reshape(T, H_heads, dk).transpose(1, 0, 2)   # (h, T, dk)
        Kh = K.reshape(T, H_heads, dk).transpose(1, 0, 2)
        Vh = V.reshape(T, H_heads, dk).transpose(1, 0, 2)
        S_raw = Qh @ Kh.transpose(0, 2, 1) / np.sqrt(dk)   # (h, T, T)
        # Claim 22, literally: each key's logit is shifted by that turn's
        # degree of engagement, and the whole row is sharpened or softened
        # by the current one.
        S = (S_raw + p[f"gamma{l}"][0] * eng[None, None, :]) / tau
        A = _softmax(S)
        Oh = A @ Vh                                          # (h, T, dk)
        Ocat = Oh.transpose(1, 0, 2).reshape(T, d)
        H1 = H + Ocat @ p[f"Wo{l}"]
        G = np.tanh(H1 @ p[f"W1{l}"] + p[f"b1{l}"])
        H2 = H1 + G @ p[f"W2{l}"] + p[f"b2{l}"]
        cache["layers"].append({"H": H, "Qh": Qh, "Kh": Kh, "Vh": Vh, "A": A,
                                "Ocat": Ocat, "H1": H1, "G": G})
        H = H2
    h = H[-1]
    y_eng = _sigmoid(h @ p["w_eng"] + p["b_eng"])[0]
    y_emph = _sigmoid(h @ p["W_emph"] + p["b_emph"])
    cache.update({"h": h, "y_eng": y_eng, "y_emph": y_emph})
    return cache


def loss_of(cache: dict, t_eng: float, t_emph: np.ndarray) -> float:
    return float((cache["y_eng"] - t_eng) ** 2
                 + np.mean((cache["y_emph"] - t_emph) ** 2))


# -- backward ----------------------------------------------------------------

def backward(p: dict, cache: dict, t_eng: float, t_emph: np.ndarray,
             config: dict = CONFIG) -> dict:
    """Gradients of ``loss_of`` with respect to every parameter, by hand.
    ``tests/test_persona_net.py`` checks each one against finite differences."""
    g = {k: np.zeros_like(v) for k, v in p.items()}
    H_heads, d = config["heads"], config["d_model"]
    dk = d // H_heads
    T = cache["X"].shape[0]
    eng, tau = cache["eng"], cache["tau"]
    h, y_eng, y_emph = cache["h"], cache["y_eng"], cache["y_emph"]

    dz_eng = 2 * (y_eng - t_eng) * y_eng * (1 - y_eng)
    g["w_eng"] = (h * dz_eng)[:, None]
    g["b_eng"] = np.array([dz_eng])
    dh = p["w_eng"][:, 0] * dz_eng
    dz_emph = 2 * (y_emph - t_emph) / len(EMPHASES) * y_emph * (1 - y_emph)
    g["W_emph"] = np.outer(h, dz_emph)
    g["b_emph"] = dz_emph
    dh = dh + p["W_emph"] @ dz_emph

    dH2 = np.zeros((T, d))
    dH2[-1] = dh
    for l in reversed(range(config["layers"])):
        c = cache["layers"][l]
        dF = dH2
        g[f"W2{l}"] = c["G"].T @ dF
        g[f"b2{l}"] = dF.sum(axis=0)
        dG = dF @ p[f"W2{l}"].T
        dZ1 = dG * (1 - c["G"] ** 2)
        g[f"W1{l}"] = c["H1"].T @ dZ1
        g[f"b1{l}"] = dZ1.sum(axis=0)
        dH1 = dH2 + dZ1 @ p[f"W1{l}"].T

        g[f"Wo{l}"] = c["Ocat"].T @ dH1
        dOcat = dH1 @ p[f"Wo{l}"].T
        dOh = dOcat.reshape(T, H_heads, dk).transpose(1, 0, 2)
        A, Vh, Qh, Kh = c["A"], c["Vh"], c["Qh"], c["Kh"]
        dA = dOh @ Vh.transpose(0, 2, 1)
        dVh = A.transpose(0, 2, 1) @ dOh
        dS = A * (dA - (dA * A).sum(axis=-1, keepdims=True))
        g[f"gamma{l}"] = np.array([(dS * eng[None, None, :]).sum() / tau])
        dS_raw = dS / tau
        dQh = dS_raw @ Kh / np.sqrt(dk)
        dKh = dS_raw.transpose(0, 2, 1) @ Qh / np.sqrt(dk)
        dQ = dQh.transpose(1, 0, 2).reshape(T, d)
        dK = dKh.transpose(1, 0, 2).reshape(T, d)
        dV = dVh.transpose(1, 0, 2).reshape(T, d)
        H = c["H"]
        g[f"Wq{l}"], g[f"Wk{l}"], g[f"Wv{l}"] = H.T @ dQ, H.T @ dK, H.T @ dV
        dH2 = (dH1 + dQ @ p[f"Wq{l}"].T + dK @ p[f"Wk{l}"].T
               + dV @ p[f"Wv{l}"].T)

    dE = dH2
    g["W_in"] = cache["X"].T @ dE
    g["b_in"] = dE.sum(axis=0)
    g["P"][:T] = dE
    return g


class Adam:
    def __init__(self, p: dict, lr: float = _LR):
        self.lr, self.t = lr, 0
        self.m = {k: np.zeros_like(v) for k, v in p.items()}
        self.v = {k: np.zeros_like(v) for k, v in p.items()}

    def step(self, p: dict, g: dict) -> None:
        self.t += 1
        for k in p:
            self.m[k] = _ADAM_B1 * self.m[k] + (1 - _ADAM_B1) * g[k]
            self.v[k] = _ADAM_B2 * self.v[k] + (1 - _ADAM_B2) * g[k] ** 2
            m_hat = self.m[k] / (1 - _ADAM_B1 ** self.t)
            v_hat = self.v[k] / (1 - _ADAM_B2 ** self.t)
            p[k] = p[k] - self.lr * m_hat / (np.sqrt(v_hat) + _ADAM_EPS)


# -- sealing -----------------------------------------------------------------

def _key() -> bytes:
    """The deployment's model key. ``QRME_MODEL_KEY`` when set; otherwise
    derived the way the watermark key is, so a local install can read its
    own weights back without configuration. Either way the weights on disk
    are ciphertext, and a copied database without the key is noise."""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    configured = os.environ.get("QRME_MODEL_KEY") or os.environ.get(
        "QRME_WATERMARK_KEY")
    ikm = (configured.encode() if configured else
           hashlib.sha256(f"qrme-watermark::{db.db_path()}".encode()).digest())
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
                info=b"qrme-persona-net").derive(ikm)


def _pack(p: dict) -> bytes:
    names = sorted(p)
    header = json.dumps({"config": CONFIG, "version": WEIGHTS_VERSION,
                         "names": names,
                         "shapes": [list(p[k].shape) for k in names]}).encode()
    body = np.concatenate([p[k].astype(np.float64).ravel() for k in names]).tobytes()
    return len(header).to_bytes(4, "big") + header + body


def _unpack(plain: bytes) -> dict:
    n = int.from_bytes(plain[:4], "big")
    header = json.loads(plain[4:4 + n])
    flat = np.frombuffer(plain[4 + n:], dtype=np.float64)
    out, at = {}, 0
    for name, shape in zip(header["names"], header["shapes"]):
        size = int(np.prod(shape)) if shape else 1
        out[name] = flat[at:at + size].reshape(shape).copy()
        at += size
    return out


def seal(profile_id: str, p: dict) -> bytes:
    """nonce || AES-GCM(weights), bound to the profile id as associated data
    so one profile's artifact cannot be slid under another's row."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    nonce = os.urandom(12)
    return nonce + AESGCM(_key()).encrypt(nonce, _pack(p), profile_id.encode())


def unseal(profile_id: str, blob: bytes) -> dict:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    return _unpack(AESGCM(_key()).decrypt(bytes(blob[:12]), bytes(blob[12:]),
                                          profile_id.encode()))


def status(profile_id: str) -> dict:
    """What the network for this profile is: trained or initial, and how."""
    row = db.connect().execute(
        "SELECT version, trained_on, loss_before, loss_after, updated_at,"
        " length(blob) AS bytes FROM persona_weights WHERE profile_id=?",
        (profile_id,)).fetchone()
    base = {"profile_id": profile_id, "config": CONFIG,
            "emphasis_names": list(EMPHASES),
            "parameters": int(sum(v.size for v in init_params(0).values())),
            "encrypted_at_rest": True, "external_transmission": False}
    if row is None:
        return {**base, "trained": False, "weights_build": 0, "trained_on": 0,
                "loss_before": None, "loss_after": None, "updated_at": None,
                "sealed_bytes": 0}
    return {**base, "trained": True, "weights_build": row["version"],
            "trained_on": row["trained_on"], "loss_before": row["loss_before"],
            "loss_after": row["loss_after"], "updated_at": row["updated_at"],
            "sealed_bytes": row["bytes"]}


_loaded: dict = {}   # (db path, profile) -> (updated_at, params, version)


def load(profile_id: str) -> tuple[dict, int]:
    """(params, version) — the sealed weights when trained, else the
    profile's deterministic initial weights at version 0. Unsealed once per
    training run rather than once per reply."""
    row = db.connect().execute(
        "SELECT blob, version, updated_at FROM persona_weights WHERE profile_id=?",
        (profile_id,)).fetchone()
    if row is None:
        return init_params(_seed(profile_id)), 0
    key = (db.db_path(), profile_id)
    hit = _loaded.get(key)
    if hit is None or hit[0] != row["updated_at"]:
        hit = (row["updated_at"], unseal(profile_id, row["blob"]), row["version"])
        _loaded[key] = hit
    return {k: v.copy() for k, v in hit[1].items()}, hit[2]


# -- inference ---------------------------------------------------------------

def condition(profile_id: str, turns: list[str], *,
              engagement: float | None = None) -> dict | None:
    """Run the network over the person's recent turns. ``engagement`` is the
    current degree of engagement (the product's score when it has one, the
    replayed average otherwise). None when there is nothing to attend to."""
    texts = [t for t in (turns or []) if (t or "").strip()][-CONFIG["window"]:]
    if not texts:
        return None
    replayed = replay_engagement(texts)
    current = replayed[-1] if engagement is None else float(engagement)
    tau = temperature(current)
    p, version = load(profile_id)
    cache = forward(p, features(texts, replayed), np.array(replayed), tau)
    # The last layer's last position, averaged over heads: where the reply
    # is looking across the turns it was given.
    row = cache["layers"][-1]["A"][:, -1, :].mean(axis=0)
    attention = [{"turn": i + 1, "weight": round(float(w), 4),
                  "engagement": round(float(e), 3),
                  "quote": (texts[i][:_QUOTE_CHARS] + ("…" if len(texts[i]) > _QUOTE_CHARS else ""))}
                 for i, (w, e) in enumerate(zip(row, replayed))]
    return {"version": version, "temperature": tau,
            "engagement": round(current, 4),
            "predicted_engagement": round(float(cache["y_eng"]), 4),
            "emphases": {name: round(float(v), 4)
                         for name, v in zip(EMPHASES, cache["y_emph"])},
            "attention": attention}


def render(c: dict) -> str:
    """The conditioning as sentences the writing model can act on."""
    top = sorted(c["attention"], key=lambda a: -a["weight"])[:3]
    attended = "; ".join(
        f'turn {a["turn"]} ({a["weight"]:.2f}) "{a["quote"]}"' for a in top)
    emph = ", ".join(f"{k} {v:.2f}" for k, v in c["emphases"].items())
    state = ("trained weights v%d" % c["version"]) if c["version"] else "initial weights"
    return (f"Engagement-conditioned attention (persona network, {state}; "
            f"temperature {c['temperature']:.2f} from engagement "
            f"{c['engagement']:.2f}). Of this person's last "
            f"{len(c['attention'])} turns the network attends most to — "
            f"{attended}. Expected engagement next turn "
            f"{c['predicted_engagement']:.2f}. Emphases for this reply — {emph}. "
            "Weight your focus accordingly; identity and boundaries stay fixed.")


def recent_turns(profile_id: str, interactor_id: str | None,
                 limit: int | None = None) -> list[str]:
    """What the person said, oldest first — or, with no interactor, the
    profile's most recent turns from anyone (a seat in a room, a letter)."""
    limit = limit or CONFIG["window"]
    conn = db.connect()
    if interactor_id:
        rows = conn.execute(
            "SELECT content FROM messages WHERE profile_id=? AND interactor_id=?"
            " AND role='interactor' AND status!='rejected'"
            " ORDER BY created_at DESC, rowid DESC LIMIT ?",
            (profile_id, interactor_id, limit)).fetchall()
    else:
        rows = conn.execute(
            "SELECT content FROM messages WHERE profile_id=?"
            " AND role='interactor' AND status!='rejected'"
            " ORDER BY created_at DESC, rowid DESC LIMIT ?",
            (profile_id, limit)).fetchall()
    return [r["content"] for r in reversed(rows)]


def record(profile_id: str, interactor_id: str | None, surface: str,
           c: dict) -> str:
    """Keep what conditioned this reply, so it can be shown afterwards."""
    conn = db.connect()
    # Commit only what this call opened: a caller mid-transaction keeps
    # its own commit, and a call that opened the write must not leave the
    # lock held for a request on another thread to run into.
    opened = not conn.in_transaction
    cid = db.new_id("cond")
    conn.execute(
        "INSERT INTO persona_conditioning (id, profile_id, interactor_id,"
        " surface, weights_version, temperature, engagement,"
        " predicted_engagement, attention, emphases, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (cid, profile_id, interactor_id, surface, c["version"],
         c["temperature"], c["engagement"], c["predicted_engagement"],
         json.dumps(c["attention"]), json.dumps(c["emphases"]), db.utcnow()))
    if opened:
        conn.commit()
    return cid


def prompt_block(profile_id: str, interactor_id: str | None, *,
                 surface: str = "reply", turns: list[str] | None = None,
                 engagement: float | None = None) -> str | None:
    """The block ``persona.build_system_prompt`` appends: run the network,
    record the conditioning, render it. ``turns`` may be supplied by a
    caller whose conversation is not in ``messages`` (the Studio Agent keeps
    none); otherwise they are read from the store."""
    if turns is None:
        turns = recent_turns(profile_id, interactor_id)
    c = condition(profile_id, turns, engagement=engagement)
    if c is None:
        return None
    record(profile_id, interactor_id, surface, c)
    return render(c)


def conditioning_of(profile_id: str, limit: int = 20) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM persona_conditioning WHERE profile_id=?"
        " ORDER BY created_at DESC, rowid DESC LIMIT ?",
        (profile_id, limit)).fetchall()
    out = []
    for r in rows:
        item = dict(r)
        item["attention"] = json.loads(item["attention"])
        item["emphases"] = json.loads(item["emphases"])
        out.append(item)
    return out


# -- fine-tuning -------------------------------------------------------------

def _samples(profile_id: str) -> list[dict]:
    """(window → next turn) pairs from every interactor's stored history.
    The target is what the next turn actually carried: its engagement, and
    the emphases a reply before it should have weighted."""
    conn = db.connect()
    interactors = [r["interactor_id"] for r in conn.execute(
        "SELECT DISTINCT interactor_id FROM messages WHERE profile_id=?"
        " AND role='interactor'", (profile_id,)).fetchall()]
    samples = []
    for interactor_id in interactors:
        texts = [r["content"] for r in conn.execute(
            "SELECT content FROM messages WHERE profile_id=? AND interactor_id=?"
            " AND role='interactor' AND status='approved'"
            " ORDER BY created_at, rowid", (profile_id, interactor_id)).fetchall()]
        if len(texts) < 2:
            continue
        rel = conn.execute(
            "SELECT relationship_type FROM relationships WHERE profile_id=?"
            " AND interactor_id=?", (profile_id, interactor_id)).fetchone()
        warmth = _WARMTH.get(rel["relationship_type"], 0.3) if rel else 0.3
        replayed = replay_engagement(texts)
        for t in range(len(texts) - 1):
            lo = max(0, t + 1 - CONFIG["window"])
            nxt = texts[t + 1]
            words = _WORD.findall(nxt.lower())
            samples.append({
                "texts": texts[lo:t + 1], "eng": replayed[lo:t + 1],
                "current": replayed[t],
                "t_eng": engagement_signal(nxt),
                "t_emph": np.array([replayed[t + 1], warmth,
                                    min(len(nxt) / 400, 1.0),
                                    _lexicon_rate(words, _NEGATIVE)]),
            })
    return samples[-_MAX_SAMPLES:]


def _mean_loss(p: dict, samples: list[dict]) -> float:
    total = 0.0
    for s in samples:
        cache = forward(p, features(s["texts"], s["eng"]), np.array(s["eng"]),
                        temperature(s["current"]))
        total += loss_of(cache, s["t_eng"], s["t_emph"])
    return total / len(samples)


def train(profile_id: str, *, epochs: int = 8) -> dict:
    """Claim 26's pass for the network: fit the weights to this profile's
    own stored history, on this host, and seal them. Returns the metrics
    ``adaptation.finetune`` reports under ``network``."""
    samples = _samples(profile_id)
    p, version = load(profile_id)
    if not samples:
        return {"trained": False, "samples": 0, "training_steps": 0,
                "loss_before": None, "loss_after": None, "weights_build": version,
                "reason": "no interactor has two approved turns yet"}
    loss_before = _mean_loss(p, samples)
    opt, steps = Adam(p), 0
    for _ in range(epochs):
        for s in samples:
            cache = forward(p, features(s["texts"], s["eng"]),
                            np.array(s["eng"]), temperature(s["current"]))
            opt.step(p, backward(p, cache, s["t_eng"], s["t_emph"]))
            steps += 1
    loss_after = _mean_loss(p, samples)
    conn = db.connect()
    conn.execute(
        "INSERT INTO persona_weights (profile_id, blob, version, trained_on,"
        " loss_before, loss_after, updated_at) VALUES (?,?,?,?,?,?,?)"
        " ON CONFLICT (profile_id) DO UPDATE SET blob=excluded.blob,"
        " version=persona_weights.version+1, trained_on=excluded.trained_on,"
        " loss_before=excluded.loss_before, loss_after=excluded.loss_after,"
        " updated_at=excluded.updated_at",
        (profile_id, seal(profile_id, p), 1, len(samples),
         round(loss_before, 6), round(loss_after, 6), db.utcnow()))
    conn.commit()
    # `weights_build`, `training_steps`: one wire name, one type. `version`
    # is a string on /health and `steps` a list on the task record.
    return {"trained": True, "samples": len(samples), "training_steps": steps,
            "loss_before": round(loss_before, 6),
            "loss_after": round(loss_after, 6),
            "weights_build": status(profile_id)["weights_build"],
            "encrypted_at_rest": True}
