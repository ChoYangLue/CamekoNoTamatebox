import os
import shutil
from datetime import datetime

def copy_with_progress(src, dst):
    # 全ファイル数をカウント
    total_files = 0
    for root, dirs, files in os.walk(src):
        total_files += len(files)

    copied_files = 0

    # 再帰的にコピー
    for root, dirs, files in os.walk(src):
        rel_path = os.path.relpath(root, src)
        dest_path = os.path.join(dst, rel_path)
        os.makedirs(dest_path, exist_ok=True)

        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dest_path, file)

            shutil.copy2(src_file, dst_file)
            copied_files += 1

            # 進捗バー
            progress = copied_files / total_files
            bar_len = 40
            bar = '#' * int(progress * bar_len)
            bar = bar.ljust(bar_len)
            print(f"\rコピー中: [{bar}] {progress*100:.1f}% ({copied_files}/{total_files})", end="")

    print("\nコピー完了！")

def copy_latest_directory_with_date(dest_dir):
    # キャレットディレクトリ / DCIM を root にする
    root_dir = os.path.join(os.getcwd(), "DCIM")

    if not os.path.exists(root_dir):
        print(f"DCIM ディレクトリがカレントディレクトリ内に見つかりません: {root_dir}")
        return

    # DCIM 内のサブディレクトリ一覧取得
    dirs = [
        os.path.join(root_dir, d)
        for d in os.listdir(root_dir)
        if os.path.isdir(os.path.join(root_dir, d))
    ]

    if not dirs:
        print("DCIM 以下にサブディレクトリが存在しません。")
        return

    # 最も更新日時が新しいディレクトリ
    latest_dir = max(dirs, key=os.path.getmtime)

    # 更新日時 → YYYYMMDD
    mtime = os.path.getmtime(latest_dir)
    date_str = datetime.fromtimestamp(mtime).strftime("%Y%m%d")

    dest_path = os.path.join(dest_dir, date_str)

    print(f"コピー元フォルダ: {latest_dir}")
    print(f"更新日時: {date_str}")
    print(f"コピー先: {dest_path}")

    # 同名フォルダがある場合は削除
    if os.path.exists(dest_path):
        print("コピー先に同名フォルダがあるため削除します。")
        shutil.rmtree(dest_path)

    # 再帰コピー + 進捗表示
    copy_with_progress(latest_dir, dest_path)


# 使用例
copy_latest_directory_with_date("D:\Pictures\RAW")
