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

def file_create(lines, path_new):
    """
        モデルの情報を読込
    """
    model_data_info = lines[[i for i, line in enumerate(lines) if '[Model data]' in line][0] + 1]
    npm = int(model_data_info.split()[1]) # 全節点数
    nem = int(model_data_info.split()[3]) # 全要素数
    nbm = int(model_data_info.split()[5]) # 全拘束数

    nod = 4 # 1つの要素を構成する接点の数（マップド4コーナー）

    element = np.zeros([nod+1, nem], dtype=np.int64) # 要素情報
    node = np.zeros([2, npm], dtype=np.float64) # 節点の座標値
    disx = np.zeros(npm, dtype=np.float64) # x方向の変位
    disy= np.zeros(npm, dtype=np.float64) # y方向の変位
    dis= np.zeros(npm, dtype=np.float64) # xy方向の変位
    strx = np.zeros(nem, dtype=np.float64)
    stry = np.zeros(nem, dtype=np.float64)
    sig = np.zeros(nem, dtype=np.float64)

    """
        以下 、座標の情報を読込
    """
    coord_data_initRow = int([i for i, line in enumerate(lines) if 'node location' in line][0]) + 2

    for i, num in enumerate(range(coord_data_initRow, coord_data_initRow+npm, 1)):
        node[0, i] = float(lines[num].split()[-2])
        node[1, i] = float(lines[num].split()[-1])

    """
        以下 、要素を構成する接点の情報を読込
    """
    element_data_initRow = int([i for i, line in enumerate(lines) if 'node condition(local-total)' in line][0]) + 2

    for i, num in enumerate(range(element_data_initRow, element_data_initRow+nem, 1)):
        element[0,i] = int(lines[num].split()[-5]) #node_1
        element[1,i] = int(lines[num].split()[-4]) #node_2
        element[2,i] = int(lines[num].split()[-3]) #node_3
        element[3,i] = int(lines[num].split()[-2]) #node_4
        element[4,i] = int(lines[num].split()[-6]) #section number

    """
        以下 、displacementの情報を読込
    """
    displacement_data_initRow = int([i for i, line in enumerate(lines) if 'Total velocity displacement' in line][0]) + 2
    
    for i, num in enumerate(range(displacement_data_initRow, displacement_data_initRow+npm, 1)):
        disx[i] = float(lines[num].split()[-2])
        disy[i] = float(lines[num].split()[-1])
        dis[i] = np.sqrt(disx[i]**2 + disy[i]**2)

    """
        以下 、応力stressおよび歪みstrainの情報を読込
    """
    strain_data_initRow = int([i for i, line in enumerate(lines) if 'No   strain-x-      -y-        -z-        -xy-' in line][0]) + 1
    
    for i, num in enumerate(range(strain_data_initRow, strain_data_initRow+nem, 1)):
        strx[i] = float(lines[num][5:17])
        stry[i] = float(lines[num][17:29])
        strxy = float(lines[num][41:53])
        sig[i] = np.sqrt(strx[i]**2 + stry[i]**2 + 0.5*strxy**2)

    """
        以下 、Datファイルに書込
    """
    file = open(path_new, "w", encoding='CP932')
    file.write("#TPTMS10\n\n")
    # file.write("[ATTRIBUTE]\n")
    file.write("[ITEM]\n")
    file.write("  X方向変位={-1, 1}\n")
    file.write("  Y方向変位={-1, 2}\n")
    file.write("  変位={-1, 3}\n")
    file.write("  応力={0, 0}\n")

    file.write("[NODE]\n")
    for i in range(npm):
        file.write("  {node}={{{x}, {y}}}\n".format(node=i+1, x=node[0, i], y=node[1, i]))

    file.write("[ELEMENT]\n")
    for i in range(nem):
        file.write("  {element}={{{x1}, {x2}, {x3}, {x4}}}\n".format(element=element[4][i], x1=element[0][i], x2=element[1][i], x3=element[2][i], x4=element[3][i]))

    file.write("[STEP]\n")
    file.write("time=0.0\n")
    file.write('procname="最終"\n')
    file.write("X方向変位={{{}}}\n".format(",".join([str(i) for i in disx])))
    file.write("Y方向変位={{{}}}\n".format(",".join([str(i) for i in disy])))
    file.write("変位={{{}}}\n".format(",".join([str(i) for i in dis])))
    file.write("等価ひずみ速度={{{}}}\n".format(",".join([str(i) for i in sig])))

    file.close()        


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("420x130")
        self.title("[RPFEM解析] result.d を TXTに変換")
        self.create_widgets()
    
    def create_widgets(self):
        self.label1 = tk.Label(self.master, text = "変換前")
        self.label2 = tk.Label(self.master, text = "変換先")
        self.label3 = tk.Label(self.master, text = "説明")

        self.input_box1 = tk.Entry(width=50)
        self.input_box2 = tk.Entry(width=50)
        self.input_box3 = tk.Entry(width=58)
        self.input_box1.insert(0, "result.d を選択してください")
        self.input_box2.insert(0, "")
        self.input_box3.insert(0, datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9), 'JST')).strftime('%Y/%m/%d %H:%M:%S'))
        self.read_button1 = tk.Button(self, text='参照', command=lambda: self.file_select(self.input_box1), width=5)
        self.read_button2 = tk.Button(self, text='参照', command=lambda: self.file_select(self.input_box2), width=5)

        self.label1.place(x=5, y=10)
        self.label2.place(x=5, y=40)
        self.label3.place(x=5, y=70)
        self.input_box1.place(x=50, y=10)
        self.input_box2.place(x=50, y=40)
        self.input_box3.place(x=50, y=70)
        self.read_button1.place(x=360, y=10)
        self.read_button2.place(x=360, y=40)

        self.excute_button = tk.Button(self, text="変換", command=lambda: self.file_read(self.input_box1.get(), self.input_box2.get()), width=10)
        self.cancel_button = tk.Button(self, text='閉じる', command=self.quit, width=10)
        self.excute_button.place(x=120, y=100)
        self.cancel_button.place(x=220, y=100)

    def file_select(self, input_box):
        global file_path
        idir = 'C:\\python_test'
        filetype = [("テキストファイル","*.d"), ("テキストファイル","*.dat"), ("テキストファイル","*.txt")]
        file_path = tkinter.filedialog.askopenfilename(filetypes = filetype, initialdir = idir)
        input_box.delete(0, tkinter.END)
        input_box.insert(tkinter.END, file_path)

        if input_box == self.input_box1:
            self.input_box2.delete(0, tkinter.END)
            self.input_box2.insert(tkinter.END, os.path.splitext(file_path)[0]+".dat")
        return file_path

    def file_read(self, path, path_new):
        global lines
        if len(path) == 0:
            tkinter.messagebox.showwarning('確認', 'ファイルが選択されていません')
            return 
        if os.path.basename(path) != 'result.d':
            tkinter.messagebox.showwarning('確認', 'result.d が選択されていません')
            return
        else:
            with open(path, "r", encoding='CP932') as file:
                lines = file.read().splitlines()
            
            n = 0
            for line in reversed(lines):
                n += 1
                if "Load factor" in line or "Safety factor" in line:
                    file_create(lines, path_new)
                    tkinter.messagebox.showinfo('完了', 'ファイルが正しく変換されました')
                    self.quit()
                    return
                elif n == 10:
                    tkinter.messagebox.showerror('エラー', 'ファイルの中身が正しくありません')
                    return

    def quit(self):
       self.destroy()


def main():
    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main()