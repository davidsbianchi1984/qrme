"""One photograph into one speakable head — the forge's own maker.

The pipeline, end to end, all of it on this machine:

1. **Find the face.** MediaPipe's face landmarker returns 478 points in
   the canonical face topology, and the topology is the whole trick: the
   triangles never change, so a mesh built from these points is already
   rigged in the only sense that matters — every index means the same
   part of a face in every head this forge ever makes.
2. **Skin it with the photograph.** Each landmark's own place in the
   picture becomes its texture coordinate, so the photo maps onto the
   geometry it was measured from. No projection guesswork, no seams to
   hide: the face wears the picture it came from.
3. **Give it shapes to make.** The morph targets are generated from the
   topology rather than learned — a jaw that opens, lips that purse and
   smile, eyes that blink — because the geometry is canonical and the
   index groups are known. Honest approximations, and named exactly as
   ARKit names them.

## Why ARKit's names

Nothing here is Apple's, and the names are Apple's on purpose. A renderer
that drives ``jawOpen`` on one of these heads drives ``jawOpen`` on a
model bought from any vendor that ships ARKit blendshapes, which is all
of them. That is what keeps a provider a *slot*: the day somebody brings
their own paid avatar, the console's mouth code does not learn a second
vocabulary — it already speaks this one.

## What this is not

It is a head built from one photograph, and it does not claim to be a
body. It does not claim photorealism against a paid full-body scanner
either. What it claims is precise: the person's own face, on this
deployment's hardware, with a mouth the room's audio can move — free,
permanent, and nobody's to discontinue.
"""

from __future__ import annotations

import io
import os

import numpy as np

#: The landmarker's weights, baked into the image at build time so a
#: running forge never reaches out for them — the ears' own rule.
_MODEL = os.environ.get("FORGE_MODEL", "/srv/face_landmarker.task")

#: The canonical mesh's index groups. These are the landmarker's own
#: numbering and they are stable across every face it measures, which is
#: what lets a morph target be written once and mean the same thing on
#: everybody.
_UPPER_LIP = (61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291,
              78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308)
_LOWER_LIP = (146, 91, 181, 84, 17, 314, 405, 321, 375,
              95, 88, 178, 87, 14, 317, 402, 318, 324)
_JAW = (172, 136, 150, 149, 176, 148, 152, 377, 400, 378, 379, 365, 397)
_MOUTH_CORNERS = (61, 291, 78, 308)
_LEFT_UPPER_LID = (159, 158, 157, 173, 246, 161, 160)
_LEFT_LOWER_LID = (145, 144, 163, 7, 33, 153, 154)
_RIGHT_UPPER_LID = (386, 385, 384, 398, 466, 388, 387)
_RIGHT_LOWER_LID = (374, 373, 390, 249, 263, 380, 381)

#: The shapes this forge makes, in ARKit's vocabulary. Small on purpose:
#: every one of them is a shape a speaking face actually needs, and a
#: long list of targets nobody drives is weight in a file rather than
#: expressiveness on a screen.
BLENDSHAPES = ("jawOpen", "mouthPucker", "mouthSmileLeft",
               "mouthSmileRight", "eyeBlinkLeft", "eyeBlinkRight")


def _landmarks(photo: bytes) -> tuple[np.ndarray, tuple[int, int]]:
    """The 478 points, and the picture's size. Raises LookupError when
    there is no face to measure — the one refusal a person can fix."""
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision
    from PIL import Image

    picture = Image.open(io.BytesIO(photo)).convert("RGB")
    width, height = picture.size
    frame = mp.Image(image_format=mp.ImageFormat.SRGB,
                     data=np.asarray(picture))
    options = vision.FaceLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=_MODEL),
        num_faces=1)
    with vision.FaceLandmarker.create_from_options(options) as landmarker:
        found = landmarker.detect(frame)
    if not found.face_landmarks:
        raise LookupError("no face in the photograph")
    points = np.array([[p.x, p.y, p.z] for p in found.face_landmarks[0]],
                      dtype=np.float32)
    return points, (width, height)


def _geometry(points: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """``(positions, uvs)``.

    The landmarker answers in picture space — x and y across the frame,
    z toward the camera. A model wants the head centred on its own
    origin, upright, and scaled to something a scene can place, so the
    points are recentred on the face's middle and normalized by its own
    width. The texture coordinates are the ORIGINAL picture places,
    taken before any of that, which is what makes the photograph land
    where it was measured.
    """
    uvs = points[:, :2].copy()                       # picture space, 0..1
    middle = points.mean(axis=0)
    centred = points - middle
    span = float(np.abs(centred[:, 0]).max()) or 1.0
    positions = centred / (span * 2.0)
    # Picture space counts y downward and a scene counts it upward, and
    # the depth the landmarker reports runs the other way from a scene's
    # too. Flipping both here is what stands the head up facing forward.
    positions[:, 1] *= -1.0
    positions[:, 2] *= -1.0
    return positions.astype(np.float32), uvs.astype(np.float32)


def _triangles() -> np.ndarray:
    """The canonical topology — the same triangles on every face."""
    from mediapipe.python.solutions import face_mesh_connections as links

    edges = links.FACEMESH_TESSELATION
    # The tessellation ships as edges; the faces are recovered from it
    # once and cached in the module, because the topology is a constant
    # of the model rather than anything about a particular person.
    global _FACES
    if _FACES is None:
        neighbours: dict[int, set[int]] = {}
        for a, b in edges:
            neighbours.setdefault(a, set()).add(b)
            neighbours.setdefault(b, set()).add(a)
        faces = set()
        for a, b in edges:
            for c in neighbours.get(a, set()) & neighbours.get(b, set()):
                faces.add(tuple(sorted((a, b, c))))
        _FACES = np.array(sorted(faces), dtype=np.uint32)
    return _FACES


_FACES: np.ndarray | None = None


def _morphs(positions: np.ndarray) -> dict[str, np.ndarray]:
    """The shapes, as position deltas over the neutral mesh.

    Generated from the topology, not learned: the index groups say which
    vertices are a lip and which are an eyelid, and the deltas move them
    the way that part of a face moves. The scale rides on the face's own
    measurements so a small face does not get a large mouth.
    """
    height = float(positions[:, 1].max() - positions[:, 1].min()) or 1.0
    width = float(positions[:, 0].max() - positions[:, 0].min()) or 1.0
    shapes: dict[str, np.ndarray] = {}

    # A jaw opens: the lower lip and the jawline drop, and the drop
    # tapers toward the hinge rather than swinging the whole chin.
    jaw = np.zeros_like(positions)
    for index in _LOWER_LIP:
        jaw[index, 1] -= height * 0.10
    for index in _JAW:
        jaw[index, 1] -= height * 0.13
    shapes["jawOpen"] = jaw

    # Lips purse: the mouth ring draws in across and pushes forward.
    pucker = np.zeros_like(positions)
    mouth = np.array(_UPPER_LIP + _LOWER_LIP, dtype=int)
    centre = positions[mouth].mean(axis=0)
    for index in mouth:
        toward = centre - positions[index]
        pucker[index, 0] += toward[0] * 0.45
        pucker[index, 2] += width * 0.05
    shapes["mouthPucker"] = pucker

    # A smile lifts and widens the corners, each side its own shape so a
    # renderer can drive half a face — which is what makes an expression
    # read as a person rather than a mask.
    for side, corners in (("Left", (61, 78)), ("Right", (291, 308))):
        smile = np.zeros_like(positions)
        outward = -1.0 if side == "Left" else 1.0
        for index in corners:
            smile[index, 0] += width * 0.06 * outward
            smile[index, 1] += height * 0.05
        shapes[f"mouthSmile{side}"] = smile

    # Eyes blink: the upper lid travels down to meet the lower one, which
    # is where the lid actually goes.
    for side, upper, lower in (("Left", _LEFT_UPPER_LID, _LEFT_LOWER_LID),
                               ("Right", _RIGHT_UPPER_LID,
                                _RIGHT_LOWER_LID)):
        blink = np.zeros_like(positions)
        meeting = positions[list(lower)].mean(axis=0)
        for index in upper:
            blink[index] = (meeting - positions[index]) * 0.85
        shapes[f"eyeBlink{side}"] = blink

    return shapes


def _portrait(photo: bytes, uvs: np.ndarray) -> bytes:
    """The still every surface in this product already knows how to
    draw: the photograph cropped to the face it was measured on, with
    room around it so a head is not a chin in a box."""
    from PIL import Image

    picture = Image.open(io.BytesIO(photo)).convert("RGB")
    width, height = picture.size
    left, right = float(uvs[:, 0].min()), float(uvs[:, 0].max())
    top, bottom = float(uvs[:, 1].min()), float(uvs[:, 1].max())
    pad_x = (right - left) * 0.35
    pad_y = (bottom - top) * 0.45
    box = (max(0, int((left - pad_x) * width)),
           max(0, int((top - pad_y) * height)),
           min(width, int((right + pad_x) * width)),
           min(height, int((bottom + pad_y) * height)))
    cropped = picture.crop(box)
    cropped.thumbnail((512, 512))
    out = io.BytesIO()
    cropped.save(out, format="PNG")
    return out.getvalue()


def _glb(positions: np.ndarray, uvs: np.ndarray, faces: np.ndarray,
         morphs: dict[str, np.ndarray], texture: bytes) -> bytes:
    """glTF 2.0 binary: the mesh, its skin, and its morph targets.

    Written straight rather than through a scene library because the
    shape is small and fixed — one mesh, one material, one image, six
    targets — and a dependency that can only build this one file is a
    dependency that can only break it.
    """
    import pygltflib as gl

    blobs: list[bytes] = []
    views: list[gl.BufferView] = []
    accessors: list[gl.Accessor] = []

    def _put(array: np.ndarray, kind: str, component: int,
             target: int | None = None) -> int:
        data = array.tobytes()
        # Every view starts on a four-byte boundary — the format's own
        # alignment rule, and the one thing a hand-written glTF gets
        # wrong first.
        while sum(len(b) for b in blobs) % 4:
            blobs.append(b"\x00")
        offset = sum(len(b) for b in blobs)
        blobs.append(data)
        views.append(gl.BufferView(buffer=0, byteOffset=offset,
                                   byteLength=len(data), target=target))
        smallest = array.min(axis=0) if array.ndim > 1 else [array.min()]
        largest = array.max(axis=0) if array.ndim > 1 else [array.max()]
        accessors.append(gl.Accessor(
            bufferView=len(views) - 1, componentType=component,
            count=len(array), type=kind,
            min=[float(v) for v in np.atleast_1d(smallest)],
            max=[float(v) for v in np.atleast_1d(largest)]))
        return len(accessors) - 1

    position_at = _put(positions, "VEC3", gl.FLOAT, gl.ARRAY_BUFFER)
    uv_at = _put(uvs, "VEC2", gl.FLOAT, gl.ARRAY_BUFFER)
    index_at = _put(faces.flatten().astype(np.uint32), "SCALAR",
                    gl.UNSIGNED_INT, gl.ELEMENT_ARRAY_BUFFER)
    targets, names = [], []
    for name in BLENDSHAPES:
        delta = morphs[name].astype(np.float32)
        targets.append(gl.Attributes(POSITION=_put(delta, "VEC3", gl.FLOAT)))
        names.append(name)

    while sum(len(b) for b in blobs) % 4:
        blobs.append(b"\x00")
    image_offset = sum(len(b) for b in blobs)
    blobs.append(texture)
    views.append(gl.BufferView(buffer=0, byteOffset=image_offset,
                               byteLength=len(texture)))

    buffer = b"".join(blobs)
    model = gl.GLTF2(
        asset=gl.Asset(generator="QRME forge"),
        scene=0,
        scenes=[gl.Scene(nodes=[0])],
        nodes=[gl.Node(mesh=0, name="head")],
        meshes=[gl.Mesh(
            name="head",
            primitives=[gl.Primitive(
                attributes=gl.Attributes(POSITION=position_at,
                                         TEXCOORD_0=uv_at),
                indices=index_at, material=0, targets=targets)],
            # The names ride in the mesh's extras because that is where
            # every engine looks for them, and a target nobody can name
            # is a target nobody can drive.
            extras={"targetNames": names})],
        materials=[gl.Material(
            pbrMetallicRoughness=gl.PbrMetallicRoughness(
                baseColorTexture=gl.TextureInfo(index=0),
                metallicFactor=0.0, roughnessFactor=0.9),
            doubleSided=True)],
        textures=[gl.Texture(source=0)],
        images=[gl.Image(bufferView=len(views) - 1, mimeType="image/png")],
        accessors=accessors,
        bufferViews=views,
        buffers=[gl.Buffer(byteLength=len(buffer))])
    model.set_binary_blob(buffer)
    return b"".join(model.save_to_bytes())


def build_head(photo: bytes, *, shot: str = "face") -> dict:
    """The whole road: a photograph in, a speakable head out.

    ``shot`` says how the picture is framed. It does not change what is
    built — one photograph supports a head and this door does not
    pretend otherwise — it changes how much picture the landmarker is
    given to find a face in, which is the honest difference between a
    selfie and a full-length shot.
    """
    from PIL import Image

    if shot in ("upper", "full"):
        # A distant face in a large frame is a small face: crop toward
        # the middle first so the landmarker measures pixels rather than
        # background. The proportions are the ordinary framings of the
        # two shots, not a guess about this particular photograph.
        picture = Image.open(io.BytesIO(photo)).convert("RGB")
        width, height = picture.size
        keep = 0.55 if shot == "full" else 0.8
        box = (int(width * (1 - keep) / 2), 0,
               int(width * (1 + keep) / 2), int(height * keep))
        held = io.BytesIO()
        picture.crop(box).save(held, format="PNG")
        photo = held.getvalue()

    points, _ = _landmarks(photo)
    positions, uvs = _geometry(points)
    faces = _triangles()
    morphs = _morphs(positions)
    portrait = _portrait(photo, uvs)
    return {"glb": _glb(positions, uvs, faces, morphs, photo),
            "portrait": portrait,
            "blendshapes": list(BLENDSHAPES)}
