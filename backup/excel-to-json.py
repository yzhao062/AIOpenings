# -*- coding: utf-8 -*-
"""
Created on Sun Aug 31 22:14:12 2025

@author: lanse
"""

import pandas as pd
import json
import re
from pathlib import Path

# ====== 配置区 ======
# 输入 Excel 文件路径
excel_path = r"PhD_RA_Interns Opening  26 Spring_Fall (PIs can request editing access).xlsx"

# 输出目录（会自动创建）
output_dir = r"./universities_json"
# ===================

def slugify(name: str) -> str:
    """把学校名字转成文件名友好的 slug"""
    s = name.lower().strip()
    s = re.sub(r'&', ' and ', s)
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = re.sub(r'-{2,}', '-', s).strip('-')
    return s or "unknown"

def convert_excel_to_json(excel_path: str, output_dir: str):
    # 读取 Excel
    df = pd.read_excel(excel_path, sheet_name=0, dtype=str)
    df = df.dropna(how="all")  # 删除全空行
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = df.fillna("")  # NaN 转空字符串

    # 检测 "University" 列
    if "University" not in df.columns:
        raise ValueError("Excel 文件中没有找到 'University' 列，请确认表头是否正确。")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    files = []
    for univ, g in df.groupby("University"):
        if not isinstance(univ, str) or not univ.strip():
            continue
        slug = slugify(univ)
        out_path = output_dir / f"{slug}.json"
        records = g.to_dict(orient="records")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        files.append((univ, out_path))

    # 生成 index.json
    index_path = output_dir / "0_index.json"
    index = [{"University": univ, "file": str(output_dir / f"{slugify(univ)}.json")}
             for univ, _ in df.groupby("University")]
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"✅ 已生成 {len(files)} 个 JSON 文件，保存到 {output_dir}")
    print(f"📑 索引文件: {index_path}")

    return files, index_path

# 在 Spyder 里运行时，只需点“Run”即可
if __name__ == "__main__":
    convert_excel_to_json(excel_path, output_dir)
