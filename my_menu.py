import bpy
from . import stretch_vertex
from . import create_ico_sphere
from . import export_scene

# --- UI：トップバーに表示される独自メニュー ---
class TOPBAR_MT_my_menu(bpy.types.Menu):
    """トップバーのメニュー項目を定義するクラス"""
    bl_idname = "TOPBAR_MT_my_menu"
    bl_label = "MyMenu"
    bl_description = "自作のレベル編集機能にアクセスするメニュー"

    def draw(self, context):
        """メニューの中身を描画"""
        layout = self.layout
        # 各オペレータをメニューに追加
        layout.operator(stretch_vertex.MYADDON_OT_stretch_vertex.bl_idname, text=stretch_vertex.MYADDON_OT_stretch_vertex.bl_label)
        layout.operator(create_ico_sphere.MYADDON_OT_create_ico_sphere.bl_idname, text=create_ico_sphere.MYADDON_OT_create_ico_sphere.bl_label)
        layout.operator(export_scene.MYADDON_OT_export_scene.bl_idname, text=export_scene.MYADDON_OT_export_scene.bl_label)
        
        # メニュー内に区切り線を引く
        layout.separator()
        
        # 外部URLを開く既存のオペレータを使ってヘルプ項目を作成
        layout.operator("wm.url_open_preset", text="Manual", icon='HELP')
        layout.operator("wm.url_open_preset", text="Tutorial", icon='HELP')
        layout.operator("wm.url_open_preset", text="Support", icon='HELP')

    def submenu(self, context):
        # 既存のメニュー構造に自分自身を追加するための関数
        self.layout.menu(TOPBAR_MT_my_menu.bl_idname)