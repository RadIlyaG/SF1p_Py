"""
commands from menu
https://stackoverflow.com/questions/27923347/tkinter-menu-command-targets-function-with-arguments/27923452
"""

import webbrowser
import os
import subprocess
import json
import socket
import re
import inspect
from winreg import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
import serial
import time
import timeit
from datetime import datetime
import logging
from serial import Serial

from pathlib import Path
from dirsync import sync
from email.message import EmailMessage
import smtplib
import ctypes

import gui_sf1p
import lib_ftp
from dialogBox import CustomDialog as DialogBox
from RL import Lib_RadApps as ra
from RL import rl_com as rlcom
from RL import RL_UsbPio
from RL import rl_autosync


def get_xy(top):
    return str("+" + str(top.winfo_x()) + "+" + str(top.winfo_y()))


def if_radnet():
    res = socket.gethostbyname_ex(socket.gethostname())
    if re.search('192.115.243', str(res[2])) or \
            re.search('172.18.9', str(res[2])):
        return True
    return False


def save_unit_init(dicti):
    ini_file = os.path.join('uutInits', dicti["dutInitName"])
    try:
        with open(ini_file, 'w') as fi:
            json.dump(dicti, fi, indent=2, sort_keys=True)
    except Exception as e:
        print(e)
        raise (e)


class Gen:
    def __init__(self):
        pass

    def get_dbr_name(parent, gaSet, *event):
        gui_sf1p.App.my_statusbar.sstatus("Getting data from DBR")
        self = 'sseellff'
        id_number = gui_sf1p.App.uut_id.get()
        print(f'\n{my_time()} get_dbr_name barcode:{id_number}')
        # print(f'get_dbr_name elf:{self}, parenr:{parent}, gaSet, event:{event}')

        # file_name = f"MarkNam_+{barcode}+.txt"
        # if os.path.exists(file_name) == True:
        #     os.remove(file_name)

        stat, dbr_name = ra.get_dbr_name(id_number)
        print(f'{my_time()}get_dbr_name stat:{stat} dbrName:{dbr_name}')

        if stat is False:
            db_dict = {
                "title": "Get DBR name fail",
                "message": f"Get DBR name fail\n\n{dbr_name}",
                "type": ["Ok"],
                "icon": "::tk::icons::error"
            }
            string, str12, ent_dict = DialogBox(parent, db_dict).show()
            return False

        gaSet['dutFullName'] = dbr_name
        gaSet['dutInitName'] = re.sub('/', '.', dbr_name) + '.json'
        gaSet['id_number'] = id_number
        gaSet['root'].title(f"{gaSet['gui_num']}: {dbr_name}")
        di = Gen.read_unit_init(self, gaSet)
        # print(di)

        # print(f'get_dbr_name self: {self}') # DA1000835558
        # Gen.retrive_dut_fam(self, gaSet) ## done in build_tests

        Gen.build_tests(Gen, gaSet)
        gui_sf1p.App.my_statusbar.sstatus("Ready")

    def get_reg(REG_PATH, name):
        reg_key = OpenKey(HKEY_LOCAL_MACHINE, REG_PATH, 0, KEY_READ | KEY_WOW64_64KEY)
        value, regtype = QueryValueEx(reg_key, name)
        CloseKey(reg_key)
        # print(value)
        return value

    def read_unit_init(self, gaSet):
        # script_dir = os.path.dirname(__file__)
        # print(f'read_unit_init script_dir {script_dir}')
        Path('uutInits').mkdir(parents=True, exist_ok=True)
        ini_file = Path(os.path.join('uutInits', gaSet['dutInitName']))
        # print(f'ini_file {ini_file}')
        if os.path.isfile(ini_file) == False:
            db_dict = {
                "title": "Load INIT",
                "message": f"INIT for {gaSet['dutFullName']} doesn't exist\n\n"
                           f"Do you want to create it from existing one?",
                "type": ["Yes", "No"],
                "icon": "::tk::icons::warning"
            }
            string, answ, ent_dict = DialogBox(gaSet['root'], db_dict).show()
            print(f'read_unit_init string:_{string}_ answ:_{answ}_')
            if answ == "No":
                return False

            script_dir = Path('uutInits')
            filetype = [('Ini files', '*json')]
            txt = "Choose ini file"
            op_file = askopenfilename(title=txt, initialdir=script_dir, filetype=filetype)
            op_file = os.path.join('uutInits', os.path.basename(op_file))
            if op_file != "":
                print(f'read_unit_init op_file _{op_file}_')
                status = subprocess.check_output(f'copy {op_file} {ini_file}', shell=True)
                # print(f'read_unit_init status _{status}_')
            else:
                return False
        else:
            answ = "no question"

        dicti = {}
        try:
            with open(ini_file, 'r') as fi:
                dicti = json.load(fi)
        except Exception as e:
            # print(e)
            # raise(e)
            raise Exception(e)

        ## if we copy from another init, we need to change some fields in the dicti:
        # print(f'read_unit_init answ{answ}')
        if answ == "Yes":
            basename = os.path.basename(ini_file)
            # print(f'read_unit_init answ: {answ} basename: {basename}')
            # convert  WindowsPath('uutInits/SF-1V.E2.12V.4U1S.2RS.L4.G.GO.json')
            # to SF-1V/E2/12V/4U1S/2RS/L4/G/GO
            #
            dicti["dutFullName"] = re.sub('\.', '/', '.'.join(basename.split('.')[0:-1]))
            dicti["dutInitName"] = basename

            save_unit_init(dicti)

        # print(f'read_unit_init before return {dict}')
        return dicti

    def delete_markNum(self):
        for filename in Path(os.path.dirname(__file__)).glob("MarkN*.txt"):
            os.remove(filename)

    def retrive_dut_fam(self, gaSet, *args):
        # print(f'retrive_dut_fam self:{self}, gaSet, {args}')
        dutInitName = gaSet['dutInitName']

        gaSet['dut_fam'] = {}

        gaSet['dut_fam']['sf'] = re.search(r'([A-Z0-9\-\_]+)\.E?', dutInitName).group(1)
        if gaSet['dut_fam']['sf'] == 'SF-1P':
            gaSet['app_prompt'] = '-1p#'
        elif gaSet['dut_fam']['sf'] == 'VB-101V':
            gaSet['app_prompt'] = 'VB101V#'

        # gaSet['dut_fam']['box'] = re.search(r'P.*\.(E\d)\.', dutInitName).group(1)
        gaSet['dut_fam']['ps'] = re.search(r'E\d\.([A-Z0-9]+)\.', dutInitName).group(1)

        if re.search(r'\.4U2S\.', dutInitName) is not None:
            gaSet['dut_fam']['wanPorts'] = '4U2S'
        elif re.search(r'\.2U\.', dutInitName) is not None:
            gaSet['dut_fam']['wanPorts'] = '2U'

        if re.search(r'\.2RS\.', dutInitName) is not None:
            gaSet['dut_fam']['serPort'] = '2RS'
        elif re.search(r'\.2RSM\.', dutInitName) is not None:
            gaSet['dut_fam']['serPort'] = '2RSM'
        elif re.search(r'\.1RS\.', dutInitName) is not None:
            gaSet['dut_fam']['serPort'] = '1RS'
        else:
            gaSet['dut_fam']['serPort'] = 0

        if re.search(r'\.CSP\.', dutInitName) is not None:
            gaSet['dut_fam']['serPortCsp'] = 'CSP'
        else:
            gaSet['dut_fam']['serPortCsp'] = 0

        if re.search(r'\.2PA\.', dutInitName) is not None:
            gaSet['dut_fam']['poe'] = '2PA'
        elif re.search(r'\.POE\.', dutInitName) is not None:
            gaSet['dut_fam']['poe'] = 'POE'
        else:
            gaSet['dut_fam']['poe'] = 0

        gaSet['dut_fam']['cell'] = {
            'cell': 0,
            'qty': 0
        }
        for cell in ['HSP', 'L1', 'L2', 'L3', 'L4']:
            qty = len([i for i, x in enumerate(dutInitName.split('.')) if x == cell])
            # print(f'cell{cell}, qty:{qty}')
            if qty > 0:
                # gaSet['dut_fam']['cell'] = str(qty)+'.'+cell
                gaSet['dut_fam']['cell'] = {
                    'cell': cell,
                    'qty': qty
                }

        if re.search(r'\.G\.', dutInitName) is not None:
            gaSet['dut_fam']['gps'] = 'G'
        else:
            gaSet['dut_fam']['gps'] = 0

        if re.search(r'\.WF\.', dutInitName) is not None:
            gaSet['dut_fam']['wifi'] = 'WF'
        else:
            gaSet['dut_fam']['wifi'] = 0

        if re.search(r'GO\.', dutInitName) is not None:
            gaSet['dut_fam']['dryCon'] = 'GO'
        else:
            gaSet['dut_fam']['dryCon'] = 'FULL'

        gaSet['dut_fam']['lora'] = {'lora': 0}
        if re.search(r'\.LR1\.', dutInitName) is not None:
            gaSet['dut_fam']['lora'] = {
                'lora': 'LR1',
                'region': 'eu433',
                'band': 'EU 433'
            }
        elif re.search(r'\.LR2\.', dutInitName) is not None:
            gaSet['dut_fam']['lora'] = {
                'lora': 'LR2',
                'region': 'eu868',
                'band': 'EU 863-870'
            }
        elif re.search(r'\.LR3\.', dutInitName) is not None:
            gaSet['dut_fam']['lora'] = {
                'lora': 'LR3',
                'region': 'au915',
                'band': 'AU 915-928 Sub-band 2'
            }
        elif re.search(r'\.LR4\.', dutInitName) is not None:
            gaSet['dut_fam']['lora'] = {
                'lora': 'LR4',
                'region': 'us902',
                'band': 'US 902-928 Sub-band 2'
            }
        elif re.search(r'\.LR6\.', dutInitName) is not None:
            gaSet['dut_fam']['lora'] = {
                'lora': 'LR6',
                'region': 'as923',
                'band': 'AS 923-925'
            }

        m = re.search('\.(PLC|PLCD|PLCGO)\.', dutInitName)
        if m is not None:
            gaSet['dut_fam']['plc'] = m.group(1)
        else:
            gaSet['dut_fam']['plc'] = 0

        if re.search(r'\.2R\.', dutInitName) is not None:
            gaSet['dut_fam']['mem'] = 2
        else:
            gaSet['dut_fam']['mem'] = 1

        # print(f'retrive_dut_fam {gaSet["dut_fam"]}')
        print_gaSet(f'retrive_dut_fam {dutInitName}:', gaSet, "dut_fam")

    def build_tests(self, gaSet, *args):
        # print(f'build_tests {self} gaSet {args}')
        Gen.retrive_dut_fam(Gen, gaSet)

        test_names_lst = ['UsbTree', 'MicroSD', 'SOC_Flash_Memory', 'SOC_i2C']
        test_names_lst += ['BrdEeprom', 'DryContactAlarm', 'ID']

        if gaSet['dut_fam']['cell']['cell'] != 0:
            if gaSet['dut_fam']['cell']['qty'] == 1:
                if gaSet['dut_fam']['cell']['cell'] == "L4":
                    test_names_lst += ['CellularModemL4']
                else:
                    test_names_lst += ['CellularModem']
            elif gaSet['dut_fam']['cell']['qty'] == 2:
                if gaSet['dut_fam']['cell']['cell'] == "L4":
                    test_names_lst += ['CellularDualModemL4']
                else:
                    test_names_lst += ['CellularDualModem']

        test_names_lst += ['DataTransmissionConf', 'DataTransmission']

        if gaSet['dut_fam']['serPort'] != 0:
            # 04/08/2021 16:36:25 test_names_lst += ['SerialPorts']
            ...

        if gaSet['dut_fam']['gps'] != 0:
            # 04/08/2021 16:36:25 test_names_lst += ['GPS']
            ...

        if gaSet['dut_fam']['wifi'] != 0:
            test_names_lst += ['WiFi_2G', 'WiFi_5G']

        if gaSet['dut_fam']['lora']['lora'] != 0:
            test_names_lst += ['LoRa']

        if gaSet['dut_fam']['poe'] != 0:
            test_names_lst += ['POE']

        if gaSet['dut_fam']['plc'] != 0:
            test_names_lst += ['PLC']

        if gaSet['dut_fam']['cell']['cell'] != 0:
            test_names_lst += ['LteLeds']

        test_names_lst += ['FrontPanelLeds', 'Factory_Settings', 'SSH', 'Mac_BarCode']

        ind = 1
        numbered_list = []
        for te in test_names_lst:
            numbered_list.append(f'{ind}..{te}')
            ind += 1

        gui_sf1p.Toolbar.cb1.config(values=numbered_list, height=1 + len(numbered_list))
        gui_sf1p.Toolbar.var_start_from.set(numbered_list[0])

        # return numbered_list





def show_log():
    webbrowser.open(r'C:\logs\updates.txt')


def openHistory():
    new = 2  # open in a new tab, if possible
    url = "history.html"
    webbrowser.open(url, new=new)


def copy_inits_to_testers():
    si_ob = rl_autosync.SyncInits(hosts_list="at-etx1p-1-10", inits_path='AT-ETX1P/software/uutInits',
                      user_def_path='AT-ETX-2i-10G/ConfFiles/Default', rtemp_path="R://IlyaG/Etx1P"
                      )
    si_ob.check_hosts()
    si_ob.sync_folders()
    if len(si_ob.files):
        si_ob.send_mail()
    ctypes.windll.user32.MessageBoxW(0, si_ob.msg, "Sync Inits", 0x00 | 0x40 | 0x0)


def gui_Power(gaSet, pair, state):
    print(f"gui_Power {pair}, {state}")
    power(gaSet, pair, state)


def gui_PowerOffOn(gaSet, pair):
    gui_Power(gaSet, pair, 0)
    time.sleep(2)
    gui_Power(gaSet, pair, 1)


def gui_MuxMngIO(chan):
    print(f"gui_MuxMngIO {chan}")


def open_teraterm(gaSet, comName):
    com = gaSet[comName][3:] # COM8 -> 8 (cut off COM)
    print(f"open_teraterm comName:{comName}, com:{com}")

    command = os.path.join('C:/Program Files (x86)', 'teraterm', 'ttermpro.exe')
    command = str(command) + ' /c=' + str(com) + ' /baud=115200'
    # os.startfile(command)
    subprocess.Popen(command)
    print(command)


def save_init(dicti, gui_num=1):
    host = socket.gethostname()
    Path(host).mkdir(parents=True, exist_ok=True)
    ini_file = Path(os.path.join(host, "init." + str(gui_num) + ".json"))

    di = {}
    try:
        # di['geom'] = "+" + str(dicti['root'].winfo_x()) + "+" + str(dicti['root'].winfo_y())
        di['geom'] = get_xy(dicti['root'])
        di['dutFullName'] = dicti['dutFullName']
        di['dutInitName'] = dicti['dutInitName']
    except:
        di['geom'] = "+230+230"

    try:
        with open(ini_file, 'w') as fi:
            json.dump(di, fi, indent=2, sort_keys=True)
            # json.dump(gaSet, fi, indent=2, sort_keys=True)
    except Exception as e:
        print(e)
        raise (e)


def read_init(gui_num=1):
    # print(f'read_init script_dir {os.path.dirname(__file__)}')
    host = socket.gethostname()
    Path(host).mkdir(parents=True, exist_ok=True)
    ini_file = Path(os.path.join(host, "init." + str(gui_num) + ".json"))
    # print(f'read_init Path(host) {Path(host)}')
    if os.path.isfile(ini_file) is False:
        dicti = {
            'eraseTitle': 0,
            'geom': '+210+210'
        }
        save_init(dicti, gui_num)

    try:
        with open(ini_file, 'r') as fi:
            dicti = json.load(fi)
    except Exception as e:
        # print(e)
        # raise(e)
        raise Exception("e")

    # print(f'read_init {ini_file} {dicti}')
    return dicti


def read_hw_init(gui_num):
    host = socket.gethostname()
    Path(host).mkdir(parents=True, exist_ok=True)
    hw_file = Path(os.path.join(host, f"HWinit.{gui_num}.json"))
    if os.path.isfile(hw_file) == False:
        hw_dict = {
            'comDut': 'COM8',
            'comSer1': 'COM2',
            'comSer2': 'COM6',
            'comSer485': 'COM6',
            'pioBoxSerNum': "FT31CTG9",
        }
        # di = {**hw_dict, **dict2}

        with open(hw_file, 'w') as fi:
            # json.dump(hw_dict, fi, indent=2, sort_keys=True)
            json.dump(hw_dict, fi, indent=2, sort_keys=True)

    try:
        with open(hw_file, 'r') as fi:
            hw_dict = json.load(fi)
    except Exception as e:
        # print(e)
        # raise(e)
        raise Exception("e")

    return hw_dict


def open_rl(gaSet):
    # close_rl(gaSet)
    ret = open_coms_uut(gaSet)
    # if ret == 0:
        # ret = open_pio(gaSet)
        # if ret !=0:
        #     close_coms_uut(gaSet)
    # else:
    #     close_coms_uut(gaSet)
    # print(f'ret of open_rl: {ret}')
    return ret


def open_coms_uut(gaSet):
    ret = rlcom.open_com(gaSet['comDut'], 115200)
    # print(f'ret of open_com: {ret}')
    gaSet['id'] = {}
    if ret:
        gaSet['id']['comDut'] = ret
        return 0
    else:
        gaSet['fail'] = f"Open {gaSet['comDut']} fail"
        return -1

def open_pio(gaSet):
    pio = RL_UsbPio.UsbPio()
    channel = pio.retrive_usb_channel(gaSet['pioBoxSerNum'])
    print(f'gen open_pio channel:{channel}')
    ret = 0
    # list_devs = pio.get_devces()
    # ret = 0
    # print(f'gen open_pio list_devs:{list_devs} len(list_devs):{len(list_devs)}')
    # if len(list_devs)==0:
    #     gaSet['fail'] = "No one free USB PIO device was discovered"
    #     # raise Exception(gaSet['fail'])
    #     ret = -1
    #
    # if ret == 0:
    #     usb_box = None
    #     for usb_box in list_devs:
    #         if usb_box == gaSet['pioBoxSerNum']:
    #             n_cardnumber = 1 + list_devs.index(usb_box)
    #             break
    #
    #     if usb_box is None:
    #         gaSet['fail'] = "USB PIO device gaSet['pioBoxSerNum'] was not discovered"
    #         # raise Exception(gaSet['fail'])
    #         ret = -1

    if ret == 0:
        gaSet['id']['pio'] = {}
        gaSet['id']['pio']['obj'] = pio
        # n_pioport = 1
        # n_portsgroup = 3  # RBA
        # port_id = pio.open_pio(n_pioport, n_portsgroup, n_cardnumber)

        # RLUsbPio::Open $rb RBA $channel
        gaSet['id']['pio']['power'] = {}
        for rb in [1]:
            port_id = pio.open_pio(rb, 'RBA', channel).strip('\r\n')
            gaSet['id']['pio']['power'][rb] = port_id
        print(f"gen open_pio"
              f" gaSet['id']['pio']['obj']:{gaSet['id']['pio']['obj']}"
              f" gaSet['id']['pio']['power']:{gaSet['id']['pio']['power']}")

    print(f"ret of open_pio:{ret}")
    return ret


def close_rl(gaSet):
    close_coms_uut(gaSet)
    # close_pio(gaSet)


def close_coms_uut(gaSet):
    # print(f'gaset before close_coms {gaSet["id"]}')
    try:
        gaSet['id']['comDut'].close()
        try:
            del gaSet['id']['comDut']
        except KeyError:
          pass
    except Exception as er:
        print(f'close_coms_uut error:{er}')
    # print(f'gaset after close_coms {gaSet["id"]}')
    return 0

def close_pio(gaSet):
    print(f'gaSet before close_pio {gaSet["id"]}')
    for rb in [1]:
        RL_UsbPio.UsbPio.close_pio(gaSet['id']['pio']['obj'], gaSet['id']['pio']['power'][rb])
    try:
        del gaSet['id']['pio']
    except Exception as err:
        print(f'close_pio err: {err}')

    # try:
    #     RL_UsbPio.UsbPio.close_pio(gaSet['id']['pio']['obj'], gaSet['id']['pio']['power'])
    #     try:
    #         del gaSet['id']['pio']
    #     except KeyError:
    #         pass
    #     # try:
    #     #     del gaSet['id']['pio']['power']
    #     # except KeyError:
    #     #     pass
    #
    # except Exception as er:
    #     print(f'close_pio error:{er}')

    print(f'gaset after close_pio {gaSet["id"]}')
    return 0


def my_send(gaSet, port, sent, exp, time_out=10):
    ser = gaSet['id'][port]
    exp = exp.replace('(', '\(')
    exp = exp.replace(')', '\)')
    start = time.time()
    res = rlcom.send(ser, sent, exp, time_out)
    dur = time.time() - start
    sent = sent.replace('\r', '\\r')
    sent = sent.replace('\n', '\\n')

    # rlcom.buffer = re.sub(r'\s+', " ", rlcom.buffer)
    print(f'my_send {my_time()} port:{port} com:{ser.port} dur:{round(dur, 2)}sec sent:{sent} '
          f'expected:{exp} res:{res} buffer:_{rlcom.buffer}_')
    # gaSet['puts_log'].info(f'my_send port:{port} dur:{round(dur, 2)}sec sent:{sent} '
    #       f'expected:{exp} res:{res} buffer:_{rlcom.buffer}_')
    return res


# since rlcom.read returns bytes, I convert it to str using utf-8 encoding
# the function returns received buffer as string
def my_read(gaSet, port):
    ser = gaSet['id'][port]
    res = str(rlcom.read(ser), 'utf-8')
    # res = re.sub(r' ', " ", res)
    # res.replace(' ', "")
    # print(f'{my_time()} my_read port:{port} buffer:_{res}_') #rlcom.buffer
    return res


def my_time():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def power(gaSet, ps, value):
    # if 'puts_log' in gaSet:
    #     gaSet['puts_log'].info(f'Power PS-{ps} -> {value}')
    # else:
    #     print(f'{my_time()} Power PS-{ps} -> {value}')
    print(f'{my_time()} Power PS-{ps} -> {value}')
    # print(f"power {gaSet['id']['pio']}")
    # RL_UsbPio.UsbPio.set_pio(gaSet['id']['pio']['obj'], gaSet['id']['pio']['power'][ps], state)
    pio = RL_UsbPio.UsbPio()
    channel = pio.retrive_usb_channel(gaSet['pioBoxSerNum'])
    # print(f'gen power channel:{channel}')

    group = 'RBA'
    ret = RL_UsbPio.UsbPio.osc_pio(pio, channel, ps, group, value)
    # print(f'gen power ret:{ret}')
    # ret = RL_UsbPio.UsbPio.osc_pio(pio, channel, 1, "PORT", "10101010", "00000000")
    # print(f'gen power ret:{ret}')
    # ret = RL_UsbPio.UsbPio.osc_pio(pio, channel, 1, "PORT", "get", "11111111")
    # print(f'gen power ret:{ret}')
    return 0


def ftp_verify_no_report(fil):
    gui_sf1p.App.my_statusbar.sstatus("Waiting for report file delete")
    start_sec = time.time()
    while True:
        res = lib_ftp.file_exist(fil)
        run_dur = int(time.time() - start_sec)
        print(f'FtpVerifyNoReport runDur:{run_dur} res:{res}')
        if run_dur > 120:
            ret = f'{fil} still exists on the FTP'
            break
        if res is False:
            ret = 0
            break
        time.sleep(10)
    return ret


def ftp_verify_report_exist(fil):
    gui_sf1p.App.my_statusbar.sstatus("Waiting for report file create")
    start_sec = time.time()
    while True:
        res = lib_ftp.file_exist(fil)
        run_dur = int(time.time() - start_sec)
        print(f'FtpVerifyReportExist runDur:{run_dur} res:{res}')
        if run_dur > 120:
            ret = f"{fil} still doesn't exists on the FTP"
            break
        if res is True:
            ret = 0
            break
        time.sleep(10)
    return ret


def create_loggers(gaSet):
    log_file = gaSet['log'][gaSet['gui_num']]
    file_log = logging.getLogger('mylogger')
    file_log.level = logging.INFO
    file_handler = logging.FileHandler(log_file, mode='a')
    formatter = logging.Formatter('%(asctime)s %(message)s')
    file_handler.setFormatter(formatter)
    file_log.addHandler(file_handler)

    # puts_log = logging.getLogger('putslogger')
    # puts_log.level = logging.INFO
    # puts_handler = logging.StreamHandler()
    # puts_handler.setFormatter(formatter)
    # puts_log.addHandler(puts_handler)

    gaSet['file_log'] = file_log
    gaSet['file_handler'] = file_handler
    # gaSet['puts_log'] = puts_log
    # gaSet['puts_handler'] = puts_handler
    return None


def close_loggers(gaSet):
    gaSet['file_handler'].close()
    gaSet['file_log'].removeHandler(gaSet['file_handler'])
    # gaSet['puts_handler'].close()
    # gaSet['puts_log'].removeHandler(gaSet['puts_handler'])
    logging.shutdown()

#
# print_gaSet('ButRun finally:', self.gaSet)
# print_gaSet('retrive_dut_fam:', gaSet, "dut_fam")
#
def print_gaSet(where, gaSet, spec='all'):
    print(f'\n{my_time()} ', where)
    for key in sorted(gaSet.keys()):
        if spec != 'all' and key != spec:
            continue
        try:
            items = gaSet[key].items()
        except:
            print(key, gaSet[key])
        else:
            for sub_key in sorted(gaSet[key].keys()):
                print(key, sub_key, gaSet[key][sub_key])


def parse_sw(gaSet):
    a, b, c, d = gaSet['SWver'].split(".")
    if a == 5 and b == 0 and c == 0 and d <= 999:
        return 'Safari'
    return "General"


# class SyncInits():
#     def __init__(self, hosts_list, inits_path, user_def_path=None, rtemp_path="R://IlyaG"):
#         self.hosts_list = ["jateteam-hp-10"]
#         self.hosts_list += [hosts_list]  # ("at-etx1p-1-10",  "jateteam-hp-10")
#         self.email_addrs = ["ilya_g@rad.com"]
#         self.inits_path = inits_path  # 'AT-ETX1P/software/uutInits'
#         self.user_def_path = user_def_path  # 'AT-ETX-2i-10G/ConfFiles/Default'
#         self.rtemp_path = rtemp_path  # "R://IlyaG/Etx1P"
#         self.inits_dests = []
#         self.user_def_dests = []
#         self.un_updated_hosts = []
#         self.msg = ''
#         self.files = []
#
#     def check_hosts(self):
#         for host in self.hosts_list:
#             if host != socket.gethostname():
#                 dest = "//" + host + "/" + "c$/" + self.inits_path
#                 # print(f'check_hosts {dest}, {os.path.isdir(dest)}, {os.path.exists(dest)}')
#                 if os.path.exists(dest):
#                     self.inits_dests += [dest]
#                     if self.user_def_path is not None and self.user_def_path != "":
#                         dest = "//" + host + "/" + "c$/" + self.user_def_path
#                         # print(f'check_hosts {dest}, {os.path.isdir(dest)}, {os.path.exists(dest)}')
#                         if os.path.exists(dest):
#                             if dest not in self.user_def_dests:
#                                 self.user_def_dests += [dest]
#                         else:
#                             if host not in self.un_updated_hosts:
#                                 self.un_updated_hosts += [host]
#                 else:
#                     self.un_updated_hosts += [host]
#
#             print(f'check_hosts inits_dests:{self.inits_dests} user_def_dests:{self.user_def_dests} un_updated_hosts:{self.un_updated_hosts}')
#
#         if len(self.un_updated_hosts):
#             self.msg += "The following PCs are not reachable:\n"
#             for h in self.un_updated_hosts:
#                 self.msg += h+'\n'
#
#         return True
#
#     def sync_folders(self):
#         self.sync_init_files()
#         self.sync_user_def_files()
#
#     def sync_init_files(self):
#         files = []
#         if len(self.inits_dests):
#             # src = 'c://'+self.inits_path
#             # rtemp = self.rtemp_path + "/inits"
#
#             for dest in self.inits_dests:
#                 files += sync('c://'+self.inits_path, dest, "sync", verbose=False, create=True)
#                 self.files += files
#                 if len(files):
#                     self.msg += '\n\n The following Inits were updated:\n'
#                 else:
#                     self.msg += '\n\n No Init files were copied\n'
#
#             self.copy_files_to_rtemp(files, self.rtemp_path + "/inits")
#
#     def sync_user_def_files(self):
#         files = []
#         if len(self.user_def_dests):
#             # src = 'c://'+self.user_def_path
#             # rtemp = self.rtemp_path + "/userDefs"
#             for dest in self.user_def_dests:
#                 files += sync('c://'+self.user_def_path, dest, "sync", verbose=False, create=True)
#                 self.files += files
#                 if len(files):
#                     self.msg += '\n\n The following User Default Files were updated:\n'
#                 else:
#                     self.msg += '\n No User Default Files were copied\n'
#
#             self.copy_files_to_rtemp(files, self.rtemp_path + "/userDefs")
#
#                 # for fil in files:
#                 #     if os.path.isfile(fil):
#                 #         Path(rtemp).mkdir(parents=True, exist_ok=True)
#                 #         status = subprocess.check_output(f'copy \"{fil}\", \"{rtemp}\"', shell=True)
#                 #         print(f'sync_folders src:{src}, dest:{dest}, fil:{fil}, status:{status}')
#                 #         self.msg += os.path.basename(fil) + '\n'
#
#     def copy_files_to_rtemp(self, files, rtemp):
#         for fil in files:
#             if os.path.isfile(fil):
#                 Path(rtemp).mkdir(parents=True, exist_ok=True)
#                 subprocess.check_output(f'copy \"{fil}\", \"{rtemp}\"', shell=True)
#                 self.msg += os.path.basename(fil)+'\n'
#         return None
#
#     def send_mail(self):
#         msg = EmailMessage()
#         cont = f'file://{self.rtemp_path}\n\r'
#         # cont += self.msg
#         for fi in self.files:
#             cont += os.path.basename(fi)+'\n\r'
#         msg.set_content(cont)
#         msg['Subject'] = f'{socket.gethostname().upper()}: Message from Tester'
#         msg['From'] = os.getlogin() + '@rad.com'
#         msg['To'] = self.email_addrs[0]
#
#         s = smtplib.SMTP('exrad-il.ad.rad.co.il')
#         s.send_message(msg)
#         s.quit()


if __name__ == "__main__":
    pass
    # si_ob = SyncInits(hosts_list="at-etx1p-1-10", inits_path='AT-ETX1P/software/uutInits',
    #                   user_def_path='AT-ETX-2i-10G/ConfFiles/Default', rtemp_path="R://IlyaG/Etx1P"
    #                   )
    # si_ob.check_hosts()
    # si_ob.sync_folders()
    # if len(si_ob.files):
    #     si_ob.send_mail()
    # ctypes.windll.user32.MessageBoxW(0, si_ob.msg, "Sync Inits", 0x00 | 0x40 | 0x0)


