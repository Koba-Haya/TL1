import bpy
import bpy_extras # ファイル保存ダイアログ（ExportHelper）を利用するためにインポート
import math       # 回転の値をラジアンから度数法（Degree）に変換するために使用
import gpu        # 描画周りを手広くサポートするモジュール
import gpu_extras.batch # ジオメトリバッチ（シェーダ、トポロジー、頂点、インデックスをまとめたもの）を提供
import copy       # リストを丸ごとコピーして増やしたい場合に使用するPython標準モジュール

# ブレンダーのアドオン管理画面に表示される情報
bl_info = {
    "name": "レベルエディタ",
    "author": "Hayato Kobayashi",
    "version": (1, 0),
    "blender": (3, 3, 1),
    "location": "TopBar > MyMenu",
    "description": "オブジェクトの階層構造を維持してファイル出力するレベルエディタ",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object",
}

# --- 描画拡張：コライダー描画クラス ---
class DrawCollider:
    """コライダー描画関数と、それに関連する静的メンバ変数をまとめるためのクラス"""
    # 描画ハンドル
    handle = None

    # 3Dビューに登録する描画関数
    def draw_collider():
        # 頂点データ（動的配列）
        vertices = {"pos": []}
        # インデックスデータ（動的配列）
        indices = []

        # 立方体の頂点となる8点分のローカル座標をデータとして用意（オブジェクト中心からのオフセット）
        offsets = [
            [-0.5, -0.5, -0.5], # 左下前
            [+0.5, -0.5, -0.5], # 右下前
            [-0.5, +0.5, -0.5], # 左上前
            [+0.5, +0.5, -0.5], # 右上前
            [-0.5, -0.5, +0.5], # 左下奥
            [+0.5, -0.5, +0.5], # 右下奥
            [-0.5, +0.5, +0.5], # 左上奥
            [+0.5, +0.5, +0.5], # 右上奥
        ]
        # 立方体のX,Y,Z方向サイズ（今回は一律2m）
        size = [2.0, 2.0, 2.0]

        # 現在シーンのオブジェクトリストを走査し、全オブジェクトについて処理
        for object in bpy.context.scene.objects:
            # 追加前の頂点数を記録（インデックス指定の基準にするため）
            start = len(vertices["pos"])

            # Boxの8頂点分回す
            for offset in offsets:
                # オブジェクトの中心座標をコピー
                pos = copy.copy(object.location)
                # 中心点を基準に各頂点ごとにずらす
                pos[0] += offset[0] * size[0]
                pos[1] += offset[1] * size[1]
                pos[2] += offset[2] * size[2]
                # 共有する頂点データリストに座標を追加
                vertices["pos"].append(pos)

            # ラインリスト（12本分）のインデックスデータを追加
            # 前面を構成する辺
            indices.append([start + 0, start + 1])
            indices.append([start + 2, start + 3])
            indices.append([start + 0, start + 2])
            indices.append([start + 1, start + 3])
            # 奥面を構成する辺
            indices.append([start + 4, start + 5])
            indices.append([start + 6, start + 7])
            indices.append([start + 4, start + 6])
            indices.append([start + 5, start + 7])
            # 手前と奥を繋ぐ辺
            indices.append([start + 0, start + 4])
            indices.append([start + 1, start + 5])
            indices.append([start + 2, start + 6])
            indices.append([start + 3, start + 7])

        # ビルトインのシェーダ（色指定のみの3D描画用）を取得
        shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        # バッチを作成（シェーダ、トポロジー"LINES"、頂点、インデックスを指定）
        batch = gpu_extras.batch.batch_for_shader(shader, "LINES", vertices, indices=indices)

        # シェーダのパラメータ設定（水色）
        color = [0.5, 1.0, 1.0, 1.0]
        shader.bind()
        shader.uniform_float("color", color)
        # 全オブジェクト分を1回で描画
        batch.draw(shader)

# --- オペレータ1：頂点を伸ばす --- 
class MYADDON_OT_stretch_vertex(bpy.types.Operator):
    """名前が 'Cube' のオブジェクトの特定の頂点を移動させるクラス"""
    bl_idname = "myaddon.myaddon_ot_stretch_vertex" 
    bl_label = "頂点を伸ばす"
    bl_description = "Cubeの0番目の頂点座標をX軸方向に移動させます"
    # 実行履歴に登録し、Undo（取り消し）を可能にする
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # シーン内にCubeが存在するかチェック
        if "Cube" in bpy.data.objects:
            # 頂点データを直接書き換えて移動させる
            bpy.data.objects["Cube"].data.vertices[0].co.x += 1.0
            self.report({'INFO'}, "頂点を伸ばしました。")
        else:
            # Cubeがない場合は警告を出す
            self.report({'WARNING'}, "Cubeが見つかりません。")
        
        return {'FINISHED'}

# --- オペレータ2：ICO球生成 ---
class MYADDON_OT_create_ico_sphere(bpy.types.Operator):
    """標準機能を使ってICO球をシーンに追加するクラス"""
    bl_idname = "myaddon.myaddon_ot_create_object" 
    bl_label = "ICO球生成"
    bl_description = "ICO球を生成します"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Blender標準のメッシュ生成コマンド（bpy.ops）を内部で実行
        bpy.ops.mesh.primitive_ico_sphere_add()
        self.report({'INFO'}, "ICO球を生成しました。")
        return {'FINISHED'}

# --- オペレータ3：シーン出力 (再帰によるツリー構造 & 整形出力) ---
class MYADDON_OT_export_scene(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """シーン内の全オブジェクトを親子関係を保ち、識別子を付けてファイル出力するクラス"""
    bl_idname = "myaddon.myaddon_ot_export_scene"
    bl_label = "シーン出力"
    bl_description = "現在のシーン情報を階層構造（インデント）付きで.sceneファイルに保存します"
    bl_options = {'REGISTER', 'UNDO'}

    # ExportHelperで作成されるファイル保存ウィンドウのデフォルト拡張子
    filename_ext = ".scene"

    def write_and_print(self, file, text):
        """コンソールへの表示とファイルへの書き出しを同時に行い、自動で改行を付与する"""
        print(text)           # Blenderのシステムコンソールに出力
        file.write(text)      # オープン中のファイルに書き込み
        file.write('\n')      # 改行コードを追加 

    def parse_scene_recursive(self, file, object, level):
        """深さ優先探索（DFS）を用いて、子オブジェクトを再帰的に解析・出力する"""
        
        # 現在の階層（深さ）に応じてタブ文字を作成し、インデントを表現する
        indent = '\t' * level

        # ローダーでの判別を容易にするため、オブジェクトの種類を出力 
        self.write_and_print(file, indent + object.type)

        # トランスフォーム行列（matrix_local）から位置・回転・スケールを分離取得
        trans, rot, scale = object.matrix_local.decompose()
        
        # 回転情報をクォータニオンからオイラー角に変換し、さらに度数法に変換
        rot = rot.to_euler()
        rot_x = math.degrees(rot.x)
        rot_y = math.degrees(rot.y)
        rot_z = math.degrees(rot.z)

        # 識別子（T, R, S）を付け、半角スペース区切りで情報を出力 
        self.write_and_print(file, indent + "T %f %f %f" % (trans.x, trans.y, trans.z))
        self.write_and_print(file, indent + "R %f %f %f" % (rot_x, rot_y, rot_z))
        self.write_and_print(file, indent + "S %f %f %f" % (scale.x, scale.y, scale.z))
        
        # カスタムプロパティ 'file_name' がある場合は識別子 'N' を付けて出力 
        if "file_name" in object:
            self.write_and_print(file, indent + "N %s" % object["file_name"])

        # オブジェクトデータの区切りを示す 'END' を出力 
        self.write_and_print(file, indent + 'END')
        self.write_and_print(file, '')

        # 子オブジェクトが存在する場合、レベルを1つ上げて自分自身を呼び出す（再帰）
        for child in object.children:
            self.parse_scene_recursive(file, child, level + 1)

    def export(self):
        """ファイルオープンからルートオブジェクトの走査までを行うメインエクスポート処理"""
        # 保存先パスはExportHelperによって self.filepath に格納されている
        print("シーン情報出力開始... %r" % self.filepath)

        # ファイルを書き出しモード（wt: write text）で安全に開く
        with open(self.filepath, "wt") as file:
            file.write("SCENE\n")

            # まずはシーン内の全オブジェクトの中から「親がいない（ルート）」ものだけを探す
            for object in bpy.context.scene.objects:
                # 親がいるオブジェクトは、その親の処理の中で再帰的に呼ばれるためここではスキップ 
                if object.parent:
                    continue
                
                # ルートオブジェクト（深さ0）として解析を開始
                self.parse_scene_recursive(file, object, 0)

    def execute(self, context):
        # export処理を実行
        self.export()
        self.report({'INFO'}, "シーン情報をExportしました")
        return {'FINISHED'}

# --- オペレータ4：カスタムプロパティ['file_name']追加 ---
class MYADDON_OT_add_filename(bpy.types.Operator):
    """今選択中のオブジェクトに 'file_name' というカスタムプロパティを追加するクラス"""
    bl_idname = "myaddon.myaddon_ot_add_filename"
    bl_label = "FileName 追加"
    bl_description = "['file_name']カスタムプロパティを追加します"
    # Undoを可能にする
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # 今選択中のオブジェクトに対してカスタムプロパティを辞書形式で追加
        context.object["file_name"] = ""
        return {'FINISHED'}

# --- UI：プロパティウィンドウ内のパネル拡張 ---
class OBJECT_PT_file_name(bpy.types.Panel):
    """オブジェクトのプロパティウィンドウに表示される、動的に表示が切り替わるカスタムパネル"""
    bl_idname = "OBJECT_PT_file_name"
    bl_label = "FileName"
    bl_space_type = "PROPERTIES" # プロパティウィンドウを指定
    bl_region_type = "WINDOW"
    bl_context = "object"         # オブジェクトモード時に表示

    def draw(self, context):
        """パネル内のUIレイアウトを描画し、プロパティの有無で表示を切り替える"""
        layout = self.layout
        
        # オブジェクトに 'file_name' カスタムプロパティがあるかチェック 
        if "file_name" in context.object:
            # 既にプロパティがあれば、直接編集できるプロパティフィールドを表示 
            layout.prop(context.object, '["file_name"]', text=self.bl_label)
        else:
            # プロパティがなければ、追加するためのオペレータボタンを表示 
            layout.operator(MYADDON_OT_add_filename.bl_idname)

# --- UI：トップバーに表示される独自メニュー ---
class TOPBAR_MT_my_menu(bpy.types.Menu):
    """トップバーのメニュー項目を定義するクラス"""
    bl_idname = "TOPBAR_MT_my_menu"
    bl_label = "MyMenu"
    bl_description = "自作のレベル編集機能にアクセスするメニュー"

    def draw(self, context):
        layout = self.layout
        
        # 各オペレータをメニューに追加
        layout.operator(MYADDON_OT_stretch_vertex.bl_idname, text=MYADDON_OT_stretch_vertex.bl_label)
        layout.operator(MYADDON_OT_create_ico_sphere.bl_idname, text=MYADDON_OT_create_ico_sphere.bl_label)
        layout.operator(MYADDON_OT_export_scene.bl_idname, text=MYADDON_OT_export_scene.bl_label)
        
        # メニュー内に区切り線を引く
        layout.separator()
        
        # 外部URLを開く既存のオペレータを使ってヘルプ項目を作成
        layout.operator("wm.url_open_preset", text="Manual", icon='HELP')
        layout.operator("wm.url_open_preset", text="Tutorial", icon='HELP')
        layout.operator("wm.url_open_preset", text="Support", icon='HELP')

    def submenu(self, context):
        # 既存のメニュー構造に自分自身を追加するための関数
        self.layout.menu(TOPBAR_MT_my_menu.bl_idname)

# 登録対象となるクラスのリスト。順序は依存関係に合わせる
classes = (
    MYADDON_OT_stretch_vertex,
    MYADDON_OT_create_ico_sphere,
    MYADDON_OT_export_scene,
    MYADDON_OT_add_filename,
    OBJECT_PT_file_name,
    TOPBAR_MT_my_menu,
)

def register():
    """アドオン有効化時にクラスをBlenderに登録する"""
    for cls in classes:
        bpy.utils.register_class(cls)
    # 既存のトップバーメニューの末尾に、定義したサブメニューを追加
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_my_menu.submenu)
    
    # アドオン有効化時に、3Dビューのクラスに描画関数を登録する。登録時にハンドルが返ってくる。
    DrawCollider.handle = bpy.types.SpaceView3D.draw_handler_add(DrawCollider.draw_collider, (), "WINDOW", "POST_VIEW")
    print("レベルエディタが有効化されました。")

def unregister():
    """アドオン無効化時に登録を解除する"""
    # アドオン無効化時に、3Dビューに登録した描画関数を登録解除する。
    bpy.types.SpaceView3D.draw_handler_remove(DrawCollider.handle, "WINDOW")

    # 登録時とは逆の順序でメニューを削除
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_my_menu.submenu)
    # クラスの登録解除
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("レベルエディタが無効化されました。")

# スクリプトとして直接実行された場合の処理
if __name__ == "__main__":
    register()