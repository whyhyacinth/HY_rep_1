#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rango 小红书笔记更新脚本
用法：python3 update_xiaohongshu.py
功能：扫描 xiaohongshu 文件夹，自动生成笔记列表数据
说明：图片文件名会作为笔记标题（可以在生成的 notes.json 中手动修改）
"""

import os
import json

PROJECT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XHS_FOLDER = os.path.join(PROJECT_FOLDER, "xiaohongshu")
DATA_FOLDER = os.path.join(PROJECT_FOLDER, "data")
NOTES_JSON = os.path.join(DATA_FOLDER, "notes.json")

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.JPG', '.JPEG', '.PNG'}


def get_note_images():
    if not os.path.exists(XHS_FOLDER):
        os.makedirs(XHS_FOLDER, exist_ok=True)
        return []
    
    files = []
    for filename in os.listdir(XHS_FOLDER):
        ext = os.path.splitext(filename)[1]
        if ext in IMAGE_EXTENSIONS:
            filepath = os.path.join(XHS_FOLDER, filename)
            mtime = os.path.getmtime(filepath)
            name_without_ext = os.path.splitext(filename)[0]
            files.append({
                'filename': filename,
                'title': name_without_ext,
                'mtime': mtime
            })
    
    files.sort(key=lambda x: x['mtime'], reverse=True)
    return files


def generate_notes_json(notes):
    os.makedirs(DATA_FOLDER, exist_ok=True)
    
    existing_notes = {}
    if os.path.exists(NOTES_JSON):
        try:
            with open(NOTES_JSON, 'r', encoding='utf-8') as f:
                existing = json.load(f)
                for note in existing:
                    existing_notes[note['src']] = note
        except:
            pass
    
    notes_data = []
    for note in notes:
        src = f"xiaohongshu/{note['filename']}"
        
        if src in existing_notes:
            notes_data.append(existing_notes[src])
        else:
            notes_data.append({
                'src': src,
                'title': note['title'],
                'likes': 0,
                'comments': 0
            })
    
    with open(NOTES_JSON, 'w', encoding='utf-8') as f:
        json.dump(notes_data, f, ensure_ascii=False, indent=2)
    
    return len(notes_data)


def main():
    print("=" * 50)
    print("📕 Rango 小红书笔记更新脚本")
    print("=" * 50)
    
    print(f"\n📂 笔记图片文件夹: {XHS_FOLDER}")
    
    print("\n🔍 扫描笔记图片中...")
    notes = get_note_images()
    
    if not notes:
        print("\n⚠️  xiaohongshu 文件夹里还没有图片")
        print(f"   文件夹路径: {XHS_FOLDER}")
        print("\n💡 使用方法：")
        print("   1. 把小红书笔记的封面图放到 xiaohongshu 文件夹")
        print("   2. 图片文件名会作为笔记标题")
        print("   3. 运行此脚本生成数据")
        print("   4. 在 data/notes.json 中可以手动修改标题和点赞数")
        return
    
    print(f"   找到 {len(notes)} 张笔记图片")
    
    print("\n📝 生成笔记数据...")
    count = generate_notes_json(notes)
    
    print(f"\n✅ 完成！共 {count} 篇笔记")
    print(f"   数据文件: {NOTES_JSON}")
    print(f"\n💡 提示：")
    print("   - 可以在 data/notes.json 中修改每篇笔记的标题、点赞数、评论数")
    print("   - 添加新图片后重新运行此脚本即可更新")
    print("=" * 50)


if __name__ == "__main__":
    main()
