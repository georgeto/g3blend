import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import bpy
from mathutils import Matrix, Vector

from .io_import_xact import load_xact
from .io_import_xcmsh import load_xcmsh
from .. import log as logging
from ..io.property_sets import eCResourceMeshLoD_PS
from ..io.property_types import bCVector
from ..io.types import bCQuaternion
from ..util import read_genome_file, to_blend_quat, to_blend_vec, without_scale

logger = logging.getLogger(__name__)


@dataclass
class _ImportState:
    context: bpy.types.Context
    global_scale: float
    global_matrix: Matrix
    bake_transform: bool


def _find_file(base_dir: Path, name: str) -> Optional[Path]:
    # TODO: Passing user-provided name to path might be insecure...
    for file in base_dir.glob('**/' + name):
        if file.is_file() and file.name == name:
            return file
    return None


def _parse_vec3(raw: str) -> Vector:
    splitted = raw.replace('//', '').split('/')
    return to_blend_vec(bCVector(float(splitted[0]), float(splitted[1]), float(splitted[2])))


def load_world(context: bpy.types.Context, filepath: Path, data_dir: Path, import_position: Vector,
               import_radius: float, ignore_y: bool, global_scale: float, global_matrix: Matrix, bake_transform: bool):
    if not data_dir.is_dir() or not (data_dir / '_compiledMesh').is_dir():
        raise ValueError('Please specify a valid resource directory')

    with filepath.open('r') as f:
        entities_list = json.load(f)

    # Checking whether a name is in context.scene.objects is really slow (iterates through all entries each time),
    # therefore we manage a set of known entities (object names) to speedup the process.
    known_entities = {obj.name for obj in context.scene.objects}
    failed_meshes = set()
    mapped_meshes = {}

    global_matrix_no_scale = without_scale(global_matrix)
    global_matrix_no_scale_inv = global_matrix_no_scale.inverted_safe()

    def get_or_create_col(name: str):
        col = bpy.data.collections[name]
        if col is None:
            col = bpy.data.collections.new(name)
            context.scene.collection.children.link(col)
        return col

    entities_col = get_or_create_col('Entities')
    landscape_col = get_or_create_col('Landscape')
    meshes_col = get_or_create_col('Meshes')

    for entity in entities_list['Entities']:
        # Filter lowpoly entities...
        if 'LOWPOLY' in entity['Name']:
            continue

        # TODO: Include NPCs as owner of body parts?
        # TODO: Attachable body parts (beard for example)
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
        if entity_name in known_entities:
            continue

        filter_location = _parse_vec3(entity['Position'])
        filter_location = Vector((filter_location.x, filter_location.z, filter_location.y))
        # TODO: Landscape seems incorrectly scaled or something, does not align at least.
        #       NO, not only landscape, it is everything. Everything is somehow misaligned. Maybe missing some conversion? Or apply of global matrix?
        #       -> Indeed meshes are wrongly rotated / flipped (see the sawlog in ardea, or the rotation of the hero).
        #       -> YESSSS, rotating the global matrix by 180° helps. Weird. Ah of course, we apply the global matrix twice.
        #       -> Once on import of the meshes and once on the object instance.
        filter_relative = filter_location - import_position
        if ignore_y:
            filter_relative.y = 0
        if filter_relative.length > import_radius and 'Landscape' not in mesh_name:
            continue

        if mesh_name in mapped_meshes:
            mesh_name = mapped_meshes[mesh_name]

        if mesh_name not in meshes_col.children:
            mesh_col = bpy.data.collections.new(mesh_name)
            meshes_col.children.link(mesh_col)

            try:
                # Lookup first mesh in LoD mesh.
                if mesh_name.endswith('.xlmsh'):
                    mesh_file = _find_file(data_dir / '_compiledMesh', mesh_name)
                    if not mesh_file:
                        logger.warning('Failed to find mesh file: {}', mesh_name)
                        continue
                    mesh_lod = read_genome_file(mesh_file, eCResourceMeshLoD_PS, allow_fallback=True)
                    mapped_meshes[mesh_name] = mesh_lod.meshes[0]
                    mesh_name = mesh_lod.meshes[0]

                if mesh_name.endswith('.xcmsh'):
                    mesh_file = _find_file(data_dir / '_compiledMesh', mesh_name)
                    if not mesh_file:
                        logger.warning('Failed to find mesh file: {}', mesh_name)
                        continue
                    load_xcmsh(context, mesh_file, mesh_name, global_scale, global_matrix, bake_transform, mesh_col)
                    # TODO: Move into mesh collection
                elif mesh_name.endswith('.xact'):
                    mesh_file = _find_file(data_dir / '_compiledAnimation', mesh_name)
                    if not mesh_file:
                        logger.warning('Failed to find mesh file: {}', mesh_name)
                        continue
                    load_xact(context, mesh_file, mesh_name, global_scale, global_matrix, False, False, True,
                              bake_transform, mesh_col)
                    # TODO: Move into actor collection
                else:
                    logger.warning('Encountered unsupported mesh type: {}', mesh_name)
                    continue
            except Exception as e:
                failed_meshes.add(mesh_name)
                # Remove incompletely imported mesh
                bpy.data.collections.remove(mesh_col)
                continue

            # Hide from viewport and render of active view layer (cannot set directly on Collection as
            # then also the instance collections are hidden)
            mesh_layer_col = context.view_layer.layer_collection.children[meshes_col.name].children[mesh_col.name]
            mesh_layer_col.exclude = True
            mesh_layer_col.hide_viewport = True
        else:
            mesh_col = meshes_col.children[mesh_name]

        # TODO: Not sure if this is correct and whether we should forward global_matrix/scale into the mesh loading.
        location = _parse_vec3(entity['Position']) * global_scale
        rotation = to_blend_quat(bCQuaternion(*entity['RotationQ']))
        scaling = _parse_vec3(entity['Scaling'])

        instance_obj = bpy.data.objects.new(
            name=entity_name,
            object_data=None
        )
        instance_obj.instance_collection = mesh_col
        instance_obj.instance_type = 'COLLECTION'
        instance_obj.matrix_basis = global_matrix_no_scale @ Matrix.LocRotScale(location, rotation,
                                                                                scaling) @ global_matrix_no_scale_inv
        if 'Landscape' in mesh_name:
            landscape_col.objects.link(instance_obj)
        else:
            entities_col.objects.link(instance_obj)
        known_entities.add(entity_name)

    if failed_meshes:
        logger.warning('Failed to load the following meshes:')
    for failed_mesh in failed_meshes:
        logger.warning(f'- {failed_mesh}')
