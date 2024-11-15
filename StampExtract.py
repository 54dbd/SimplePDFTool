import tkinter as tk
from tkinter import filedialog, messagebox
import pikepdf
from PyPDF2 import PdfReader
from PIL import Image
import io


# 核心逻辑类
class PDFProcessor:
    def __init__(self):
        self.pdf_path = None
        self.unlocked_pdf_path = None
        self.fileName = None
        self.file_directory = None

    def open_pdf(self, file_path):
        """打开 PDF 文件"""
        self.pdf_path = file_path
        self.fileName = file_path.split("/")[-1].split(".")[0]
        self.file_directory = "/".join(file_path.split("/")[:-1])
        return self.pdf_path is not None

    def unlock_pdf(self):
        """解锁 PDF 文件"""
        if not self.pdf_path:
            raise ValueError("未加载 PDF 文件")
        
        unlocked_path = f"{self.file_directory}/{self.fileName}_unlocked.pdf"
        with pikepdf.open(self.pdf_path) as pdf:
            pdf.save(unlocked_path)
        self.unlocked_pdf_path = unlocked_path
        return self.unlocked_pdf_path

    def extract_stamp(self, save_dir):
        """提取印章并保存为图像文件"""
        if not self.unlocked_pdf_path:
            raise ValueError("请先解锁 PDF")

        reader = PdfReader(self.unlocked_pdf_path)
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
                                image_path = f"{save_dir}/{self.fileName}_stamp_{stamp_count}.png"
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
        self.open_button = tk.Button(self.root, text="打开 PDF", command=self.open_pdf)
        self.open_button.pack(pady=10)

        # 创建一个 Frame 容器，用于水平布局
        # button_frame = tk.Frame(self.root)
        # button_frame.pack(pady=10)

        # 解锁按钮
        self.unlock_button = tk.Button(text="解锁 PDF", command=self.unlock_pdf, state=tk.DISABLED)
        self.unlock_button.pack(pady=10)  # 使用 padx 增加按钮之间的间距

        # 保存解锁文件按钮
        # self.save_button = tk.Button(button_frame, text="保存解锁 PDF", command=self.save_unlocked_pdf, state=tk.DISABLED)
        # self.save_button.pack(side=tk.LEFT, padx=5)  # 按钮水平排列
        
        # 提取印章按钮
        self.extract_button = tk.Button(self.root, text="提取印章", command=self.extract_stamp, state=tk.DISABLED)
        self.extract_button.pack(pady=10)

    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path and self.processor.open_pdf(file_path):
            messagebox.showinfo("成功", f"已加载文件: {file_path}")
            self.unlock_button.config(state=tk.NORMAL)

    def unlock_pdf(self):
        try:
            unlocked_path = self.processor.unlock_pdf()
            messagebox.showinfo("成功", f"PDF 解锁成功，路径: {unlocked_path}")
            # self.save_button.config(state=tk.NORMAL)
            self.extract_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("错误", f"解锁失败: {e}")

    def save_unlocked_pdf(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if save_path:
            try:
                with open(self.processor.unlocked_pdf_path, "rb") as src, open(save_path, "wb") as dst:
                    dst.write(src.read())
                messagebox.showinfo("成功", f"解锁的 PDF 已保存到: {save_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {e}")

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
    root = tk.Tk()
    app = PDFToolGUI(root)
    root.mainloop()