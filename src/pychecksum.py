# The MIT License (MIT)
#
# Copyright (c) 2018 Bryan San Juan Tavera
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from app_image import image_code, paypal_code
from app_license import license_msg
from app_donate import donate_msg
from tkinter import filedialog
from threading import Thread
from subprocess import Popen
from tkinter import ttk
import webbrowser as wb
import winsound as ws
import tkinter as tk
import platform
import hashlib
import time
import os


class AddTooltip(object):

    def __init__(self, widget, text):
        """
        Initialize tooltip class
        """
        self.widget = widget
        self.text = text
        self.time = None
        self.block = False
        self.display = False
        self._set_styles()
        self._set_formats()
        self._create_styles()
        self._create_tooltip()
        self._add_tooltip()

    def loc_inside_widget(self, loc_left, loc_top):
        """
        Verify if location is inside widget
        """
        widget_left = self.widget.winfo_rootx()
        widget_top = self.widget.winfo_rooty()
        widget_width = self.widget.winfo_width()
        widget_height = self.widget.winfo_height()
        is_inside = False
        if widget_left < loc_left < (widget_left + widget_width):
            if widget_top < loc_top < (widget_top + widget_height):
                is_inside = True
        return is_inside

    def _set_styles(self):
        """
        Setting frame and text styles
        """
        self.frame_style = 'Gray.TFrame'
        self.text_style = 'Gray.TLabel'

    def _set_formats(self):
        """
        Setting special formats
        """
        self.geometry_fmt = '+{left}+{top}'

    def _create_styles(self):
        """
        Create frame and text styles
        """
        self.styles = ttk.Style()
        self.styles.configure(style=self.frame_style, background='dim gray')
        self.styles.configure(style=self.text_style, foreground='dim gray', background='white')

    def _create_tooltip(self):
        """
        Create tooltip window
        """
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.withdraw()
        self.tooltip.overrideredirect(True)
        self.frame = ttk.Frame(self.tooltip)
        self.label = ttk.Label(self.frame, text=self.text)
        self.frame.configure(style=self.frame_style, padding=1)
        self.label.configure(style=self.text_style, padding=(2, 0))
        self.frame.pack()
        self.label.pack()

    def _add_tooltip(self):
        """
        Add tooltip to widget
        """
        self.widget.bind('<Enter>', func=self.enter_event)
        self.widget.bind('<Leave>', func=self.leave_event)
        self.widget.bind('<Button-1>', func=self.leave_event)

    def enter_event(self, event):
        """
        Display tooltip after 500 ms when event is fired
        """
        self.time = time.time()
        self.block = False
        self.display = False
        self.widget.after(500, self.display_tooltip)

    def leave_event(self, event):
        """
        Hide tooltip after 0 ms when event is fired
        """
        self.block = True
        self.widget.after(0, self.hide_tooltip)

    def display_tooltip(self):
        """
        Display tooltip window
        """
        if not self.block:
            cursor_left = self.widget.winfo_pointerx()
            cursor_top = self.widget.winfo_pointery()
            is_inside = self.loc_inside_widget(cursor_left, cursor_top)
            if is_inside:
                self.display = True
                kwargs = {'left': cursor_left, 'top': cursor_top + 18}
                self.tooltip.geometry(self.geometry_fmt.format(**kwargs))
                self.tooltip.deiconify()
                self.widget.after(5000, lambda: self.hide_tooltip(5.5))

    def hide_tooltip(self, sec=0.0):
        """
        Hide tooltip window
        """
        if (time.time() - self.time) > sec:
            if self.display:
                self.display = False
                self.tooltip.withdraw()


class AddMoveControl(object):

    def __init__(self, master, buttons, move='horizontal'):
        """
        Initialize movement control class
        """
        self.master = master
        self.buttons = buttons
        self.move = move.lower()
        self.active_button = None
        self._gen_button_dict()
        self._add_move_control()

    def _gen_button_dict(self):
        """
        Generate button dictionary structure
        """
        self.button_dict = {}
        self.button_num = 0
        for button in self.buttons:
            self.button_num += 1
            self.button_dict[self.button_num] = button

    def _add_move_control(self):
        """
        Add movement control to buttons
        """
        direct_dict = {'horizontal': {'left': -1, 'right': 1, 'up': 0, 'down': 0},
                       'vertical': {'left': 0, 'right': 0, 'up': -1, 'down': 1}}
        if self.move.count('v'):
            self.move = 'vertical'
        else:
            self.move = 'horizontal'
        self.direct = direct_dict[self.move]
        self.master.bind('<Left>', func=self.select_button)
        self.master.bind('<Right>', func=self.select_button)
        self.master.bind('<Up>', func=self.select_button)
        self.master.bind('<Down>', func=self.select_button)
        self.master.bind('<Button-1>', func=self.deselect_button)
        self.master.bind('<Button-2>', func=self.deselect_button)
        self.master.bind('<Button-3>', func=self.deselect_button)
        self.master.bind('<Escape>', func=self.deselect_button)

    def select_button(self, event):
        """
        Change button selection when event is fired
        """
        self.deselect_button(event)
        if self.active_button is None:
            self.active_button = 1
        else:
            key = event.keysym.lower()
            self.active_button += self.direct[key]
            if self.active_button < 1:
                self.active_button = self.button_num
            elif self.active_button > self.button_num:
                self.active_button = 1
        self.button_dict[self.active_button].configure(state='active')
        self.master.bind('<Return>', func=self.press_button)

    def deselect_button(self, event):
        """
        Release button selection when event is fired
        """
        if self.active_button is not None:
            self.button_dict[self.active_button].configure(state='normal')
            self.master.unbind('<Return>')
            key = event.keysym.lower()
            if key not in self.direct:
                self.active_button = None

    def press_button(self, event):
        """
        Invoke selected button when event is fired
        """
        if self.active_button is not None:
            active_button = self.active_button
            self.deselect_button(event)
            self.button_dict[active_button].invoke()


class MainApp(object):

    def __init__(self, master=None, *args, **kwargs):
        """
        Initialize main application
        """
        self.master = master
        if master is None:
            self.window = self.open_window(MainWin, top_level=False, display=True)
            self.window.master.mainloop()

    def open_window(self, win_class, top_level=True, *args, **kwargs):
        """
        Open a tkinter window by using a window class
        """
        if top_level:
            root = tk.Toplevel(self.master)
        else:
            root = tk.Tk()
        return win_class(master=root, *args, **kwargs)

    def close_window(self, window=None):
        """
        Close a tkinter window
        """
        if window is None:
            window = self
        window.master.withdraw()
        window.master.after(0, window.master.destroy)

    def display_window(self, window=None):
        """
        Display a tkinter window
        """
        if window is None:
            window = self
        window.master.deiconify()
        window.master.update()
        window.master.focus()

    def hide_window(self, window=None):
        """
        Hide a tkinter window
        """
        if window is None:
            window = self
        window.master.withdraw()


class MainWin(MainApp):

    def __init__(self, master=None, display=False, *args, **kwargs):
        """
        Initialize main window
        """
        if master is None:
            master = tk.Tk()
        super().__init__(master)
        self.hide_window()
        self._set_info()
        self._set_dicts()
        self._set_tooltips()
        self._set_styles()
        self._set_formats()
        self._set_texts()
        self._create_styles()
        self._create_menus()
        self._create_frames()
        self._create_labels()
        self._create_buttons()
        self._center_window()
        self._config_window()
        if display:
            self.display_window()

    def _set_info(self):
        """
        Setting application information
        """
        self.app_author = 'Bryan San Juan Tavera'
        self.app_year = '2018'
        self.app_name = 'PyChecksum'
        self.app_ver = '1.0'
        self.app_title = ' '.join([self.app_name, self.app_ver])
        self.app_phrase = 'The Python Checksum Program'
        self.app_wiki_info = 'https://en.wikipedia.org/wiki/File_verification'
        self.app_tutorial = 'https://www.youtube.com/channel/UCH6Fdvj08buQTV1dj-lJTQw'
        self.app_website = 'https://github.com/pychecksum'
        self.app_paypal = 'https://www.paypal.me/pychecksum'
        self.app_email = 'pychecksum@gmail.com'
        self.app_fma = 'https://en.wikipedia.org/wiki/Fullmetal_Alchemist:_Brotherhood'
        self.app_image = tk.PhotoImage(master=self.master, data=image_code)
        self.app_license = license_msg.format(year=self.app_year, author=self.app_author)
        self.app_donate = donate_msg.format(name=self.app_name)
        self.app_ini_dir = os.path.expanduser('~\Desktop')

    def _set_dicts(self):
        """
        Setting option, algorithm, and color dictionaries
        """
        self.opt_dict = {1: 'Hash Calculation', 2: 'Hash Table Generation', 3: 'Hash Table Verification'}
        self.alg_dict = {1: 'md5', 2: 'sha1', 3: 'sha224', 4: 'sha256', 5: 'sha384', 6: 'sha512'}
        self.color_dict = {0: '#000000', 1: '#0000ff', 2: '#009900', 3: '#ff0000'}

    def _set_tooltips(self):
        """
        Setting option and algorithm tooltips
        """
        self.opt_tooltip = {1: "Calculate the hash of a file",
                            2: "Generate the hash table of a directory",
                            3: "Verify the hash table of a directory"}
        self.alg_tooltip = {1: "Use Message Digest Algorithm 5",
                            2: "Use Secure Hash Algorithm 1",
                            3: "Use Secure Hash Algorithm 224",
                            4: "Use Secure Hash Algorithm 256",
                            5: "Use Secure Hash Algorithm 384",
                            6: "Use Secure Hash Algorithm 512"}

    def _set_styles(self):
        """
        Setting text and button styles
        """
        self.text_style = {0: 'Black.TLabel', 1: 'Blue.TLabel', 2: 'Green.TLabel', 3: 'Red.TLabel'}
        self.button_style = {0: 'Black.TButton', 1: 'Blue.TButton', 2: 'Green.TButton', 3: 'Red.TButton'}

    def _set_formats(self):
        """
        Setting special formats
        """
        self.copyright_fmt = 'Copyright © {year}{sep}{author}'
        self.geometry_fmt = '{width}x{height}+{left}+{top}'
        self.open_fmt = 'explorer /select,"{path}"'
        self.action_fmt = '{action}... {path}'
        self.icon_fmt = '::tk::icons::{type}'
        self.title_fmt = '{main} ({add})'
        self.info_fmt = '{info}: {data}'
        self.hash_fmt = '{hash} *{path}\n'
        self.err_fmt = '{err} *{path}\n'
        self.sep_fmt = '-' * 120

    def _set_texts(self):
        """
        Setting window texts
        """
        self.win_title = "Welcome!"
        self.win_msg = "Please enter the option you want to use."

    def _create_styles(self):
        """
        Create text and button styles
        """
        self.styles = ttk.Style()
        for key in self.color_dict:
            self.styles.configure(self.text_style[key], foreground=self.color_dict[key])
            self.styles.configure(self.button_style[key], foreground=self.color_dict[key])

    def _create_menus(self):
        """
        Create file, help, and extra menus
        """
        self.menu_bar = tk.Menu(self.master)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.help_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.extra_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.file_menu.configure(activeforeground='black', activebackground='light blue')
        self.help_menu.configure(activeforeground='black', activebackground='light blue')
        self.extra_menu.configure(activeforeground='black', activebackground='light blue')
        self.menu_bar.add_cascade(label='File', underline=0, menu=self.file_menu)
        self.menu_bar.add_cascade(label='Help', underline=0, menu=self.help_menu)
        self.menu_bar.add_cascade(label='Extra', underline=0, menu=self.extra_menu)
        self.file_menu.add_command(label='Exit', underline=1, command=self.close_window)
        self.help_menu.add_command(label='Wiki Info', underline=2, command=lambda: wb.open(self.app_wiki_info))
        self.help_menu.add_command(label='Tutorial', underline=0, command=lambda: wb.open(self.app_tutorial))
        self.help_menu.add_command(label='Website', underline=0, command=lambda: wb.open(self.app_website))
        self.help_menu.add_command(label='About', underline=0, command=lambda: self.open_window(AboutWin))
        self.extra_menu.add_command(label='Fullmetal Alchemist', underline=0, command=lambda: wb.open(self.app_fma))
        self.master.configure(menu=self.menu_bar)

    def _create_frames(self):
        """
        Create upper and lower frames
        """
        self.upper_frame = ttk.Frame(self.master)
        self.lower_frame = ttk.Frame(self.master)
        self.upper_frame.pack(fill='both', expand='yes')
        self.lower_frame.pack(fill='both', expand='yes')

    def _create_labels(self):
        """
        Create title and message labels
        """
        self.win_text = '\n'.join([self.win_title, self.win_msg])
        self.label = ttk.Label(self.upper_frame, text=self.win_text)
        self.label.configure(padding=10, justify='center')
        self.label.pack(expand='yes')

    def _create_buttons(self):
        """
        Create option buttons
        """
        self.button1 = ttk.Button(self.lower_frame, text=self.opt_dict[1])
        self.button2 = ttk.Button(self.lower_frame, text=self.opt_dict[2])
        self.button3 = ttk.Button(self.lower_frame, text=self.opt_dict[3])
        self.button1.configure(style=self.button_style[1], padding=(15, 10), takefocus=False)
        self.button2.configure(style=self.button_style[2], padding=(15, 10), takefocus=False)
        self.button3.configure(style=self.button_style[3], padding=(15, 10), takefocus=False)
        self.button1['command'] = lambda: self.open_window(AlgWin, main_win=self, opt_num=1, display=True)
        self.button2['command'] = lambda: self.open_window(AlgWin, main_win=self, opt_num=2, display=True)
        self.button3['command'] = lambda: self.open_window(AlgWin, main_win=self, opt_num=3, display=False)
        self.button1.pack(side='left', fill='both', expand='yes', padx=(10, 2), pady=(0, 10))
        self.button2.pack(side='left', fill='both', expand='yes', padx=(2, 2), pady=(0, 10))
        self.button3.pack(side='left', fill='both', expand='yes', padx=(2, 10), pady=(0, 10))
        AddTooltip(widget=self.button1, text=self.opt_tooltip[1])
        AddTooltip(widget=self.button2, text=self.opt_tooltip[2])
        AddTooltip(widget=self.button3, text=self.opt_tooltip[3])
        self.buttons = [self.button1, self.button2, self.button3]
        AddMoveControl(master=self.master, buttons=self.buttons)

    def _center_window(self):
        """
        Center main window
        """
        self.master.update()
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()
        self.win_width = self.master.winfo_reqwidth()
        self.win_height = self.master.winfo_reqheight()
        self.menu_bar_height = 10
        self.task_bar_height = 40
        system, version = platform.platform().split('-')[:2]
        if (system == 'Windows') and (version < '8'):
            if self.__class__ == ProcWin:
                self.win_width += 86
                self.win_height += 8
            elif self.__class__ == LicenseWin:
                self.win_width += 60
            self.menu_bar_height = 12
        self.win_left = (self.screen_width // 2) - (self.win_width // 2)
        self.win_top = (self.screen_height // 2) - (self.win_height // 2)
        if not hasattr(self, 'menu_bar'):
            self.win_top += self.menu_bar_height
        self.win_top -= self.task_bar_height
        kwargs = {'width': self.win_width, 'height': self.win_height,
                  'left': self.win_left, 'top': self.win_top}
        self.master.geometry(self.geometry_fmt.format(**kwargs))

    def _config_window(self):
        """
        Configure main window
        """
        self.master.title(self.app_name)
        self.master.iconphoto(True, self.app_image)
        self.master.protocol('WM_DELETE_WINDOW', func=self.close_window)
        self.master.minsize(self.win_width, self.win_height)
        self.master.resizable(width=False, height=False)


class AlgWin(MainWin):

    def __init__(self, master=None, main_win=None, opt_num=None, *args, **kwargs):
        """
        Initialize algorithm window
        """
        if main_win is None:
            main_win = MainWin()
        if opt_num is None:
            opt_num = 1
        self.main_win = main_win
        self.opt_num = opt_num
        self.app_ini_dir = None
        super().__init__(master, *args, **kwargs)
        if master is not None:
            if opt_num == 3:
                self.select_path(opt_num)

    def select_path(self, opt_num, alg=None):
        """
        Select a file or directory path to process
        """
        func_dict = {1: [filedialog.askopenfilename, "Select a file"],
                     2: [filedialog.askdirectory, "Select a directory"],
                     3: [filedialog.askopenfilename, "Select a hash table file"]}
        func, msg = func_dict[opt_num]
        if opt_num == 3:
            ini_dir = self.main_win.app_ini_dir
            title = self.opt_dict[opt_num]
            name = 'Hash table files'
            exts = ';'.join([''.join(['*.', value]) for value in self.alg_dict.values()])
        else:
            ini_dir = self.app_ini_dir
            title = self.title_fmt.format(main=self.opt_dict[opt_num], add=alg.upper())
            name = 'All files'
            exts = '*.*'
        ask_root = tk.Toplevel(self.master)
        ask_root.withdraw()
        title = ' ➜ '.join([title, msg])
        types = [(name, exts)]
        if opt_num == 2:
            path = func(parent=ask_root, initialdir=ini_dir, title=title)
        else:
            path = func(parent=ask_root, initialdir=ini_dir, title=title, filetypes=types)
        try:
            ask_root.destroy()
            if not path:
                if opt_num == 3:
                    self.close_window()
            else:
                new_dir = os.path.dirname(path)
                if opt_num == 3:
                    self.main_win.app_ini_dir = new_dir
                    alg = os.path.splitext(path)[1][1:]
                else:
                    self.app_ini_dir = new_dir
                alg = alg.lower()
                path = os.path.abspath(path)
                kwargs = {'alg_win': self, 'opt_num': opt_num, 'alg': alg, 'path': path}
                self.master.after(0, lambda: self.open_window(ProcWin, **kwargs))
        except tk.TclError:
            pass

    def _set_texts(self):
        """
        Setting window texts
        """
        self.win_title = self.opt_dict[self.opt_num]
        self.win_msg = "Please enter the algorithm you want to use."

    def _create_buttons(self):
        """
        Create algorithm buttons
        """
        self.buttons = []
        self.lower_frame.configure(padding=(10, 0))
        stmt_a = "self.button{num} = ttk.Button(self.lower_frame, text='{text}', width=(len('{text}') + 2))"
        stmt_b = "self.button{num}.configure(style='{style}', padding=(11, 3), takefocus=False)"
        stmt_c = "self.button{num}['command'] = lambda self=self: self.select_path({opt_num}, '{alg}')"
        stmt_d = "self.button{num}.pack(side='left', fill='both', expand='yes', pady=(0, 10))"
        stmt_e = "AddTooltip(widget=self.button{num}, text=self.alg_tooltip[{num}])"
        stmt_f = "self.buttons.append(self.button{num})"
        for key, value in self.alg_dict.items():
            exec(stmt_a.format(num=key, text=value.upper()))
            exec(stmt_b.format(num=key, style=self.button_style[self.opt_num]))
            exec(stmt_c.format(num=key, opt_num=self.opt_num, alg=value))
            exec(stmt_d.format(num=key))
            exec(stmt_e.format(num=key))
            exec(stmt_f.format(num=key))
        AddMoveControl(master=self.master, buttons=self.buttons)


class ProcWin(MainWin):

    def __init__(self, master=None, alg_win=None, opt_num=None, alg=None, path=None, *args, **kwargs):
        """
        Initialize process window
        """
        if alg_win is None:
            alg_win = AlgWin()
        if opt_num is None:
            opt_num = alg_win.opt_num
        if alg is None:
            alg = alg_win.alg_dict[1]
        if path is None:
            path = ''
        self.alg_win = alg_win
        self.opt_num = opt_num
        self.alg = alg
        self.path = path
        super().__init__(master, *args, **kwargs)
        self._create_progress_bar()
        self._center_window()
        if master is not None:
            self.run_process(opt_num, alg, path, display=True)

    def _create_progress_bar(self):
        """
        Create progress bar
        """
        self.label.configure(padding=16)
        self.prog_bar = ttk.Progressbar(self.lower_frame, length=422)
        self.prog_bar.pack(fill='both', expand='yes', padx=10, pady=(0, 10))

    def run_process(self, opt_num, alg, path, display=False):
        """
        Run application process
        """
        func_dict = {1: self.calc_hash, 2: self.gen_hash, 3: self.verif_hash}
        func = func_dict[opt_num]
        args = (alg, path, display)
        proc = Thread(target=func, args=args)
        proc.start()

    def calc_hash(self, alg, file_path, display=False):
        """
        Calculate the hash of a file
        """
        block_size = 2 ** 16
        file_size = os.path.getsize(file_path)
        total_num = int(file_size / block_size) + 1
        stmt = 'hashlib.{method}()'
        hasher = eval(stmt.format(method=alg))
        if not display:
            try:
                with open(file_path, mode='rb') as file:
                    for i in range(total_num):
                        buffer = file.read(block_size)
                        hasher.update(buffer)
                file_hash = hasher.hexdigest()
                return file_hash
            except PermissionError as perm_err:
                return perm_err
        else:
            try:
                self.display_window()
                with open(file_path, mode='rb') as file:
                    for i in range(total_num):
                        chunk_num = i + 1
                        buffer = file.read(block_size)
                        hasher.update(buffer)
                        progress = (chunk_num / total_num) * 100
                        self.prog_bar['value'] = progress
                        self.master.update()
                file_hash = hasher.hexdigest()
                self.hide_window()
                calc_msg = '\n\n'.join([self.win_title, file_path, file_hash])
                kwargs = {'proc_win': self, 'alg_win': self.alg_win,
                          'win_type': 1, 'win_text': calc_msg}
                self.master.after(0, lambda: self.open_window(MsgWin, **kwargs))
            except PermissionError as perm_err:
                self.hide_window()
                file_path = os.path.abspath(perm_err.filename)
                calc_msg = '\n\n'.join([self.win_title, self.perm_msg, file_path])
                kwargs = {'proc_win': self, 'alg_win': self.alg_win,
                          'win_type': 2, 'win_text': calc_msg}
                self.master.after(0, lambda: self.open_window(MsgWin, **kwargs))
            except (tk.TclError, RuntimeError):
                pass

    def gen_hash(self, alg, dir_path, display=False):
        """
        Generate the hash table of a directory
        """
        dir_name = os.path.basename(dir_path)
        hash_name = '.'.join([dir_name, alg])
        hash_path = os.path.join(dir_path, hash_name)
        err_path = '.'.join([hash_path, 'err'])
        path_dict = {}
        hash_lines = []
        err_lines = []
        if not display:
            try:
                for path, dirs, files in os.walk(dir_path):
                    for file in files:
                        file_path = os.path.join(path, file)
                        base_path = os.path.dirname(file_path)
                        if base_path != dir_path:
                            path_dict[file_path] = None
                        else:
                            file_ext = os.path.splitext(file_path)[1][1:].lower()
                            if file_ext not in self.alg_dict.values():
                                if file_ext != 'err':
                                    path_dict[file_path] = None
                                else:
                                    temp_path = os.path.splitext(file_path)[0]
                                    file_ext = os.path.splitext(temp_path)[1][1:].lower()
                                    if file_ext not in self.alg_dict.values():
                                        path_dict[file_path] = None
                for key in path_dict:
                    file_path = key
                    rel_path = os.path.relpath(file_path, start=dir_path)
                    file_hash = self.calc_hash(alg, file_path)
                    if type(file_hash) == str:
                        hash_line = self.hash_fmt.format(hash=file_hash, path=rel_path)
                        hash_lines.append(hash_line)
                    elif type(file_hash) == PermissionError:
                        err_line = self.err_fmt.format(err='Permission ', path=rel_path)
                        err_lines.append(err_line)
                    else:
                        err_line = self.err_fmt.format(err='Unknown    ', path=rel_path)
                        err_lines.append(err_line)
                if err_lines:
                    with open(err_path, mode='w', encoding='utf-8') as err_file:
                        time_info = self.info_fmt.format(info='Generated', data=time.ctime())
                        num_info = self.info_fmt.format(info='Number of Errors', data=len(err_lines))
                        err_title = 'Error Type'
                        header_lines = [self.app_title, self.app_website, self.sep_fmt, time_info,
                                        num_info, self.sep_fmt, err_title, self.sep_fmt, '']
                        header_lines = '\n'.join(header_lines)
                        err_file.write(header_lines)
                        err_file.writelines(err_lines)
                    if os.path.isfile(hash_path):
                        os.remove(hash_path)
                    return err_lines
                elif hash_lines:
                    with open(hash_path, mode='w', encoding='utf-8') as hash_file:
                        time_info = self.info_fmt.format(info='Generated', data=time.ctime())
                        num_info = self.info_fmt.format(info='Number of Hashes', data=len(hash_lines))
                        alg_title = self.title_fmt.format(main='Hash Algorithm', add=alg.upper())
                        header_lines = [self.app_title, self.app_website, self.sep_fmt, time_info,
                                        num_info, self.sep_fmt, alg_title, self.sep_fmt, '']
                        header_lines = '\n'.join(header_lines)
                        hash_file.write(header_lines)
                        hash_file.writelines(hash_lines)
                    if os.path.isfile(err_path):
                        os.remove(err_path)
                    return hash_lines
                else:
                    return None
            except PermissionError as perm_err:
                return perm_err
        else:
            try:
                self.prog_bar.configure(mode='indeterminate')
                kwargs = {'action': 'Reading', 'path': dir_path}
                win_text = self.modif_text.format(**kwargs)
                self.label.configure(text=win_text)
                self.display_window()
                self.prog_bar.start(15)
                for path, dirs, files in os.walk(dir_path):
                    for file in files:
                        file_path = os.path.join(path, file)
                        base_path = os.path.dirname(file_path)
                        if base_path != dir_path:
                            path_dict[file_path] = None
                        else:
                            file_ext = os.path.splitext(file_path)[1][1:].lower()
                            if file_ext not in self.alg_dict.values():
                                if file_ext != 'err':
                                    path_dict[file_path] = None
                                else:
                                    temp_path = os.path.splitext(file_path)[0]
                                    file_ext = os.path.splitext(temp_path)[1][1:].lower()
                                    if file_ext not in self.alg_dict.values():
                                        path_dict[file_path] = None
                self.prog_bar.stop()
                self.prog_bar.configure(mode='determinate')
                kwargs = {'action': 'Processing', 'path': dir_path}
                win_text = self.win_text.format(**kwargs)
                self.label.configure(text=win_text)
                total_num = len(path_dict)
                file_num = 0
                for key in path_dict:
                    file_num += 1
                    file_path = key
                    rel_path = os.path.relpath(file_path, start=dir_path)
                    file_hash = self.calc_hash(alg, file_path)
                    if type(file_hash) == str:
                        hash_line = self.hash_fmt.format(hash=file_hash, path=rel_path)
                        hash_lines.append(hash_line)
                    elif type(file_hash) == PermissionError:
                        err_line = self.err_fmt.format(err='Permission ', path=rel_path)
                        err_lines.append(err_line)
                    else:
                        err_line = self.err_fmt.format(err='Unknown    ', path=rel_path)
                        err_lines.append(err_line)
                    progress = (file_num / total_num) * 100
                    self.prog_bar['value'] = progress
                    self.master.update()
                if err_lines:
                    with open(err_path, mode='w', encoding='utf-8') as err_file:
                        time_info = self.info_fmt.format(info='Generated', data=time.ctime())
                        num_info = self.info_fmt.format(info='Number of Errors', data=len(err_lines))
                        err_title = 'Error Type'
                        header_lines = [self.app_title, self.app_website, self.sep_fmt, time_info,
                                        num_info, self.sep_fmt, err_title, self.sep_fmt, '']
                        header_lines = '\n'.join(header_lines)
                        err_file.write(header_lines)
                        err_file.writelines(err_lines)
                    if os.path.isfile(hash_path):
                        os.remove(hash_path)
                    self.hide_window()
                    gen_msg = '\n\n'.join([self.win_title, self.err_msg, err_path])
                    kwargs = {'proc_win': self, 'alg_win': self.alg_win,
                              'win_type': 2, 'win_text': gen_msg}
                    self.master.after(0, lambda: self.open_window(MsgWin, **kwargs))
                elif hash_lines:
                    with open(hash_path, mode='w', encoding='utf-8') as hash_file:
                        time_info = self.info_fmt.format(info='Generated', data=time.ctime())
                        num_info = self.info_fmt.format(info='Number of Hashes', data=len(hash_lines))
                        alg_title = self.title_fmt.format(main='Hash Algorithm', add=alg.upper())
                        header_lines = [self.app_title, self.app_website, self.sep_fmt, time_info,
                                        num_info, self.sep_fmt, alg_title, self.sep_fmt, '']
                        header_lines = '\n'.join(header_lines)
                        hash_file.write(header_lines)
                        hash_file.writelines(hash_lines)
                    if os.path.isfile(err_path):
                        os.remove(err_path)
                    self.hide_window()
                    gen_msg = '\n\n'.join([self.win_title, self.ok_msg, hash_path])
                    kwargs = {'proc_win': self, 'alg_win': self.alg_win,
                              'win_type': 1, 'win_text': gen_msg}
                    self.master.after(0, lambda: self.open_window(MsgWin, **kwargs))
                else:
                    self.hide_window()
                    gen_msg = '\n\n'.join([self.win_title, self.empty_msg, dir_path])
                    kwargs = {'proc_win': self, 'alg_win': self.alg_win,
                              'win_type': 2, 'win_text': gen_msg}
                    self.master.after(0, lambda: self.open_window(MsgWin, **kwargs))
            except PermissionError as perm_err:
                self.hide_window()
                file_path = os.path.abspath(perm_err.filename)
                gen_msg = '\n\n'.join([self.win_title, self.perm_msg, file_path])
                kwargs = {'proc_win': self, 'alg_win': self.alg_win,
                          'win_type': 2, 'win_text': gen_msg}
                self.master.after(0, lambda: self.open_window(MsgWin, **kwargs))
            except (tk.TclError, RuntimeError):
                pass

    def verif_hash(self, alg, hash_path, display=False):
        """
        Verify the hash table of a directory
        """
        dir_path = os.path.dirname(hash_path)
        err_path = '.'.join([hash_path, 'err'])
        path_dict = {}
        hash_dict = {}
        skip_dict = {}
        err_lines = []
        if not display:
            try:
                for path, dirs, files in os.walk(dir_path):
                    for file in files:
                        file_path = os.path.join(path, file)
                        base_path = os.path.dirname(file_path)
                        if base_path != dir_path:
                            path_dict[file_path] = None
                        else:
                            file_ext = os.path.splitext(file_path)[1][1:].lower()
                            if file_ext in self.alg_dict.values():
                                skip_dict[file_path] = None
                            else:
                                if file_ext != 'err':
                                    path_dict[file_path] = None
                                else:
                                    temp_path = os.path.splitext(file_path)[0]
                                    file_ext = os.path.splitext(temp_path)[1][1:].lower()
                                    if file_ext in self.alg_dict.values():
                                        skip_dict[file_path] = None
                                    else:
                                        path_dict[file_path] = None
                with open(hash_path, mode='r', encoding='utf-8') as hash_file:
                    for line in hash_file:
                        if line.count('*'):
                            file_hash, rel_path = map(str.strip, line.split('*')[:2])
                            file_hash = file_hash.lower()
                            file_path = os.path.join(dir_path, rel_path)
                            file_path = os.path.abspath(file_path)
                            base_path = os.path.dirname(file_path)
                            if base_path == dir_path:
                                file_ext = os.path.splitext(file_path)[1][1:].lower()
                                if file_ext in self.alg_dict.values():
                                    skip_dict[file_path] = None
                                else:
                                    if file_ext == 'err':
                                        temp_path = os.path.splitext(file_path)[0]
                                        file_ext = os.path.splitext(temp_path)[1][1:].lower()
                                        if file_ext in self.alg_dict.values():
                                            skip_dict[file_path] = None
                            if file_path not in hash_dict:
                                hash_dict[file_path] = file_hash
                            else:
                                err_line = self.err_fmt.format(err='Duplicated ', path=rel_path)
                                if err_line not in err_lines:
                                    err_lines.append(err_line)
                            if file_path in skip_dict:
                                err_line = self.err_fmt.format(err='Not skipped', path=rel_path)
                                if err_line not in err_lines:
                                    err_lines.append(err_line)
                            if not os.path.isfile(file_path):
                                err_line = self.err_fmt.format(err='Not found  ', path=rel_path)
                                if err_line not in err_lines:
                                    err_lines.append(err_line)
                for key in path_dict:
                    file_path = key
                    rel_path = os.path.relpath(file_path, start=dir_path)
                    if file_path not in hash_dict:
                        err_line = self.err_fmt.format(err='Not listed ', path=rel_path)
                        err_lines.append(err_line)
                    else:
                        old_hash = hash_dict[file_path]
                        new_hash = self.calc_hash(alg, file_path)
                        if type(new_hash) == str:
                            if new_hash != old_hash:
                                err_line = self.err_fmt.format(err='Not match  ', path=rel_path)
                                err_lines.append(err_line)
                        elif type(new_hash) == PermissionError:
                            err_line = self.err_fmt.format(err='Permission ', path=rel_path)
                            err_lines.append(err_line)
                        else:
                            err_line = self.err_fmt.format(err='Unknown    ', path=rel_path)
                            err_lines.append(err_line)
                if err_lines:
                    with open(err_path, mode='w', encoding='utf-8') as err_file:
                        time_info = self.info_fmt.format(info='Generated', data=time.ctime())
                        num_info = self.info_fmt.format(info='Number of Errors', data=len(err_lines))
                        err_title = 'Error Type'
                        header_lines = [self.app_title, self.app_website, self.sep_fmt, time_info,
                                        num_info, self.sep_fmt, err_title, self.sep_fmt, '']
                        header_lines = '\n'.join(header_lines)
                        err_file.write(header_lines)
                        err_file.writelines(err_lines)
                    return err_lines
                else:
                    if os.path.isfile(err_path):
                        os.remove(err_path)
                    return None
            except PermissionError as perm_err:
                return perm_err
            except UnicodeDecodeError as code_err:
                return code_err
        else:
            try:
                self.prog_bar.configure(mode='indeterminate')
                kwargs = {'action': 'Reading', 'path': dir_path}
                win_text = self.modif_text.format(**kwargs)
                self.label.configure(text=win_text)
                self.display_window()
                self.prog_bar.start(15)
                for path, dirs, files in os.walk(dir_path):
                    for file in files:
                        file_path = os.path.join(path, file)
                        base_path = os.path.dirname(file_path)
                        if base_path != dir_path:
                            path_dict[file_path] = None
                        else:
                            file_ext = os.path.splitext(file_path)[1][1:].lower()
                            if file_ext in self.alg_dict.values():
                                skip_dict[file_path] = None
                            else:
                                if file_ext != 'err':
                                    path_dict[file_path] = None
                                else:
                                    temp_path = os.path.splitext(file_path)[0]
                                    file_ext = os.path.splitext(temp_path)[1][1:].lower()
                                    if file_ext in self.alg_dict.values():
                                        skip_dict[file_path] = None
                                    else:
                                        path_dict[file_path] = None
                self.prog_bar.stop()
                kwargs = {'action': 'Reading', 'path': hash_path}
                win_text = self.win_text.format(**kwargs)
                self.label.configure(text=win_text)
                self.prog_bar.start(15)
                with open(hash_path, mode='r', encoding='utf-8') as hash_file:
                    for line in hash_file:
                        if line.count('*'):
                            file_hash, rel_path = map(str.strip, line.split('*')[:2])
                            file_hash = file_hash.lower()
                            file_path = os.path.join(dir_path, rel_path)
                            file_path = os.path.abspath(file_path)
                            base_path = os.path.dirname(file_path)
                            if base_path == dir_path:
                                file_ext = os.path.splitext(file_path)[1][1:].lower()
                                if file_ext in self.alg_dict.values():
                                    skip_dict[file_path] = None
                                else:
                                    if file_ext == 'err':
                                        temp_path = os.path.splitext(file_path)[0]
                                        file_ext = os.path.splitext(temp_path)[1][1:].lower()
                                        if file_ext in self.alg_dict.values():
                                            skip_dict[file_path] = None
                            if file_path not in hash_dict:
                                hash_dict[file_path] = file_hash
                            else:
                                err_line = self.err_fmt.format(err='Duplicated ', path=rel_path)
                                if err_line not in err_lines:
                                    err_lines.append(err_line)
                            if file_path in skip_dict:
                                err_line = self.err_fmt.format(err='Not skipped', path=rel_path)
                                if err_line not in err_lines:
                                    err_lines.append(err_line)
                            if not os.path.isfile(file_path):
                                err_line = self.err_fmt.format(err='Not found  ', path=rel_path)
                                if err_line not in err_lines:
                                    err_lines.append(err_line)
                self.prog_bar.stop()
                self.prog_bar.configure(mode='determinate')
                kwargs = {'action': 'Processing', 'path': hash_path}
                win_text = self.win_text.format(**kwargs)
                self.label.configure(text=win_text)
                total_num = len(path_dict)
                file_num = 0
                for key in path_dict:
                    file_num += 1
                    file_path = key
                    rel_path = os.path.relpath(file_path, start=dir_path)
                    if file_path not in hash_dict:
                        err_line = self.err_fmt.format(err='Not listed ', path=rel_path)
                        err_lines.append(err_line)
                    else:
                        old_hash = hash_dict[file_path]
                        new_hash = self.calc_hash(alg, file_path)
                        if type(new_hash) == str:
                            if new_hash != old_hash:
                                err_line = self.err_fmt.format(err='Not match  ', path=rel_path)
                                err_lines.append(err_line)
                        elif type(new_hash) == PermissionError:
                            err_line = self.err_fmt.format(err='Permission ', path=rel_path)
                            err_lines.append(err_line)
                        else:
                            err_line = self.err_fmt.format(err='Unknown    ', path=rel_path)
                            err_lines.append(err_line)
                    progress = (file_num / total_num) * 100
                    self.prog_bar['value'] = progress
                    self.master.update()
                if err_lines:
                    with open(err_path, mode='w', encoding='utf-8') as err_file:
                        time_info = self.info_fmt.format(info='Generated', data=time.ctime())
                        num_info = self.info_fmt.format(info='Number of Errors', data=len(err_lines))
                        err_title = 'Error Type'
                        header_lines = [self.app_title, self.app_website, self.sep_fmt, time_info,
                                        num_info, self.sep_fmt, err_title, self.sep_fmt, '']
                        header_lines = '\n'.join(header_lines)
                        err_file.write(header_lines)
                        err_file.writelines(err_lines)
                    self.hide_window()
                    verif_msg = '\n\n'.join([self.win_title, self.err_msg, err_path])
                    kwargs = {'proc_win': self, 'alg_win': self.alg_win,
                              'win_type': 2, 'win_text': verif_msg}
                    self.master.after(0, lambda: self.open_window(MsgWin, **kwargs))
                else:
                    if os.path.isfile(err_path):
                        os.remove(err_path)
                    self.hide_window()
                    verif_msg = '\n\n'.join([self.win_title, self.ok_msg, hash_path])
                    kwargs = {'proc_win': self, 'alg_win': self.alg_win,
                              'win_type': 1, 'win_text': verif_msg}
                    self.master.after(0, lambda: self.open_window(MsgWin, **kwargs))
            except PermissionError as perm_err:
                self.hide_window()
                file_path = os.path.abspath(perm_err.filename)
                verif_msg = '\n\n'.join([self.win_title, self.perm_msg, file_path])
                kwargs = {'proc_win': self, 'alg_win': self.alg_win,
                          'win_type': 2, 'win_text': verif_msg}
                self.master.after(0, lambda: self.open_window(MsgWin, **kwargs))
            except UnicodeDecodeError as code_err:
                self.hide_window()
                fmt = code_err.encoding.upper()
                verif_msg = '\n\n'.join([self.win_title, self.code_msg.format(fmt=fmt), hash_path])
                kwargs = {'proc_win': self, 'alg_win': self.alg_win,
                          'win_type': 2, 'win_text': verif_msg}
                self.master.after(0, lambda: self.open_window(MsgWin, **kwargs))
            except (tk.TclError, RuntimeError):
                pass

    def _set_texts(self):
        """
        Setting window texts
        """
        self.win_title = self.title_fmt.format(main=self.opt_dict[self.opt_num], add=self.alg.upper())
        self.win_msg = self.action_fmt.format(action='Processing', path=self.path)
        self.modif_text = '\n'.join([self.win_title, self.action_fmt])
        self.perm_msg = "Permission Error! We can't process the following file."
        self.code_msg = "Decoding Error! The file must be encoded in {fmt} format."
        self.empty_msg = "Empty Error! The directory doesn't have correct files to process."
        self.ok_msg = "The process has been successfully completed.\nThank you very much!"
        self.err_msg = "Warning! The verification process has failed.\nPlease check the error file for more details."

    def _create_menus(self):
        pass

    def _create_buttons(self):
        pass


class MsgWin(MainWin):

    def __init__(self, master=None, proc_win=None, alg_win=None, win_type=None, win_text=None, *args, **kwargs):
        """
        Initialize message window
        """
        if proc_win is None:
            proc_win = ProcWin()
        if alg_win is None:
            alg_win = proc_win.alg_win
        if win_type is None:
            win_type = 1
        if win_text is None:
            win_text = ''
        self.proc_win = proc_win
        self.alg_win = alg_win
        self.win_type = win_type
        self.win_text = win_text
        super().__init__(master, *args, **kwargs)
        if master is not None:
            self.display_sound(self.win_type)
            self.display_window()

    def display_sound(self, win_type=None):
        """
        Display sound depending on window type
        """
        if win_type is None:
            self.master.bell()
        else:
            sound_dict = {1: ws.MB_OK, 2: ws.MB_ICONHAND}
            ws.MessageBeep(sound_dict[win_type])

    def save_to_clipboard(self, text):
        """
        Save some text to clipboard
        """
        self.master.clipboard_clear()
        self.master.clipboard_append(text)

    def open_directory(self, path):
        """
        Open a directory by path
        """
        Popen(self.open_fmt.format(path=path))

    def close_window(self, window=None):
        """
        Execute special actions when window is closed
        """
        text_list = self.win_text.split('\n\n')
        if (self.proc_win.opt_num == 1) and (self.win_type == 1):
            alg = text_list[0].split(' ')[-1]
            file_path = text_list[1]
            file_hash = text_list[2]
            calc_line = ' '.join([file_hash, file_path, alg])
            func = self.save_to_clipboard
            arg = calc_line
        else:
            file_path = text_list[-1]
            func = self.open_directory
            arg = file_path
        if self.proc_win.opt_num == 3:
            close = self.alg_win.close_window
        else:
            close = self.proc_win.close_window
        if not ((self.proc_win.opt_num == 3) and (self.win_type == 1)):
            func(arg)
        close()

    def _create_menus(self):
        pass

    def _create_labels(self):
        """
        Create icon and text labels
        """
        type_dict = {1: 'information', 2: 'warning'}
        style_dict = {1: self.text_style[0], 2: self.text_style[3]}
        icon_type = self.icon_fmt.format(type=type_dict[self.win_type])
        self.icon_label = ttk.Label(self.upper_frame, image=icon_type)
        self.text_label = ttk.Label(self.upper_frame, text=self.win_text)
        self.text_label.configure(style=style_dict[self.win_type])
        self.icon_label.pack(side='left', fill='both', expand='yes', padx=(10, 5), pady=15)
        self.text_label.pack(side='right', fill='both', expand='yes', padx=(0, 15), pady=15)

    def _create_buttons(self):
        """
        Create ok button
        """
        self.ok_button = ttk.Button(self.lower_frame, text='OK')
        self.ok_button.configure(style=self.button_style[0], padding=(6, 3), takefocus=False)
        self.ok_button['command'] = self.close_window
        self.ok_button.pack(side='right', padx=15, pady=(5, 15))
        AddMoveControl(master=self.master, buttons=[self.ok_button])


class AboutWin(MainWin):

    def __init__(self, master=None, *args, **kwargs):
        """
        Initialize about window
        """
        super().__init__(master, *args, **kwargs)
        self._create_about()
        self._center_window()
        if master is not None:
            self.display_window()

    def _create_about(self):
        """
        Create application about
        """
        self.master.title('About')
        copyright_msg = self.copyright_fmt.format(year=self.app_year, sep='\n', author=self.app_author)
        self.image_label = ttk.Label(self.upper_frame, image=self.app_image)
        self.title_label = ttk.Label(self.upper_frame, text=self.app_title)
        self.phrase_label = ttk.Label(self.upper_frame, text=self.app_phrase)
        self.copyright_label = ttk.Label(self.lower_frame, text=copyright_msg)
        self.license_button = ttk.Button(self.lower_frame, text='License')
        self.donate_button = ttk.Button(self.lower_frame, text='Donate')
        self.close_button = ttk.Button(self.lower_frame, text='Close')
        self.image_label.configure(padding=15, justify='center')
        self.title_label.configure(font='Helvetica 16 bold', justify='center')
        self.phrase_label.configure(font='Helvetica 10', justify='center')
        self.copyright_label.configure(font='Helvetica 8', padding=20, justify='center')
        self.license_button.configure(style=self.button_style[0], padding=(6, 3), takefocus=False)
        self.donate_button.configure(style=self.button_style[0], padding=(6, 3), takefocus=False)
        self.close_button.configure(style=self.button_style[0], padding=(6, 3), takefocus=False)
        self.license_button['command'] = lambda: self.open_window(LicenseWin)
        self.donate_button['command'] = lambda: self.open_window(DonateWin)
        self.close_button['command'] = self.close_window
        self.image_label.pack(expand='yes')
        self.title_label.pack(expand='yes')
        self.phrase_label.pack(expand='yes')
        self.copyright_label.pack(expand='yes')
        self.license_button.pack(side='left', fill='x', expand='yes', padx=(15, 7), pady=(5, 15))
        self.donate_button.pack(side='left', fill='x', expand='yes', padx=(7, 7), pady=(5, 15))
        self.close_button.pack(side='left', fill='x', expand='yes', padx=(7, 15), pady=(5, 15))
        self.buttons = [self.license_button, self.donate_button, self.close_button]
        AddMoveControl(master=self.master, buttons=self.buttons)

    def _create_menus(self):
        pass

    def _create_labels(self):
        pass

    def _create_buttons(self):
        pass


class LicenseWin(MainWin):

    def __init__(self, master=None, *args, **kwargs):
        """
        Initialize license window
        """
        super().__init__(master, *args, **kwargs)
        self._create_license()
        self._center_window()
        if master is not None:
            self.display_window()

    def _create_license(self):
        """
        Create application license
        """
        self.master.title('License')
        self.license_text = tk.Text(self.upper_frame)
        self.scroll_bar = ttk.Scrollbar(self.upper_frame)
        self.license_text.insert(index='end', chars=self.app_license)
        self.license_text.configure(font='Helvetica 8', state='disable')
        self.license_text.configure(yscrollcommand=self.scroll_bar.set)
        self.scroll_bar['command'] = self.license_text.yview
        self.upper_frame.bind('<MouseWheel>', func=self.scroll_text)
        self.scroll_bar.bind('<MouseWheel>', func=self.scroll_text)
        self.scroll_bar.pack(side='right', fill='y')
        self.license_text.pack(fill='both', expand='yes', padx=10, pady=10)
        self.master.bind('<Up>', func=self.scroll_text)
        self.master.bind('<Down>', func=self.scroll_text)

    def scroll_text(self, event):
        """
        Scroll license text when event is fired
        """
        sign = int(event.delta / 120) * (-1)
        key = event.keysym.lower()
        if key == 'up':
            sign = -1
        elif key == 'down':
            sign = 1
        value = sign * 3
        self.license_text.yview_scroll(number=value, what='units')

    def _create_menus(self):
        pass

    def _create_labels(self):
        pass

    def _create_buttons(self):
        pass


class DonateWin(MainWin):

    def __init__(self, master=None, *args, **kwargs):
        """
        Initialize donate window
        """
        super().__init__(master, *args, **kwargs)
        self._create_donate()
        self._center_window()
        if master is not None:
            self.display_window()

    def _create_donate(self):
        """
        Create application donate
        """
        self.master.title('Donate')
        self.paypal_icon = tk.PhotoImage(master=self.master, data=paypal_code)
        self.donate_label = ttk.Label(self.upper_frame, text=self.app_donate)
        self.paypal_label = ttk.Label(self.upper_frame, image=self.paypal_icon)
        self.paypal_button = ttk.Button(self.upper_frame, text=self.paypal_msg)
        self.email_label = ttk.Label(self.lower_frame, text=self.email_msg)
        self.email_link = ttk.Label(self.lower_frame, text=self.app_email)
        self.donate_label.configure(style=self.text_style[0], padding=(15, 10, 15, 15))
        self.paypal_button.configure(style=self.button_style[1], padding=(20, 3), takefocus=False)
        self.email_link.configure(foreground='dark violet', cursor='hand2')
        self.paypal_button['command'] = lambda: wb.open(self.app_paypal)
        self.email_link.bind('<Button-1>', func=self.display_menu)
        self.donate_label.pack(expand='yes')
        self.paypal_label.pack(side='left', expand='yes', padx=(30, 0), pady=5)
        self.paypal_button.pack(side='right', expand='yes', padx=(0, 30), pady=5)
        self.email_label.pack(expand='yes', pady=(15, 0))
        self.email_link.pack(expand='yes', pady=(0, 20))
        AddTooltip(widget=self.paypal_button, text=self.app_paypal)
        AddMoveControl(master=self.master, buttons=[self.paypal_button])

    def display_menu(self, event):
        """
        Display popup menu when event is fired
        """
        self.popup_menu.post(event.x_root, event.y_root)

    def copy_email(self):
        """
        Copy application email to clipboard
        """
        self.master.clipboard_clear()
        self.master.clipboard_append(self.app_email)

    def _set_texts(self):
        """
        Setting window texts
        """
        self.paypal_msg = "Donate with PayPal"
        self.email_msg = "For feedback and suggestions, please send an email to:"

    def _create_menus(self):
        """
        Create popup menu
        """
        self.popup_menu = tk.Menu(self.master, tearoff=False)
        self.popup_menu.configure(activeforeground='black', activebackground='light blue')
        self.popup_menu.add_command(label='Copy', command=self.copy_email)

    def _create_labels(self):
        pass

    def _create_buttons(self):
        pass


app = MainApp()
