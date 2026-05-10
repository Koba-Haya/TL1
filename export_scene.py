import bpy
import bpy_extras
import math
import json
import mathutils

# --- オペレータ3：シーン出力 (JSON形式・再帰パッキング版) ---
class MYADDON_OT_export_scene(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """シーン内の全オブジェクトを親子関係を保ち、JSON形式でファイル出力するクラス"""
    bl_idname = "myaddon.myaddon_ot_export_scene"
    bl_label = "シーン出力"
    bl_description = "現在のシーン情報を階層構造を維持したJSONファイルとして保存します"
    bl_options = {'REGISTER', 'UNDO'}

    # 出力するファイルの拡張子を.jsonに設定
    filename_ext = ".json"

    def parse_scene_recursive_json(self, data_parent, object, level):
        """深さ優先探索（DFS）を用いて、オブジェクト1個分の情報をdictにパッキングし、親のリストに追加する"""
        
        # シーンのオブジェクト1個分のjsonオブジェクト(dict)生成
        json_object = dict()
        # オブジェクト種類と名前を格納
        json_object["type"] = object.type
        json_object["name"] = object.name

        # トランスフォーム行列（matrix_local）から位置・回転・スケールを分離取得
        trans, rot, scale = object.matrix_local.decompose()
        # 回転情報をクォータニオンからオイラー角に変換し、さらに度数法に変換
        rot = rot.to_euler()
        rot_x = math.degrees(rot.x)
        rot_y = math.degrees(rot.y)
        rot_z = math.degrees(rot.z)

        # トランスフォーム情報をディクショナリに登録
        transform = dict()
        # ゲームエンジン側の座標系（例：Yが上、Zが奥）に合わせる場合はここで軸を入れ替える
        transform["translation"] = (trans.x, trans.y, trans.z)
        transform["rotation"] = (rot_x, rot_y, rot_z)
        transform["scaling"] = (scale.x, scale.y, scale.z)
        # まとめて1個分のjsonオブジェクトに登録
        json_object["transform"] = transform

        # カスタムプロパティ 'file_name' がある場合は追加
        if "file_name" in object:
            json_object["file_name"] = object["file_name"]

        # カスタムプロパティ 'collider' がある場合
        if "collider" in object:
            collider = dict()
            collider["type"] = object["collider"]
            # mathutils.Vector型はそのままではエンコードできないため、to_list()でリストに変換する
            collider["center"] = object["collider_center"].to_list()
            collider["size"] = object["collider_size"].to_list()
            json_object["collider"] = collider

        # --- カスタムプロパティ '無効オプション' がある場合は追加 ---
        if "無効オプション" in object:
            json_object["無効オプション"] = object["無効オプション"]

        # 1個分の情報をまとめた後、親オブジェクトの引数リストに子供として登録
        data_parent.append(json_object)

        # 子オブジェクトが存在する場合、レベルを1つ上げて自分自身を呼び出す（再帰）
        if len(object.children) > 0:
            json_object["children"] = list()
            for child in object.children:
                self.parse_scene_recursive_json(json_object["children"], child, level + 1)

    def export_json(self):
        """JSON形式でのパッキングからファイル書き出しまでを行うメイン処理"""
        # 保存する情報をまとめるルートのdict（連想配列）を作成
        json_object_root = dict()
        # ローダー側でのファイルチェック用識別名
        json_object_root["name"] = "scene"
        json_object_root["objects"] = list()

        # シーン内の全オブジェクトを走査してパック
        for object in bpy.context.scene.objects:
            # 親がいるオブジェクトは子として再帰的に呼ばれるため、ここではルートのみ処理 
            if object.parent:
                continue
            # ルートオブジェクト（深さ0）として解析を開始 
            self.parse_scene_recursive_json(json_object_root["objects"], object, 0)

        # オブジェクトをJSON文字列にエンコード（改行・インデント付き）
        # ensure_ascii=Falseで日本語化けを防ぎ、indent=4で見やすく整形する 
        json_text = json.dumps(json_object_root, ensure_ascii=False, cls=json.JSONEncoder, indent=4)
        
        # コンソールに表示（確認用）
        print(json_text)

        # ファイルをテキスト形式で安全に開く（UTF-8指定）
        with open(self.filepath, "wt", encoding="utf-8") as file:
            # JSON文字列を一括で書き込む
            file.write(json_text)

    def execute(self, context):
        # JSON形式のエクスポート処理を実行
        print("シーン情報をExportします")
        self.export_json()
        self.report({'INFO'}, "シーン情報をExportしました")
        print("シーン情報をExportしました")
        return {'FINISHED'}