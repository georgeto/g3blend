meta:
  id: genomfle
  title: Gothic 3 common structures
  endian: le
  encoding: windows-1252
doc: |
  Gothic 3 common structures
seq:
  - id: header
    type: genomfle_header
instances:  
  tail:
    type: genomfle_tail
    pos: header.tail_offset
  content_size:
    value: header.tail_offset - _io.pos
types:
  genomfle_header:
    seq:
      - id: magic
        contents: 'GENOMFLE'
      - id: version
        type: u2
      - id: tail_offset
        type: u4
  genomfle_tail:
    seq:
      - id: deadbeef
        contents: [0xef, 0xbe, 0xad, 0xde]
      - id: strtbl_present
        type: u1
      - id: num_strtbl_entries
        type: u4
        if: strtbl_present == 1
      - id: strtbl_entries
        type: genomfle_str
        repeat: expr
        repeat-expr: num_strtbl_entries
        if: strtbl_present== 1
  genomfle_str:
    seq:
      - id: len
        type: u2
      - id: data
        type: str
        size: len
