# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import sys
import os
import socket
from tkinter import Tk, messagebox
from gui_sf1p import App, MenuBar
from lib_gen_sf1p import Gen, read_hw_init, read_init, if_radnet
from RL import rl_autosync
import ctypes


if __name__ == '__main__':

    s1 = "//prod-svm1/tds/AT-Testers/JER_AT/ilya/Python/SF-1P/AT-SF-1P"
    d1 = "d:/PythonS/AT-SF1P"
    s2 = "//prod-svm1/tds/AT-Testers/JER_AT/ilya/TCL/SF-1V/download/sf1v/"
    d2 = "d:/temp"
    no_check_dirs = 'stam__pycache__ stam_venv __pycache__ .idea'
    no_check_files = '*zip init*.json'
    email_addrs = [['ilya_g@rad.com'], []]
    msg, ret = rl_autosync.AutoSync((s1, d1, s2, d2), no_check_dirs, no_check_files, email_addrs).auto_sync()
    print(f'ret of asy:{msg}, {ret}')
    if ret is False:
        msg += "\n\nDo you want to continue?"
        """
        0x04 == MB_YESNO
        0x30 == MB_ICONWARNING
        0x100 == MB_DEFBUTTON2
        Return code/value 7 == IDNO
        from https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messagebox?redirectedfrom=MSDN
        """
        ret = ctypes.windll.user32.MessageBoxW(0, msg, "AutoSync problem", 0x04 | 0x20 | 0x100)
        if ret == 7:
            # print(msg, ret)
            # messagebox.showerror("AutoSync problem", msg)
            exit()

    # msg, ret = asy.auto_sync()
    # print(msg, ret)

    gaSet = {}
    root = Tk()

    Gen.delete_markNum(Gen)

    if len(sys.argv) == 1:
        gui_num = 2
    else:
        gui_num = sys.argv[1]
    print(gui_num)
    hw_dict = read_hw_init(gui_num)
    # print(f'hw_dict {hw_dict}')
    ini_dict = read_init(gui_num)
    # print(f'ini_dict {ini_dict}')

    gaSet = {**hw_dict, **ini_dict, 'root': root}
    # print(f'main01 {gaSet}')

    unit_ini_dict = Gen.read_unit_init("self", gaSet)
    # if read of a init file succeeded - unit_ini_dict is dict and not False
    if unit_ini_dict is not False:
        gaSet = {**hw_dict, **ini_dict, **unit_ini_dict}

    gaSet['gui_num'] = gui_num
    gaSet['root'] = root

    # print(f'main1 {gaSet}')
    gaSet['relDebMode'] = "Release"

    gaSet['host_decrpt'] = Gen.get_reg(r"SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters", r'srvcomment')
    jav = Gen.get_reg(r"SOFTWARE\javasoft\Java Runtime Environment", r'CurrentVersion')
    res = Gen.get_reg(f'SOFTWARE\javasoft\Java Runtime Environment\{jav}', r'JavaHome')
    gaSet['java_location'] = os.path.join(res, "bin")

    gaSet['rad_net'] = if_radnet()
    gaSet['wifi_net'] = f'{socket.gethostname()}_{gui_num}'
    gaSet['use_exist_barcode'] = 0
    gaSet['IdBarcode'] = {}
    gaSet['act'] = 1

    root.geometry(gaSet['geom'])
    app = App(root, gaSet)
    menu_bar = MenuBar(root, gaSet)
    # print(f'main2 {app.gaSet}')

    #root.update()
    # all_tests = AllTests()

    Gen.build_tests(Gen, gaSet)
    # print(f'main3 {gaSet}')
    # print(f'main3 {gaSet["dut_fam"]}')

    App.my_statusbar.sstatus("Ready")

    # AllTests.stam_tst(gaSet)

    root.mainloop()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
