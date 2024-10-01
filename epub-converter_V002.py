import os
import zipfile
import shutil
from opencc import OpenCC
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re

VERSION = "V002"

def clean_html_content(content):
    # 移除HTML标签，保留文本内容
    content = re.sub(r'<style.*?</style>', '', content, flags=re.DOTALL)
    content = re.sub(r'<script.*?</script>', '', content, flags=re.DOTALL)
    
    # 处理标题
    content = re.sub(r'<title>(.*?)</title>', r'# \1\n', content)
    content = re.sub(r'<h[1-6].*?>(.*?)</h[1-6]>', r'# \1\n', content)
    
    # 处理段落
    content = re.sub(r'<p.*?>(.*?)</p>', r'　　\1\n', content)
    
    # 移除剩余的HTML标签
    content = re.sub(r'<.*?>', '', content)
    
    # 移除多余的空行
    content = re.sub(r'\n\s*\n', '\n\n', content)
    
    return content.strip()

def convert_simplified_to_traditional_epub(input_epub, output_epub, dict_file=None, output_txt=False):
    cc = OpenCC('s2t')
    temp_dir = 'temp_epub_dir'
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    with zipfile.ZipFile(input_epub, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    # 文件类型过滤
    files_to_convert = ['.html', '.xhtml', '.ncx', '.opf']
    
    all_text_content = ""
    
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if any(file.endswith(ext) for ext in files_to_convert):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                converted_content = cc.convert(content)
                
                # 应用字典替换
                if dict_file:
                    with open(dict_file, 'r', encoding='utf-8') as df:
                        for line in df:
                            original, replacement = line.strip().split(',')
                            converted_content = converted_content.replace(original, replacement)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(converted_content)
                
                if output_txt:
                    cleaned_content = clean_html_content(converted_content)
                    all_text_content += cleaned_content + "\n\n"
    
    with zipfile.ZipFile(output_epub, 'w') as zip_ref:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zip_ref.write(file_path, arcname)
    
    shutil.rmtree(temp_dir)
    
    if output_txt:
        txt_output = os.path.splitext(output_epub)[0] + '.txt'
        with open(txt_output, 'w', encoding='utf-8') as f:
            f.write(all_text_content)
    
    messagebox.showinfo("完成", f"轉換完成：{input_epub} 已保存為 {output_epub}")

def select_input_file():
    input_file = filedialog.askopenfilename(filetypes=[("EPUB files", "*.epub")])
    if input_file:
        input_file_var.set(input_file)
        default_output_file = os.path.splitext(input_file)[0] + '_繁體.epub'
        output_file_var.set(cc.convert(default_output_file))
        default_dict_file = os.path.join(os.path.dirname(input_file), "dictionary.txt")
        dict_file_var.set(default_dict_file)

def select_output_file():
    output_file = filedialog.asksaveasfilename(defaultextension=".epub", filetypes=[("EPUB files", "*.epub")])
    if output_file:
        output_file_var.set(cc.convert(output_file))

def select_dict_file():
    dict_file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if dict_file:
        dict_file_var.set(dict_file)

def start_conversion():
    input_file = input_file_var.get()
    output_file = output_file_var.get()
    dict_file = dict_file_var.get() if dict_file_var.get() else None
    output_txt = output_txt_var.get()
    
    if not input_file:
        messagebox.showerror("錯誤", "請輸入一個有效的EPUB文件")
        return
    
    if not output_file:
        output_file = cc.convert(os.path.splitext(input_file)[0] + '_繁體.epub')
    
    convert_simplified_to_traditional_epub(input_file, output_file, dict_file, output_txt)

# GUI界面
root = tk.Tk()
root.title(f"EPUB 簡繁轉換工具 {VERSION}")

cc = OpenCC('s2t')

input_file_var = tk.StringVar()
output_file_var = tk.StringVar()
dict_file_var = tk.StringVar()
output_txt_var = tk.BooleanVar()

tk.Label(root, text="輸入文件:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
tk.Entry(root, textvariable=input_file_var, width=50).grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="選擇文件", command=select_input_file).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="輸出文件:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
tk.Entry(root, textvariable=output_file_var, width=50).grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="選擇保存位置", command=select_output_file).grid(row=1, column=2, padx=5, pady=5)

tk.Label(root, text="字典文件:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
tk.Entry(root, textvariable=dict_file_var, width=50).grid(row=2, column=1, padx=5, pady=5)
tk.Button(root, text="選擇字典", command=select_dict_file).grid(row=2, column=2, padx=5, pady=5)

tk.Checkbutton(root, text="輸出純文字文件", variable=output_txt_var).grid(row=3, column=0, columnspan=3, padx=5, pady=5)

tk.Button(root, text="開始轉換", command=start_conversion).grid(row=4, column=0, columnspan=3, padx=5, pady=10)

root.mainloop()
