"""Blender's own FBX → glTF 2.0, with the shape keys kept.

## Why Blender and not something smaller

The shelf has told people for months to do this by hand: *"Blender: File
→ Import → FBX, then File → Export → glTF 2.0, leaving Shape Keys
checked so the mouth survives."* Doing it in the app with a different
tool would mean the automatic path and the documented path produce
different faces, and only one of them would be tested.

`assimp` was measured against the alternative and lost on the thing that
matters. Round-tripping a MetaPerson avatar through it:

    morph targets   114 -> 111        three gone, from AvatarHead and
                                      AvatarTeethLower — the two meshes
                                      that move when a face SPEAKS
    target names    114 -> 0          its glTF writer emits no
                                      `extras.targetNames` at all

A face with 111 unnamed targets is a face nothing can speak through: the
console drives the mouth by NAME — `jawOpen`, `CH`, `DD`, `E`, `FF` — so
a nameless target is a target no viseme can find. Blender reproduces the
provider's own export exactly: 114 targets, 114 names, 82 nodes, 1 skin,
every mesh's count identical.

Run headless:

    blender --background --factory-startup --python to_glb.py -- in.fbx out.glb

    asked     convert the export in the app
    mattered  does the mouth still move afterwards
"""

import sys

import bpy


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1:]
    if len(argv) != 2:
        print("usage: ... -- <in.fbx> <out.glb>", file=sys.stderr)
        return 2
    src, dst = argv

    # An empty room.
    #
    # `--factory-startup` still opens the DEFAULT SCENE, which ships a
    # cube, a camera and a lamp. All three would ride into the export and
    # arrive as furniture inside somebody's avatar.
    bpy.ops.wm.read_factory_settings(use_empty=True)

    bpy.ops.import_scene.fbx(filepath=src)

    # The three that matter are named rather than left to defaults, so a
    # Blender upgrade cannot quietly change what this produces:
    #
    #   export_morph          the shape keys themselves — the whole point
    #   export_morph_normal   normals per shape, or a face deforms flat
    #   export_skins          the armature, or nothing can pose it
    bpy.ops.export_scene.gltf(
        filepath=dst,
        export_format="GLB",
        export_morph=True,
        export_morph_normal=True,
        export_skins=True,
        export_apply=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
