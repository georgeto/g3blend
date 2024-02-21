meta:
  id: xact
  title: Gothic 3 animation actor
  file-extension: xact
  endian: le
  encoding: windows-1252
  imports:
    - genomfle
doc: |
  Gothic 3 animation actor format
seq:
  - id: meta
    type: genomfle
  - id: version
    contents: [0x36, 0x00]
  - id: resource_size
    type: u4
  - id: resource_priority
    type: f4
  - id: native_file_time
    type: u8 # bCDateTime
  - id: native_file_size
    type: u4
  - id: boundary_min
    type: vector
  - id: boundary_max
    type: vector
  - id: num_look_at_constraints
    type: u4
  - id: look_at_constraints
    type: look_at_constraint
    repeat: expr
    repeat-expr: num_look_at_constraints
  - id: num_lods
    type: u4
  - id: lods
    type: emfx2_actor
    repeat: expr
    repeat-expr: num_lods
  - id: actor
    type: emfx2_actor
  
types:
  look_at_constraint:
    seq:
      - id: node_name
        type: string
      - id: interpolation_speed
        type: f4
      - id: min_constraints
        type: vector
      - id: max_constraints
        type: vector        
        
  emfx2_actor: # TODO: This is eCWrapper... (maybe extract later)
    seq:
      - id: magic1
        contents: 'gena'
      - id: version
        contents: [0x04, 0x00]
      - id: size
        type: u4
      - id: magic2
        contents: 'FXA '
      - id: high_version
        contents: [1]
      - id: low_version
        contents: [1]
      - id: chunks
        type: chunks
        size: size - 6
      - id: num_materials
        type: u4
      - id: materials
        type: material_reference
        repeat: expr
        repeat-expr: num_materials
      - id: reserved
        contents: [0x01]
        doc: bTArray writes a useless byte during serialization.
      - id: num_lods
        type: u4
      - id: ambient_occlusion
        type: ambient_occlusion
        doc: Per LoD
        repeat: expr
        repeat-expr: num_lods
      - id: tangent_vertices
        type: tangent_vertices
        size: ambient_occlusion[_index].num_per_lod_vertices * 12
        repeat: expr
        repeat-expr: num_lods        
  
  chunks:
    seq:
      - id: chunks
        type: chunk
        repeat: eos
  
  chunk:
    seq:
      - id: chunk_id
        type: u4
        enum: lma_chunk_id
      - id: chunk_size
        type: u4
      - id: version
        type: u4
      - id: content
        type:
          switch-on: chunk_id
          cases:
            'lma_chunk_id::node': cnk_node
            'lma_chunk_id::mesh': cnk_mesh
            'lma_chunk_id::skinninginfo': cnk_skinninginfo
            'lma_chunk_id::material': cnk_material
        size: chunk_size

  cnk_unknown:
    seq:
      - id: data
        size-eos: true

  cnk_node:
    seq:
      - id: version_guard
        process: report_wrong_version
        size: 0
        if: _parent.version != 3
      - id: position
        type: vector
      - id: rotation
        type: quaternion
      - id: scale
        type: vector
      - id: scale_orient
        type: quaternion
      - id: shear
        type: vector
      - id: name
        type: lma_string
      - id: parent
        type: lma_string
  
  cnk_mesh:
    seq:
      - id: version_guard
        process: report_wrong_version
        size: 0
        if: _parent.version != 3
      - id: node_number
        type: u4
      - id: num_org_verts
        type: u4
      - id: total_verts
        type: u4
      - id: total_indices
        type: u4
      - id: num_submeshes
        type: u4
      - id: num_uv_sets
        type: u4
      - id: is_collision_mesh
        type: u1  # boolean
      - id: padding
        size: 3
      - id: submeshes
        type: submesh
        repeat: expr
        repeat-expr: num_submeshes
  
  submesh:
    seq:
      - id: mat_id
        type: u1
      - id: num_uv_sets
        type: u1
      - id: padding
        size: 2
      - id: num_indices
        type: u4
      - id: num_verts
        type: u4
      - id: vertices
        type: vertex
        repeat: expr
        repeat-expr: num_verts
      - id: indices
        type: u4
        repeat: expr
        repeat-expr: num_indices
    instances:
      override_num_uv_sets:
        # Workaround for broken Rimy3D meshes (does not trip the original MeshChunkProcessor3,
        # because it ignores the numUVSets property of submeshes, and instead uses the one from
        # the mesh)
        value: _parent.num_uv_sets
  
  vertex:
    seq:
      - id: org_vertex
        type: u4 
      - id: position
        type: vector
        doc: Z, Y, X
      - id: normal
        type: vector
        doc: Z, Y, X
      - id: uv_sets
        type: vector2
        repeat: expr
        repeat-expr: _parent.override_num_uv_sets
  
  cnk_skinninginfo:
    seq:
      - id: version_guard
        process: report_wrong_version
        size: 0
        if: _parent.version != 1
      - id: node_index
        type: u4
      - id: influences
        type: influences
        repeat: eos
  
  influences:
    seq:
      - id: num_influences
        type: u1
      - id: influences
        type: skin_influence
        repeat: expr
        repeat-expr: num_influences
  
  skin_influence:
    seq:
      - id: node_index
        type: u2
      - id: padding
        size: 2
      - id: weight
        type: f4
  
  cnk_material:
    seq:
      - id: version_guard
        process: report_wrong_version
        size: 0
        if: _parent.version != 5
      - id: ambient_color
        type: float_color
      - id: diffuse_color
        type: float_color
      - id: specular_color
        type: float_color
      - id: emissive_color
        type: float_color
        doc: self illumination color
      - id: shine
        type: f4
      - id: shine_strength
        type: f4
      - id: opacity
        type: f4
        doc: the opacity amount [1.0=full opac, 0.0=full transparent]
      - id: ior
        type: f4
        doc: index of refraction
      - id: double_sided
        type: u1  # boolean
      - id: wire_frame
        type: u1  # boolean
        doc: render in wireframe?
      - id: transparency_type
        type: str
        size: 1
        doc: |
          F -> Filter
          S -> Substractive
          A -> Additive
          U -> Unknown
      - id: padding
        size: 1
      - id: material_name
        type: lma_string
      - id: shader_file_name
        type: lma_string
  
  
  float_color:
    seq:
      - id: red
        type: f4
      - id: green
        type: f4
      - id: blue
        type: f4

  lma_string:
    seq:
      - id: len
        type: u4
      - id: data
        type: str
        size: len

  material_reference:
    seq:
      - id: lod_index
        type: u2
        doc: |
          LoD level inside a emfx2Actor (not to be confused with LoD level in
          eCResourceAnimationActor_PS), seems to be always zero
      - id: mat_index
        type: u2
        doc: |
          MaterialID = matIndex | lodIndex
      - id: name
        type: string
        doc: |
          Needs workaround for broken Rimy3D meshes.
          (they don't have a stringtable, but still refer to stringtable entries here)

  ambient_occlusion:
    seq:
      - id: reserved
        contents: [0x01]
        doc: bTArray writes a useless byte during serialization.
      - id: num_per_lod_vertices
        type: u4
      - id: per_lod_vertices
        type: u4
        repeat: expr
        repeat-expr: num_per_lod_vertices

  tangent_vertices:
    seq:
      - id: values
        type: vector
        repeat: eos

  vector2:
    seq:
      - id: x
        type: f4
      - id: y
        type: f4

  vector:
    seq:
      - id: x
        type: f4
      - id: y
        type: f4  
      - id: z
        type: f4

  quaternion:
    seq:
      - id: x
        type: f4
      - id: y
        type: f4  
      - id: z
        type: f4
      - id: w
        type: f4

  string:
    seq:
      - id: strtab_index
        type: u2

enums:
  lma_chunk_id:
    0: node                   # a node (LMA_Node) coming up next
    1: motionpart             # a motion part (LMA_MotionPart) coming up next
    2: anim                   # an animation (LMA_Anim) coming up next
    3: mesh                   # a mesh (LMA_Mesh) coming up next
    4: skinninginfo           # skinning information (LMA_SkinInfluence)
    5: collisionmesh          # a collision mesh
    6: material               # a material (LMA_Material)
    7: materiallayer          # a material layer (LMA_MaterialLayer)
    8: limit                  # a node limit information
    9: physicsinfo            # physic information
    10: meshexpressionpart    # a mesh expression part
    11: expressionmotionpart  # a expression motion part
    12: phonememotiondata     # list of phonemes and keyframe data
    13: fxmaterial            # a FX material
    16: scene_info            # scene info
