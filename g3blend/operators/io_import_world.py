import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import bpy
from mathutils import Matrix, Vector

from .io_import_xact import load_xact
from .io_import_xcmsh import load_xcmsh
from .. import log as logging
from ..io.property_types import bCVector
from ..io.types import bCQuaternion
from ..util import to_blend_quat, to_blend_vec

logger = logging.getLogger(__name__)


@dataclass
class _ImportState:
    context: bpy.types.Context
    global_scale: float
    global_matrix: Matrix
    bake_transform: bool


def _find_file(base_dir: Path, name: str) -> Optional[Path]:
    for file in base_dir.glob('**/*'):
        if file.is_file() and file.name == name:
            return file
    return None


def _parse_vec3(raw: str) -> Vector:
    splitted = raw.replace('//', '').split('/')
    return to_blend_vec(bCVector(float(splitted[0]), float(splitted[1]), float(splitted[2])))


def load_world(context: bpy.types.Context, filepath: Path, data_dir: Path, global_scale: float, global_matrix: Matrix,
               bake_transform: bool):
    with filepath.open('r') as f:
        entities_list = json.load(f)

    scene_col = context.scene.collection
    failed_meshes = set()

    for entity in entities_list['Entities']:
        # Filter lowpoly entities...
        if 'LOWPOLY' in entity['Name']:
            continue

        if 'Mesh' not in entity:
            # Skip entities without mesh.
            continue

        entity_name = f"{entity['Name']}_{entity['Guid']}"
        mesh_name = f"{entity['Mesh']}"

        # TODO: Somehow broken, missing SkinningInfoChunk and MeshChunk.
        # Areda_Orcboss probably has a different xact in reality.
        if mesh_name.endswith('_Skeleton.xact'):
            continue

        if mesh_name in failed_meshes:
            continue

        # Already imported.
        if entity_name in context.scene.objects:
            continue

        filter_location = _parse_vec3(entity['Position'])
        # TODO: Landscape seems incorrectly scaled or something, does not align at least.
        #       NO, not only landscape, it is everything. Everything is somehow misaligned. Maybe missing some conversion? Or apply of global matrix?
        #       -> Indeed meshes are wrongly rotated / flipped (see the sawlog in ardea, or the rotation of the hero).
        #       -> YESSSS, rotating the global matrix by 180° helps. Weird. Ah of course, we apply the global matrix twice.
        #       -> Once on import of the meshes and once on the object instance.
        if ((filter_location - Vector((88000, -10000, 5000))).length >= 20000) and 'Landscape' not in mesh_name:
            continue

        if mesh_name not in scene_col.children:
            try:
                # TODO: Support xlmsh for buildings...
                if mesh_name.endswith('.xcmsh'):
                    mesh_file = _find_file(data_dir / '_compiledMesh', mesh_name)
                    if not mesh_file:
                        logger.warning('Failed to find mesh file: {}', mesh_name)
                        continue
                    load_xcmsh(context, mesh_file, mesh_name, global_scale, global_matrix, bake_transform)
                    # TODO: Move into mesh collection
                elif mesh_name.endswith('.xact'):
                    mesh_file = _find_file(data_dir / '_compiledAnimation', mesh_name)
                    if not mesh_file:
                        logger.warning('Failed to find mesh file: {}', mesh_name)
                        continue
                    load_xact(context, mesh_file, mesh_name, global_scale, global_matrix, False, False, True,
                              bake_transform)
                    # TODO: Move into actor collection
                else:
                    logger.warning('Encountered unsupported mesh type: {}', mesh_name)
                    continue
            except Exception:
                failed_meshes.add(mesh_name)
                # Remove incompletely imported mesh
                if mesh_name in context.scene.objects:
                    mesh_obj = context.scene.objects[mesh_name]
                    for child in mesh_obj.children:
                        scene_col.objects.unlink(child)
                    scene_col.objects.unlink(mesh_obj)
                continue

            mesh_obj = context.scene.objects[mesh_name]
            mesh_col = bpy.data.collections.new(mesh_name)
            # Add to wrapper collection and remove from scene collection.
            mesh_col.objects.link(mesh_obj)
            scene_col.objects.unlink(mesh_obj)
            for child in mesh_obj.children:
                mesh_col.objects.link(child)
                scene_col.objects.unlink(child)
            scene_col.children.link(mesh_col)
            # Hide from viewport and render of active view layer (cannot set directly on Collection as
            # then also the instance collections are hidden)
            mesh_layer_col = context.view_layer.layer_collection.children[mesh_col.name]
            mesh_layer_col.exclude = True
            mesh_layer_col.hide_viewport = True
        else:
            mesh_col = scene_col.children[mesh_name]

        location = global_matrix @ _parse_vec3(entity['Position'])
        rotation = (global_matrix @ to_blend_quat(
            bCQuaternion(*entity['RotationQ'])).to_matrix().to_4x4()).to_quaternion()
        scaling = _parse_vec3(entity['Scaling'])

        instance_obj = bpy.data.objects.new(
            name=entity_name,
            object_data=None
        )
        instance_obj.instance_collection = mesh_col
        instance_obj.instance_type = 'COLLECTION'
        instance_obj.matrix_basis = Matrix.LocRotScale(location, rotation, scaling)
        scene_col.objects.link(instance_obj)

    if failed_meshes:
        logger.warning('Failed to load the following meshes:')
    for failed_mesh in failed_meshes:
        logger.warning(f'- {failed_mesh}')
