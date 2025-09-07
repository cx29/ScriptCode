import os
import random
import time
import numpy as np
import tempfile
import pytest

from main import collect_csv_files, classify_and_read, read_last_value


def create_file(path: str, rows: int = 10, cols: int = 5, col_index: int = 2, fixed_value: int = 2):
    """
        创建 CSV 文件:
        - 最后一行的 col_index 列值固定为 fixed_value
        """
    with open(path, "w", encoding="utf-8") as f:
        # 生成前 rows-1 行随机数
        for _ in range(rows - 1):
            f.write(",".join(str(random.randint(0, 100)) for _ in range(cols)) + "\n")
        # 最后一行，固定 col_index 列值
        last_row = [str(random.randint(0, 100)) for _ in range(cols)]
        last_row[col_index] = str(fixed_value)
        f.write(",".join(last_row) + "\n")


@pytest.mark.slow
def test_collect_csv_files_stress():
    keywords = {"keyA", "keyB", "keyC"}
    col_index = 2  # 指定读取第3列

    with tempfile.TemporaryDirectory() as tmpdir:
        folder = os.path.join(tmpdir, "bigfolder")
        os.makedirs(folder)

        files = []
        # 创建 10,000 个 CSV 文件
        for i in range(10000):
            keyword = random.choice(list(keywords))
            prefix = f"prefix{random.choice(['X', 'Y', 'Z'])}"
            file_name = f"{prefix}_{keyword}_{i}.csv"
            path = os.path.join(folder, file_name)
            create_file(path)
            files.append(path)

        # 1️⃣ 收集文件
        folder_files = collect_csv_files(tmpdir, max_workers=8)
        assert "bigfolder" in folder_files
        assert len(folder_files["bigfolder"]) == 10000

        # 2️⃣ 多线程分类并读取最后一行
        result = classify_and_read(folder_files, keywords, col_index=col_index, max_workers=16)

        # 3️⃣ 验证结果结构
        # 每个 key 应该是 (folder, prefix, keyword)
        for k in result.keys():
            folder_name, prefix, keyword = k
            assert folder_name == "bigfolder"
            assert prefix.startswith("prefix")
            assert keyword in keywords or keyword == "others"

        # 4️⃣ 验证每个数组长度 >= 1
        for values in result.values():
            assert isinstance(values, np.ndarray)
            assert values.size >= 1

        # 5️⃣ 可选：检查某些值（最后一行第 col_index 列值）
        sample_key = list(result.keys())[0]
        sample_values = result[sample_key]
        # 因为最后一行生成是固定的数值 [0,1,2,3,4]，col_index=2 → 2
        assert 2 in sample_values
