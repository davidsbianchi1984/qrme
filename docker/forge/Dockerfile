# The stack's forge: a photograph in, a speakable 3-D head out, on this
# deployment's own hardware. The landmarker's weights are baked in at
# build time — the same rule the ears keep — so a running forge never
# reaches out for a model, and a face costs nobody a subscription.
FROM python:3.12-slim
# libEGL and friends are not optional: MediaPipe 1.0 loads its native
# bindings through ctypes at first use, and a container missing
# libEGL.so.1 imports the module perfectly and then throws the moment a
# photograph arrives. That is exactly how the forge shipped answering
# "ready" while being unable to build anything.
# Blender is here to convert, not to render.
#
#     asked     do the FBX to .glb conversion in the app
#     mattered  does the mouth still move afterwards
#
# The shelf has told people to do this by hand in Blender for months, so
# the app doing it in the same tool is the only version that cannot
# produce a different face from the documented one. `assimp` is a tenth
# the size and was measured against it: round-tripping a MetaPerson
# avatar, it returned 111 of 114 morph targets — the three missing from
# AvatarHead and AvatarTeethLower, the meshes that move when a face
# speaks — and NONE of their names, because its glTF writer emits no
# `extras.targetNames`. The console drives the mouth by name, so that is
# a face nothing can speak through.
#
# `python3-numpy` is not optional and is the reason this line does not
# lean on `--no-install-recommends` alone. Blender's FBX importer does
# `import numpy` at the top of `import_fbx`, so without it the addon
# registers, the container answers "ready", and the first file to arrive
# dies with `ModuleNotFoundError`. That is the same shape as the libEGL
# fault below — a forge that is confidently unable to do its job — and it
# is why `/health` opens the importer rather than asking Blender its
# version.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libegl1 libgles2 libglib2.0-0 libgomp1 curl \
    blender python3-numpy \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir fastapi uvicorn mediapipe pillow \
    numpy pygltflib scipy
# The face landmarker, fetched once here on the machine running
# `docker compose build` and never at runtime.
RUN curl -fsSL -o /srv/face_landmarker.task \
    https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task \
    || (mkdir -p /srv && curl -fsSL -o /srv/face_landmarker.task \
        https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task)
WORKDIR /srv
COPY server.py facebuild.py to_glb.py ./
EXPOSE 8600
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8600"]
