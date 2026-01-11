from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import bpy

from mathutils import Matrix

from .. import log as logging
from ..io.property_sets import eCResourceMeshComplex_PS
from ..io.property_types import bCVector, bCVector2
from ..io.structs import eCMeshElement
from ..io.structs.mesh_element import eEVertexStreamArrayType
from ..util import read_genome_file, to_blend_vec2_tuple, to_blend_vec_tuple, to_blend_vec_tuple_transform


logger = logging.getLogger(__name__)


@dataclass
class _ImportState:
    context: bpy.types.Context
    global_scale: float
    global_matrix: Matrix
    bake_transform: bool


def load_xcmsh(
    context: bpy.types.Context,
    filepath: Path,
    mesh_name: str,
    global_scale: float,
    global_matrix: Matrix,
    bake_transform: bool,
):
    name = mesh_name if mesh_name else filepath.stem
    mesh_complex = read_genome_file(filepath, eCResourceMeshComplex_PS, allow_fallback=True)

    # Create and select object for actor
    # TODO: With this approach meshes are not deleted properly (on reimport they get .001 prefix)
    mesh_obj = bpy.data.objects.new(name, None)
    context.scene.collection.objects.link(mesh_obj)
    context.view_layer.objects.active = mesh_obj
    mesh_obj.select_set(True)

    state = _ImportState(context, global_scale, global_matrix, bake_transform)

    for i, mesh_elem in enumerate(mesh_complex.mesh_elements):
        mesh_elem_name = f'{name}_p{i}'
        mesh = _import_mesh(mesh_elem_name, mesh_elem, state)
        if mesh is None:
            continue
        mesh_elem_obj = bpy.data.objects.new(mesh_elem_name, mesh)
        if not state.bake_transform:
            mesh_elem_obj.matrix_basis = state.global_matrix
        mesh_elem_obj.parent = mesh_obj
        context.scene.collection.objects.link(mesh_elem_obj)


def _import_mesh(mesh_name: str, mesh_elem: eCMeshElement, state: _ImportState) -> Optional[bpy.types.Mesh]:
    mesh = bpy.data.meshes.new(mesh_name)

    vertices_arr: list[bCVector] = mesh_elem.get_stream_array_by_type(eEVertexStreamArrayType.VertexPosition)
    if vertices_arr is None:
        raise ValueError(f"Invalid mesh '{mesh_name}': No vertices array.")
    # Vertices and faces
    if state.bake_transform:
        vertices = [to_blend_vec_tuple_transform(v, state.global_matrix) for v in vertices_arr]
    else:
        vertices = [to_blend_vec_tuple(v) for v in vertices_arr]

    indices_arr: list[int] = mesh_elem.get_stream_array_by_type(eEVertexStreamArrayType.Face)
    if indices_arr is None:
        raise ValueError(f"Invalid mesh '{mesh_name}': No face indices array.")
    if len(indices_arr) % 3 != 0:
        raise ValueError(f"Invalid mesh '{mesh_name}': Number of face indices not a multiple of 3.")

    faces = list(zip(*([iter(indices_arr)] * 3), strict=True))
    mesh.from_pydata(vertices, [], faces)
    if mesh.validate(verbose=True):
        # Avoid crash
        raise ValueError(f"Invalid mesh '{mesh_name}': Validation failed (see log for details).")

    # TODO: Normals?

    # Texture coordinates
    tex_coords_arr: list[bCVector2] = mesh_elem.get_stream_array_by_type(eEVertexStreamArrayType.TextureCoordinate)
    if tex_coords_arr:
        uv_layer = mesh.uv_layers.new(name='uv', do_init=False)
        for i, vert_index in enumerate(indices_arr):
            uv_layer.uv[i].vector = to_blend_vec2_tuple(tex_coords_arr[vert_index])

    return mesh
