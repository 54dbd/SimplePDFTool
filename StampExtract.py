import os
import io
import tkinter as tk

from math import sqrt
from pikepdf import Pdf
from PIL import Image
from tkinter import filedialog, messagebox
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
        移除 PDF 中的签名
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
            image_path = f"{save_dir}/{self.fileName}/signature_{count}.png"

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
                                image_path = f"{save_dir}/{self.fileName}/stamp_{stamp_count}.png"
                                os.makedirs(f"{save_dir}/{self.fileName}", exist_ok=True)
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
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        self.processor = PDFProcessor()
        self.create_widgets()

    def create_widgets(self):
        """创建 GUI 组件"""
        # 打开文件按钮
        self.open_button = tk.Button(self.root, text="导入 PDF", command=self.open_pdf)
        self.open_button.pack(pady=10)

        # 解锁按钮
        self.unlock_button = tk.Button(text="解锁 PDF", command=self.unlock_pdf, state=tk.DISABLED)
        self.unlock_button.pack(pady=10)  # 使用 padx 增加按钮之间的间距
        
        # 提取印章按钮
        self.extract_button = tk.Button(self.root, text="提取印章", command=self.extract_stamp, state=tk.DISABLED)
        self.extract_button.pack(pady=10)

    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path and self.processor.open_pdf(file_path):
            messagebox.showinfo("成功", f"已加载文件: {file_path}")
            self.unlock_button.config(state=tk.NORMAL)
    
    def save_unlocked_pdf(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")], initialdir=self.processor.file_directory, title="保存解锁 PDF")
        if save_path:
            try:
                self.processor.save_unlocked_pdf(save_path)
                messagebox.showinfo("成功", f"解锁的 PDF 已保存到: {save_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {e}")

    def unlock_pdf(self):
        try:
            self.processor.unlock_pdf()
            self.processor.remove_signature()
            messagebox.showinfo("成功", f"PDF 已解锁并移除所有签名，请选择保存目录")
            self.save_unlocked_pdf()
            self.extract_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("错误", f"解锁失败: {e}")


    def extract_stamp(self):
        save_dir = filedialog.askdirectory(initialdir=self.processor.file_directory, title="选择保存目录")
        if save_dir:
            try:
                self.processor.extract_stamp(save_dir)
                messagebox.showinfo("成功", f"印章已提取到目录: {save_dir}")
            except Exception as e:
                messagebox.showerror("错误", f"提取印章失败: {e}")

# 启动应用
if __name__ == "__main__":
    # pdf_path = "/Users/ross/Downloads/Inspection Certificate Sample_304L.pdf"
    pdf_path = "/Users/ross/Downloads/remove_sign.pdf"
    processor = PDFProcessor()
    processor.open_pdf(pdf_path)
    processor.unlock_pdf()
    save_dir = "/Users/ross/Downloads"
    processor.extract_stamp(save_dir)
    processor.remove_signature(save_dir)

    processor.save_unlocked_pdf("/Users/ross/Downloads/remove_sign_unlocked.pdf")
    
    # root = tk.Tk()
    # app = PDFToolGUI(root)
    # root.mainloop()