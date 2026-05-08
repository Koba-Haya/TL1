import bpy

# ブレンダーに登録するアドオン情報
bl_info = {
    "name": "レベルエディタ",
    "author": "Hayato Kobayashi",
    "version": (1, 0),
    "blender": (3, 3, 1),
    "location": "TopBar > MyMenu",
    "description": "レベルエディタ",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object",
}

# --- オペレータ1：頂点を伸ばす ---
class MYADDON_OT_stretch_vertex(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_stretch_vertex" # クラスを識別するID
    bl_label = "頂点を伸ばす"                         # 表示名
    bl_description = "頂点座標を引っ張って伸ばします"   # 説明文
    # アドオンの実行履歴に登録し、やり直し(Undo)を可能にする
    bl_options = {'REGISTER', 'UNDO'}

    # 実行される中身
    def execute(self, context):
        # 名前が "Cube" のオブジェクトの0番目の頂点を移動させる
        if "Cube" in bpy.data.objects:
            bpy.data.objects["Cube"].data.vertices[0].co.x += 1.0
            self.report({'INFO'}, "頂点を伸ばしました。")
        else:
            self.report({'WARNING'}, "Cubeが見つかりません。")
        
        return {'FINISHED'} # 正常終了を通知

# --- オペレータ2：ICO球生成 ---
class MYADDON_OT_create_ico_sphere(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_create_object" # 資料のIDに合わせる
    bl_label = "ICO球生成"
    bl_description = "ICO球を生成します"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Blender標準のメッシュ生成コマンドを呼び出す
        bpy.ops.mesh.primitive_ico_sphere_add()
        self.report({'INFO'}, "ICO球を生成しました。")
        return {'FINISHED'}

# トップバーの拡張メニュークラス
class TOPBAR_MT_my_menu(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_my_menu" # クラスを識別するID
    bl_label = "MyMenu"              # 表示名
    bl_description = "拡張メニュー by " + bl_info["author"] # 説明文

    # サブメニュー内の描画処理
    def draw(self, context):
        layout = self.layout
        
        # 自作オペレータをメニューに追加
        layout.operator(MYADDON_OT_stretch_vertex.bl_idname, text=MYADDON_OT_stretch_vertex.bl_label)
        layout.operator(MYADDON_OT_create_ico_sphere.bl_idname, text=MYADDON_OT_create_ico_sphere.bl_label)
        
        # 区切り線を追加
        layout.separator()
        
        # オペレータ（マニュアル等）を追加
        layout.operator("wm.url_open_preset", text="Manual", icon='HELP')
        layout.operator("wm.url_open_preset", text="Tutorial", icon='HELP')
        layout.operator("wm.url_open_preset", text="Support", icon='HELP')

    # 既存のメニューに自分自身を追加するための関数
    def submenu(self, context):
        self.layout.menu(TOPBAR_MT_my_menu.bl_idname)

# 登録するクラスのリスト
classes = (
    MYADDON_OT_stretch_vertex,
    MYADDON_OT_create_ico_sphere,
    TOPBAR_MT_my_menu,
)

# アドオン有効化時コールバック
def register():
    # 自作クラスをBlenderに登録
    for cls in classes:
        bpy.utils.register_class(cls)
    # メニューをトップバーに追加
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_my_menu.submenu)

# アドオン無効化時コールバック
def unregister():
    # メニューをトップバーから削除
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_my_menu.submenu)
    # 自作クラスをBlenderから登録解除
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

# スクリプトエディタから直接実行する場合の処理
if __name__ == "__main__":
    register()