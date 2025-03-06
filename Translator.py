import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import google.generativeai as genai
import threading

class TruyenDichApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dịch Truyện AI")
        self.root.geometry("800x600")

        # Cấu hình API Gemini
        self.setup_api_config()

        # Tạo giao diện
        self.create_widgets()

    def setup_api_config(self):
        """Thiết lập cấu hình API Gemini"""
        try:
            # Nhập API key của bạn ở đây
            self.api_key = "API_key"
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        except Exception as e:
            messagebox.showerror("Lỗi API", f"Không thể kết nối API: {str(e)}")

    def create_widgets(self):
        """Tạo các widget cho giao diện"""
        # Frame chọn file
        file_frame = tk.Frame(self.root)
        file_frame.pack(padx=10, pady=10, fill='x')

        self.file_path = tk.StringVar()
        tk.Label(file_frame, text="File Truyện:").pack(side='left')
        tk.Entry(file_frame, textvariable=self.file_path, width=50).pack(side='left', padx=5)
        tk.Button(file_frame, text="Chọn File", command=self.chon_file).pack(side='left')

        # Frame cài đặt dịch
        setting_frame = tk.Frame(self.root)
        setting_frame.pack(padx=10, pady=5, fill='x')

        tk.Label(setting_frame, text="Số chương dịch mỗi lần:").pack(side='left')
        self.so_chuong = tk.IntVar(value=1)
        tk.Spinbox(setting_frame, from_=1, to=10, textvariable=self.so_chuong, width=5).pack(side='left', padx=5)

        # Nút bắt đầu dịch
        tk.Button(self.root, text="Bắt Đầu Dịch", command=self.bat_dau_dich).pack(pady=10)

        # Khung hiển thị log
        self.log_text = scrolledtext.ScrolledText(self.root, height=15, width=90, wrap=tk.WORD)
        self.log_text.pack(padx=10, pady=10)

        # Thanh tiến trình
        self.progress = ttk.Progressbar(self.root, orient='horizontal', length=700, mode='determinate')
        self.progress.pack(padx=10, pady=5)

    def chon_file(self):
        """Mở hộp thoại chọn file"""
        filename = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        self.file_path.set(filename)

    def doc_file_theo_chuong(self, duong_dan, so_chuong):
        """Đọc file và chia theo số chương"""
        with open(duong_dan, 'r', encoding='utf-8') as f:
            noi_dung = f.read()
            
        # Tách chương
        cac_chuong = noi_dung.split('Chương')
        cac_chuong = [f'Chương{c}' for c in cac_chuong[1:]]
        return cac_chuong

    def dich_chuong(self, chuong):
        """Dịch một chương từ Trung sang Việt"""
        try:
            prompt = f"Dịch đoạn văn sau từ tiếng Trung sang tiếng Việt một cách chính xác và trôi chảy:\n{chuong}"
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            self.log_text.insert(tk.END, f"Lỗi dịch: {str(e)}\n")
            return chuong

    def luu_chuong_da_dich(self, duong_dan_goc, chuong_da_dich):
        """Lưu chương đã dịch"""
        thu_muc = os.path.dirname(duong_dan_goc)
        ten_file = os.path.splitext(os.path.basename(duong_dan_goc))[0]
        
        thu_muc_dich = os.path.join(thu_muc, f"{ten_file}_Da_Dich")
        os.makedirs(thu_muc_dich, exist_ok=True)
        
        duong_dan_moi = os.path.join(thu_muc_dich, os.path.basename(duong_dan_goc))
        
        with open(duong_dan_moi, 'w', encoding='utf-8') as f:
            f.write('\n'.join(chuong_da_dich))

    def bat_dau_dich(self):
        """Bắt đầu quá trình dịch"""
        if not self.file_path.get():
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file!")
            return

        # Khởi động luồng dịch để không block giao diện
        threading.Thread(target=self._qua_trinh_dich, daemon=True).start()

    def _qua_trinh_dich(self):
        """Quá trình dịch chính"""
        try:
            # Đọc file và chia chương
            cac_chuong = self.doc_file_theo_chuong(self.file_path.get(), self.so_chuong.get())
            
            # Chuẩn bị tiến trình
            self.progress['maximum'] = len(cac_chuong)
            chuong_da_dich = []

            # Dịch từng chương
            for idx, chuong in enumerate(cac_chuong, 1):
                self.log_text.insert(tk.END, f"Đang dịch chương {idx}...\n")
                self.log_text.see(tk.END)
                
                chuong_dich = self.dich_chuong(chuong)
                chuong_da_dich.append(chuong_dich)
                
                # Cập nhật thanh tiến trình
                self.progress['value'] = idx
                self.root.update_idletasks()

            # Lưu file đã dịch
            self.luu_chuong_da_dich(self.file_path.get(), chuong_da_dich)
            
            # Thông báo hoàn thành
            messagebox.showinfo("Thành Công", "Đã dịch xong truyện!")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {str(e)}")

def main():
    root = tk.Tk()
    app = TruyenDichApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()