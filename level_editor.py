import bpy
import math # ラジアンから度数法への変換に使用 

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

# --- オペレータ3：シーン出力 (トランスフォーム情報・親子関係表示) ---
class MYADDON_OT_export_scene(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_export_scene"
    bl_label = "シーン出力"
    bl_description = "シーン情報をExportします"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # シーン情報をExportする処理 
        print("シーン情報をExportします")

        # シーン内の全オブジェクトについて走査 
        for object in bpy.context.scene.objects:
            # オブジェクトの種類と名前を表示 
            print(object.type + " - " + object.name)

            # ローカルトランスフォーム行列から平行移動、回転、スケーリングを抽出 
            # 型は Vector, Quaternion, Vector
            trans, rot, scale = object.matrix_local.decompose()

            # 回転を Quaternion から Euler (3軸での回転角) に変換 
            rot = rot.to_euler()

            # ラジアンから度数法に変換 
            rot.x = math.degrees(rot.x)
            rot.y = math.degrees(rot.y)
            rot.z = math.degrees(rot.z)

            # トランスフォーム情報を表示 (C風の書式指定子を使用) 
            print("Trans(%f,%f,%f)" % (trans.x, trans.y, trans.z))
            print("Rot(%f,%f,%f)" % (rot.x, rot.y, rot.z))
            print("Scale(%f,%f,%f)" % (scale.x, scale.y, scale.z))

            # 親オブジェクトがある場合は名前を表示 
            if object.parent:
                print("Parent: " + object.parent.name)
            
            # オブジェクト間の区切り用空行 
            print()

        print("シーン情報をExportしました")
        self.report({'INFO'}, "シーン情報をExportしました")
        
        return {'FINISHED'}

# トップバーの拡張メニュークラス
class TOPBAR_MT_my_menu(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_my_menu" # クラスを識別するID
    bl_label = "MyMenu"              # 表示名
    bl_description = "拡張メニュー by " + bl_info["author"] # 説明文

    # サブメニュー内の描画処理
    def draw(self, context):
        layout = self.layout
        
        # 自作オペレータをメニューに追加 (資料11枚目)
        layout.operator(MYADDON_OT_stretch_vertex.bl_idname, text=MYADDON_OT_stretch_vertex.bl_label)
        layout.operator(MYADDON_OT_create_ico_sphere.bl_idname, text=MYADDON_OT_create_ico_sphere.bl_label)
        # シーン走査オペレータを追加
        layout.operator(MYADDON_OT_export_scene.bl_idname, text=MYADDON_OT_export_scene.bl_label)
        
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
    MYADDON_OT_export_scene,
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