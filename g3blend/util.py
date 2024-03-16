import math
from typing import Any, Iterable, Optional, Type, TypeVar, cast

import bpy
from bpy_extras.io_utils import axis_conversion

from .ksy.genomfle import Genomfle
from .ksy.kaitaistruct import KaitaiStream

T = TypeVar('T')


def read_genomfle(obj_type: Type[T], path) -> T:
    with open(path, 'rb') as f:
        obj = obj_type(KaitaiStream(f))
        obj._read()
        obj._fetch_instances()
        return obj


def write_genomfle(obj, path):
    with open(path, 'wb') as f:
        stream = KaitaiStream(f)

        # Write header and body
        obj.meta.tail__to_write = False
        obj._write(stream)

        # Update the tail offset
        obj.meta.header.tail_offset = stream.pos()

        # Write the tail
        obj.meta.tail._write(stream)

        # Write updated header again
        stream.seek(0)
        obj.meta.header._write(stream)


def set_genomfle(obj, strtbl: list[str], version: int = 1):
    genomfle = Genomfle()
    genomfle.header = genomfle.cst(Genomfle.GenomfleHeader)
    genomfle.header.version = version
    genomfle.header.tail_offset = 0

    genomfle.tail = genomfle.cst(Genomfle.GenomfleTail)
    genomfle.tail.strtbl_present = 1
    strtbl_entries = []
    for entry in strtbl:
        entry_str = genomfle.tail.cst(Genomfle.GenomfleStr)
        entry_str.data = entry
        strtbl_entries.append(entry_str)
    genomfle.tail.strtbl_entries = strtbl_entries

    obj.meta = genomfle


def get_chunks_by_type(chunk_type: Type[T], chunks: Any) -> list[T]:
    return [chunk.content for chunk in chunks.chunks if isinstance(chunk.content, chunk_type)]


def get_chunk_by_type(chunk_type: Type[T], chunks: Any) -> T:
    typed_chunks = get_chunks_by_type(chunk_type, chunks)
    assert len(typed_chunks) == 1
    return cast(T, typed_chunks[0])


def get_child_nodes(node: T, nodes: list[T]) -> Iterable[T]:
    return (child for child in nodes if child.parent.data == node.name.data)


def lookup_strtab(meta: Genomfle.GenomfleTail, index: int) -> str:
    if not meta.strtbl_present:
        raise IndexError('Stringtable lookup in file without stringtable.')

    if index < meta.num_strtbl_entries:
        return meta.strtbl_entries[index].data
    else:
        raise IndexError(f'Stringtable lookup with out of range index {index} (has {meta.num_strtbl_entries} entries)')


def similar_values_iter(v1, v2, epsilon=1e-4):
    """Return True if iterables v1 and v2 are nearly the same."""
    return v1 == v2 or all(math.isclose(c1, c2, abs_tol=epsilon) for c1, c2 in zip(v1, v2))


# Matrix to rotate local axes of all bones for better looking of models in Blender which were created in 3ds max.
# (In 3dsmax any bone lies along its local X direction, however in Blender any bone lies along its local Y direction,
# so we can want to rotate axes around Z direction to match the directions).
bone_correction_matrix = axis_conversion(from_forward='Y', from_up='Z', to_forward='X', to_up='Y').to_4x4()
bone_correction_matrix_inv = bone_correction_matrix.inverted_safe()


def find_armature(context: bpy.types.Context) -> Optional[bpy.types.Object]:
    # TODO: Find actor by name or at least check compatibility?
    actor_obj = context.active_object
    if actor_obj is None:
        return None

    if arm_obj := next((c for c in actor_obj.children if c.type == 'ARMATURE'), None):
        return arm_obj

    if actor_obj.parent:
        return next((c for c in actor_obj.parent.children if c.type == 'ARMATURE'), None)


# Note: Taken from KrxImpExp
# Reset the current scene
def reset_scene():
    import bpy
    # Remove scenes
    empty_scn = bpy.data.scenes.new("Scene")
    for i in range(len(bpy.data.scenes) - 1, -1, -1):
        scn = bpy.data.scenes[i]
        if scn != empty_scn:
            bpy.data.scenes.remove(scn)

    # Remove objects
    for i in range(len(bpy.data.objects) - 1, -1, -1):
        obj = bpy.data.objects[i]
        if obj.users == 0:
            bpy.data.objects.remove(obj)

    # Remove meshes
    for i in range(len(bpy.data.meshes) - 1, -1, -1):
        msh = bpy.data.meshes[i]
        if msh.users == 0:
            bpy.data.meshes.remove(msh)

    # Remove armatures
    for i in range(len(bpy.data.armatures) - 1, -1, -1):
        arm = bpy.data.armatures[i]
        if arm.users == 0:
            bpy.data.armatures.remove(arm)

    # Remove actions
    for i in range(len(bpy.data.actions) - 1, -1, -1):
        act = bpy.data.actions[i]
        if act.users == 0:
            bpy.data.actions.remove(act)

    # Remove materials
    for i in range(len(bpy.data.materials) - 1, -1, -1):
        mat = bpy.data.materials[i]
        if mat.users == 0:
            bpy.data.materials.remove(mat)

    # Remove textures
    for i in range(len(bpy.data.textures) - 1, -1, -1):
        tex = bpy.data.textures[i]
        if tex.users == 0:
            bpy.data.textures.remove(tex)

    # Remove images
    for i in range(len(bpy.data.images) - 1, -1, -1):
        img = bpy.data.images[i]
        if img.users == 0:
            bpy.data.images.remove(img)


# Note: Taken from FBX importer
# Scale/unit mess. FBX can store the 'reference' unit of a file in its UnitScaleFactor property
# (1.0 meaning centimeter, afaik). We use that to reflect user's default unit as set in Blender with scale_length.
# However, we always get values in BU (i.e. meters), so we have to reverse-apply that scale in global matrix...
# Note that when no default unit is available, we assume 'meters' (and hence scale by 100).
def units_blender_to_g3_factor(scene):
    return 100.0 if (scene.unit_settings.system == 'NONE') else (100.0 * scene.unit_settings.scale_length)
