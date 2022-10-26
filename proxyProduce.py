from tkinter import *
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter.ttk import Combobox
from threading import Thread
import pyperclip
import requests
import base64


class Produce_Vmess:

    def center_window(self, title, width, height):
        self.root = Tk()
        # 设置标题
        self.root.title(title)
        # 设置图标
        self.root.iconphoto(False, PhotoImage(file='logo.png'))
        # 设置宽度
        self.root['width'] = width
        # 设置高度
        self.root['height'] = height
        # 设置窗口居中
        screenwidth = self.root.winfo_screenwidth()  # 获取显示屏宽度
        screenheight = self.root.winfo_screenheight()  # 获取显示屏高度
        size = '%dx%d+%d+%d' % (width, height, (screenwidth-width)/2,
                                (screenheight-height)/2)  # 设置窗口居中
        self.root.geometry(size)  # 让窗口居中显示

    def set_widget(self):
        # 节点文本框的标签
        self.label_vmess = Label(self.root, text='节点列表 :')
        self.label_vmess.place(x=50, y=20)
        # 清空的按钮
        self.btn_clearscan = Button(
            self.root, text='清空原始节点', command=self.OnBtnClearScan)
        self.btn_clearscan.place(x=500, y=20)
        self.btn_cleartextbox = Button(
            self.root, text='清空生成节点', command=self.OnBtnClearTextbox)
        self.btn_cleartextbox.place(x=660, y=20)
        # 节点文本框
        self.textbox_vmess = scrolledtext.ScrolledText(
            self.root, width=100, height=20, state='disabled')
        self.textbox_vmess.place(x=50, y=60)
        # 原始节点链接输入框的标签
        self.label_scan = Label(self.root, text='原始节点 :')
        self.label_scan.place(x=50, y=350)
        # 原始节点链接的输入框
        self.scan_vmess = Entry(self.root, width=90)
        self.scan_vmess.place(x=120, y=350)
        # 生成节点按钮
        self.btn_produce = Button(self.root, text='生成节点', height=2,
                                  width=20, command=self.OnBtnProduceVmess)
        self.btn_produce.place(x=320, y=420)
        # 退出gui按钮
        self.btn_exit = Button(self.root, text='退出', height=2,
                               width=20, command=self.OnBtnExit)
        self.btn_exit.place(x=600, y=420)
        # 选择cdn的下拉框的标签
        self.label_cdn = Label(self.root, text='设置cdn供应商 :')
        self.label_cdn.place(x=50, y=390)
        # 选择cdn的下拉框
        self.select_cdn = Combobox(self.root, state='readonly', width=15)
        self.select_cdn['value'] = ('cloudflare', 'cloudfront', 'gcore')
        self.select_cdn.current(0)
        self.select_cdn.place(x=50, y=410)
        # 设置生成链接数量的输入框的标签
        self.label_num = Label(self.root, text='设置生成节点数量 :')
        self.label_num.place(x=50, y=440)
        # 设置生成链接数量的下拉框
        self.scan_num = Entry(self.root, width=18)
        self.scan_num.place(x=50, y=460)
        self.scan_num.insert(END, '100')
        # 创建一个弹出菜单

        def popout(event):
            self.menu.post(event.x_root, event.y_root)

        def callback1(event=None):
            self.scan_vmess.event_generate('<<Cut>>')

        def callback2(event=None):
            self.scan_vmess.event_generate('<<Copy>>')

        def callback3(event=None):
            self.scan_vmess.event_generate('<<Paste>>')

        self.menu = Menu(self.root, tearoff=False)
        self.menu.add_command(label='剪切', command=callback1)
        self.menu.add_command(label='复制', command=callback2)
        self.menu.add_command(label='粘贴', command=callback3)
        self.scan_vmess.bind('<Button-3>', popout)

    def OnBtnProduceVmess(self):
        vmess_url = self.scan_vmess.get().strip('\n')
        limit_num = int(self.scan_num.get())

        def execute():
            self.btn_produce.config(state='disabled')

            ip_list = []
            cdn_source = self.select_cdn.current()
            if cdn_source == 0:
                ip_url = 'https://www.cloudflare.com/ips-v4'
                res = requests.get(ip_url)
                ip_list = res.text.split('\n')
            elif cdn_source == 1:
                ip_url = 'https://ip-ranges.amazonaws.com/ip-ranges.json'
                res = requests.get(ip_url)
                for i in eval(res.text)['prefixes']:
                    try:
                        ip_list.append(i['ip_prefix'])
                    except:
                        pass
                ip_list = set(ip_list)
            elif cdn_source == 2:
                ip_url = 'https://api.gcorelabs.com/cdn/public-net-list'
                res = requests.get(ip_url)
                ip_list = eval(res.text)['addresses']

            real_ip_list = []
            for ip_range in ip_list:
                ip_start, range_num = ip_range.split(
                    '/')[0], int(ip_range.split('/')[1])
                for i in range(range_num+1):
                    real_ip_list.append(f'{ip_start[:-1]}{i}')

            vmess_code = vmess_url[8:]
            vmess_dict = eval(base64.b64decode(vmess_code).decode('utf-8'))
            num = 0
            finalvmess = ''
            for ip in real_ip_list:
                new_vmess_dict = vmess_dict
                new_vmess_dict['add'] = ip
                new_vmess_code = base64.b64encode(
                    str(vmess_dict).encode('utf-8')).decode('utf-8')
                new_vmess_url = f'vmess://{new_vmess_code}'
                finalvmess += new_vmess_url + '\n'
                num += 1
                if num >= limit_num:
                    break

            self.textbox_vmess.config(state='normal')
            self.textbox_vmess.insert(END, finalvmess[:-1])
            pyperclip.copy(finalvmess)
            self.textbox_vmess.config(state='disabled')
            messagebox.showinfo(title='提示', message='生成节点已复制到剪切板!')
            self.btn_produce.config(state='normal')

        t = Thread(target=execute)
        t.daemon = True
        t.start()

    def OnBtnExit(self):
        self.root.destroy()

    def OnBtnClearScan(self):
        self.scan_vmess.delete(0, END)

    def OnBtnClearTextbox(self):
        self.textbox_vmess.config(state='normal')
        self.textbox_vmess.delete(0.0, END)
        self.textbox_vmess.config(state='disabled')


if __name__ == '__main__':
    PV = Produce_Vmess()
    PV.center_window('节点生成器', 800, 500)
    PV.set_widget()
    mainloop()
