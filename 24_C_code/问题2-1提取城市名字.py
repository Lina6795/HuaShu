import os
import json
import argparse
from pypinyin import lazy_pinyin

def extract_city_names(folder_path):
    """从指定文件夹的所有csv文件中提取城市名（文件名），中文为键，拼音为值"""
    city_names = {}

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            # 去除扩展名获取城市名
            city_name = os.path.splitext(filename)[0]
            # 将城市名转为拼音（例如：北京 -> beijing）
            pinyin = ''.join(lazy_pinyin(city_name))
            # 中文作为键，拼音作为值
            city_names[city_name] = pinyin

    return city_names


def save_to_json(data, output_file):
    """将数据保存为JSON文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='从CSV文件中提取城市名并生成JSON')
    parser.add_argument('folder_path', nargs='?', default='/Users/lina/2025/4数模准备/1华数杯/2024年第五届华数杯C/附件', help='包含CSV文件的文件夹路径(默认: 当前目录)')
    parser.add_argument('output_file', nargs='?', default='city_my.json', help='输出JSON文件名(默认为city.json)')

    args = parser.parse_args()

    # 提取城市名
    city_data = extract_city_names(args.folder_path)

    # 保存为JSON文件
    save_to_json(city_data, args.output_file)
    print(f"成功提取 {len(city_data)} 个城市名并保存到 {args.output_file}")