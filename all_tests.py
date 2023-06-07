""" Class of all Tests"""
import re
import time

import lib_gen_sf1p as lgen
# import gui_sf1p
from lib_put_sf1p import Put
# from RL import RL_UsbPio as usbpio
from gui_sf1p import App, Toolbar, MenuBar
import lib_ftp
import lib_barcode
import RL


class AllTests():
    def __init__(self, gaSet):
        self.gaSet = gaSet
        self.put = Put(self.gaSet)

    def stam_tst(self):
        # put = Put(self.gaSet)
        ret = self.put.login_2_app()
        if ret == 0:
            # ret = Put.login_2_linux(Put, gaSet)
            # ret = Put.read_eth_port_status(Put, gaSet, 3)
            # ret = put.read_utp_port_status(3)
            ret = self.put.read_wan_lan_status()
        # ret = -1
        return ret

    def stam_tst2(self):
        # put = Put(self.gaSet)
        ret = self.put.login_2_app()
        if ret == 0:
            ret = self.put.read_wan_lan_status()
        # ret = -1
        return ret

    def ftp_tst(gaSet):
        fil = 'wifireport_at-etx1p-1-10_2.txt'
        fil = '2021.09.01-10.27.29-abcd123.txt'
        ret = lgen.ftp_verify_report_exist(fil)
        print(f'ftp_tst ret:{ret}')

        fil = '2021.09.01-10.27.29-abcd123.txt'
        ret = lib_ftp.upload_file(fil)
        print(f'ftp_tst ret:{ret}')
        return ret

    def WiFi_2G(gaSet):
        # return 0
        lgen.power(gaSet, 1, 0)
        time.sleep(4)
        lgen.power(gaSet, 1, 1)

        fil = f"startMeasurement_{gaSet['wifi_net']}"
        ret = lib_ftp.delete_file(fil)
        # gaSet['puts_log'].info(f'File "{fil}" deleted from FTP')
        print(f"{lgen.my_time()}File '{fil}' deleted from FTP")

        fil = f"wifireport_{gaSet['wifi_net']}"
        ret = lib_ftp.delete_file(fil)
        # gaSet['puts_log'].info(f'File "{fil}" deleted from FTP')
        print(f"{lgen.my_time()}File '{fil}' deleted from FTP")

        return 0

    def Mac_BarCode(self):
        if self.gaSet['dut_fam']['cell']['cell'] != 0:
            if self.gaSet['dut_fam']['cell']['qty'] == 1:
                try:
                    imei1 = self.gaSet['dut_fam']['cell']['imei1']
                except:
                    self.gaSet['fail'] = f'No IMEI-1 was read'
                    return -1
            elif self.gaSet['dut_fam']['cell']['qty'] == 2:
                try:
                    imei1 = self.gaSet['dut_fam']['cell']['imei1']
                except:
                    self.gaSet['fail'] = f'No IMEI-1 was read'
                    return -1
                try:
                    imei2 = self.gaSet['dut_fam']['cell']['imei2']
                except:
                    self.gaSet['fail'] = f'No IMEI-2 was read'
                    return -1
        return lib_barcode.reg_id_barcode(self.gaSet)

    def UsbTree(self):
        com = 'comDut'
        lgen.my_send(self.gaSet, com, '\r', 'stam', 0.25)
        lgen.my_send(self.gaSet, com, '\r', 'stam', 0.25)
        # put = Put(self.gaSet)
        if re.search('PCPE>', RL.rl_com.buffer):
            ret = 0
        else:
            ret = self.put.pwr_rst_login_2_boot()

        if ret == 0:
            ret = self.put.usb_tree_perform()

        return ret

    def MicroSD(self):
        com = 'comDut'
        lgen.my_send(self.gaSet, com, '\r', 'stam', 0.25)
        lgen.my_send(self.gaSet, com, '\r', 'stam', 0.25)
        # put = Put(self.gaSet)
        if re.search('PCPE>', RL.rl_com.buffer):
            ret = 0
        else:
            ret = self.put.pwr_rst_login_2_boot()

        if ret == 0:
            ret = self.put.micro_sd_perform()

        return ret

    def SOC_Flash_Memory(self):
        com = 'comDut'
        lgen.my_send(self.gaSet, com, '\r', 'stam', 0.25)
        lgen.my_send(self.gaSet, com, '\r', 'stam', 0.25)
        # put = Put(self.gaSet)
        if re.search('PCPE>', RL.rl_com.buffer):
            ret = 0
        else:
            ret = self.put.pwr_rst_login_2_boot()

        if ret == 0:
            ret = self.put.soc_flash_perform()

        return ret

    def SOC_i2C(self):
        com = 'comDut'
        lgen.my_send(self.gaSet, com, '\r', 'stam', 0.25)
        lgen.my_send(self.gaSet, com, '\r', 'stam', 0.25)
        # put = Put(self.gaSet)
        if re.search('PCPE>', RL.rl_com.buffer):
            ret = 0
        else:
            ret = self.put.pwr_rst_login_2_boot()

        if ret == 0:
            ret = self.put.soc_2ic_perform()

        return ret

    def BrdEeprom(self):
        # put = Put(self.gaSet)
        ret = self.put.brd_eeprom_perform()
        return ret

    def ID(self):
        ret = self.put.id_perform("ID")
        if ret != 0:
            return ret

        ret = self.put.read_wan_lan_status()
        if ret != 0:
            return ret

        ret = self.put.read_boot_params()
        return ret


    def testing_loop(self):
        # print(f"testing_loop gui_sf1v.Toolbar.cb1.cget('values')")


        # gaSet['file_log'].info('********* DUT start *********')

        # '1..BrdEeprom' '1..WiFi_2G', '2..Mac_BarCode' ['ftp_tst']:  # 'stam_tst', gui_sf1v.Toolbar.cb1.cget('values')

        tests = Toolbar.cb1.cget('values')
        for tst in tests[tests.index(Toolbar.var_start_from.get()):]:
            App.curr_tst.set(tst)
            tst = tst.split('..')[1]
            self.gaSet['file_log'].info(f"Test '{tst}' started")
            # self.gaSet['puts_log'].info(f"Test '{tst}' started")
            print(f"\n{lgen.my_time()} Test '{tst}' started")
            # ret = getattr(AllTests, tst)(self.gaSet)
            ret = getattr(AllTests, tst)(self)
            if ret == 0:
                ret_txt = f'PASS'
            else:
                ret_txt = f"FAIL. Reason: {self.gaSet['fail']}"

            self.gaSet['file_log'].info(f"Test '{tst}' {ret_txt}")
            # self.gaSet['puts_log'].info(f"Test '{tst}' {ret_txt}")
            print(f"{lgen.my_time()} Test '{tst}' {ret_txt}\n")

            if ret != 0:
                break

            if MenuBar.one_tst.get() == 1:
                MenuBar.one_tst.set(0)
                ret = 1
                break

        if ret == 0:
            self.gaSet['file_log'].info(f"All tests pass")

        return ret




