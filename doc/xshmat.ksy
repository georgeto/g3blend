meta:
  id: xshmat
  title: Gothic 3 shader material
  file-extension: xshmat
  endian: le
  encoding: windows-1252
  imports:
    - genomfle
doc: |
  Gothic 3 shader material format
seq:
  - id: meta
    type: genomfle
  - id: sub_class
    type: sub_class
  # Post class version
  - id: res_base
    type: ec_resource_base_ps
  # eCResourceShaderMaterial_PS
  - id: shader
    type: ec_shader_base_ps
types:
  sub_class:
    seq:
      - id: sub_class_identifier
        contents: [0x01, 0x00, 0x01, 0x01, 0x00, 0x01]
      - id: class_name
        type: string
      - id: type_to_version_filler
        contents: [0x01, 0x00, 0x00, 0x53, 0x00]
      - id: version
        type: u2
      - id: deadcode_offset
        type: u4
      - id: dicard_entry
        type: string
        if: version == 1
      - id: dicard_guid
        size: 20
        if: version <= 0x51 
      - id: property_class_version
        type: u2
      - id: property_type_count
        type: u4
      - id: properties
        type: class_property
        repeat: expr
        repeat-expr: property_type_count
      # TODO: Pre class version
      - id: class_version
        type: u2


  class_property:
    seq:
      - id: name
        type: string
      - id: class_type
        type: string
      - id: magic_value
        type: u2
      - id: size
        type: u4
      - id: data
        size: size

  # eCResourceBase_PS
  ec_resource_base_ps:
    seq:
      - id: resource_version
        type: u2
      - id: resource_size
        type: u4
        if: resource_version >= 0x17
      - id: discard_skip1
        type: u1
        if: resource_version < 0x1E
      - id: discard_skip2
        type: u1
        if: resource_version < 0x1E and discard_skip1 > 1

  # eCResourceBase_PS
  ec_shader_base_ps:
    seq:
      - id: sub_class
        type: sub_class

  string:
    seq:
      - id: strtab_index
        type: u2