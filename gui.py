"""
OPlus ROM Converter - GUI Module
Professional 3-Column Dashboard Interface with Driver Tools & Localization
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
import subprocess
import ctypes
from typing import Optional, List, Dict
import datetime
import webbrowser
import zipfile
from PIL import Image, ImageTk

from converter import (
    find_rawprogram_xmls, find_super_def, parse_super_def,
    find_all_super_defs, get_region_display_name,
    parse_rawprogram_xml, check_super_exists, create_super_image,
    get_super_path, is_sparse_image, get_sparse_info, SuperConfig, RegionInfo
)

import sys
import os

def resource_path(relative_path: str) -> Path:
    """Get absolute path to resource, works for dev and PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    return Path(os.path.abspath(".")) / relative_path

# --- Localization Data ---
TRANSLATIONS = {
    'VI': {
        'title': 'Q-FLASH FORGE',
        'rom_source': 'Nguồn ROM',
        'browse': '📂 Chọn Thư Mục',
        'extract_btn': '📂 Chọn File ZIP',
        'region_selection': 'Chọn Khu Vực (Region)',
        'drivers_tools': 'Driver & Công Cụ',
        'options': 'Tùy Chọn',
        'partitions': 'Danh Sách Phân Vùng',
        'log': 'Nhật Ký (Log)',
        'run_zadig': '🛠️ Chạy Zadig (WinUSB)',
        'install_kedacom': '🔌 Cài Driver Kedacom',
        'append_nvid': 'Thêm NV ID vào tên file',
        'create_btn': 'TẠO SUPER IMAGE',
        'recreate_btn': 'TẠO LẠI SUPER IMAGE',
        'processing': 'ĐANG XỬ LÝ...',
        'extracting': 'ĐANG GIẢI NÉN...',
        'retry': 'THỬ LẠI',
        'status_ready': 'Sẵn sàng',
        'status_done': 'Hoàn tất',
        'status_failed': 'Thất bại',
        'col_region': 'Khu Vực',
        'col_nvid': 'NV ID',
        'col_name': 'Tên',
        'col_size': 'Kích thước',
        'col_group': 'Nhóm',
        'col_status': 'Trạng thái',
        'msg_success': 'Thành công',
        'msg_failed': 'Thất bại',
        'msg_overwrite': 'File đã tồn tại. Bạn có muốn ghi đè không?',
        'msg_driver_success': 'Đã cài đặt/xác minh Driver thành công!',
        'msg_driver_fail': 'Cài đặt thất bại',
        'menu_about': 'Giới thiệu',
        'menu_donate': 'Ủng hộ',
        'menu_terms': 'Điều khoản',
        'lang_switch': '🇬🇧 English',
        'about_title': 'Giới thiệu',
        'about_text': 'Q-Flash Forge\n\nTool hỗ trợ convert ROM và fix driver cho các dòng máy Oppo/OnePlus/Realme (Factory/Domestic/Export ROMs).\n\nNgười phát triển: Xuan Nguyen\nFacebook: https://www.facebook.com/xuannguyen030923\nTelegram: https://t.me/mitomtreem',
        'donate_title': 'Ủng hộ (Donate)',
        'donate_text': 'Nếu tool hữu ích, bạn có thể ủng hộ mình qua:\n\nBinance ID: 381766288\n\nCảm ơn bạn rất nhiều! ❤️',
        'terms_title': 'Điều khoản sử dụng',
        'terms_text': '1. Phần mềm này là Open Source và miễn phí.\n2. Sử dụng với rủi ro của riêng bạn.\n3. Tác giả không chịu trách nhiệm về bất kỳ hư hỏng nào đối với thiết bị.',
        'zadig_guide_title': 'Hướng Dẫn Cài đặt & Sử Dụng Zadig',
        'zadig_step1': 'Bước 1: Chọn "Options" -> "List All Devices".',
        'zadig_step2': 'Bước 2: Chọn thiết bị "QUSB_BULK" hoặc thiết bị 9008 trong danh sách.',
        'zadig_step3': 'Bước 3: Chọn driver "WinUSB" ở khung bên phải và bấm "Install Driver" hoặc "Replace Driver".'
    },
    'EN': {
        'title': 'Q-FLASH FORGE',
        'rom_source': 'ROM Source',
        'browse': '📂 Browse Folder',
        'extract_btn': '📂 Extract .ZIP',
        'region_selection': 'Region Selection',
        'drivers_tools': 'Drivers & Tools',
        'options': 'Options',
        'partitions': 'Partitions',
        'log': 'Log',
        'run_zadig': '🛠️ Run Zadig (WinUSB)',
        'install_kedacom': '🔌 Install Kedacom Driver',
        'append_nvid': 'Append NV ID to filename',
        'create_btn': 'CREATE SUPER IMAGE',
        'recreate_btn': 'RE-CREATE SUPER IMAGE',
        'processing': 'PROCESSING...',
        'extracting': 'EXTRACTING...',
        'retry': 'RETRY',
        'status_ready': 'Ready',
        'status_done': 'Done',
        'status_failed': 'Failed',
        'col_region': 'Region',
        'col_nvid': 'NV ID',
        'col_name': 'Name',
        'col_size': 'Size',
        'col_group': 'Group',
        'col_status': 'Status',
        'msg_success': 'Success',
        'msg_failed': 'Failed',
        'msg_overwrite': 'File exists. Overwrite?',
        'msg_driver_success': 'Driver Installed/Verified Successfully!',
        'msg_driver_fail': 'Install Failed',
        'menu_about': 'About',
        'menu_donate': 'Donate',
        'menu_terms': 'Terms',
        'lang_switch': '🇻🇳 Tiếng Việt',
        'about_title': 'About',
        'about_text': 'Q-Flash Forge\n\nTool for converting ROMs and fixing drivers for Oppo/OnePlus/Realme devices (Factory/Domestic/Export).\n\nDeveloper: Xuan Nguyen\nFacebook: https://www.facebook.com/xuannguyen030923\nTelegram: https://t.me/mitomtreem',
        'donate_title': 'Donate',
        'donate_text': 'If you find this tool helpful, you can support me via:\n\nBinance ID: 381766288\n\nThank you very much! ❤️',
        'terms_title': 'Terms of Use',
        'terms_text': '1. This software is Open Source and free to use.\n2. Use at your own risk.\n3. The author is not responsible for any damage to your device.',
        'zadig_guide_title': 'Zadig Usage Guide',
        'zadig_step1': 'Step 1: Select "Options" -> "List All Devices".',
        'zadig_step2': 'Step 2: Select "QUSB_BULK" or 9008 device from the drop-down list.',
        'zadig_step3': 'Step 3: Choose "WinUSB" driver on the right side and click "Install Driver" or "Replace Driver".'
    }
}

# --- Design Tokens ---
COLORS = {
    'header_bg': '#1565C0',    # Deep Blue Header
    'header_text': '#FFFFFF',
    'bg': '#F0F2F5',           # Light Gray Background
    'card_bg': '#FFFFFF',      # White Cards
    'text_primary': '#333333',
    'text_secondary': '#666666',
    'primary': '#1976D2',      # Blue Actions
    'success': '#43A047',      # Green Start Button
    'folder_icon': '#FFA000',  # Amber Folder
    'border': '#E0E0E0',
    'log_bg': '#FFFFFF',
    'selected_bg': '#E3F2FD'
}

FONTS = {
    'header': ('Segoe UI', 12, 'bold'),
    'card_title': ('Segoe UI', 10, 'bold'),
    'label': ('Segoe UI', 9),
    'value': ('Segoe UI', 9),
    'button': ('Segoe UI', 9, 'bold'),
    'mono': ('Consolas', 9)
}

class RomConverterApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.geometry("1100x800")
        self.root.minsize(1000, 700)
        
        # Set Window Icon
        try:
            icon_path = resource_path("assets/icon.ico")
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except: pass
        
        self.current_lang = 'VI'  # Default Language
        
        self.setup_styles()
        
        # UI Element References (for dynamic translation)
        self.ui_elements = {}
        
        # State
        self.rom_folder: Optional[Path] = None
        self.super_config: Optional[SuperConfig] = None
        self.available_regions: List[RegionInfo] = []
        self.selected_region_index: int = -1
        self.is_processing = False
        
        self.create_layout()
        self.update_texts() # Initial Text Load
        
    def setup_styles(self):
        self.root.configure(bg=COLORS['bg'])
        style = ttk.Style()
        style.theme_use('clam')
        
        # General
        style.configure('.', background=COLORS['bg'], font=FONTS['label'])
        
        # Treeview
        style.configure('Treeview', background='white', fieldbackground='white', rowheight=28, borderwidth=0)
        style.configure('Treeview.Heading', background='#F5F5F5', font=('Segoe UI', 9, 'bold'), foreground='#444')
        style.map('Treeview', background=[('selected', COLORS['selected_bg'])], foreground=[('selected', 'black')])
        
        # Frame
        style.configure('Card.TFrame', background=COLORS['card_bg'])
        style.configure('Header.TFrame', background=COLORS['header_bg'])
        
        # LabelFrame
        style.configure('Card.TLabelframe', background=COLORS['card_bg'], relief='solid', borderwidth=1, bordercolor=COLORS['border'])
        # Font will be set dynamically via style config or recreating widgets if needed, 
        # but ttk.Style is global. We'll handle text updates on widgets directly.
        style.configure('Card.TLabelframe.Label', background=COLORS['card_bg'], font=FONTS['card_title'], foreground=COLORS['primary'])

        # Progress
        style.configure('Horizontal.TProgressbar', background=COLORS['success'], troughcolor='#E0E0E0', bordercolor=COLORS['card_bg'])

    def tr(self, key):
        return TRANSLATIONS[self.current_lang].get(key, key)

    def toggle_language(self):
        self.current_lang = 'EN' if self.current_lang == 'VI' else 'VI'
        self.update_texts()

    def update_texts(self):
        self.root.title(self.tr('title'))
        
        # Header
        self.header_label.config(text=self.tr('title'))
        self.lang_btn.config(text=self.tr('lang_switch'))
        self.btn_about.config(text=self.tr('menu_about'))
        self.btn_donate.config(text=self.tr('menu_donate'))
        self.btn_terms.config(text=self.tr('menu_terms'))

        # Cards
        self.ui_elements['card_source'].config(text=f" {self.tr('rom_source')} ")
        self.ui_elements['card_region'].config(text=f" {self.tr('region_selection')} ")
        self.ui_elements['card_drivers'].config(text=f" {self.tr('drivers_tools')} ")
        self.ui_elements['card_options'].config(text=f" {self.tr('options')} ")
        self.ui_elements['card_partitions'].config(text=f" {self.tr('partitions')} ")
        self.ui_elements['card_log'].config(text=f" {self.tr('log')} ")

        # Buttons & Labels
        self.ui_elements['btn_browse'].config(text=self.tr('browse'))
        self.ui_elements['btn_extract'].config(text=self.tr('extract_btn'))
        self.ui_elements['btn_zadig'].config(text=self.tr('run_zadig'))
        self.ui_elements['btn_driver'].config(text=self.tr('install_kedacom'))
        self.ui_elements['chk_nvid'].config(text=self.tr('append_nvid'))
        
        if not self.is_processing:
            if self.start_btn['state'] == 'disabled':
                 self.start_btn.config(text=self.tr('create_btn'))
            else:
                 # Check simple logic to see if we should show RE-CREATE or CREATE
                 # This is a bit tricky since we lost context of 'existing file' unless we re-check
                 # For simplicity, default to CREATE, scan_rom will update if needed
                 self.start_btn.config(text=self.tr('create_btn'))

        # Treeview Headings
        self.region_list.heading('region', text=self.tr('col_region'))
        self.region_list.heading('nvid', text=self.tr('col_nvid'))
        
        self.partition_tree.heading('name', text=self.tr('col_name'))
        self.partition_tree.heading('len', text=self.tr('col_size'))
        self.partition_tree.heading('grp', text=self.tr('col_group'))
        self.partition_tree.heading('status', text=self.tr('col_status'))

    def create_layout(self):
        # 1. Header Bar
        header = tk.Frame(self.root, bg=COLORS['header_bg'], height=45)
        header.pack(fill=tk.X, side=tk.TOP)
        
        # Title
        self.header_label = tk.Label(header, text="", bg=COLORS['header_bg'], fg='white', 
                 font=FONTS['header'], padx=20)
        self.header_label.pack(side=tk.LEFT, pady=10)
        
        # Menu Toolbar (Right aligned)
        toolbar = tk.Frame(header, bg=COLORS['header_bg'])
        toolbar.pack(side=tk.RIGHT, padx=10)
        
        def mk_menu_btn(text, cmd):
            return tk.Button(toolbar, text=text, bg=COLORS['header_bg'], fg='white', 
                             activebackground='#1976D2', activeforeground='white',
                             relief='flat', font=('Segoe UI', 9), command=cmd, cursor='hand2')

        self.lang_btn = mk_menu_btn("🌐", self.toggle_language)
        self.lang_btn.pack(side=tk.RIGHT, padx=5)
        
        self.btn_terms = mk_menu_btn("Terms", self.show_terms)
        self.btn_terms.pack(side=tk.RIGHT, padx=5)
        
        self.btn_donate = mk_menu_btn("Donate", self.show_donate)
        self.btn_donate.pack(side=tk.RIGHT, padx=5)
        
        self.btn_about = mk_menu_btn("About", self.show_about)
        self.btn_about.pack(side=tk.RIGHT, padx=5)

        # 2. Main Container (Grid Layout)
        main_container = tk.Frame(self.root, bg=COLORS['bg'], padx=10, pady=10)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Setup Grid Weights: 30% - 50% - 20%
        main_container.grid_columnconfigure(0, weight=30, uniform="cols")
        main_container.grid_columnconfigure(1, weight=50, uniform="cols")
        main_container.grid_columnconfigure(2, weight=20, uniform="cols")
        main_container.grid_rowconfigure(0, weight=1)
        
        # === COLUMN 1: LEFT CONFIG (30%) ===
        left_col = tk.Frame(main_container, bg=COLORS['bg'])
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Cards (Stored in self.ui_elements for updating)
        self.ui_elements['card_source'] = self.create_card(left_col, "rom_source", self.create_source_content)
        self.ui_elements['card_region'] = self.create_card(left_col, "region_selection", self.create_region_list_content, expand=True)
        self.ui_elements['card_drivers'] = self.create_card(left_col, "drivers_tools", self.create_driver_content)
        self.ui_elements['card_options'] = self.create_card(left_col, "options", self.create_options_content)

        # === COLUMN 2: CENTER CONTENT (50%) ===
        center_col = tk.Frame(main_container, bg=COLORS['bg'])
        center_col.grid(row=0, column=1, sticky="nsew", padx=(0, 10))
        
        self.ui_elements['card_partitions'] = self.create_card(center_col, "partitions", self.create_partitions_content, expand=True)
        self.create_action_area(center_col)

        # === COLUMN 3: RIGHT LOGS (20%) ===
        right_col = tk.Frame(main_container, bg=COLORS['bg'])
        right_col.grid(row=0, column=2, sticky="nsew")
        
        self.ui_elements['card_log'] = self.create_card(right_col, "log", self.create_log_content, expand=True)

    def create_card(self, parent, translation_key, content_func, expand=False):
        # We store the LabelFrame to update its text later.
        # Initial text is empty or key, updated in update_texts
        card = tk.LabelFrame(parent, text="", bg=COLORS['card_bg'], fg=COLORS['primary'],
                             font=FONTS['card_title'], relief='flat', bd=1, padx=10, pady=10)
        if expand:
            card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        else:
            card.pack(fill=tk.X, pady=(0, 10))
            
        content_func(card)
        return card

    def create_source_content(self, parent):
        self.folder_var = tk.StringVar()
        entry = tk.Entry(parent, textvariable=self.folder_var, bg='#FAFAFA', relief='flat', 
                         bd=1, fg='#444', font=FONTS['mono'])
        # Border frame
        border = tk.Frame(parent, bg=COLORS['border'], bd=1)
        border.pack(fill=tk.X, pady=(5, 5))
        entry.pack(in_=border, fill=tk.X, padx=1, pady=1)
        
        self.ui_elements['btn_browse'] = tk.Button(parent, text="", bg='#FFF3E0', fg='#E65100', 
                        relief='flat', command=self.browse_folder, font=FONTS['button'], cursor='hand2')
        self.ui_elements['btn_browse'].pack(fill=tk.X, pady=(5, 0))

        self.ui_elements['btn_extract'] = tk.Button(parent, text="", bg='#E0F2F1', fg='#00695C', 
                        relief='flat', command=self.extract_source_zip, font=FONTS['button'], cursor='hand2')
        self.ui_elements['btn_extract'].pack(fill=tk.X, pady=(5, 0))

    def create_region_list_content(self, parent):
        container = tk.Frame(parent, bg=COLORS['card_bg'])
        container.pack(fill=tk.BOTH, expand=True)

        columns = ('region', 'nvid')
        self.region_list = ttk.Treeview(container, columns=columns, show='headings', selectmode='browse')
        
        # Headings set in update_texts
        self.region_list.column('region', width=80)
        self.region_list.column('nvid', width=100)
        
        vsb = ttk.Scrollbar(container, orient="vertical", command=self.region_list.yview)
        self.region_list.configure(yscrollcommand=vsb.set)
        
        self.region_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.region_list.bind('<<TreeviewSelect>>', self.on_region_selected)

    def create_driver_content(self, parent):
        # Frame for Zadig + Help
        z_frame = tk.Frame(parent, bg=COLORS['card_bg'])
        z_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.ui_elements['btn_zadig'] = tk.Button(z_frame, text="", bg='#E3F2FD', fg=COLORS['primary'], 
                             relief='flat', command=self.run_zadig, font=FONTS['button'], cursor='hand2')
        self.ui_elements['btn_zadig'].pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Help Button (?)
        btn_help = tk.Button(z_frame, text="?", bg='#BBDEFB', fg='#1565C0', width=3,
                            relief='flat', command=self.show_zadig_guide, font=('Segoe UI', 9, 'bold'), cursor='hand2')
        btn_help.pack(side=tk.RIGHT, padx=(5, 0))

        self.ui_elements['btn_driver'] = tk.Button(parent, text="", bg='#F3E5F5', fg='#7B1FA2', 
                              relief='flat', command=self.install_driver, font=FONTS['button'], cursor='hand2')
        self.ui_elements['btn_driver'].pack(fill=tk.X, pady=(5, 0))

    def create_options_content(self, parent):
        self.use_nv_suffix = tk.BooleanVar(value=False)
        self.ui_elements['chk_nvid'] = tk.Checkbutton(parent, text="", variable=self.use_nv_suffix,
                           bg=COLORS['card_bg'], fg=COLORS['text_primary'], selectcolor=COLORS['card_bg'], activebackground=COLORS['card_bg'])
        self.ui_elements['chk_nvid'].pack(anchor='w')
        tk.Label(parent, text="(e.g. super.10000010.img)", bg=COLORS['card_bg'], fg=COLORS['text_secondary'], font=('Segoe UI', 8)).pack(anchor='w', padx=20)

    def create_partitions_content(self, parent):
        container = tk.Frame(parent, bg='white')
        container.pack(fill=tk.BOTH, expand=True)
        
        self.partition_tree = ttk.Treeview(container, columns=('name', 'len', 'grp', 'status'), show='headings')
        # Headings set in update_texts
        
        self.partition_tree.column('name', width=150)
        self.partition_tree.column('len', width=80)
        self.partition_tree.column('grp', width=150)
        self.partition_tree.column('status', width=100)
        
        vsb = ttk.Scrollbar(container, orient="vertical", command=self.partition_tree.yview)
        self.partition_tree.configure(yscrollcommand=vsb.set)
        
        self.partition_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

    def create_action_area(self, parent):
        frame = tk.Frame(parent, bg=COLORS['bg'])
        frame.pack(fill=tk.X, pady=(0, 0))
        
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(frame, textvariable=self.status_var, bg=COLORS['bg'], fg=COLORS['text_secondary']).pack(anchor='w')
        
        self.progress_var = tk.DoubleVar()
        pb = ttk.Progressbar(frame, variable=self.progress_var, maximum=100, style='Horizontal.TProgressbar')
        pb.pack(fill=tk.X, pady=(2, 10))
        
        self.start_btn = tk.Button(frame, text="", bg=COLORS['success'], fg='white',
                                  font=('Segoe UI', 11, 'bold'), relief='flat', height=2, 
                                  command=self.create_super, state='disabled', cursor='hand2')
        self.start_btn.pack(fill=tk.X)

    def create_log_content(self, parent):
        container = tk.Frame(parent, bg='white')
        container.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(container, bg='white', fg='#333', font=FONTS['mono'], 
                               relief='flat', state='disabled')
        vsb = ttk.Scrollbar(container, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=vsb.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text.tag_config('INFO', foreground='#2196F3')
        self.log_text.tag_config('SUCCESS', foreground='#4CAF50')
        self.log_text.tag_config('ERROR', foreground='#F44336')
        self.log_text.tag_config('WARN', foreground='#FF9800')
        
        self.log("System Ready", "INFO")

    # --- Menu Actions ---

    def show_about(self):
        messagebox.showinfo(self.tr('about_title'), self.tr('about_text'))

    def show_donate(self):
        messagebox.showinfo(self.tr('donate_title'), self.tr('donate_text'))

    def show_terms(self):
        messagebox.showinfo(self.tr('terms_title'), self.tr('terms_text'))

    def show_zadig_guide(self):
        top = tk.Toplevel(self.root)
        top.title(self.tr('zadig_guide_title'))
        top.geometry("700x850") # Increased height for images
        top.configure(bg='white')
        
        # Prevent GC of images
        top.image_refs = [] 

        def add_step(parent, text, img_name):
            tk.Label(parent, text=text, bg='white', anchor='w', justify='left', font=('Segoe UI', 9, 'bold')).pack(fill=tk.X, pady=(10, 5))
            
            img_path = resource_path(f"assets/{img_name}")
            if img_path.exists():
                try:
                    # Load and resize using Pillow
                    pil_img = Image.open(img_path)
                    
                    # Resize logic (Width 600px)
                    base_width = 600
                    w_percent = (base_width / float(pil_img.size[0]))
                    h_size = int((float(pil_img.size[1]) * float(w_percent)))
                    pil_img = pil_img.resize((base_width, h_size), Image.Resampling.LANCZOS)
                    
                    img = ImageTk.PhotoImage(pil_img)
                    
                    lbl = tk.Label(parent, image=img, bg='#FAFAFA', bd=1, relief='solid')
                    lbl.pack(pady=5)
                    top.image_refs.append(img) # Keep ref
                except Exception as e:
                    tk.Label(parent, text=f"[Error loading image: {e}]", fg='red', bg='white').pack()
            else:
                tk.Label(parent, text="[Image not found]", fg='#999', bg='#EEE').pack(fill=tk.X, pady=5)

        # Header
        tk.Label(top, text=self.tr('zadig_guide_title'), font=FONTS['header'], bg='white', fg=COLORS['primary']).pack(pady=10)
        
        # Scrollable Frame for content
        canvas = tk.Canvas(top, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(top, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white', padx=20)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add Steps
        add_step(scrollable_frame, self.tr('zadig_step1'), "zadig_step_1.png")
        add_step(scrollable_frame, self.tr('zadig_step2'), "zadig_step_2.png")
        add_step(scrollable_frame, self.tr('zadig_step3'), "zadig_step_3.png")
        
        tk.Button(top, text="OK", command=top.destroy, bg=COLORS['primary'], fg='white', relief='flat', width=10).pack(pady=10, side=tk.BOTTOM)

    # --- Core Logic ---

    def log(self, msg, level="INFO"):
        try:
            self.log_text.configure(state='normal')
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"[{ts}] ", 'dim')
            self.log_text.insert(tk.END, f"{msg}\n", level)
            self.log_text.see(tk.END)
            self.log_text.configure(state='disabled')
        except: pass

    def browse_folder(self):
        folder = filedialog.askdirectory(title=self.tr('browse'))
        if folder:
            self.rom_folder = Path(folder)
            self.folder_var.set(str(self.rom_folder))
            self.scan_rom()

    def scan_rom(self):
        if not self.rom_folder: return
        self.log(f"Scanning: {self.rom_folder.name}", "INFO")
        
        # Reset UI
        self.partition_tree.delete(*self.partition_tree.get_children())
        self.region_list.delete(*self.region_list.get_children())
        self.selected_region_index = -1
        
        self.available_regions = find_all_super_defs(self.rom_folder)
        
        if self.available_regions:
            count = len(self.available_regions)
            self.log(f"Found {count} regions", "SUCCESS")
            
            # Populate Region List
            for i, r in enumerate(self.available_regions):
                self.region_list.insert('', tk.END, iid=str(i), values=(r.nv_text, r.nv_id))
            
            # Select first item by default
            self.region_list.selection_set('0')
            # Trigger selection manually
            self.load_region(self.available_regions[0])
            self.selected_region_index = 0
            
        else:
            self.log("No super_def.json found", "ERROR")
            self.start_btn.configure(state='disabled')

    def on_region_selected(self, event):
        selection = self.region_list.selection()
        if not selection: return
        
        idx = int(selection[0])
        if idx != self.selected_region_index:
            self.selected_region_index = idx
            self.load_region(self.available_regions[idx])

    def load_region(self, region: RegionInfo):
        self.selected_region = region
        self.log(f"Config loaded: {region.nv_text}", "INFO")
        
        self.super_config = parse_super_def(region.config_path)
        
        # Populate table
        self.partition_tree.delete(*self.partition_tree.get_children())
        for p in self.super_config.partitions:
            if not p.path: continue
            
            img_path = self.rom_folder / p.path
            status = "Missing ⚠️"
            if img_path.exists():
                status = "Ready" if not is_sparse_image(img_path) else "Sparse"
                
            self.partition_tree.insert('', tk.END, values=(
                p.name, 
                f"{p.size/1024/1024:.1f} MB", 
                p.group_name, 
                status
            ))
            
        self.start_btn.configure(state='normal', bg=COLORS['success'])
        self.start_btn.configure(text=self.tr('create_btn'))

        # Check existing output
        super_path = get_super_path(self.rom_folder)
        if super_path.exists():
            self.log("super.img exists (Will Overwrite)", "WARN")
            self.start_btn.configure(text=self.tr('recreate_btn'), bg='#FF9800')
        else:
            self.start_btn.configure(text=self.tr('create_btn'), bg=COLORS['success'])

    def run_zadig(self):
        zadig_path = resource_path("zadig-2.9.exe")
        if zadig_path.exists():
            try:
                # Use ShellExecute with "runas" to trigger UAC elevation
                ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", str(zadig_path), None, None, 1)
                if ret > 32: # > 32 indicates success
                    self.log("Launched Zadig 2.9 (Elevated)", "INFO")
                else:
                    self.log(f"Failed to launch Zadig (Code {ret})", "ERROR")
            except Exception as e:
                self.log(f"Failed to launch Zadig: {e}", "ERROR")
        else:
            self.log("zadig-2.9.exe not found!", "ERROR")
            messagebox.showerror("Error", "zadig-2.9.exe not found in application directory.")

    def install_driver(self, event=None):
        inf_path = resource_path("DriverKedacomUSB/android_winusb.inf")
        if not inf_path.exists():
            self.log("Driver file not found!", "ERROR")
            messagebox.showerror("Error", f"{inf_path} not found.")
            return

        self.log("Installing Kedacom Driver...", "INFO")
        try:
            cmd = ['pnputil', '/add-driver', str(inf_path), '/install']
            
            def _install():
                process = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                output = process.stdout + "\n" + process.stderr
                
                if "successfully" in output or "Already exists" in output:
                    self.root.after(0, lambda: self.log(self.tr('msg_driver_success'), "SUCCESS"))
                    self.root.after(0, lambda: messagebox.showinfo("Success", self.tr('msg_driver_success')))
                else:
                    self.root.after(0, lambda: self.log(f"Install Output: {output.strip()}", "WARN"))
                    if process.returncode != 0 and "successfully" not in output:
                         self.root.after(0, lambda: self.log(self.tr('msg_driver_fail'), "ERROR"))
            
            threading.Thread(target=_install, daemon=True).start()
            
        except Exception as e:
            self.log(f"Driver Error: {e}", "ERROR")

    def create_super(self):
        if not self.super_config: return
        if self.is_processing: return
        
        suffix = self.use_nv_suffix.get()
        if suffix:
            out = get_super_path(self.rom_folder, self.selected_region.nv_id)
        else:
            out = get_super_path(self.rom_folder)
            
        if out.exists():
            if not messagebox.askyesno("Overwrite?", self.tr('msg_overwrite')):
                return

        self.is_processing = True
        self.start_btn.configure(state='disabled', text=self.tr('processing'), bg='#9E9E9E')
        self.progress_var.set(0)
        
        threading.Thread(target=self._worker, args=(out,), daemon=True).start()

    def _worker(self, out_path):
        try:
            success = create_super_image(
                self.super_config, self.rom_folder, out_path,
                lambda msg: self.root.after(0, lambda: self.log(msg, "INFO")),
                lambda cur, tot: self.root.after(0, lambda: self._update_prog(cur, tot))
            )
            
            if success:
                self.root.after(0, lambda: self._finish(True, out_path))
            else:
                self.root.after(0, lambda: self._finish(False, None))
                
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Crash: {e}", "ERROR"))
            self.root.after(0, lambda: self._finish(False, None))

    def _update_prog(self, cur, tot):
        if tot > 0:
            pct = (cur/tot)*100
            self.progress_var.set(pct)
            self.status_var.set(f"Progress: {int(pct)}%")

    def _finish(self, success, path):
        self.is_processing = False
        self.start_btn.configure(state='normal')
        
        if success:
            self.log(self.tr('msg_success'), "SUCCESS")
            self.status_var.set(self.tr('status_done'))
            if path.name == "super.img":
                self.start_btn.configure(text=self.tr('recreate_btn'), bg='#FF9800')
            messagebox.showinfo("Success", f"File created:\n{path.name}")
        else:
            self.log(self.tr('msg_failed'), "ERROR")
            self.status_var.set(self.tr('status_failed'))
            self.start_btn.configure(text=self.tr('retry'), bg=COLORS['success'])

    # --- ZIP Extraction ---

    def extract_source_zip(self):
        if self.is_processing: return
        
        zip_path = filedialog.askopenfilename(
            title=self.tr('extract_btn'),
            filetypes=[("ZIP Files", "*.zip")]
        )
        if not zip_path: return
        
        out_root = filedialog.askdirectory(title=self.tr('browse'))
        if not out_root: return
        
        # Create subfolder based on zip name
        zip_name = Path(zip_path).stem
        final_out_dir = Path(out_root) / zip_name
        
        if not final_out_dir.exists():
            try:
                final_out_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                 messagebox.showerror("Error", f"Cannot create folder {final_out_dir}: {e}")
                 return

        # Start extraction
        self.is_processing = True
        self.start_btn.configure(state='disabled', text=self.tr('extracting'), bg='#9E9E9E')
        self.progress_var.set(0)
        self.log(f"Extracting: {Path(zip_path).name} -> {final_out_dir.name}", "INFO")
        
        threading.Thread(target=self._extract_worker, args=(zip_path, final_out_dir), daemon=True).start()

    def _extract_worker(self, zip_path, out_dir):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                infos = zf.infolist()
                total = sum(1 for x in infos if not x.is_dir())
                current = 0
                
                for info in infos:
                    if info.is_dir(): continue
                    zf.extract(info, out_dir)
                    current += 1
                    # Update every 5 files to reduce UI lag per file
                    if current % 5 == 0 or current == total:
                         self.root.after(0, lambda c=current, t=total: self._extract_prog(c, t))
            
            self.root.after(0, lambda: self._extract_finish(True, out_dir))
            
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Extraction Error: {e}", "ERROR"))
            self.root.after(0, lambda: self._extract_finish(False, None))

    def _extract_prog(self, cur, tot):
        if tot > 0:
            pct = (cur/tot)*100
            self.progress_var.set(pct)
            self.status_var.set(f"Extracting: {int(pct)}%")

    def _extract_finish(self, success, out_dir):
        self.is_processing = False
        self.start_btn.configure(state='normal')
        self.progress_var.set(0)
        self.status_var.set(self.tr('status_done') if success else self.tr('status_failed'))
        
        if success and out_dir:
            self.log("Extraction Complete", "SUCCESS")
            # Auto-load
            self.rom_folder = Path(out_dir)
            self.folder_var.set(str(self.rom_folder))
            self.scan_rom()
        else:
            self.log("Extraction Failed", "ERROR")
            self.start_btn.configure(text=self.tr('create_btn'), bg=COLORS['success'])

def main():
    root = tk.Tk()
    app = RomConverterApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
