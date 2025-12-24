import os
import shutil
import random, string

def randomname(n):
   randlst = [random.choice(string.ascii_letters) for i in range(n)]
   return ''.join(randlst)

def move_files_out_of_directory(source_dir: str, destination_dir: str):
    """
    指定されたディレクトリ内のファイルを、指定されたディレクトリの外に移動します。
    
    Args:
        source_dir (str): ファイルが格納されているディレクトリのパス。
        destination_dir (str): ファイルを移動先のディレクトリのパス。
    
    Returns:
        None
    
    Raises:
        FileNotFoundError: source_dirまたはdestination_dirが存在しない場合に発生します。
        OSError: ファイルの移動中にエラーが発生した場合に発生します。
    """
    if not os.path.exists(source_dir):
        raise FileNotFoundError(f"Source directory not found: {source_dir}")
    if not os.path.exists(destination_dir):
        raise FileNotFoundError(f"Destination directory not found: {destination_dir}")

    random_prefix = randomname(6) # ディレクトリごとにランダムワード生成
    for filename in os.listdir(source_dir):
        source_path = os.path.join(source_dir, filename)
        if os.path.isfile(source_path):
            destination_path = os.path.join(destination_dir, str(random_prefix+filename))
            print(destination_path)
            try:
                shutil.move(source_path, destination_path)
                print(f"Moved: {filename} to {destination_dir}") # ログ出力
            except OSError as e:
                print(f"Error moving {filename}: {e}")
                raise # エラーを再送出


def get_directory_paths_in_current_directory() -> list[str]:
    """
    カレントディレクトリに存在するディレクトリのパスをリストで返します。

    Returns:
        list[str]: カレントディレクトリ内のディレクトリのパスのリスト。
    """
    directory_paths = []
    for item in os.listdir():
        item_path = os.path.join(os.getcwd(), item)
        if os.path.isdir(item_path):
            directory_paths.append(item_path)
    return directory_paths

def get_parent_directory(directory_path: str) -> str:
    """
    指定されたディレクトリの親ディレクトリのパスを返します。

    Args:
        directory_path (str): 対象のディレクトリのパス。

    Returns:
        str: 親ディレクトリのパス。ディレクトリパスがルートディレクトリの場合はNoneを返します。
    """
    parent_directory = os.path.dirname(directory_path)
    if parent_directory == directory_path:  # ルートディレクトリの場合
        return None
    return parent_directory


dir_list = get_directory_paths_in_current_directory()
#print(dir_list)
for dirc in dir_list:
    #print(dirc)
    #print(get_parent_directory(dirc))
    move_files_out_of_directory(dirc, get_parent_directory(dirc))
#move_files_out_of_directory("L:\動画\BUENA\BUENA-120", "L:\動画\BUENA")

