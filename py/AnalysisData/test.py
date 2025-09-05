import os
import pandas as pd
import numpy as np
import time
import random
import string


def random_folder_names(n=3, seed=None):
    if seed is not None:
        random.seed(seed)
    folders = []
    for _ in range(n):
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        folders.append(f"{month:02d}{day:02d}")
    return folders


def random_file_name():
    test_num = random.randint(1, 3)
    suffix = ''.join(random.choices(string.digits, k=3))
    return f"test{test_num}_{suffix}.csv", f"test{test_num}"


def generate_csv(path, filename, file_type, folder_offset=0, rows=10, seed=None):
    if seed is not None:
        np.random.seed(seed)
    os.makedirs(path, exist_ok=True)
    # 按类型区分数值范围
    if file_type == "test1":
        temp_range = (20, 30)
        hum_range = (40, 60)
        pres_range = (1000, 1010)
    elif file_type == "test2":
        temp_range = (30, 40)
        hum_range = (50, 70)
        pres_range = (1010, 1020)
    else:  # test3
        temp_range = (40, 50)
        hum_range = (60, 80)
        pres_range = (1020, 1030)

    # 文件夹偏移
    temperature = np.random.uniform(*temp_range, rows) + folder_offset
    humidity = np.random.uniform(*hum_range, rows) + folder_offset
    pressure = np.random.uniform(*pres_range, rows) + folder_offset

    df = pd.DataFrame({
        "temperature": temperature,
        "humidity": humidity,
        "pressure": pressure
    })
    file_path = os.path.join(path, filename)
    df.to_csv(file_path, index=False)
    return file_path


def generate_test_data(base_path="test_data", folder_count=3, files_per_folder=5, interval=60, seed=None):
    """
    生成验证数据：
    - folder_count: 文件夹数量
    - files_per_folder: 每个文件夹生成 CSV 文件数量
    - interval: 文件修改时间间隔
    - seed: 随机种子，保证可复现
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    folders = random_folder_names(folder_count, seed=seed)
    now = time.time()
    i = 0

    for idx, folder in enumerate(folders):
        folder_path = os.path.join(base_path, folder)
        os.makedirs(folder_path, exist_ok=True)
        folder_offset = idx * 5  # 不同文件夹数据偏移，增加区分度
        for _ in range(files_per_folder):
            filename, file_type = random_file_name()
            generate_csv(folder_path, filename, file_type, folder_offset, seed=seed)
            mod_time = now + i * interval
            file_path = os.path.join(folder_path, filename)
            os.utime(file_path, (mod_time, mod_time))
            i += 1

    print(f"✅ 验证数据已生成到 {base_path}/，共 {folder_count} 个文件夹，每个 {files_per_folder} 个文件，种子={seed}")


if __name__ == "__main__":
    # 调用示例
    generate_test_data(
        base_path="test_data",
        folder_count=59,
        files_per_folder=100,
        interval=60,
        seed=42
    )