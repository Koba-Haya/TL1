import bpy

# ブレンダーに登録するアドオン情報
bl_info = {
    "name": "レベルエディタ",
    "author": "Hayato Kobayashi",
    "version": (1, 0),
    "blender": (3, 3, 1),
    "location": "",
    "description": "レベルエディタ",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object",
}

# トップバーの拡張メニュークラス
class TOPBAR_MT_my_menu(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_my_menu" # クラスを識別するID
    bl_label = "MyMenu"              # 表示名
    bl_description = "拡張メニュー by " + bl_info["author"] # 説明文

    # サブメニュー内の描画処理
    def draw(self, context):
        layout = self.layout
        # オペレータ（マニュアル）を追加
        layout.operator("wm.url_open_preset", text="Manual", icon='HELP')
        layout.operator("wm.url_open_preset", text="Tutorial", icon='HELP')
        
        # 区切り線を追加
        layout.separator()
        
        layout.operator("wm.url_open_preset", text="Support", icon='HELP')

    # 既存のメニューに自分自身を追加するための関数
    def submenu(self, context):
        self.layout.menu(TOPBAR_MT_my_menu.bl_idname)

# 登録するクラスのリスト
classes = (
    TOPBAR_MT_my_menu,
)

# アドオン有効化時コールバック
def register():
    # 自作クラスをBlenderに登録
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # トップバーにサブメニューを追加
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_my_menu.submenu)
    print("レベルエディタが有効化されました。")

# アドオン無効化時コールバック
def unregister():
    # トップバーからサブメニューを削除
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_my_menu.submenu)
    
    # 自作クラスをBlenderから登録解除
    for cls in classes:
        bpy.utils.unregister_class(cls)
    print("レベルエディタが無効化されました。")

# テスト用実行コード
if __name__ == "__main__":
    register()