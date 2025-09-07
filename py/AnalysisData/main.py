import os
import csv
from collections import defaultdict
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Any, Set


def collect_csv_files(base_path: str, max_workers: int = 8) -> Dict[str, List[str]]:
    result: Dict[str, List[str]] = {}
    with os.scandir(base_path) as folder_it:
        folder_entries = [entry for entry in folder_it if entry.is_dir()]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scan_folder, entry): entry.name for entry in folder_entries}
        for future in as_completed(futures):
            folder, files = future.result()
            if files:
                result[folder] = files

    return result


def scan_folder(folder_entry: os.DirEntry) -> Tuple[str, List[str]]:
    files_info = []
    with os.scandir(folder_entry.path) as file_it:
        for file_entry in file_it:
            if file_entry.is_file() and file_entry.name.lower().endswith(".csv"):
                try:
                    mtime = file_entry.stat().st_mtime
                except OSError:
                    continue
                files_info.append((file_entry.path, mtime))
    if files_info:
        files_info.sort(key=lambda x: x[1])
        return folder_entry.name, [file for file, _ in files_info]
    return folder_entry.name, []


def read_last_value(file_path: str, col_index: int, chunk_size: int = 409) -> Any:
    col_index -= 1
    with open(file_path, "rb") as file:
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        buffer = b""
        offset = 0

        while file_size > 0:
            offset = min(file_size, chunk_size)
            file_size -= offset
            file.seek(file_size)
            chunk = file.read(offset)
            buffer = chunk + buffer

            if buffer.count(b"\n") >= 2 or file_size == 0:
                break
        lines = buffer.splitlines()
        if not lines:
            return None
        last_line = lines[-1].decode("utf-8", errors="ignore").strip()
        if not last_line:
            if len(lines) > 1:
                last_line = lines[-2].decode("utf-8", errors="ignore").strip()
            else:
                return None
        reader = csv.reader([last_line])
        for row in reader:
            if col_index < len(row):
                return row[col_index]
    return None


def classify_and_read(
        folder_files: Dict[str, List[str]],
        keywords: Set[str],
        col_index: int,
        max_workers: int = 8
) -> Dict[Tuple[str, str, str], np.ndarray]:
    temp_results: List[Tuple[str, str, str], List[Any]] = []

    def process_file(folder: str, file_path: str):
        file_name = os.path.basename(file_path)
        prefix = file_name.split("_", 1)[0]
        low_name = file_name.lower()
        keyword = next((kw for kw in keywords if kw.lower() in low_name), "Others")

        value = read_last_value(file_path, col_index)
        if value is not None:
            return folder, prefix, keyword, value
        return None

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for folder, files in folder_files.items():
            for file in files:
                futures.append(executor.submit(process_file, folder, file))

        for fut in as_completed(futures):
            res = fut.result()
            if res:
                temp_results.append(res)

    temp_dict: Dict[Tuple[str, str, str], List[Any]] = defaultdict(list)
    for folder, prefix, keyword, value in temp_results:
        temp_dict[(folder, prefix, keyword)].append(value)
    result: Dict[Tuple[str, str, str], np.ndarray] = {}
    for k, v in temp_dict.items():
        try:
            result[k] = np.array([float(x) for x in v], dtype=float)
        except ValueError:
            result[k] = np.array(v)
    return result


def plot_results(values_maps: dict, save_dir: str, column: str):
    """
    values_maps: Dict[Tuple[folder, prefix, keyword], np.ndarray]
    save_dir: 保存目录
    column: 列名或索引
    """
    os.makedirs(save_dir, exist_ok=True)

    # 按 keyword 收集数据
    keyword_dict: Dict[str, List[float]] = defaultdict(list)
    for (_, _, keyword), values in values_maps.items():
        keyword_dict[keyword].extend(values.tolist())

    for keyword, values in keyword_dict.items():
        if not values:
            continue
        # 散点图
        plt.figure(figsize=(10, 6))
        x_vals = [keyword] * len(values)
        plt.scatter(x_vals, values, alpha=0.6)
        plt.title(f"Scatter plot for {keyword} - column {column}")
        plt.xlabel("Keyword")
        plt.ylabel(column)
        scatter_file = os.path.join(save_dir, f"scatter_{keyword}.png")
        plt.savefig(scatter_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved scatter plot: {scatter_file}")

        # 箱线图
        plt.figure(figsize=(6, 5))
        plt.boxplot(values, labels=[keyword])
        plt.title(f"Boxplot for {keyword} - column {column}")
        plt.ylabel(column)
        box_file = os.path.join(save_dir, f"box_{keyword}.png")
        plt.savefig(box_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved box plot: {box_file}")


def export_values_to_csv(values_maps: Dict[Tuple[str, str, str], np.ndarray],
                         save_path: str):
    """
    将 values_maps 转换为 CSV 文件，横向为 prefix，纵向为 keyword
    """
    # 1️⃣ 收集所有 prefix 和 keyword
    prefixes = set()
    keywords = set()
    for (_, prefix, keyword) in values_maps.keys():
        prefixes.add(prefix)
        keywords.add(keyword)

    prefixes = sorted(prefixes)
    keywords = sorted(keywords)

    # 2️⃣ 构建二维表
    table: Dict[str, Dict[str, str]] = defaultdict(dict)
    for (folder, prefix, keyword), values in values_maps.items():
        # 将 np.ndarray 转为逗号分隔字符串
        table[keyword][prefix] = ",".join(map(str, values.tolist()))

    # 3️⃣ 写入 CSV
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # 写表头
        writer.writerow(["Keyword/Prefix"] + prefixes)
        for keyword in keywords:
            row = [keyword]
            for prefix in prefixes:
                row.append(table.get(keyword, {}).get(prefix, ""))
            writer.writerow(row)

    print(f"CSV file saved to: {save_path}")


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    base_path = input('Enter base path: ').strip()
    keywords = {
        "_Y_XpostSOA_2V_", "_X_XpostSOA_2V", "_Z_XpostSOA_2V",
        "_Y_YpostSOA_2V_", "_X_YpostSOA_2V", "_Z_YpostSOA_2V",
        "_Y_Xpost_", "_X_Xpost", "_Z_Xpost",
        "_Y_Ypost_", "_X_Ypost", "_Z_Ypost",
        "_YClimb_Xpost", "_YClimb_Input", "_YClimb_Ypost",
        "_Y_Input_SP", "_X_Input_SP", "_Z_Input_SP",
        "_Y_Input", "_X_Input", "_Z_Input",
    }
    if os.path.isdir(base_path):
        csv_dic = collect_csv_files(base_path)
        col = input('Enter column name: ').strip()
        values_maps = classify_and_read(csv_dic, keywords, int(col))
        save_dir = input('Enter directory to save summary: ').strip()
        if not save_dir:
            save_dir = os.path.join(base_path, "values.csv")
        # plot_results(values_maps, save_dir=save_dir, column=f"Column {col}")
        export_values_to_csv(values_maps, save_dir)
    else:
        print('Invalid path')
