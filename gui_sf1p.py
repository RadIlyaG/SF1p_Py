"""
file gui
https://runestone.academy/runestone/books/published/thinkcspy/GUIandEventDrivenProgramming/02_standard_dialog_boxes.html
"""
import sys
import os
import tkinter
# from tkinter import Tk as tk
from tkinter import ttk, Menu, Listbox
from tkinter.ttk import *
from PIL import Image, ImageTk
from functools import partial
import re
from tkinter import IntVar, StringVar, Toplevel
from tkinter import X, N, S, W, E, VERTICAL, TOP, END, DISABLED, RAISED, BOTH, LEFT, BOTTOM, GROOVE, MULTIPLE
from tkinter.filedialog import askopenfilename, asksaveasfilename
from datetime import datetime
from pathlib import Path
import winsound

# from RL import Lib_RadApps as ra
from lib_gen_sf1p import Gen, get_xy, save_init, show_log, openHistory, copy_inits_to_testers
from lib_gen_sf1p import gui_Power, gui_PowerOffOn, gui_MuxMngIO, open_teraterm, save_unit_init
from lib_gen_sf1p import my_time, open_rl, close_rl, create_loggers, close_loggers, print_gaSet
from dialogBox import CustomDialog as DialogBox
import lib_barcode


class App(Gen):
    """ main class for the application """

    def __init__(self, parent, glob_dict, *args, **kwargs):
        self.gaSet = glob_dict
        # print(f'App.init1 {self.gaSet}')
        parent.title(str(self.gaSet['gui_num']) + " : " + self.gaSet['dutFullName'])
        parent.resizable(False, False)
        parent.wm_protocol("WM_DELETE_WINDOW", partial(self.my_quit, parent, self.gaSet))
        self.mainframe = ttk.Frame(parent)
        self.menuframe = ttk.Frame(self.mainframe)
        self.topframe = ttk.Frame(self.mainframe)
        self.centerframe = ttk.Frame(self.mainframe)
        self.bottomframe = ttk.Frame(self.mainframe)

        self.my_toolbar = Toolbar(self.topframe, self.gaSet)

        self.my_statusbar = StatusBar(self.mainframe)
        App.my_statusbar = self.my_statusbar
        self.my_statusbar.sstatus("This is the statusbar")

        self.fr0 = ttk.Frame(self.centerframe, relief="flat")

        self.fr_uut_id = ttk.Frame(self.fr0, relief="groove")
        self.lab_uut_id = ttk.Label(self.fr_uut_id, text="UUT's ID Number: ")
        self.uut_id = tkinter.StringVar()
        App.uut_id = self.uut_id
        self.ent_uut_id = ttk.Entry(self.fr_uut_id, textvariable=self.uut_id, width=20)
        self.ent_uut_id.bind('<Return>', partial(Gen.get_dbr_name, parent, self.gaSet))
        script_dir = os.path.dirname(__file__)
        self.img = Image.open(os.path.join(script_dir, "images", "clear1.ico"))
        use_img = ImageTk.PhotoImage(self.img)
        self.bt_clr_uut_id = ttk.Button(self.fr_uut_id, image=use_img,
                                        command=lambda: self.uut_id.set(""))
        self.bt_clr_uut_id.image = use_img
        self.lab_uut_id.pack(side="left", padx=2)
        self.ent_uut_id.pack(side="left")
        self.bt_clr_uut_id.pack(side="left")
        self.fr_uut_id.pack(anchor="w", padx=2, pady=2, fill=BOTH, expand=True, ipady=3)

        self.fr_curr_tst = ttk.Frame(self.fr0, relief="groove")
        self.lab_curr_tst = ttk.Label(self.fr_curr_tst, text="Current Test: ")
        self.curr_tst = tkinter.StringVar()
        App.curr_tst = self.curr_tst
        self.ent_curr_tst = ttk.Entry(self.fr_curr_tst, textvariable=self.curr_tst, width=35, justify='center')
        self.lab_curr_tst.pack(side="left", padx=2)
        self.ent_curr_tst.pack(side="left")

        self.relDebMode = tkinter.StringVar()
        # print(f'App.init2 {self.gaSet}')
        self.relDebMode.set(self.gaSet['relDebMode'])
        self.lab_relDeb = tkinter.Label(self.fr_curr_tst, textvariable=self.relDebMode, bg="SystemButtonFace")
        self.lab_relDeb.pack(side="right", padx=2)
        global gaGui
        gaGui = {
            'relDebMode': self.relDebMode,
            'lab_relDeb': self.lab_relDeb
        }

        self.fr_curr_tst.pack(anchor="w", padx=2, pady=2, fill=BOTH, expand=True, ipady=3)

        # if self.gaSet['relDebMode'] in locals():
        #     print("gui gaSet is local")
        # if self.gaSet['relDebMode'] in globals():
        #     print("gui gaSet is global")

        self.fr0.pack(side=LEFT, padx=2, fill=BOTH, expand=True)
        # self.centerlabel = ttk.Label(self.centerframe, text="Center stuff goes here")
        # self.centerlabel.pack()

        self.topframe.pack(side=TOP, fill=X)
        self.centerframe.pack(side=TOP, fill=BOTH)
        self.bottomframe.pack(side=BOTTOM, fill=X)
        self.mainframe.pack(side=TOP, expand=True, fill=BOTH)

        parent.bind('<F1>', partial(self.view_geom, parent))
        parent.bind('<Alt-r>', partial(self.my_toolbar.button_run))

    def button_function(self, *event):
        print("filter")

    def view_geom(self, parent, event):
        print(event)
        print(parent.winfo_geometry())
        print(parent.winfo_x())
        print(get_xy(parent))

    def my_quit(self, parent, gaSet):
        print(f"my_quit, parent:{parent}, gaSet")
        save_init(gaSet, gaSet['gui_num'])
        Gen.delete_markNum(Gen)
        db_dict = {
            "title": "Confirm exit",
            "message": "Are you sure you want to close the application?",
            "type": ["Yes", "No"],
            "icon": "::tk::icons::question",
            'default': 0
        }
        string, res_but, ent_dict = DialogBox(parent, db_dict).show()
        print(string, res_but)
        if res_but == "Yes":
            parent.destroy()
            sys.exit()

    def gui_ReleaseDebugMode(gaSet):
        base = Toplevel()
        base.geometry(get_xy(gaSet['root']))  ## gaSet['geom']
        base.title("Release/Debug Mode")

        radVar = StringVar()
        # print(f'gui_ReleaseDebugMode {gaSet}')
        fr1 = Frame(base, relief=GROOVE)
        fr11 = Frame(fr1)
        fr12 = Frame(fr1)
        rb1 = Radiobutton(fr11, text="Release Mode", value='Release', variable=radVar,
                          command=partial(App.rel_deb_mode_rb, 'Release'))
        rb2 = Radiobutton(fr11, text="Debug Mode", value='Debug', variable=radVar,
                          command=partial(App.rel_deb_mode_rb, 'Debug'))

        but_refresh = ttk.Button(fr11, text='Refresh Tests')
        but_refresh.configure(command=partial(App.refresh_tests, "selkkf"))
        rb1.pack(anchor="w")
        rb2.pack(anchor="w")
        but_refresh.pack(anchor="w")

        fr121 = Frame(fr12)
        fr122 = Frame(fr12)
        fr123 = Frame(fr12)

        lab121 = ttk.Label(fr121, text='Available Tests')
        lbox121 = Listbox(fr121, width=28, selectmode=MULTIPLE, height=1 + len(Toolbar.cb1.cget('values')))
        App.lbox121 = lbox121

        for te in Toolbar.cb1.cget('values'):
            lbox121.insert(END, te)

        lab121.pack()
        lbox121.pack()

        lab123 = ttk.Label(fr123, text='Tests to run')
        lbox123 = Listbox(fr123, width=28, selectmode=MULTIPLE, height=1 + len(Toolbar.cb1.cget('values')))
        App.lbox123 = lbox123
        lab123.pack()
        lbox123.pack()

        lbox121.bind('<Double-Button-1>', partial(App.select_lb121))

        lab_stam = Label(fr122, text="")
        App.but_add_tst = but_add_tst = ttk.Button(fr122, text=">", width=5, command=partial(App.cmd_add_tst, 'sel'))
        App.but_add_tsts = but_add_tsts = ttk.Button(fr122, text=">>", width=5, command=partial(App.cmd_add_tst, 'all'))
        App.but_rem_tst = but_rem_tst = ttk.Button(fr122, text="<", width=5, command=partial(App.cmd_rem_tst, 'sel'))
        App.but_rem_tsts = but_rem_tsts = ttk.Button(fr122, text="<<", width=5, command=partial(App.cmd_rem_tst, 'all'))
        lab_stam.pack(pady=1)
        but_add_tst.pack(pady=1)
        but_add_tsts.pack(pady=1)
        but_rem_tst.pack(pady=1)
        but_rem_tsts.pack(pady=1)

        if gaSet['relDebMode'] == "Release":
            rb1.invoke()
            App.cmd_add_tst('all')
        else:
            rb2.invoke()
            App.cmd_rem_tst('all')

        # but_add_tst.configure(command=partial(App.refresh_tests, 'gfgfg', lbox121, lbox123))

        fr121.pack(side=LEFT)
        fr122.pack(side=LEFT, anchor='n')
        fr123.pack(side=LEFT)

        fr11.pack(side=LEFT, anchor=N, padx=2, pady=2)
        fr12.pack(side=LEFT, anchor=N, padx=2, pady=2)
        fr1.pack()

        fr2 = Frame(base, relief=GROOVE)
        but_ok = Button(fr2, text="OK", command=partial(App.but_OkReleaseDebugMode, base, radVar, gaSet))
        but_ok.pack(anchor="w")
        fr2.pack()

    def refresh_tests(self, *args):
        print(f'refresh_tests, self:{self}')

    def select_lb121(event):
        # print(args)
        # self, event, lbox121, lbox123
        # print(App.lbox121.curselection())
        App.cmd_add_tst("sel")

    def cmd_add_tst(mode):
        lbox123_items = App.lbox_get_items(App.lbox123)
        if mode == 'sel':
            for ind in App.lbox121.curselection():
                lb121_item = App.lbox121.get(ind)
                if lb121_item not in lbox123_items:
                    App.lbox123.insert(END, lb121_item)
        else:
            for ft in App.lbox121.get(0, END):
                if ft not in lbox123_items:
                    App.lbox123.insert(END, ft)

        temp_list = list(App.lbox123.get(0, END))
        srt_list = sorted(temp_list, key=lambda x: int(x.split('..')[0]))
        App.lbox123.delete(0, END)
        for item in srt_list:
            App.lbox123.insert(END, item)

        App.lbox121.selection_clear(0, END)

    def lbox_get_items(lbox):
        return lbox.get(0, END)

    def cmd_rem_tst(mode):
        if mode == 'sel':
            for ind in App.lbox123.curselection():
                App.lbox123.delete(ind)
        else:
            for ft in App.lbox123.get(0, END):
                ind = App.lbox123.get(0, END).index(ft)
                App.lbox123.delete(ind)

    def rel_deb_mode_rb(mode):
        # print(f'rel_deb_mode_rb {mode}')
        if mode == "Release":
            App.cmd_add_tst("all")
            state = 'disabled'
        else:
            App.cmd_rem_tst("all")
            state = 'normal'

        App.but_add_tst.configure(state=state)
        App.but_add_tsts.configure(state=state)
        App.but_rem_tst.configure(state=state)
        App.but_rem_tsts.configure(state=state)

    def but_OkReleaseDebugMode(base, radVar, gaSet):
        mode = radVar.get()
        gaSet['relDebMode'] = mode
        gaGui['relDebMode'].set(mode)
        if mode == "Debug":
            bg = "yellow"
        else:
            bg = "SystemButtonFace"
        gaGui['lab_relDeb'].configure(background=bg)
        # print(f'but_OkReleaseDebugMode {gaSet}')
        lbox123_items = App.lbox_get_items(App.lbox123)
        if len(lbox123_items):
            Toolbar.cb1.config(values=lbox123_items, height=len(lbox123_items))
            Toolbar.var_start_from.set(lbox123_items[0])
            base.destroy()


class StatusBar(ttk.Frame):
    """ Simple Status Bar class - based on Frame """

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.label1 = tkinter.Label(self, anchor='center', width=66, relief="groove")
        self.label1.pack(side='left', padx=1, pady=1)
        self.label2 = tkinter.Label(self, anchor=W, width=15, relief="sunken")
        self.label2.pack(side='left', padx=1, pady=1)
        self.label3 = tkinter.Label(self, width=5, relief="sunken", anchor='center')
        self.label3.pack(side='left', padx=1, ipadx=2, pady=1)
        self.pack(side=BOTTOM, fill=X, padx=2, pady=2)

    def sstatus(self, texto, bg="SystemButtonFace"):
        if bg == 'red':
            bg = 'salmon'
        elif bg == 'green':
            bg = 'springgreen'
        self.label1.config(text=texto, bg=bg)  # 'salmon' for red , springgreen 'olivedrab1' for green
        self.label1.update_idletasks()
        # self.gaSet['file_log'].info(f"{texto}")
        # self.gaSet['puts_log'].info(f"{texto}")

    def rstatus(self):
        return self.label1.cget('text')

    def startTime(self, texto):
        self.label2.config(text=texto)
        self.label2.update_idletasks()

    def runTime(self, texto):
        self.label3.config(text=texto)
        self.label3.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()


class Toolbar:
    """ Toolbar """

    def button_run(self, *event):
        print(f"{my_time()} Button RUN pressed, event={event}")
        clear = lambda: os.system('cls')
        clear()
        from all_tests import AllTests
        App.my_statusbar.startTime(my_time())
        App.my_statusbar.sstatus("")
        self.gaSet['act'] = 1
        self.button1.state(["pressed", "disabled"])
        self.button2.state(["!pressed", "!disabled"])
        # self.button1.config(relief="sunken", state="disabled")

        now = datetime.now()
        self.gaSet['log_time'] = now.strftime("%Y.%m.%d-%H.%M.%S")

        Path('c:\\logs').mkdir(parents=True, exist_ok=True)

        gui_num = self.gaSet['gui_num']
        self.gaSet['log'] = {}
        self.gaSet['log'][gui_num] = f"c:/logs/{self.gaSet['log_time']}.txt"

        ret = lib_barcode.gui_read_barcode(self.gaSet)

        create_loggers(self.gaSet)
        self.gaSet['file_log'].info(f"ID Barcode: {self.gaSet['IdBarcode']['DUT']}")
        self.gaSet['file_log'].info(f"DUT: {self.gaSet['dutFullName']} \n")
        if ret == 0:
            ret = open_rl(self.gaSet)
            if ret == 0:
                run_status = ''
                all_tests_obj = AllTests(self.gaSet)
                #ret = AllTests.testing_loop(self.gaSet)
                ret = all_tests_obj.testing_loop()
                # self.gaSet['puts_log'].info(f'Ret of Testing:{ret}')
                print(f"{my_time()} Ret of Testing:{ret}")
                close_rl(self.gaSet)

        # After Tests
        App.my_statusbar.runTime("")
        close_loggers(self.gaSet)

        # since gaSet['log'][gaSet['gui_num']] is just an str,
        # i convert it to path by Path(str)
        src = Path(self.gaSet['log'][self.gaSet['gui_num']])

        if ret == 0:
            wav = "C:\\RLFiles\\Sound\\Wav\\pass.wav"
            App.my_statusbar.sstatus("")
            App.my_statusbar.sstatus("Done", 'green')

            dst = f'{os.path.splitext(src)[0]}-PASS.txt'
            os.rename(src, dst)
            run_status = 'Pass'
        elif ret == 1:
            wav = "C:\\RLFiles\\Sound\\Wav\\info.wav"
            App.my_statusbar.sstatus("The test has been perform", 'yellow')
        else:
            run_status = 'Fail'
            if ret == -2:
                self.gaSet['fail'] = 'User stop'
                run_status = ''
            elif ret == -3:
                run_status = ''

            App.my_statusbar.sstatus(f"Test FAIL: {self.gaSet['fail']}", 'red')
            wav = "C:\\RLFiles\\Sound\\Wav\\fail.wav"
            if os.path.isfile(src):
                dst = f'{os.path.splitext(src)[0]}-FAIL.txt'
                os.rename(src, dst)

        self.button1.state(["!pressed", "!disabled"])
        self.button2.state(["pressed", "disabled"])
        # self.button1.config(relief="raised", state="normal")
        # self.button2.config(relief="sunken", state="disabled")

        try:
            # playsound(wav, block=False)
            winsound.PlaySound(wav, winsound.SND_FILENAME)
        except Exception as e:
            pass
        finally:
            MenuBar.use_ex_barc.set(0)
            print_gaSet('ButRun finally:', self.gaSet)



    def button_stop(self):
        print("button_stop 1 pressed")
        self.gaSet['act'] = 0
        self.button1.state(["!pressed", "!disabled"])
        self.button2.state(["pressed", "disabled"])
        close_rl(self.gaSet)
        # self.button1.config(relief="raised", state="normal")
        # self.button2.config(relief="sunken", state="disabled")

    def button_two(self):
        print("button 2 pressed")

    def __init__(self, parent, gaSet):
        self.gaSet = gaSet
        self.sep1 = Separator(parent)
        self.sep1.pack(fill="x", expand=True)
        self.sep2 = Separator(parent)
        self.sep2.pack(side="bottom", fill="x", expand=True)

        self.l1 = Label(parent, text="Start from:")
        self.l1.pack(side="left", padx=2)

        self.var_start_from = StringVar()
        Toolbar.var_start_from = self.var_start_from
        self.cb1 = ttk.Combobox(parent, justify='center', width=35, textvariable=self.var_start_from)
        # self.cb1.option_add('*TCombobox*Listbox.Justify', 'center')
        Toolbar.cb1 = self.cb1
        self.cb1.pack(side="left", padx=2)

        script_dir = os.path.dirname(__file__)
        self.img = Image.open(os.path.join(script_dir, "images", "run1.gif"))
        use_img = ImageTk.PhotoImage(self.img)
        self.button1 = ttk.Button(parent, command=partial(self.button_run), image=use_img)
        self.button1.image = use_img

        self.img = Image.open(os.path.join(script_dir, "images", "stop1.gif"))
        use_img = ImageTk.PhotoImage(self.img)
        self.button2 = ttk.Button(parent, command=partial(self.button_stop), image=use_img)
        self.button2.image = use_img

        self.img = Image.open(os.path.join(script_dir, "images", "find1.1.ico"))
        use_img = ImageTk.PhotoImage(self.img)
        self.button3 = ttk.Button(parent, command=self.button_two, image=use_img)
        self.button3.image = use_img

        self.button1.pack(side="left", padx=(12, 0))
        self.button2.pack(side="left", padx=(2, 2))
        self.button3.pack(side="left", padx=(10, 2))


def donothing():
    pass
    # filewin = Toplevel()
    # button = Button(filewin, text="Do nothing button", command=lambda: print(gaSet["useExistBarcode"].get()))
    # button.pack()
    # print(gaSet)


class MenuBar:
    def __init__(self, parent, glob_dict, *args, **kwargs):
        print(f'parent:{parent}, type:{type(parent)}')
        self.gaSet = glob_dict
        menubar = Menu(parent)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Log File", command=partial(show_log))
        filemenu.add_command(label="History", command=partial(openHistory))
        filemenu.add_separator()
        filemenu.add_command(label="Update INIT and UserDefault files on all the Testers",
                             command=copy_inits_to_testers)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=partial(App.my_quit, self, parent, glob_dict))

        menubar.add_cascade(label="File", menu=filemenu)

        toolsmenu = Menu(menubar, tearoff=0)
        toolsmenu.add_command(label="Inventory", command=lambda: GuiInventory(self.gaSet))
        toolsmenu.add_separator()
        pwr_menu = Menu(toolsmenu, tearoff=0)
        pwr_menu.add_command(label="PS-1 & PS-2 ON", command=lambda: gui_Power(self.gaSet, 1, 1))
        pwr_menu.add_command(label="PS-1 & PS-2 OFF", command=lambda: gui_Power(self.gaSet, 1, 0))
        pwr_menu.add_command(label="PS-1 & PS-2 OFF and ON", command=lambda: gui_PowerOffOn(self.gaSet, 1))
        toolsmenu.add_cascade(label="Power", menu=pwr_menu)
        toolsmenu.add_separator()

        # global gaSet
        self.use_ex_barc = IntVar()
        try:
            set = self.gaSet['use_exist_barcode']
        except KeyError:
            set = 0
        self.use_ex_barc.set(set)
        MenuBar.use_ex_barc = self.use_ex_barc
        toolsmenu.add_radiobutton(label="Don't use exist Barcodes", variable=self.use_ex_barc,
                                  value=0,
                                  command=partial(self.rb_ueb_cmd, self.gaSet,
                                                  'use_exist_barcode',
                                                  self.use_ex_barc))
        toolsmenu.add_radiobutton(label="Use exist Barcodes", variable=self.use_ex_barc,
                                  value=1,
                                  command=partial(self.rb_ueb_cmd, self.gaSet,
                                                  'use_exist_barcode',
                                                  self.use_ex_barc))
        toolsmenu.add_separator()

        self.one_tst = IntVar()
        MenuBar.one_tst = self.one_tst
        try:
            set = self.gaSet['one_test']
        except KeyError:
            set = 0
        self.one_tst.set(set)
        toolsmenu.add_radiobutton(label="One test ON", variable=self.one_tst, value=1,
                                  command=partial(self.rb_ueb_cmd, self.gaSet,
                                                  'one_test',
                                                  self.one_tst))
        toolsmenu.add_radiobutton(label="One test OFF", variable=self.one_tst, value=0,
                                  command=partial(self.rb_ueb_cmd, self.gaSet,
                                                  'one_test',
                                                  self.one_tst))

        toolsmenu.add_separator()

        toolsmenu.add_command(label="Release / Debug mode", command=partial(App.gui_ReleaseDebugMode, self.gaSet))

        menubar.add_cascade(label="Tools", menu=toolsmenu)

        termmenu = Menu(menubar, tearoff=0)
        termmenu.add_command(label=f"UUT: {self.gaSet['comDut']}",
                             command=lambda: open_teraterm(self.gaSet, "comDut"))
        termmenu.add_command(label=f"Gen-1: {self.gaSet['comGen1']}",
                             command=lambda: open_teraterm(self.gaSet, "comGen1"))
        termmenu.add_command(label=f"Gen-2: {self.gaSet['comGen2']}",
                             command=lambda: open_teraterm(self.gaSet, "comGen2"))
        termmenu.add_command(label=f"Serial-1: {self.gaSet['comSer1']}",
                             command=lambda: open_teraterm(self.gaSet, "comSer1"))
        termmenu.add_command(label=f"Serial-2: {self.gaSet['comSer2']}",
                             command=lambda: open_teraterm(self.gaSet, "comSer2"))
        termmenu.add_command(label=f"485-2: {self.gaSet['comSer485']}",
                             command=lambda: open_teraterm(self.gaSet, "comSer485"))
        menubar.add_cascade(label="Terminal", menu=termmenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About...", command=lambda: about(parent))
        menubar.add_cascade(label="Help", menu=helpmenu)

        parent.config(menu=menubar)

    def rb_ueb_cmd(self, gaSet, key, value):
        val = value.get()
        print(f'rb_ueb_cmd', {self}, {key}, {val})
        gaSet[key] = val
        save_init(gaSet)

    # root.mainloop()


def about(root):
    # regsub -all -- {<[\w\=\#\d\s\"\/]+>} $hist "" a
    # regexp {<!---->\s(.+)\s<!---->} $a m date
    with open("history.html", 'r') as f:
        hist = f.read()
    res = re.sub(r'<[\w\=\#\d\s\"\/]+>', '', hist)
    aa = re.search(r'<!---->\s([0-9a-zA-Z\-\"\:\.\s]+)<!---->', res)
    date = str(aa.group(1))
    db_dict = {
        "title": "About",
        "message": f"ATE software upgrade\n\n{date}",
        "type": ["Ok"],
        "icon": "::tk::icons::information"
    }
    string, str12, ent_dict = DialogBox(root, db_dict).show()
    print(string, str12)


class GuiInventory:
    def __init__(self, gaSet, *args, **kwargs):
        self.var_csl = StringVar()
        self.var_mc_pcbId = StringVar()
        self.var_mc_hw = StringVar()
        self.sw_ver = StringVar()
        self.dbr_sw_num = StringVar()
        self.uut_sw_from = StringVar()
        self.gaSet = gaSet
        # print(f'GuiInventory {gaSet}')
        self.base = Toplevel()
        self.base.geometry(get_xy(self.gaSet['root']))
        # self.base.title(f"Inventory of {self.gaSet['dutFullName']}")
        self.base.title(f"Inventory")
        self.pathWith = 60
        self.script_dir = os.path.dirname(__file__)
        self.tmp_gaSet = {}
        self.tmp_gaSet["dutInitName"] = self.gaSet["dutInitName"]

        self.create_up_fr(self.base)
        self.create_butt_fr(self.base)

    def create_up_fr(self, parent):
        gaSet = self.gaSet
        fr_up = tkinter.Frame(parent, relief="groove")

        self.lab_title = ttk.Label(fr_up, text=self.gaSet["dutFullName"], relief='groove', anchor='center')
        self.lab_title.pack(fill='both', padx=2, pady=2, anchor="c")

        fr_sw = ttk.Labelframe(fr_up, text="UUT Software", relief="groove")
        fr1 = Frame(fr_sw)
        self.uut_sw_from.set(gaSet['uutSWfrom'])
        self.tmp_gaSet['uutSWfrom'] = self.gaSet['uutSWfrom']
        chb_sw_dbr = ttk.Radiobutton(fr1, text="From DBR", variable=self.uut_sw_from, value='fromDbr')
        self.dbr_sw_num.set(gaSet['dbrSWnum'])
        self.tmp_gaSet['dbrSWnum'] = self.gaSet['dbrSWnum']
        ent_dbr_sw_num = ttk.Entry(fr1, textvariable=self.dbr_sw_num, width=10, justify='center')
        self.sw_ver.set(gaSet['SWver'])
        self.tmp_gaSet['SWver'] = self.gaSet['SWver']
        ent_dbr_sw_ver = ttk.Entry(fr1, textvariable=self.sw_ver, justify='center')
        chb_sw_dbr.pack(side=LEFT, padx=2)
        ent_dbr_sw_num.pack(side=LEFT, padx=2)
        ent_dbr_sw_ver.pack(side=LEFT, padx=2)

        fr1.pack(pady=2, anchor="w")
        fr_sw.pack(fill="x", padx=2, pady=2)

        fr_main_crd = ttk.Labelframe(fr_up, text="Main Card", relief="groove")
        fr1 = Frame(fr_main_crd)
        lab_mc_hw = ttk.Label(fr1, text="HW version", width=12)
        self.var_mc_hw.set(gaSet['mainHW'])
        f = "mainHW"
        self.tmp_gaSet[f] = self.gaSet[f]
        ent_mc_hw = ttk.Entry(fr1, textvariable=self.var_mc_hw, justify='center')
        lab_mc_hw.pack(side='left', padx=2)
        ent_mc_hw.pack(side='right', padx=2, pady=2)
        fr1.pack(pady=2, anchor="w", fill=BOTH)
        fr2 = Frame(fr_main_crd,)
        lab_mc_pcb_id = ttk.Label(fr2, text="PCB ID")
        self.var_mc_pcbId.set(gaSet['mainPcbId'])
        f = "mainPcbId"
        self.tmp_gaSet[f] = self.gaSet[f]
        ent_mc_pcb_id = ttk.Entry(fr2, textvariable=self.var_mc_pcbId, width=23,
                                  justify='center')
        lab_mc_pcb_id.pack(side='left', padx=2)
        ent_mc_pcb_id.pack(side='right', padx=2, pady=2)
        fr2.pack(pady=2, anchor="w", fill='both')

        fr_main_crd.pack(fill="x", padx=2, pady=2)

        fr_csl = ttk.Frame(fr_up, relief="groove")
        lab_csl = ttk.Label(fr_csl, text='CSL')
        if 'csl' not in gaSet:
            gaSet['csl'] = 'A'
        self.var_csl.set(gaSet['csl'])
        f = "csl"
        self.tmp_gaSet[f] = self.gaSet[f]
        ent_csl = ttk.Entry(fr_csl, textvariable=self.var_csl, justify='center')
        lab_csl.pack(side='left', padx=2)
        ent_csl.pack(side='right', padx=2, pady=2)

        fr_csl.pack(fill="x", padx=2, pady=2)

        fr_up.pack(fill="both", padx=2, pady=2)

    def create_butt_fr(self, parent):
        gaSet = self.gaSet
        fr_butt = tkinter.Frame(parent)
        # butt_inv_ok = Button(fr_butt, text="OK",
        # command=partial(self.but_inv_ok_cmd, gaSet, base, tmp_gaSet, var_uboot, var_uboot_ver, var_uboot_path))
        butt_inv_save = Button(fr_butt, text="Save", command=self.but_inv_save_cmd)
        butt_inv_cls = Button(fr_butt, text="Close", command=self.but_inv_cls_cmd)
        butt_inv_cls.pack(side='right', padx=2)
        butt_inv_save.pack(side='right', padx=2)
        fr_butt.pack(side='bottom', fill="x", padx=2, pady=2)

    def but_inv_save_cmd(self, *args):
        # print(f'but_inv_save_cmd gaSet:{self.gaSet}')
        # print(f'but_inv_save_cmd tmp_gaSet:{self.tmp_gaSet}')
        # print(f'but_inv_save_cmd args:{args}')
        # self.var_uboot.set(self.gaSet['dbrUbootSWnum'])

        # self.gaSet['dbrUbootSWnum'] = self.tmp_gaSet['dbrUbootSWnum'] = self.var_uboot.get()
        # self.gaSet['dbrUbootSWver'] = self.tmp_gaSet['dbrUbootSWver'] = self.var_uboot_ver.get()
        # self.gaSet['UbootSWpath'] = self.tmp_gaSet['UbootSWpath'] = self.var_uboot_path.get()
        self.gaSet['uutSWfrom'] = self.tmp_gaSet['uutSWfrom'] = self.uut_sw_from.get()
        self.gaSet['dbrSWnum'] = self.tmp_gaSet['dbrSWnum'] = self.dbr_sw_num.get()
        self.gaSet['SWver'] = self.tmp_gaSet['SWver'] = self.sw_ver.get()
        # self.gaSet['UutSWpath'] = self.tmp_gaSet['UutSWpath'] = self.var_sw_path.get()
        # self.gaSet['LXDpath'] = self.tmp_gaSet['LXDpath'] = self.var_lxd_path.get()
        self.gaSet['mainHW'] = self.tmp_gaSet['mainHW'] = self.var_mc_hw.get()
        self.gaSet['mainPcbId'] = self.tmp_gaSet['mainPcbId'] = self.var_mc_pcbId.get()
        # self.gaSet['sub1HW'] = self.tmp_gaSet['sub1HW'] = self.var_sub1_hw.get()
        # self.gaSet['sub1PcbId'] = self.tmp_gaSet['sub1PcbId'] = self.var_sub1_pcbId.get()
        # self.gaSet['loraDashBver'] = self.tmp_gaSet['loraDashBver'] = self.var_lora.get()
        self.gaSet['csl'] = self.tmp_gaSet['csl'] = self.var_csl.get()
        save_unit_init(self.tmp_gaSet)
        self.but_inv_cls_cmd()

    def but_inv_cls_cmd(self):
        self.base.destroy()

    def but_browse_file(self, txt, path, fileType):
        # var_uboot_path
        dir = f'c:/download/sf1v'
        filetype = [fileType, ('All', '*')]
        op_fi = askopenfilename(title=txt, initialdir=dir, filetype=filetype)
        if op_fi != "":
            path.set(op_fi)
            # self.tmp_gaSet[f] = op_fi
