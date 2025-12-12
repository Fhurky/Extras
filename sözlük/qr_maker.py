"""
Modern ve Şık Sözlük QR Oluşturucu
Mor-Mavi Tema

Kullanım:
    pip install qrcode[pil] pillow
    python dictionary_qr_gui.py
"""
# pyinstaller --onefile --windowed --name "QR_Sozluk" --icon=64.ico qr_maker.py
import io
import urllib.parse
import tkinter as tk
from tkinter import messagebox, ttk, filedialog

import qrcode
from PIL import Image, ImageTk

TURENG_BASE = "https://tureng.com/tr/turkce-ingilizce/"
LDOCE_BASE = "https://www.ldoceonline.com/dictionary/"


class ModernQRApp:
    def __init__(self, root):
        self.root = root
        root.title("✨ QR Sözlük")
        root.resizable(False, False)
        root.configure(bg='#f0e6ff')
        
        # Pencere boyutunu sabitle
        root.geometry('450x650')

        # Modern stil - Mor-Mavi tema
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background='#f0e6ff')
        style.configure("TLabel", background='#f0e6ff', foreground='#4a1a8f', 
                       font=('Segoe UI', 10))
        style.configure("TButton", font=('Segoe UI', 9), borderwidth=0)
        style.configure("TRadiobutton", background='#f0e6ff', foreground='#4a1a8f', 
                       font=('Segoe UI', 10))
        style.map("TButton", background=[('active', '#b794f6')])

        main = ttk.Frame(root, padding="20")
        main.pack(fill='both', expand=True)

        # Başlık - Gradient efekti için
        title_frame = tk.Frame(main, bg='#9b6dff', bd=0, height=60)
        title_frame.pack(fill='x', pady=(0, 15))
        title_frame.pack_propagate(False)
        
        title = tk.Label(title_frame, text="✨ Sözlük QR Oluşturucu ✨", 
                        font=('Segoe UI', 14, 'bold'), 
                        foreground='white', bg='#9b6dff')
        title.pack(expand=True)

        # Sözlük seçimi - Şık kartlar
        dict_label = ttk.Label(main, text="Sözlük Seçin:", 
                              font=('Segoe UI', 10, 'bold'))
        dict_label.pack(anchor='w', pady=(0, 8))
        
        self.dict_var = tk.StringVar(value="Tureng")
        
        dict_frame = tk.Frame(main, bg='#f0e6ff')
        dict_frame.pack(fill='x', pady=(0, 15))
        
        # Tureng butonu
        tureng_btn = tk.Radiobutton(dict_frame, text="🇹🇷 Tureng", 
                                    variable=self.dict_var, value="Tureng",
                                    bg='#e0d4ff', fg='#4a1a8f', 
                                    font=('Segoe UI', 10, 'bold'),
                                    selectcolor='#b794f6', activebackground='#d4c5ff',
                                    relief='flat', bd=0, padx=20, pady=10,
                                    cursor='hand2', indicatoron=False)
        tureng_btn.pack(side='left', expand=True, fill='x', padx=(0, 8))
        
        # Longman butonu
        ldoce_btn = tk.Radiobutton(dict_frame, text="📖 Longman", 
                                   variable=self.dict_var, value="LDOCE",
                                   bg='#e0d4ff', fg='#4a1a8f',
                                   font=('Segoe UI', 10, 'bold'),
                                   selectcolor='#b794f6', activebackground='#d4c5ff',
                                   relief='flat', bd=0, padx=20, pady=10,
                                   cursor='hand2', indicatoron=False)
        ldoce_btn.pack(side='left', expand=True, fill='x', padx=(8, 0))

        # Kelime girişi - Yuvarlak köşeli
        entry_label = ttk.Label(main, text="Kelime:", 
                               font=('Segoe UI', 10, 'bold'))
        entry_label.pack(anchor='w', pady=(0, 8))
        
        entry_frame = tk.Frame(main, bg='white', bd=0, 
                              highlightbackground='#b794f6', 
                              highlightthickness=2)
        entry_frame.pack(fill='x', pady=(0, 15))
        
        self.entry = tk.Entry(entry_frame, width=30, font=('Segoe UI', 11),
                             bg='white', fg='#4a1a8f', relief='flat', bd=0)
        self.entry.pack(padx=12, pady=10, fill='x')
        self.entry.insert(0, "Kelime girin...")
        self.entry.bind('<FocusIn>', self._clear_placeholder)
        self.entry.bind('<FocusOut>', self._restore_placeholder)
        self.entry.bind('<Return>', lambda e: self.generate_qr())
        self.entry.config(foreground='#b794f6')

        # Butonlar - Gradient tarzı
        btn_frame = tk.Frame(main, bg='#f0e6ff')
        btn_frame.pack(fill='x', pady=(0, 15))
        
        gen_btn = tk.Button(btn_frame, text="✨ Oluştur", command=self.generate_qr,
                           bg='#9b6dff', fg='white', font=('Segoe UI', 11, 'bold'),
                           relief='flat', cursor='hand2', padx=20, pady=12,
                           activebackground='#7c4dff', bd=0)
        gen_btn.pack(side='left', expand=True, fill='x', padx=(0, 5))
        
        save_btn = tk.Button(btn_frame, text="💾 Kaydet", command=self.save_qr,
                           bg='#5e8cff', fg='white', font=('Segoe UI', 11, 'bold'),
                           relief='flat', cursor='hand2', padx=20, pady=12,
                           activebackground='#4a70ff', bd=0)
        save_btn.pack(side='left', expand=True, fill='x', padx=(5, 5))
        
        clr_btn = tk.Button(btn_frame, text="🗑️ Temizle", command=self.clear,
                           bg='#d4c5ff', fg='#4a1a8f', font=('Segoe UI', 10, 'bold'),
                           relief='flat', cursor='hand2', padx=20, pady=12,
                           activebackground='#b794f6', bd=0)
        clr_btn.pack(side='left', expand=True, fill='x', padx=(5, 0))

        # QR gösterim alanı - Yuvarlak çerçeve
        qr_outer = tk.Frame(main, bg='#9b6dff', bd=0)
        qr_outer.pack(pady=(0, 10))
        
        qr_container = tk.Frame(qr_outer, bg='white', bd=0, width=220, height=220)
        qr_container.pack(padx=3, pady=3)
        qr_container.pack_propagate(False)
        
        self.qr_label = tk.Label(qr_container, bg='white')
        self.qr_label.place(relx=0.5, rely=0.5, anchor='center')

        # Alt bilgi
        footer = ttk.Label(main, text="💜 Her kelime bir keşif 💙", 
                          font=('Segoe UI', 9, 'italic'),
                          foreground='#7c4dff')
        footer.pack(pady=(5, 0))

        self._photo = None
        self._placeholder_active = True
        self._current_qr_image = None  # QR görselini saklamak için

    def _clear_placeholder(self, event):
        if self._placeholder_active:
            self.entry.delete(0, tk.END)
            self.entry.config(foreground='#4a1a8f')
            self._placeholder_active = False

    def _restore_placeholder(self, event):
        if not self.entry.get():
            self.entry.insert(0, "Kelime girin...")
            self.entry.config(foreground='#b794f6')
            self._placeholder_active = True

    def _build_url(self, word):
        word = word.strip().lower()
        if not word or word == "kelime girin...":
            return ""
        
        safe_word = urllib.parse.quote(word, safe='')
        
        if self.dict_var.get() == "Tureng":
            return TURENG_BASE + safe_word
        else:
            return LDOCE_BASE + safe_word

    def generate_qr(self):
        url = self._build_url(self.entry.get())
        
        if not url:
            messagebox.showwarning("✨ Uyarı", "Lütfen bir kelime girin.")
            return

        try:
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H,
                              box_size=4, border=2)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#7c4dff", back_color="white")
            
            # Orijinal QR görselini sakla
            self._current_qr_image = img

            with io.BytesIO() as buff:
                img.save(buff, format="PNG")
                buff.seek(0)
                pil_img = Image.open(buff)
                pil_img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                
                self._photo = ImageTk.PhotoImage(pil_img)
                self.qr_label.config(image=self._photo)
                                     
        except Exception as e:
            messagebox.showerror("❌ Hata", f"QR oluşturulamadı:\n{e}")

    def save_qr(self):
        if self._current_qr_image is None:
            messagebox.showwarning("✨ Uyarı", "Önce bir QR kod oluşturun!")
            return
        
        word = self.entry.get().strip()
        if word == "Kelime girin...":
            word = "qr_kod"
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            initialfile=f"{word}_qr.jpg",
            filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # QR kodunu beyaz arka plana çevir ve JPG olarak kaydet
                rgb_img = self._current_qr_image.convert('RGB')
                rgb_img.save(filename, quality=95)
                messagebox.showinfo("✨ Başarılı", f"QR kod kaydedildi:\n{filename}")
            except Exception as e:
                messagebox.showerror("❌ Hata", f"Kaydetme hatası:\n{e}")

    def clear(self):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, "Kelime girin...")
        self.entry.config(foreground='#b794f6')
        self._placeholder_active = True
        self.qr_label.config(image="")
        self._photo = None
        self._current_qr_image = None
        self.entry.focus_set()


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernQRApp(root)
    root.mainloop()