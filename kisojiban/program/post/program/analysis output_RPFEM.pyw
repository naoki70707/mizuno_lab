##############################################################
### 基礎地盤コンサルタンツ株式会社 ##############################
### 剛塑性有限要素法解析のためのポスト処理用ファイル作成 ##########
##############################################################
### 作成者 : 岐阜工業高等専門学校 環境都市工学科 水野和憲研究室 ###
### 作成日 : 令和４年 ３月 １４日 ###############################
##############################################################
"""
●システム作成の背景
 基礎地盤コンサルタンツ株式会社で剛塑性有限要素法解析を使用したい 。
●システム内容
 基礎地盤コンサルタンツ株式会社で使用しているメッシュ作成ソフト（MESH2）で作成したMSHファイルを剛塑性有限要素法解析の入力データファイル2Dyouso.datに変換する 。
●作成した関数一覧
file_create(lines, path_new)
    第一引数 : result.dの中身を格納した一次元配列 、第二引数 : 作成ファイルのパス
"""

import datetime
import os

import numpy as np
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox

def read_model(lines):
    """
        モデルの情報を読込
    """
    global npm
    global nem
    global nbm
    model_data_info = lines[[i for i, line in enumerate(lines) if '[Model data]' in line][0] + 1]
    npm = int(model_data_info.split()[1]) # 全節点数
    nem = int(model_data_info.split()[3]) # 全要素数
    nbm = int(model_data_info.split()[5]) # 全拘束数


    return npm, nem, nbm



"""
    以下 、座標の情報を読込
"""
def read_node(lines):
    node = np.zeros([2, npm], dtype=np.float64) # 節点の座標値
    coord_data_initRow = int([i for i, line in enumerate(lines) if 'node location' in line][0]) + 2
    for i, num in enumerate(range(coord_data_initRow, coord_data_initRow+npm, 1)):
        node[0, i] = float(lines[num].split()[-2])
        node[1, i] = float(lines[num].split()[-1])
    return node

"""
    以下 、要素を構成する接点の情報を読込
"""
def read_element(lines):
    nod = 4 # 1つの要素を構成する接点の数（マップド4コーナー）
    element = np.zeros([nod+1, nem], dtype=np.int64) # 要素情報
    element_data_initRow = int([i for i, line in enumerate(lines) if 'node condition(local-total)' in line][0]) + 2
    for i, num in enumerate(range(element_data_initRow, element_data_initRow+nem, 1)):
        element[0,i] = int(lines[num].split()[-5]) #node_1
        element[1,i] = int(lines[num].split()[-4]) #node_2
        element[2,i] = int(lines[num].split()[-3]) #node_3
        element[3,i] = int(lines[num].split()[-2]) #node_4
        element[4,i] = int(lines[num].split()[-6]) #section number

    return element

"""
    変位速度
"""
def create_displacement(lines):
    disx = np.zeros(npm, dtype=np.float64) # x方向の変位
    disy= np.zeros(npm, dtype=np.float64) # y方向の変位
    dis= np.zeros(npm, dtype=np.float64) # xy方向の変位
    displacement_data_initRow = int([i for i, line in enumerate(lines) if 'Total velocity displacement' in line][0]) + 2
    
    for i, num in enumerate(range(displacement_data_initRow, displacement_data_initRow+npm, 1)):
        disx[i] = float(lines[num].split()[-2])
        disy[i] = float(lines[num].split()[-1])
        dis[i] = np.sqrt(disx[i]**2 + disy[i]**2)
    
    return disx, disy, dis

"""
    32. 等価ひずみ速度
"""
def create_strain(lines):
    strx = np.zeros(nem, dtype=np.float64)
    stry = np.zeros(nem, dtype=np.float64)
    sig = np.zeros(nem, dtype=np.float64)
    strain_data_initRow = int([i for i, line in enumerate(lines) if 'No   strain-x-      -y-        -z-        -xy-' in line][0]) + 1
    
    for i, num in enumerate(range(strain_data_initRow, strain_data_initRow+nem, 1)):
        strx[i] = float(lines[num][5:17])
        stry[i] = float(lines[num][17:29])
        strxy = float(lines[num][41:53])
        sig[i] = np.sqrt(strx[i]**2 + stry[i]**2 + 0.5*strxy**2)
    
    return strx, stry, sig


"""
    40. 応力の第一不変量
"""
def create_PI1(liens):
    pi1 = np.zeros(nem, dtype=np.float64)
    pi1_data_initRow = int([i for i, line in enumerate(lines) if 'No.      -I1-        -SJ2- ' in line][0]) + 1

    for i, num in enumerate(range(pi1_data_initRow, pi1_data_initRow+nem, 1)):
        pi1[i] = float(lines[num].split()[1])
    
    return pi1
"""
    41. 偏差応力の第二不変量
"""
def create_SJ2(lines):
    SJ2 = np.zeros(nem, dtype=np.float64)
    SJ2_data_initRow = int([i for i, line in enumerate(lines) if 'No.      -I1-        -SJ2- ' in line][0]) + 1
    for i, num in enumerate(range(SJ2_data_initRow, SJ2_data_initRow+nem, 1)):
        SJ2[i] = float(lines[num].split()[2])
    
    return SJ2

"""
    42.  平均応力
"""
def create_p(lines):
    p = np.zeros(nem, dtype=np.float64)
    p_data_initRow = int([i for i, line in enumerate(lines) if 'No.      -I1-        -SJ2- ' in line][0]) + 1

    for i, num in enumerate(range(p_data_initRow, p_data_initRow+nem, 1)):
        p[i] = float(lines[num].split()[1]) / 3
    
    return p

"""
    43. 降伏関数
"""
def create_yield(lines):
    yield_ = np.zeros(nem, dtype=np.float64)
    yield_data_initRow = int([i for i, line in enumerate(lines) if 'No.  Yield Function' in line][0]) + 1
    for i, num in enumerate(range(yield_data_initRow, yield_data_initRow+nem, 1)):
        yield_[i] = float(lines[num].split()[1])
    
    return yield_
"""
    44. Druker-Prager降伏関数の係数
"""
def create_gkei(lines):
    gkei = np.zeros(nem, dtype=np.float64)
    gkei_data_initRow = int([i for i, line in enumerate(lines) if 'No.      gkei' in line][0]) + 1
    for i, num in enumerate(range(gkei_data_initRow, gkei_data_initRow+nem, 1)):
        gkei[i] = float(lines[num].split()[1])
    
    return gkei
   


"""
    以下 、Datファイルに書込
"""
def create_file(path_new, node, element, npm, nem, nbm, disx, disy, dis, sig, pi1, SJ2, p, yield_, gkei):
    file = open(path_new, "w", encoding='CP932')
    file.write("#TPTMS10\n\n")
    # file.write("[ATTRIBUTE]\n")
    file.write("[ITEM]\n")
    file.write("  X方向の変位ひずみ={-1, 1}\n")
    file.write("  Y方向の変位ひずみ={-1, 2}\n")
    file.write("  変位速度={-1, 3}\n")
    file.write("  等価ひずみ速度={0, 0}\n")
    file.write("  応力の第一不変量={0, 1}\n")
    file.write("  偏差応力の第二不変量={0, 2}\n")
    file.write("  平均応力={0, 3}\n")
    file.write("  降伏関数={0, 4}\n")
    file.write("  Prager降伏関数の係数={0, 5}\n")

    file.write("[NODE]\n")
    for i in range(npm):
        file.write("  {node}={{{x}, {y}}}\n".format(node=i+1, x=node[0, i], y=node[1, i]))

    file.write("[ELEMENT]\n")
    for i in range(nem):
        file.write("  {element}={{{x1}, {x2}, {x3}, {x4}}}\n".format(element=element[4][i], x1=element[0][i], x2=element[1][i], x3=element[2][i], x4=element[3][i]))

    file.write("[STEP]\n")
    file.write("time=0.0\n")
    file.write('procname="最終"\n')
    file.write("X方向の変位ひずみ={{{}}}\n".format(",".join([str(i) for i in disx])))
    file.write("Y方向の変位ひずみ={{{}}}\n".format(",".join([str(i) for i in disy])))
    file.write("変位速度={{{}}}\n".format(",".join([str(i) for i in dis])))
    file.write("等価ひずみ速度={{{}}}\n".format(",".join([str(i) for i in sig])))
    file.write("応力の第一不変量={{{}}}\n".format(",".join([str(i) for i in pi1])))
    file.write("偏差応力の第二不変量={{{}}}\n".format(",".join([str(i) for i in SJ2])))
    file.write("平均応力={{{}}}\n".format(",".join([str(i) for i in p])))
    file.write("降伏関数={{{}}}\n".format(",".join([str(i) for i in yield_])))
    file.write("Druker-Prager降伏関数の係数={{{}}}\n".format(",".join([str(i) for i in gkei])))

    file.close()

def create_seepage(lines, nem, num):
    SE = {}
    PH = {}
    GH = {}
    HH = {}
    FLOW = {}
    for i in range(num):
        list_SE = []
        list_PH = []
        list_GH = []
        list_HH = []
        list_FLOW = []
        time = int(float(lines[(nem + 4) * i + 3].split()[1]))
        for j in range(nem):
            data = lines[(nem + 4) * i + 5 + j].split()
            list_SE.append(data[1])
            list_PH.append(data[2])
            list_GH.append(data[3])
            list_HH.append(data[4])
            list_FLOW.append(data[5])
        SE[time] = list_SE      
        PH[time] = list_PH      
        GH[time] = list_GH      
        HH[time] = list_HH      
        FLOW[time] = list_FLOW      
    return SE, PH, GH, HH, FLOW

def create_file_seepage(path_new, node, element, npm, nem, nbm, SE, PH, GH, HH, FLOW):
    file = open(path_new, "w", encoding='CP932')
    file.write("#TPTMS10\n\n")
    # file.write("[ATTRIBUTE]\n")
    file.write("[ITEM]\n")
    file.write("  有効飽和度={0, 0}\n")
    file.write("  圧力水頭={0, 1}\n")
    file.write("  位置水頭={0, 2}\n")
    file.write("  全水頭={0, 3}\n")
    file.write("  流速={0, 4}\n")

    file.write("[NODE]\n")
    for i in range(npm):
        file.write("  {node}={{{x}, {y}}}\n".format(node=i+1, x=node[0, i], y=node[1, i]))

    file.write("[ELEMENT]\n")
    for i in range(nem):
        file.write("  {element}={{{x1}, {x2}, {x3}, {x4}}}\n".format(element=element[4][i], x1=element[0][i], x2=element[1][i], x3=element[2][i], x4=element[3][i]))

    for time in SE.keys():

        file.write("[STEP]\n")
        file.write("time={}\n".format(time))
        file.write('procname="{}"\n'.format(time))

        file.write("有効飽和度={{{}}}\n".format(",".join([str(i) for i in SE[time]])))
        file.write("圧力水頭={{{}}}\n".format(",".join([str(i) for i in PH[time]])))
        file.write("位置水頭={{{}}}\n".format(",".join([str(i) for i in GH[time]])))
        file.write("全水頭={{{}}}\n".format(",".join([str(i) for i in HH[time]])))
        file.write("流速={{{}}}\n".format(",".join([str(i) for i in FLOW[time]])))

    file.close()

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("420x220")
        self.title("[RPFEM解析] result.d を TXTに変換")
        self.create_widgets()
    
    def create_widgets(self):
        self.labelframe = tk.LabelFrame(self.master, text = "出力結果を選択してください")
        self.radio_value = tk.IntVar(value = 0)
        self.radio1 = tk.Radiobutton(self.labelframe, text = "剛塑性有限要素解析", variable = self.radio_value, value = 0, command=self.switch_state)
        self.radio2 = tk.Radiobutton(self.labelframe, text = "浸透流解析", variable = self.radio_value, value = 1, command=self.switch_state2)
        self.radio1.grid(row=1, column=1)
        self.radio2.grid(row=1, column=2)
        self.labelframe.place(x=50, y=5, width=240)

        self.label1 = tk.Label(self.master, text = "変換前")
        self.label2 = tk.Label(self.master, text = "浸透流")
        self.label3 = tk.Label(self.master, text = "変換先")
        self.label4 = tk.Label(self.master, text = "説明")

        self.input_box1 = tk.Entry(width=50)
        self.input_box2 = tk.Entry(width=50)
        self.input_box3 = tk.Entry(width=50)
        self.input_box4 = tk.Entry(width=58)
        self.input_box1.insert(0, "result.d を選択してください")
        self.input_box2.insert(0, "out_seepage_element.dを選択してください")
        self.input_box4.insert(0, datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9), 'JST')).strftime('%Y/%m/%d %H:%M:%S'))
        self.read_button1 = tk.Button(self, text='参照', command=lambda: self.file_select(self.input_box1), width=5)
        self.read_button2 = tk.Button(self, text='参照', command=lambda: self.file_select(self.input_box2), width=5)
        self.read_button3 = tk.Button(self, text='参照', command=lambda: self.file_select(self.input_box3), width=5)
        self.input_box2.configure(state='readonly')
        self.read_button2.configure(state='disabled')

        self.label1.place(x=5, y=60)
        self.label2.place(x=5, y=90)
        self.label3.place(x=5, y=120)
        self.label4.place(x=5, y=150)
        self.input_box1.place(x=50, y=60)
        self.input_box2.place(x=50, y=90)
        self.input_box3.place(x=50, y=120)
        self.input_box4.place(x=50, y=150)
        self.read_button1.place(x=360, y=60)
        self.read_button2.place(x=360, y=90)
        self.read_button3.place(x=360, y=120)

        self.excute_button = tk.Button(self, text="変換", command=lambda: self.file_read(self.input_box1.get(), self.input_box2.get(), self.input_box3.get()), width=10)
        self.cancel_button = tk.Button(self, text='閉じる', command=self.quit, width=10)
        self.excute_button.place(x=120, y=180)
        self.cancel_button.place(x=220, y=180)

    def switch_state(self):
            self.input_box2.configure(state='readonly')
            self.read_button2.configure(state='disabled')
    def switch_state2(self):
            self.input_box2.configure(state='normal')
            self.read_button2.configure(state='normal')




    def file_select(self, input_box):
        global file_path
        idir = 'C:\\python_test'
        filetype = [("テキストファイル","*.d"), ("テキストファイル","*.dat"), ("テキストファイル","*.txt")]
        file_path = tkinter.filedialog.askopenfilename(filetypes = filetype, initialdir = idir)
        input_box.delete(0, tkinter.END)
        input_box.insert(tkinter.END, file_path)

        if input_box == self.input_box1:
            self.input_box3.delete(0, tkinter.END)
            self.input_box3.insert(tkinter.END, os.path.splitext(file_path)[0]+".dat")
        return file_path

    def file_read(self, path, path_seepage, path_new):
        global lines
        if len(path) == 0:
            tkinter.messagebox.showwarning('確認', 'ファイルが選択されていません')
            return

        if len(path_seepage) == 0:
            tkinter.messagebox.showwarning('確認', 'ファイルが選択されていません')
            return         
        
        if os.path.basename(path) != 'result.d':
            tkinter.messagebox.showwarning('確認', 'result.d が選択されていません')
            return
        
        if os.path.basename(path_seepage) != 'out_seepage_element.d':
            tkinter.messagebox.showwarning('確認', 'out_seepage_element.d が選択されていません')
            return

        with open(path, "r", encoding='CP932') as file:
            lines = file.read().splitlines()
        npm, nem, nbm = read_model(lines)
        node = read_node(lines)
        element = read_element(lines)

        if self.radio_value.get() == 0:
            n = 0
            for line in reversed(lines):
                n += 1
                if "Load factor" in line or "Safety factor" in line:
                    
                    disx, disy, dis = create_displacement(lines) # 変形
                    strx, stry, sig = create_strain(lines) # 等価ひずみ速度
                    pi1 = create_PI1(line) # 応力の第一不変量
                    SJ2 = create_SJ2(lines) # 偏差応力の第二不変量
                    p = create_p(lines) # 平均応力
                    yield_ = create_yield(lines) # 降伏関数
                    gkei = create_gkei(lines) # Druker-Prager降伏関数の係数

                    create_file(path_new, node, element, npm, nem, nbm, disx, disy, dis, sig, pi1, SJ2, p, yield_, gkei)

                    tkinter.messagebox.showinfo('完了', 'ファイルが正しく変換されました')
                    self.quit()
                    return
                elif n == 10:
                    tkinter.messagebox.showerror('エラー', 'ファイルの中身が正しくありません')
                    return
        elif self.radio_value.get() == 1:
            with open(path_seepage, "r", encoding='CP932') as file:
                lines_seepage = file.read().splitlines()

            step_count = lines_seepage.count("   NSTEP & TIME")


        
            SE, PH, GH, HH, FLOW = create_seepage(lines_seepage, nem, step_count) # 有効飽和度, 圧力水頭, 位置水頭, 全水頭, 流速

            create_file_seepage(path_new, node, element, npm, nem, nbm, SE, PH, GH, HH, FLOW)
            tkinter.messagebox.showinfo('完了', 'ファイルが正しく変換されました')
            self.quit()
            return
        else:
            pass
    def quit(self):
       self.destroy()


def main():
    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main()