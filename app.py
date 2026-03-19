#!/usr/bin/env python3
"""
中綴じ面付け GUIアプリ
Flask バックエンド
"""

import json
import subprocess
from pathlib import Path

from flask import Flask, render_template, request, jsonify
from pypdf import PdfReader, PdfWriter, PageObject, Transformation

app = Flask(__name__)

# 選択されたファイルの実パス
_selected_file_path = None


def get_imposition_order(total_pages):
    """中綴じの面付け順を計算する"""
    pairs = []
    sheets = total_pages // 4

    for sheet in range(sheets):
        front_left = total_pages - sheet * 2
        front_right = sheet * 2 + 1
        back_left = sheet * 2 + 2
        back_right = total_pages - sheet * 2 - 1

        pairs.append({"left": front_left, "right": front_right, "side": "おもて"})
        pairs.append({"left": back_left, "right": back_right, "side": "うら"})

    return pairs


def impose(input_path, output_path=None):
    """面付け処理を実行"""
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)

    if total_pages % 4 != 0:
        raise ValueError(f"ページ数({total_pages})が4の倍数ではありません。")

    first_page = reader.pages[0]
    page_width = float(first_page.mediabox.width)
    page_height = float(first_page.mediabox.height)

    # A4横サイズ (pt)
    A4_LANDSCAPE_W = 841.89
    A4_LANDSCAPE_H = 595.28

    # 2ページ並べたサイズ
    spread_width = page_width * 2
    spread_height = page_height

    # A4に収まるスケール率を計算
    scale = min(A4_LANDSCAPE_W / spread_width, A4_LANDSCAPE_H / spread_height, 1.0)

    # 出力ページサイズ（スケール後）
    out_width = spread_width * scale
    out_height = spread_height * scale
    scaled_page_width = page_width * scale

    pairs = get_imposition_order(total_pages)
    writer = PdfWriter()

    for pair in pairs:
        new_page = PageObject.create_blank_page(width=out_width, height=out_height)

        left_page = reader.pages[pair["left"] - 1]
        new_page.merge_transformed_page(
            left_page,
            Transformation().scale(scale, scale).translate(0, 0),
        )

        right_page = reader.pages[pair["right"] - 1]
        new_page.merge_transformed_page(
            right_page,
            Transformation().scale(scale, scale).translate(scaled_page_width, 0),
        )

        writer.add_page(new_page)

    if output_path is None:
        input_p = Path(input_path)
        output_path = str(input_p.parent / f"{input_p.stem}_saddle.pdf")

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path, len(pairs), total_pages // 4


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/select-file", methods=["POST"])
def select_file():
    """macOSネイティブダイアログでPDFファイルを選択し、ページ情報を返す"""
    global _selected_file_path

    # osascript でファイル選択ダイアログを表示
    script = '''
        set chosenFile to choose file with prompt "面付けするPDFファイルを選択" of type {"com.adobe.pdf"}
        return POSIX path of chosenFile
    '''
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            return jsonify({"error": "ファイル選択がキャンセルされました"}), 400

        file_path = result.stdout.strip()
        if not file_path or not Path(file_path).exists():
            return jsonify({"error": "ファイルが見つかりません"}), 400

        _selected_file_path = file_path
    except subprocess.TimeoutExpired:
        return jsonify({"error": "ファイル選択がタイムアウトしました"}), 400
    except Exception as e:
        return jsonify({"error": f"ファイル選択に失敗しました: {str(e)}"}), 500

    return _analyze_file()


def _analyze_file():
    """選択されたファイルのページ情報を解析して返す"""
    try:
        reader = PdfReader(_selected_file_path)
        total_pages = len(reader.pages)

        first_page = reader.pages[0]
        width_pt = float(first_page.mediabox.width)
        height_pt = float(first_page.mediabox.height)

        is_valid = total_pages % 4 == 0
        imposition_order = get_imposition_order(total_pages) if is_valid else []

        # A4に収まるかチェック
        A4_LANDSCAPE_W = 841.89
        A4_LANDSCAPE_H = 595.28
        scale = min(A4_LANDSCAPE_W / (width_pt * 2), A4_LANDSCAPE_H / height_pt, 1.0)

        return jsonify(
            {
                "filename": Path(_selected_file_path).name,
                "filepath": _selected_file_path,
                "total_pages": total_pages,
                "page_width_pt": round(width_pt, 1),
                "page_height_pt": round(height_pt, 1),
                "page_width_mm": round(width_pt / 72 * 25.4, 1),
                "page_height_mm": round(height_pt / 72 * 25.4, 1),
                "is_valid": is_valid,
                "imposition_order": imposition_order,
                "sheets": total_pages // 4 if is_valid else 0,
                "scale": round(scale * 100, 1),
                "needs_scaling": scale < 1.0,
            }
        )
    except Exception as e:
        return jsonify({"error": f"PDFの読み込みに失敗しました: {str(e)}"}), 400


@app.route("/api/impose", methods=["POST"])
def run_impose():
    """面付け処理を実行する"""
    global _selected_file_path

    if _selected_file_path is None:
        return jsonify({"error": "ファイルが選択されていません"}), 400

    try:
        output_path, total_imposed_pages, sheets = impose(_selected_file_path)
        return jsonify(
            {
                "success": True,
                "output_path": output_path,
                "total_imposed_pages": total_imposed_pages,
                "sheets": sheets,
            }
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"面付け処理に失敗しました: {str(e)}"}), 500


@app.route("/api/reveal", methods=["POST"])
def reveal_in_finder():
    """出力ファイルをFinderで表示する"""
    data = request.get_json()
    path = data.get("path", "")

    if not path or not Path(path).exists():
        return jsonify({"error": "ファイルが見つかりません"}), 404

    subprocess.run(["open", "-R", path])
    return jsonify({"success": True})


if __name__ == "__main__":
    print("=" * 50)
    print("  中綴じ面付け GUIアプリ")
    print("  http://localhost:8080 をブラウザで開いてください")
    print("=" * 50)
    app.run(debug=True, port=8080)
