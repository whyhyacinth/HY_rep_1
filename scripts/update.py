#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rango 照片墙更新脚本
用法：python3 update.py
功能：扫描源照片文件夹，自动复制照片到项目并生成网页数据
特性：自动将HEIC格式转换为浏览器支持的JPG格式
"""

import os
import shutil
import json
import subprocess
from datetime import datetime

SOURCE_FOLDER = "/Users/bytedance/Documents/Rango_photo"
PROJECT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTOS_FOLDER = os.path.join(PROJECT_FOLDER, "photos")
DATA_FOLDER = os.path.join(PROJECT_FOLDER, "data")
PHOTOS_JSON = os.path.join(DATA_FOLDER, "photos.json")

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.heic', '.HEIC', '.JPG', '.JPEG', '.PNG'}
HEIC_EXTENSIONS = {'.heic', '.HEIC'}


def get_image_files(folder):
    if not os.path.exists(folder):
        print(f"❌ 源文件夹不存在：{folder}")
        return []
    
    files = []
    for filename in os.listdir(folder):
        ext = os.path.splitext(filename)[1]
        if ext in IMAGE_EXTENSIONS:
            filepath = os.path.join(folder, filename)
            mtime = os.path.getmtime(filepath)
            files.append({
                'name': filename,
                'path': filepath,
                'mtime': mtime,
                'date': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
            })
    
    files.sort(key=lambda x: x['mtime'], reverse=True)
    return files


def convert_heic_to_jpg(src_path, dest_path):
    try:
        subprocess.run(
            ['sips', '-s', 'format', 'jpeg', src_path, '--out', dest_path],
            check=True,
            capture_output=True
        )
        return True
    except Exception as e:
        print(f"  ⚠️  转换失败: {os.path.basename(src_path)} - {e}")
        return False


def copy_photos(image_files):
    os.makedirs(PHOTOS_FOLDER, exist_ok=True)
    
    copied = []
    for img in image_files:
        filename = img['name']
        ext = os.path.splitext(filename)[1]
        
        if ext in HEIC_EXTENSIONS:
            dest_name = os.path.splitext(filename)[0] + '.jpg'
            dest_path = os.path.join(PHOTOS_FOLDER, dest_name)
            
            if os.path.exists(dest_path):
                src_mtime = img['mtime']
                dest_mtime = os.path.getmtime(dest_path)
                if src_mtime <= dest_mtime:
                    copied.append({'name': dest_name, 'date': img['date']})
                    print(f"  ✅ 跳过（已存在）: {filename}")
                    continue
            
            print(f"  📸 转换: {filename} -> {dest_name}")
            if convert_heic_to_jpg(img['path'], dest_path):
                copied.append({'name': dest_name, 'date': img['date']})
            continue
        
        dest_path = os.path.join(PHOTOS_FOLDER, filename)
        
        if os.path.exists(dest_path):
            src_size = os.path.getsize(img['path'])
            dest_size = os.path.getsize(dest_path)
            if src_size == dest_size:
                copied.append({'name': filename, 'date': img['date']})
                print(f"  ✅ 跳过（已存在）: {filename}")
                continue
        
        try:
            shutil.copy2(img['path'], dest_path)
            copied.append({'name': filename, 'date': img['date']})
            print(f"  ✅ 复制: {filename}")
        except Exception as e:
            print(f"  ❌ 失败: {filename} - {e}")
    
    return copied


def cleanup_old_heic():
    for filename in os.listdir(PHOTOS_FOLDER):
        ext = os.path.splitext(filename)[1]
        if ext in HEIC_EXTENSIONS:
            filepath = os.path.join(PHOTOS_FOLDER, filename)
            try:
                os.remove(filepath)
                print(f"  🗑️ 删除旧HEIC: {filename}")
            except:
                pass


def generate_photos_json(copied_photos):
    os.makedirs(DATA_FOLDER, exist_ok=True)
    
    photos_data = []
    for img in copied_photos:
        photos_data.append({
            'src': f"photos/{img['name']}",
            'name': img['name'],
            'date': img['date']
        })
    
    with open(PHOTOS_JSON, 'w', encoding='utf-8') as f:
        json.dump(photos_data, f, ensure_ascii=False, indent=2)
    
    return len(photos_data)


def main():
    print("=" * 50)
    print("🐕 Rango 照片墙更新脚本")
    print("=" * 50)
    
    print(f"\n📂 源文件夹: {SOURCE_FOLDER}")
    print(f"📂 项目文件夹: {PROJECT_FOLDER}")
    
    print("\n🔍 扫描照片中...")
    image_files = get_image_files(SOURCE_FOLDER)
    
    if not image_files:
        print("\n⚠️  没有找到照片，请检查源文件夹路径是否正确")
        print(f"   当前路径: {SOURCE_FOLDER}")
        print("\n💡 提示：你可以修改脚本开头的 SOURCE_FOLDER 变量")
        return
    
    print(f"   找到 {len(image_files)} 张照片")
    
    print("\n📋 复制/转换照片到项目文件夹...")
    copied = copy_photos(image_files)
    
    print("\n🧹 清理旧HEIC文件...")
    cleanup_old_heic()
    
    print(f"\n📝 生成数据文件...")
    count = generate_photos_json(copied)
    
    print(f"\n✅ 完成！共处理 {count} 张照片")
    print(f"   数据文件: {PHOTOS_JSON}")
    print(f"\n🌐 现在打开 index.html 就能看到照片墙啦！")
    print("=" * 50)


if __name__ == "__main__":
    main()
