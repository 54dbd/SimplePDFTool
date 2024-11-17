import os
import io
import tkinter as tk

from math import sqrt
from pikepdf import Pdf
from PIL import Image
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES 
from PyPDF2 import PdfReader, PdfWriter


# 核心逻辑类
class PDFProcessor:
    def __init__(self):
        self.pdf_path = None
        self.unlocked_pdf_stream = None  # 用于存储解锁后的 PDF 数据流
        self.fileName = None
        self.file_directory = None

    def open_pdf(self, file_path):
        """打开 PDF 文件"""
        self.pdf_path = file_path
        self.fileName = file_path.split("/")[-1].split(".")[0]
        self.file_directory = "/".join(file_path.split("/")[:-1])
        return self.pdf_path is not None

    def unlock_pdf(self, password=None):
        """
        解锁 PDF 并存储到内存中
        """
        try:
            with Pdf.open(self.pdf_path) as pdf:
                # 创建一个 BytesIO 对象，将解锁后的 PDF 写入其中
                self.unlocked_pdf_stream = io.BytesIO()
                pdf.save(self.unlocked_pdf_stream)
                self.unlocked_pdf_stream.seek(0)  # 将流指针重置到开头
                print("PDF 解锁成功，并存储在内存中！")
        except Exception as e:
            print(f"解锁 PDF 时出错: {e}")
    
    def remove_signature(self, save_dir):
        """
        移除 PDF 中的签名 并尝试保存签名中的图像
        """
        def extract_images_from_form_xobject(form_xobject):
            """
            递归解析 Form XObject，提取其中的图像
            :param form_xobject: 一个 Form 类型的 XObject
            :return: 提取的图像对象列表
            """
            images = []
            if "/Resources" in form_xobject and "/XObject" in form_xobject["/Resources"]:
                xobjects = form_xobject["/Resources"]["/XObject"].get_object()
                for name, obj in xobjects.items():
                    obj = obj.get_object()
                    if obj.get("/Subtype") == "/Image":
                        # 直接提取图像数据
                        images.append(obj)
                    elif obj.get("/Subtype") == "/Form":
                        # 递归解析嵌套的 Form XObject
                        images.extend(extract_images_from_form_xobject(obj))
            return images

        def save_image(image_obj, count, save_dir):
            """保存提取的图像"""
            width = image_obj.get("/Width")
            height = image_obj.get("/Height")
            data = image_obj.get_data()            
            ideal_width = int(sqrt(len(data))) - 1
            filter_type = image_obj.get("/Filter")
            image_path = f"{save_dir}/[Images] {self.fileName}/signature_{count}.png"
            os.makedirs(f"{save_dir}/[Images] {self.fileName}", exist_ok=True)

            if filter_type == "/DCTDecode":
                # 保存为 JPEG
                image_path = image_path.replace(".png", ".jpg")
                with open(image_path, "wb") as f:
                    f.write(data)
            elif filter_type == "/FlateDecode":
                # 解码并保存为 PNG
                try:
                    img = Image.frombytes("RGB", (width, height), data, "raw" )
                    img.save(image_path, "PNG")
                    print(f"保存成功：width:{width}, height:{height}, \ntotalPixels:{width*height}, \npictureSize:{len(data)}")
                except Exception as e:
                    print(f"无法保存 PNG 图像signature_{count}: {e}")
            else:
                print(f"不支持的图像过滤器: {filter_type}")
            return image_path

        if not self.unlocked_pdf_stream:
            raise ValueError("PDF 尚未解锁，请先调用 unlock_pdf() 方法")

        # 使用 PyPDF2 从内存流中加载 PDF
        reader = PdfReader(self.unlocked_pdf_stream)
        writer = PdfWriter()
        stamp_count = 0
        # 遍历每个页面并检查是否存在签名字段
        for page_index, page in enumerate(reader.pages):
            if "/Annots" in page:
                annotations = page["/Annots"]
                if annotations:
                    # 确保页面有 /Resources 和 /XObject
                    if "/Resources" not in page:
                        page["/Resources"] = {}
                    if "/XObject" not in page["/Resources"]:
                        page["/Resources"]["/XObject"] = {}
                    xobjects = page["/Resources"]["/XObject"].get_object()

                    for annot_ref in annotations:
                        annot = annot_ref.get_object()

                        # 提取注释的外观流中的图像
                    if "/AP" in annot and "/N" in annot["/AP"]:
                        appearance = annot["/AP"]["/N"].get_object()
                        if appearance.get("/Subtype") == "/Form":
                            # 提取 Form XObject 中的图像
                            images = extract_images_from_form_xobject(appearance)
                            for img in images:
                                save_image(img, stamp_count, save_dir)
                                stamp_count += 1

                    # 删除所有注释
                    del page["/Annots"]

            writer.add_page(page)



        # 将处理后的 PDF 数据写入新的 BytesIO 对象
        new_pdf_stream = io.BytesIO()
        writer.write(new_pdf_stream)
        new_pdf_stream.seek(0)
        # 存回
        self.unlocked_pdf_stream = new_pdf_stream

    def extract_stamp(self, save_dir):
        """
        使用 PyPDF2 处理解锁后的 PDF 数据
        """
        if not self.unlocked_pdf_stream:
            raise ValueError("PDF 尚未解锁，请先调用 unlock_pdf() 方法")

        # 使用 PyPDF2 从内存流中加载 PDF
        reader = PdfReader(self.unlocked_pdf_stream)
        extracted = False
        stamp_count = 0

        for i, page in enumerate(reader.pages):
            if "/XObject" in page["/Resources"]:
                x_objects = page["/Resources"]["/XObject"].get_object()
                for obj_name, obj in x_objects.items():
                    obj = obj.get_object()
                    if obj["/Subtype"] == "/Image":
                        # 提取基本图像元数据
                        width = obj.get("/Width", 0)
                        height = obj.get("/Height", 0)
                        color_space = obj.get("/ColorSpace")
                        bits_per_component = obj.get("/BitsPerComponent", 8)

                        # 获取图像数据和过滤器
                        data = obj.get_data()
                        filter_type = obj.get("/Filter")

                        if filter_type == "/DCTDecode":
                            # JPEG 数据
                            ext = "jpg"
                            image_path = f"{save_dir}/stamp_{stamp_count}.jpg"
                            stamp_count += 1
                            with open(image_path, "wb") as image_file:
                                image_file.write(data)
                            extracted = True
                            continue

                        elif filter_type == "/FlateDecode":
                            # 尝试解码 PNG 数据
                            ext = "png"
                            try:
                                img = Image.frombytes(
                                    "RGB", (width, height), data, "raw", "RGB", 0, 1
                                )

                                # 将黑色背景替换为透明背景
                                img = img.convert("RGBA")  # 转换为 RGBA 模式
                                datas = img.getdata()
                                new_data = []
                                for item in datas:
                                    # 如果是黑色像素 (0, 0, 0)，替换为透明
                                    if item[:3] == (0, 0, 0):
                                        new_data.append((0, 0, 0, 0))
                                    else:
                                        new_data.append(item)
                                img.putdata(new_data)

                                # 保存处理后的图像
                                image_path = f"{save_dir}/[Images] {self.fileName}/stamp_{stamp_count}.png"
                                os.makedirs(f"{save_dir}/[Images] {self.fileName}", exist_ok=True)
                                stamp_count += 1
                                img.save(image_path, format="PNG")
                                extracted = True
                                continue
                            except Exception as e:
                                print(f"无法处理 PNG 图像 stamp_{stamp_count}.png: {e}")
                                stamp_count += 1
                                # 跳过当前图像，继续下一个

                        else:
                            raise RuntimeError(f"不支持的图像过滤器: {filter_type}")

        if not extracted:
            raise RuntimeError("未发现可提取的印章")
        return save_dir
    
    def save_unlocked_pdf(self, save_path):
        """
        保存解锁后的 PDF
        """
        if not self.unlocked_pdf_stream:
            raise ValueError("PDF 尚未解锁，请先调用 unlock_pdf() 方法")

        try:
            self.unlocked_pdf_stream.seek(0)
            with open(save_path, "wb") as dst:
                dst.write(self.unlocked_pdf_stream.read())
            print(f"解锁的 PDF 已保存到: {save_path}")
        except Exception as e:
            print(f"保存解锁后的 PDF 时出错: {e}")
            
# GUI 类
class PDFToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF 工具")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.processors: list[PDFProcessor] = []
        self.create_widgets()

        # 启用拖放支持
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self.handle_file_drop)


    def create_widgets(self):
        """创建 GUI 组件"""
        # 打开文件按钮
        self.open_button = tk.Button(self.root, text="导入 PDF", command=self.open_pdf)
        self.open_button.pack(pady=10)

        # 解锁按钮
        self.unlock_button = tk.Button(text="解锁 PDF 并提取所有图片", command=self.unlock_all_pdf, state=tk.DISABLED)
        self.unlock_button.pack(pady=10)  # 使用 padx 增加按钮之间的间距
        
        # 清空按钮
        self.clear_button = tk.Button(text="清空", command=self.clear_pdf_list ,state=tk.DISABLED)
        self.clear_button.pack(pady=10)
        
        # 显示所有已导入的 pdf
        self.pdf_list = tk.Text(self.root, height=5, width=50)
        self.pdf_list.pack(pady=10)
        
        
        
    def clear_pdf_list(self):
        self.processors = []
        self.refresh_pdf_list()
        self.unlock_button.config(state=tk.DISABLED)
    
    def refresh_pdf_list(self):
        self.pdf_list.delete(1.0, tk.END)
        if not self.processors:
            self.clear_button.config(state=tk.DISABLED)
        else:
            self.clear_button.config(state=tk.NORMAL)
        for index, processor in enumerate(self.processors):
            self.pdf_list.insert(tk.END, f"File{index+1}. {processor.fileName}\n")
                    
    def handle_file_drop(self, event):
        """处理文件拖放"""  
        def split_filenames(input_string):
            """
            将输入的文件名字符串分割为文件名列表。
            - 文件名用空格分隔。
            - 如果文件名包含空格，则用大括号 {} 包裹。

            :param input_string: 包含文件名的字符串
            :return: 分割后的文件名列表
            """
            filenames = []
            current_file = []
            in_braces = False

            for char in input_string:
                if char == '{':  # 开始文件名中的大括号
                    in_braces = True
                    current_file = []
                elif char == '}':  # 结束文件名中的大括号
                    in_braces = False
                    filenames.append("".join(current_file))
                    current_file = []
                elif char == ' ' and not in_braces:  # 文件名分隔符（仅在不在大括号内时生效）
                    if current_file:
                        filenames.append("".join(current_file))
                        current_file = []
                else:  # 其他字符，加入当前文件名
                    current_file.append(char)

            # 处理最后一个文件名
            if current_file:
                filenames.append("".join(current_file))

            return filenames
        
        file_paths = split_filenames(str(event.data))
        for file_path in file_paths:
            file_path = file_path.replace("{", "").replace("}", "")
            if os.path.isfile(file_path) and file_path.lower().endswith(".pdf"):
                newProcesspr = PDFProcessor()
                if newProcesspr.open_pdf(file_path):
                        self.processors.append(newProcesspr)
                
            else:
                messagebox.showerror("错误", f"仅支持拖放 PDF 文件！\n错误文件:{file_path}")
        self.unlock_button.config(state=tk.NORMAL)
        self.refresh_pdf_list()
        
    def open_pdf(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        if file_paths:
            for file_path in file_paths:
                newProcesspr = PDFProcessor()
                if newProcesspr.open_pdf(file_path):
                    self.processors.append(newProcesspr)
                    # messagebox.showinfo("成功", f"已加载文件: {file_path}")
            self.refresh_pdf_list()
            self.unlock_button.config(state=tk.NORMAL)
    
    def save_unlocked_pdf(self, save_dir = None):
        if not save_dir:
            save_dir = filedialog.askdirectory(initialdir=self.processors[0].file_directory, title="选择保存目录")
        try:
            for processor in self.processors:
                save_path = save_dir + "/[Unlocked] " + processor.fileName + ".pdf"
                processor.save_unlocked_pdf(save_path)
            messagebox.showinfo("成功", f"解锁的 PDF 已保存到: {save_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")


    def unlock_all_pdf (self):
        """_summary_
        解锁所有 PDF 文件，并且移除签名，保存所有图像
        """
        save_dir = filedialog.askdirectory(initialdir=self.processors[0].file_directory, title="选择保存目录")

        try:
            for processor in self.processors:
                processor.unlock_pdf()
                processor.remove_signature(save_dir)
                processor.extract_stamp(save_dir)
            self.save_unlocked_pdf(save_dir=save_dir)
            # self.extract_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("错误", f"解锁失败: {e}")


# 启动应用
if __name__ == "__main__":
    # pdf_path = "/Users/ross/Downloads/Inspection Certificate Sample_304L.pdf"
    # pdf_path = "/Users/ross/Downloads/remove_sign.pdf"
    # processor = PDFProcessor()
    # processor.open_pdf(pdf_path)
    # processor.unlock_pdf()
    # save_dir = "/Users/ross/Downloads"
    # processor.extract_stamp(save_dir)
    # processor.remove_signature(save_dir)

    # processor.save_unlocked_pdf("/Users/ross/Downloads/remove_sign_unlocked.pdf")
    
    root = TkinterDnD.Tk()
    app = PDFToolGUI(root)
    root.mainloop()