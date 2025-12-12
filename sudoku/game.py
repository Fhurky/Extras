import tkinter as tk
from tkinter import messagebox
import random
import copy
from datetime import datetime, timedelta

GRID_SIZE = 9
BOX = 3

class ModernSudoku:
    def __init__(self, root):
        self.root = root
        root.title("Modern Sudoku")
        root.configure(bg='#1a1625')
        
        # Renkler
        self.colors = {
            'bg': '#1a1625',
            'primary': '#8b5cf6',
            'secondary': '#ec4899',
            'cell_bg': '#2d2438',
            'cell_hover': '#3d3448',
            'cell_selected': '#8b5cf6',
            'cell_given': '#4a3f5c',
            'cell_error': '#ef4444',
            'cell_highlight': '#3b3558',
            'text': '#ffffff',
            'text_given': '#a78bfa',
            'text_user': '#60a5fa',
            'button_bg': '#8b5cf6',
            'button_hover': '#7c3aed',
        }
        
        # Oyun verileri
        self.board = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.initial_board = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.solution = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.selected = None
        self.difficulty = 'medium'
        self.start_time = None
        self.elapsed_time = 0
        self.is_paused = False
        self.pencil_mode = False
        self.notes = [[set() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.history = []
        
        self.cells = [[None]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.cell_frames = [[None]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.note_labels = [[None]*GRID_SIZE for _ in range(GRID_SIZE)]
        
        self.create_ui()
        self.new_game()
        self.update_timer()
        
    def create_ui(self):
        # Ana container
        main_frame = tk.Frame(self.root, bg=self.colors['bg'], padx=20, pady=20)
        main_frame.pack()
        
        # Başlık
        title_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        title_frame.pack(pady=(0, 15))
        
        title = tk.Label(
            title_frame, 
            text="✨ SUDOKU ✨",
            font=('Arial', 32, 'bold'),
            fg=self.colors['primary'],
            bg=self.colors['bg']
        )
        title.pack()
        
        subtitle = tk.Label(
            title_frame,
            text="Modern & Şık Sudoku Oyunu",
            font=('Arial', 11),
            fg='#c4b5fd',
            bg=self.colors['bg']
        )
        subtitle.pack()
        
        # Üst panel (zorluk + zamanlayıcı)
        top_panel = tk.Frame(main_frame, bg=self.colors['bg'])
        top_panel.pack(pady=(0, 15), fill='x')
        
        # Zorluk butonları
        difficulty_frame = tk.Frame(top_panel, bg=self.colors['bg'])
        difficulty_frame.pack(side='left')
        
        difficulties = [('Kolay', 'easy'), ('Orta', 'medium'), ('Zor', 'hard')]
        self.diff_buttons = {}
        for text, diff in difficulties:
            btn = tk.Button(
                difficulty_frame,
                text=text,
                font=('Arial', 10, 'bold'),
                bg=self.colors['button_bg'] if diff == self.difficulty else self.colors['cell_bg'],
                fg=self.colors['text'],
                activebackground=self.colors['button_hover'],
                activeforeground=self.colors['text'],
                relief='flat',
                padx=15,
                pady=8,
                cursor='hand2',
                command=lambda d=diff: self.change_difficulty(d)
            )
            btn.pack(side='left', padx=3)
            self.diff_buttons[diff] = btn
        
        # Zamanlayıcı
        self.timer_label = tk.Label(
            top_panel,
            text="00:00",
            font=('Arial', 20, 'bold'),
            fg=self.colors['primary'],
            bg=self.colors['cell_bg'],
            padx=20,
            pady=8
        )
        self.timer_label.pack(side='right')
        
        # Oyun tahtası frame
        board_bg = tk.Frame(main_frame, bg=self.colors['cell_bg'], padx=15, pady=15)
        board_bg.pack(pady=(0, 15))
        
        board_frame = tk.Frame(board_bg, bg='#8b5cf6', padx=3, pady=3)
        board_frame.pack()
        
        # 9x9 grid oluştur
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                # Kalın kenarlıklar için frame
                pad_x = (3 if c % 3 == 0 else 1, 3 if c % 3 == 2 else 1)
                pad_y = (3 if r % 3 == 0 else 1, 3 if r % 3 == 2 else 1)
                
                cell_container = tk.Frame(board_frame, bg='#8b5cf6')
                cell_container.grid(row=r, column=c, padx=pad_x, pady=pad_y)
                
                cell_frame = tk.Frame(
                    cell_container,
                    bg=self.colors['cell_bg'],
                    width=55,
                    height=55
                )
                cell_frame.pack_propagate(False)
                cell_frame.pack()
                
                # Sayı label
                cell = tk.Label(
                    cell_frame,
                    text="",
                    font=('Arial', 22, 'bold'),
                    bg=self.colors['cell_bg'],
                    fg=self.colors['text'],
                    cursor='hand2'
                )
                cell.place(relx=0.5, rely=0.5, anchor='center')
                cell.bind('<Button-1>', lambda e, row=r, col=c: self.select_cell(row, col))
                cell_frame.bind('<Button-1>', lambda e, row=r, col=c: self.select_cell(row, col))
                
                # Not label (küçük sayılar)
                note_label = tk.Label(
                    cell_frame,
                    text="",
                    font=('Arial', 7),
                    bg=self.colors['cell_bg'],
                    fg='#94a3b8',
                    cursor='hand2'
                )
                note_label.place(x=2, y=2)
                note_label.bind('<Button-1>', lambda e, row=r, col=c: self.select_cell(row, col))
                
                self.cells[r][c] = cell
                self.cell_frames[r][c] = cell_frame
                self.note_labels[r][c] = note_label
        
        # Sayı butonları
        numbers_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        numbers_frame.pack(pady=(0, 15))
        
        for num in range(1, 10):
            btn = tk.Button(
                numbers_frame,
                text=str(num),
                font=('Arial', 16, 'bold'),
                bg=self.colors['button_bg'],
                fg=self.colors['text'],
                activebackground=self.colors['button_hover'],
                activeforeground=self.colors['text'],
                relief='flat',
                width=4,
                height=2,
                cursor='hand2',
                command=lambda n=num: self.input_number(n)
            )
            btn.pack(side='left', padx=3)
            
            # Hover efekti
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=self.colors['button_hover']))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg=self.colors['button_bg']))
        
        # Kontrol butonları
        control_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        control_frame.pack()
        
        buttons = [
            ("🔄 Yeni Oyun", self.new_game, '#10b981'),
            ("✏️ Notlar", self.toggle_pencil, '#f59e0b'),
            ("💡 İpucu", self.give_hint, '#3b82f6'),
            ("↶ Geri Al", self.undo_move, '#ef4444'),
            ("⏸ Durdur", self.toggle_pause, '#8b5cf6'),
        ]
        
        for text, cmd, color in buttons:
            btn = tk.Button(
                control_frame,
                text=text,
                font=('Arial', 10, 'bold'),
                bg=color,
                fg=self.colors['text'],
                activebackground=color,
                activeforeground=self.colors['text'],
                relief='flat',
                padx=12,
                pady=10,
                cursor='hand2',
                command=cmd
            )
            btn.pack(side='left', padx=3)
            
            # Hover efekti
            original_color = color
            btn.bind('<Enter>', lambda e, b=btn, c=original_color: 
                    b.config(bg=self.adjust_brightness(c, 1.2)))
            btn.bind('<Leave>', lambda e, b=btn, c=original_color: b.config(bg=c))
            
            if text == "✏️ Notlar":
                self.pencil_button = btn
        
        # Klavye bağlama
        self.root.bind('<Key>', self.handle_key)
        
        # Bilgi metni
        info = tk.Label(
            main_frame,
            text="🎮 Ok tuşları | 1-9 sayı gir | Backspace/Delete sil",
            font=('Arial', 9),
            fg='#c4b5fd',
            bg=self.colors['bg']
        )
        info.pack(pady=(10, 0))
    
    def adjust_brightness(self, color, factor):
        """Renk parlaklığını ayarla"""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def change_difficulty(self, diff):
        self.difficulty = diff
        for d, btn in self.diff_buttons.items():
            if d == diff:
                btn.config(bg=self.colors['button_bg'])
            else:
                btn.config(bg=self.colors['cell_bg'])
    
    def is_safe(self, board, row, col, num):
        for i in range(GRID_SIZE):
            if board[row][i] == num or board[i][col] == num:
                return False
        box_row, box_col = (row // BOX) * BOX, (col // BOX) * BOX
        for r in range(box_row, box_row + BOX):
            for c in range(box_col, box_col + BOX):
                if board[r][c] == num:
                    return False
        return True
    
    def solve_board(self, board):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if board[r][c] == 0:
                    for num in range(1, 10):
                        if self.is_safe(board, r, c, num):
                            board[r][c] = num
                            if self.solve_board(board):
                                return True
                            board[r][c] = 0
                    return False
        return True
    
    def generate_sudoku(self):
        board = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
        nums = list(range(1, 10))
        
        def fill_board(b):
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if b[r][c] == 0:
                        random.shuffle(nums)
                        for num in nums:
                            if self.is_safe(b, r, c, num):
                                b[r][c] = num
                                if fill_board(b):
                                    return True
                                b[r][c] = 0
                        return False
            return True
        
        fill_board(board)
        solution = [row[:] for row in board]
        
        # Hücreleri çıkar
        cells_to_remove = {'easy': 35, 'medium': 45, 'hard': 55}[self.difficulty]
        cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]
        random.shuffle(cells)
        
        for i in range(min(cells_to_remove, len(cells))):
            r, c = cells[i]
            board[r][c] = 0
        
        return board, solution
    
    def new_game(self):
        self.board, self.solution = self.generate_sudoku()
        self.initial_board = [row[:] for row in self.board]
        self.selected = None
        self.notes = [[set() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.history = []
        self.start_time = datetime.now()
        self.elapsed_time = 0
        self.is_paused = False
        self.update_board()
    
    def select_cell(self, row, col):
        if self.is_paused:
            return
        self.selected = (row, col)
        self.update_board()
    
    def update_board(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                cell = self.cells[r][c]
                frame = self.cell_frames[r][c]
                note_label = self.note_labels[r][c]
                val = self.board[r][c]
                
                # Arkaplan rengi
                if self.selected and self.selected == (r, c):
                    bg = self.colors['cell_selected']
                elif self.selected and self.is_same_group(r, c, self.selected[0], self.selected[1]):
                    bg = self.colors['cell_highlight']
                elif self.initial_board[r][c] != 0:
                    bg = self.colors['cell_given']
                else:
                    bg = self.colors['cell_bg']
                
                frame.config(bg=bg)
                cell.config(bg=bg)
                note_label.config(bg=bg)
                
                # Değer ve renk
                if val != 0:
                    cell.config(text=str(val))
                    if self.initial_board[r][c] != 0:
                        cell.config(fg=self.colors['text_given'], font=('Arial', 22, 'bold'))
                    else:
                        cell.config(fg=self.colors['text_user'], font=('Arial', 22, 'bold'))
                    note_label.config(text="")
                else:
                    cell.config(text="")
                    # Notları göster
                    if self.notes[r][c]:
                        note_text = ""
                        for i in range(1, 10):
                            if i in self.notes[r][c]:
                                note_text += str(i)
                            else:
                                note_text += " "
                            if i % 3 == 0 and i != 9:
                                note_text += "\n"
                        note_label.config(text=note_text)
                    else:
                        note_label.config(text="")
    
    def is_same_group(self, r1, c1, r2, c2):
        if r1 == r2 or c1 == c2:
            return True
        return (r1 // 3 == r2 // 3) and (c1 // 3 == c2 // 3)
    
    def input_number(self, num):
        if not self.selected or self.is_paused:
            return
        row, col = self.selected
        if self.initial_board[row][col] != 0:
            return
        
        # Geçmişe kaydet
        self.history.append({
            'board': [row[:] for row in self.board],
            'notes': [row[:] for row in self.notes]
        })
        
        if self.pencil_mode:
            # Not modu
            if num in self.notes[row][col]:
                self.notes[row][col].remove(num)
            else:
                self.notes[row][col].add(num)
        else:
            # Normal mod
            if self.board[row][col] == num:
                self.board[row][col] = 0
            else:
                self.board[row][col] = num
                self.notes[row][col].clear()
        
        self.update_board()
        self.check_win()
    
    def toggle_pencil(self):
        self.pencil_mode = not self.pencil_mode
        if self.pencil_mode:
            self.pencil_button.config(bg='#f59e0b', text="✏️ Notlar (Açık)")
        else:
            self.pencil_button.config(bg='#f59e0b', text="✏️ Notlar")
    
    def give_hint(self):
        if not self.selected or self.is_paused:
            return
        row, col = self.selected
        if self.initial_board[row][col] != 0:
            return
        
        self.board[row][col] = self.solution[row][col]
        self.initial_board[row][col] = self.solution[row][col]
        self.update_board()
        self.check_win()
    
    def undo_move(self):
        if not self.history:
            return
        last = self.history.pop()
        self.board = last['board']
        self.notes = last['notes']
        self.update_board()
    
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            # Tahtayı gizle
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    self.cells[r][c].config(text="")
                    self.note_labels[r][c].config(text="")
        else:
            self.update_board()
    
    def handle_key(self, event):
        if not self.selected or self.is_paused:
            return
        
        row, col = self.selected
        
        if event.char in '123456789':
            self.input_number(int(event.char))
        elif event.keysym in ('BackSpace', 'Delete'):
            if self.initial_board[row][col] == 0:
                self.board[row][col] = 0
                self.notes[row][col].clear()
                self.update_board()
        elif event.keysym == 'Up' and row > 0:
            self.select_cell(row - 1, col)
        elif event.keysym == 'Down' and row < 8:
            self.select_cell(row + 1, col)
        elif event.keysym == 'Left' and col > 0:
            self.select_cell(row, col - 1)
        elif event.keysym == 'Right' and col < 8:
            self.select_cell(row, col + 1)
    
    def update_timer(self):
        if not self.is_paused and self.start_time:
            elapsed = (datetime.now() - self.start_time).seconds + self.elapsed_time
            mins = elapsed // 60
            secs = elapsed % 60
            self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
        self.root.after(1000, self.update_timer)
    
    def check_win(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.board[r][c] != self.solution[r][c]:
                    return
        
        elapsed = (datetime.now() - self.start_time).seconds
        mins = elapsed // 60
        secs = elapsed % 60
        messagebox.showinfo(
            "Tebrikler! 🎉",
            f"Sudoku'yu çözdünüz!\n\nSüre: {mins:02d}:{secs:02d}"
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernSudoku(root)
    root.mainloop()