import os
from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd


def collect_csv_files(base_path: str) -> dict:
    result = {}
    for root, dirs, files in os.walk(base_path):
        folder_name = os.path.basename(root)
        csv_files = [
            f
            for f in files
            if f.lower().endswith('.csv')
        ]
        if not csv_files:
            continue

        csv_files.sort(key=lambda f: os.path.getmtime(os.path.join(root, f)))
        type_dic = defaultdict(list)
        for f in csv_files:
            file_type = f.split('_', 1)[0]
            type_dic[file_type].append(os.path.join(root, f))
        result[folder_name] = dict(type_dic)

    return result


def extract_last_value(data_map: dict, column: int, group_by: str = "folder"):
    result = defaultdict(list)
    for folder, type_map in data_map.items():
        for file_type, files in type_map.items():
            for f in files:
                try:
                    df = pd.read_csv(f)
                    if column >= df.shape[1]:
                        print("cannot find column {}".format(column))
                        continue
                    value = df.iloc[-1, column]  # 取最后一行的值
                    key = folder if group_by == "folder" else file_type
                    result[key].append(value)
                except Exception as e:
                    print(f"read file {f} error: {e}")
    return result


def plot_results(values_maps: dict, column: str, save_dir: str):
    os.makedirs(save_dir, exist_ok=True)
    plt.figure(figsize=(8, 5))
    for i, (key, values) in enumerate(values_maps.items()):
        plt.scatter([key] * len(values), values, label=key)
    plt.title(f"Scatter plot of {column}")
    plt.xlabel("Group")
    plt.ylabel(column)
    plt.legend()
    scatter_file = os.path.join(save_dir, f"scatter_{column}.png")
    plt.savefig(scatter_file, dpi=300, bbox_inches='tight')
    print(f"saved scatter plot {scatter_file}")

    plt.figure(figsize=(8, 5))
    plt.boxplot(values_maps.values(), labels=values_maps.keys())
    plt.title(f"Boxplot of {column}")
    plt.xlabel("Group")
    plt.ylabel(column)
    box_file = os.path.join(save_dir, f"box_{column}.png")
    plt.savefig(box_file, dpi=300, bbox_inches='tight')
    print(f"saved box plot {box_file}")


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    base_path = input('Enter base path: ').strip()
    if os.path.isdir(base_path):
        csv_dic = collect_csv_files(base_path)
        col = input('Enter column name: ').strip()
        group_by = input('Enter group by[folder/type] : ').strip().lower()
        if group_by not in ('folder', 'type'):
            print('Invalid group, use folder')
            group_by = 'folder'
        values_map = extract_last_value(csv_dic, int(col), group_by)
        if values_map:
            plot_results(values_map, col, base_path)
        else:
            print('No results found')
    else:
        print('Invalid path')
