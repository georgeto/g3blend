from bpy.types import Operator, Panel, UIList

from ..extension import defer_migrate


class G3BLEND_UL_FrameEffect_List(UIList):
    bl_idname = "G3BLEND_UL_FrameEffect_List"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        frame_col = layout.column()
        frame_col.prop(item, "key_frame", text="", emboss=False)
        frame_col.scale_x = 0.3
        layout.prop(item, "effect_name", text="", emboss=False)


class G3BLEND_OT_FrameEffect_List_Add(Operator):
    bl_idname = "g3blend.frame_effect_list_add"
    bl_label = "Add"

    def execute(self, context):
        ext = context.active_action.g3blend_ext
        ext.frame_effects.add()
        ext.frame_effects_index = len(ext.frame_effects) - 1
        return {'FINISHED'}


class G3BLEND_OT_FrameEffect_List_Remove(Operator):
    bl_idname = "g3blend.frame_effect_list_remove"
    bl_label = "Remove"

    def execute(self, context):
        ext = context.active_action.g3blend_ext
        idx = ext.frame_effects_index
        if len(ext.frame_effects) > idx:
            ext.frame_effects.remove(idx)
            ext.frame_effects_index = min(idx, max(0, len(ext.frame_effects) - 1))
            return {'FINISHED'}
        else:
            return {"CANCELLED"}


class G3BLEND_OT_FrameEffect_List_MoveUp(Operator):
    bl_idname = "g3blend.frame_effect_list_move_up"
    bl_label = "Move Up"

    def execute(self, context):
        ext = context.active_action.g3blend_ext
        idx = ext.frame_effects_index
        if len(ext.frame_effects) > idx:
            new_index = (idx - 1) % len(ext.frame_effects)
            ext.frame_effects.move(idx, new_index)
            ext.frame_effects_index = new_index
            return {'FINISHED'}
        else:
            return {"CANCELLED"}


class G3BLEND_OT_FrameEffect_List_MoveDown(Operator):
    bl_idname = "g3blend.frame_effect_list_move_down"
    bl_label = "Move Down"

    def execute(self, context):
        ext = context.active_action.g3blend_ext
        idx = ext.frame_effects_index
        if len(ext.frame_effects) > idx:
            new_index = (idx + 1) % len(ext.frame_effects)
            ext.frame_effects.move(idx, new_index)
            ext.frame_effects_index = new_index
            return {'FINISHED'}
        else:
            return {"CANCELLED"}


# Panel to display collection on object properties
class G3BLEND_PT_Action_FrameEffects(Panel):
    bl_label = "Frame Effects"
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_category = "Action"
    bl_region_type = 'UI'
    bl_context = "data"

    def draw(self, context):
        layout = self.layout
        action = context.active_action
        defer_migrate(action)

        row = layout.row()
        # Simulated column headers
        frame_col = row.column()
        frame_col.label(text="Frame")
        frame_col.scale_x = 0.3
        row.label(text="Effect")

        row = layout.row()
        row.template_list(G3BLEND_UL_FrameEffect_List.bl_idname, "", action.g3blend_ext, "frame_effects",
                          action.g3blend_ext, "frame_effects_index")

        col = row.column(align=True)
        col.operator(G3BLEND_OT_FrameEffect_List_Add.bl_idname, icon='ADD', text="")
        col.operator(G3BLEND_OT_FrameEffect_List_Remove.bl_idname, icon='REMOVE', text="")
        col.operator(G3BLEND_OT_FrameEffect_List_MoveUp.bl_idname, icon="TRIA_UP", text="")
        col.operator(G3BLEND_OT_FrameEffect_List_MoveDown.bl_idname, icon="TRIA_DOWN", text="")

    @classmethod
    def poll(cls, context):
        return bool(context.active_action)


classes = (
    G3BLEND_UL_FrameEffect_List,
    G3BLEND_OT_FrameEffect_List_Add,
    G3BLEND_OT_FrameEffect_List_Remove,
    G3BLEND_OT_FrameEffect_List_MoveUp,
    G3BLEND_OT_FrameEffect_List_MoveDown,
    G3BLEND_PT_Action_FrameEffects
)
