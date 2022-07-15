##############################################################
### 基礎地盤コンサルタンツ株式会社 ##############################
### 剛塑性有限要素法解析のためのファイル2Dyouso.dat作成 ##########
##############################################################
### 作成者 : 岐阜工業高等専門学校 環境都市工学科 水野和憲研究室 ###
### 作成日 : 令和４年 ３月 １４日 ###############################
##############################################################

"""
● システム作成の背景
 基礎地盤コンサルタンツ株式会社で剛塑性有限要素法解析を使用したい。
●システム内容
 基礎地盤コンサルタンツ株式会社で使用しているメッシュ作成ソフト（MESH2）で作成したMSHファイルを剛塑性有限要素法解析の入力データファイル2Dyouso.datに変換する。
●作成した関数一覧
･get_index(lines, x)
	第一引数 : MSHファイルの中身を格納した一次元配列、第二引数 : 探索する文字列
	戻り値 : 探索した文字列のインデックス番号
･get_data(lines)
	第一引数 : MSHファイルの中身を格納した一次元配列
	戻り値 : 全節点数、全要素数
･read_data(npm, nem, lines)
	第一引数 : 全節点数、第二引数 : 全要素数、第三引数 : MSHファイルの中身を格納した一次元配列
	戻り値 : 節点情報（変数はnode）、要素情報（変数はelement）
	変数node : [節点番号、x座標値、y座標値]
	変数element : [構成節点1, 構成節点2、構成節点3、構成節点4、材料番号]
･devise_data(node, element)
	第一引数 : 節点情報、第二引数 : 要素情報
	戻り値 : 修正後の節点情報、修正後の要素情報
	修正内容 : 要素情報の構成節点の数え方、原点の移動
	※MESH2内に機能があれば不要な関数、その他修正機能があれば、この関数に追記。
･file_create(lines, path_new, dummy_text, q_1, q_2, q_3, q_4, q_5, q_6)
	第一引数 : MSHファイルの中身を格納した一次元配列
	第二引数 : 2Dyouso.datの作成パス、第三引数 : ダミーデータ
	第四引数～第九引数 : ダミーデータ作成のための選択番号

以下、Application(tk.Tk)内での関数
･create_widgets(self)
	・UI（ユーザーインターフェイス）のウィジェットを配置する関数
	・ラジオボタンでの選択に応じて、ダミーデータが作成
･file_select(self, input_box)
	・MSHファイルをエクスプローラーから選択するための関数
	・作成する2Dyouso.datはMSHファイルと同一ディレクトリとなるように自動入力
･file_read(self, path, path_new, q_1, q_2, q_3, q_4, q_5, q_6)
	・MSHファイルの中身を読み込み、中身を確認
"""
import datetime
import os
import sys

import numpy as np
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox

"""
    ダミーデータ
"""
dummy_text = {"edge":
"""     1   0.000d0   0.000d0     1.00000d-5
E    2   0.000d0   0.000d0    1.00000d+10
     1  676  817    1
E    2  701  842    1
""",
              "beam":
"""E    1  1.000d+5  2.000d-1  2.000d+2  1.000d+2  1.000d-1
     1 7702 7703    1      
E    1 7703 7704    1      
  7702        0.00000        0.00000
  7703        0.00000        0.00000
E 7704        0.00000        0.00000
  7702    0    0    0            
  7703    0    0    0            
E 7704    0    0    0            
""",
              "joint":
"""E    1  30.00000  30.00000       20.00000   0.00000
     1   92   93   64   58    1      0.00000         0.000000000000000E+00         0.000000000000000E+00    0
E    2   92   93   64   58    1      0.00000         0.000000000000000E+00         0.000000000000000E+00    0
""",
              "beam_joint":
"""E    1  30.00000  30.00000       20.00000  17.50000
     1 1874 1875 7702 7703    1      0.00000         0.000000000000000E+00         0.000000000000000E+00    1
E    2 1874 1875 7703 7704    1      0.00000         0.000000000000000E+00         0.000000000000000E+00    1
""",
              "loading":
"""     1        0.00000       -1.00000
     2        0.00000       -1.00000
E    3        0.00000       -1.00000
     1    2
E    2    3
     1        0.00000       -1.00000
     2        0.00000       -1.00000
E    3        0.00000       -1.00000
     1    2
E    2    3
     1        0.00000       -1.00000
     2        0.00000       -1.00000
E    3        0.00000       -1.00000
""",
              "water":
"""                   ---Sis---                     ---Sir--- 
    1   0.32700   0.00000
                    ---Se---                     ---Pres--- 
""",
              "seepage":
"""    1    0    0    0    0    0    0    0    0    0
    1.0d-0
E   1  3.600d-4    1.2d-4   0.00000   0.34800   0.00000   5.22000   5.67800
   774        0.00000    5     0.000
   775        0.00000    1     0.000
   776        0.00000    1     0.000
   777        0.00000    0     0.000
E  778        0.00000    0     0.000
        0.00000     0
"""
             }

"""
    配列から指定した文字列を含む行のインデックスを返す関数
"""
def get_index(lines, x):
    idx = [i for i, j in enumerate(lines) if x in j]
    if len(idx) == 1:
        return idx[0]
    elif len(idx) == 0:
        print("ファイル内に［{}］を確認できませんでした".format(x))
        sys.exit()
    else:
        print("ファイルの中身が正しくありません。［{}］を確認してください。".format(x))
        sys.exit()

"""
    全要素数、全節点数を返す関数
"""
def get_data(lines):
    node_row = get_index(lines, "NODE")
    element_row = get_index(lines, "ELEMENT")
    npm = element_row - node_row - 1
    nem = get_index(lines, "END") - element_row - 1 # <---------------要修正
    return npm, nem

"""
    節点の座標、要素の構成節点を取得する関数
    節点の情報を変数node, 要素の情報を変数elementに格納して返す
"""
def read_data(npm, nem, lines):
    nod = 4
    node_row = get_index(lines, "NODE")
    element_row = get_index(lines, "ELEMENT")
    element = np.zeros([nem, nod+1], dtype=np.int64)
    x = np.zeros(npm, dtype=np.float64)
    y = np.zeros(npm, dtype=np.float64)
    node = np.zeros([npm, 3], dtype=np.float64)

    for i, n in enumerate(range(node_row+1, node_row+npm+1, 1)):
        node[i, 0] = int(lines[n].split()[0])
        node[i, 1] = float(lines[n].split()[-2])
        node[i, 2] = float(lines[n].split()[-1])

    node[:, 1] = np.round(node[:, 1] + np.abs(min(node[:, 1])), 4)
    node[:, 2] = np.round(node[:, 2] + np.abs(min(node[:, 2])), 4)
    node = np.array(node)
        
    for i, n in enumerate(range(element_row+1, element_row+nem+1, 1)):
        sep = lines[n].split()
        element[i, 0] = int(sep[1]) # node_1
        element[i, 1] = int(sep[2]) # node_2
        element[i, 2] = int(sep[3]) # node_3
        if len(sep) != 5:
            element[i, 3] = int(sep[4]) # node_4
        elif len(sep) == 5:
            element[i, 3] = 0 # node_4
        element[i, 4] = int(sep[-1]) # section number

    # 要素番号の整列 
    element = sorted(element.tolist(), key=lambda x:(x[1])) #<----MESH2で要素の整列をすれば, 削除してもよい

    element = np.array(element)
    return node, element

"""
    1要素を構成する接点の並びを確認および修正する関数 <----反時計まわりにするための関数、MESH2でできるなら削除してもよい。
    ※要素の形によって、正しく並ばないことがあるが、メッシュ作成では想定してない
"""
def devise_data(node, element):
    for i in range(len(element)):
        if element[i][3] != 0:
            aa = np.zeros([4, 2], dtype=np.float64)
            n1=element[i,0]-1; aa[0, 0]=node[:, 1][n1]; aa[0, 1]=node[:, 2][n1]
            n2=element[i,1]-1; aa[1, 0]=node[:, 1][n2]; aa[1, 1]=node[:, 2][n2]
            n3=element[i,2]-1; aa[2, 0]=node[:, 1][n3]; aa[2, 1]=node[:, 2][n3]
            n4=element[i,3]-1; aa[3, 0]=node[:, 1][n4]; aa[3, 1]=node[:, 2][n4]
            
            aa = np.array(aa)
            aa = [list(i) for i in aa]
            x_sort = sorted(aa, key=lambda x:(x[0]), reverse=False)
            y_sort = sorted(aa, key=lambda x:(x[1]), reverse=False)
            x_sortR = sorted(aa, key=lambda x:(x[0]), reverse=True)
            y_sortR = sorted(aa, key=lambda x:(x[1]), reverse=True)
                
            y_max = y_sortR[:2]
            y_min = y_sort[:2]
            x_max = x_sortR[:2]
            x_min = x_sort[:2]
            
            if x_sort[1][0] == x_sort[2][0]:
                n_1 = x_sort[0]
                n_2  = [i for i in x_max if i in y_min][0]
                n_3  = [i for i in x_min if i in y_max][0]
                n_4 = x_sort[3]
            elif y_sort[1][1] == y_sort[2][1]:
                n_1  = [i for i in x_min if i in y_min][0]
                n_2  = y_sort[0]
                n_3  = y_sort[3]
                n_4  = [i for i in x_max if i in y_max][0]
            else:
                n_1  = [i for i in x_min if i in y_min][0]
                n_2  = [i for i in x_max if i in y_min][0]
                n_3  = [i for i in x_min if i in y_max][0]
                n_4  = [i for i in x_max if i in y_max][0]

            element[i, 0] = int(node[np.where((n_3[0]==node[:,1]) & (n_3[1]==node[:,2])), 0][0][0])
            element[i, 1] = int(node[np.where((n_1[0]==node[:,1]) & (n_1[1]==node[:,2])), 0][0][0])
            element[i, 2] = int(node[np.where((n_2[0]==node[:,1]) & (n_2[1]==node[:,2])), 0][0][0])
            element[i, 3] = int(node[np.where((n_4[0]==node[:,1]) & (n_4[1]==node[:,2])), 0][0][0])

        if element[i][3] == 0:
            n1=element[i,0]-1; x1=node[:, 1][n1]; y1=node[:, 2][n1]
            n2=element[i,1]-1; x2=node[:, 1][n2]; y2=node[:, 2][n2]
            n3=element[i,2]-1; x3=node[:, 1][n3]; y3=node[:, 2][n3]

    node = np.array(node)
    element = np.array(element)
    return node, element

"""
    2Dyouso.datを作成する関数
"""
def file_create(lines, path_new, dummy_text, q_1, q_2, q_3, q_4, q_5, q_6):
    npm, nem = get_data(lines)
    node, element = read_data(npm, nem, lines)
    node, element = devise_data(node, element)

    file = open(path_new, "w", encoding='CP932')

    con_1 = [int(node[i, 2]) for i in range(npm) if node[i,1] == min(node[:, 1])]
    con_2 = [int(node[i, 2]) for i in range(npm) if node[i,0] == min(node[:, 0]) or node[i,0] == max(node[:, 0])]
    con_2 = [i for i in con_2 if i not in con_1]
    con_1 = sorted(con_1)
    con_2 = sorted(con_2)

    kousoku = len(con_1) * 2 + len(con_2)
    jiban = max(element[:, 4])

    file.write(str(npm).rjust(5) + str(nem).rjust(5) + str(kousoku).rjust(5) +  str(jiban).rjust(5) +  "0".rjust(5) +  "0".rjust(5)+"\n")
    file.write("    0    0\n")
    file.write("    0    0\n")
    file.write("    0    0    0    0    0\n")
    file.write("    0 1000\n")
    file.write("    0    0    0\n")
    file.write("E1000\n")
    file.write("    3    1    1    {a}    {b}    {c}    {d}    {e}    0    0\n".format(a=q_5, b=q_2, c=q_6, d=q_3, e=q_4)) #<---入力の数字によって変更
    file.write("    0    0    0    0    0    0    0    0    0    0\n")
    file.write("    0    0    0    0    0    0    0    0    0    0\n")
    file.write("    1.0d-4   1.0d-10    1.0d-2    1.0d-6    1.0d10    1.0d-7   0.0d+0    1.0d+0    2\n")
    file.write("    2.0d-3 2302.0d-3    0.0d+0    1.4d+0    1.0d-0    1.0d-1\n")
    file.write("    1.0d-8         0\n")
    file.write("    1  1        9.1000000000        0.0005000000      -86.0000000000       33.7100000000\n")
    file.write("    1  2        9.1000000000        0.0005000000      -86.0000000000       33.7100000000\n")
    file.write("E   1  3        0.0000000000        0.0000000000        0.0000000000        1.2000000000\n")
    file.write("  1  2  2  0  0  0  0  8  0  0  0  1 -2\n")

    for i in range(jiban):
        E = " "
        if i == int(jiban)-1:
            E = "E"    
        file.write("{}    {}    10000.00000        0.49999  40.00000   40.0000        1.00000  18.00000\n".format(E, i+1))

    for i in range(len(element)):
        if i+1 != len(element):
            file.write(str(i+1).rjust(6) + str(element[i][0]).rjust(5) + str(element[i][1]).rjust(5) + str(element[i][2]).rjust(5) + str(element[i][3]).rjust(5) + str(element[i][4]).rjust(5) + "\n")
        else:
            file.write("E" +str(i+1).rjust(5) + str(element[i][0]).rjust(5) + str(element[i][1]).rjust(5) + str(element[i][2]).rjust(5) + str(element[i][3]).rjust(5) + str(element[i][4]).rjust(5) + "\n")
        
    for i in range(len(node)):
        if i+1 != len(node):
            file.write(str(i+1).rjust(6) + f"{node[i, 1]:15.05f}" + f"{node[i, 2]:15.05f}" + "\n")
        else:
            file.write("E" + str(i+1).rjust(5) + f"{node[i, 1]:15.05f}" + f"{node[i, 2]:15.05f}" + "\n")

    con_1 = [int(node[i, 0]) for i in range(npm) if node[i,1] == min(node[:, 1])]
    con_2 = [int(node[i, 0]) for i in range(npm) if node[i,0] == min(node[:, 0]) or node[i,0] == max(node[:, 0])]
    con_2 = [i for i in con_2 if i not in con_1]
    con_1 = sorted(con_1)
    con_2 = sorted(con_2)

    for i in range(len(con_1)):
        file.write(str(con_1[i]).rjust(6) + "    1    1" + "\n")

    for i in range(len(con_2)):
        if i+1 != len(con_2):
            file.write(str(con_2[i]).rjust(6) + "    1    0" + "\n")
        else:
            file.write("E" + str(con_2[i]).rjust(5) + "    1    0" + "\n")
            
    if q_2 == 1:
        file.write(dummy_text["joint"])
        
    if q_3 == 1:
        file.write(dummy_text["edge"])

    if q_4 == 1:
        file.write(dummy_text["beam"])
        
    if q_4 == 2:
        file.write(dummy_text["beam"])
        file.write(dummy_text["beam_joint"])
    file.close()

class Application(tk.Tk):
    def __init__(self):
        global file_path
        self.file_path = ''
        super().__init__()
        # アプリのタイトル
        self.geometry("420x480")
        self.title("[RPFEM解析] .MSH を 2Dyouso.datに変換")
        self.create_widgets()
    
    def create_widgets(self):
        self.label1 = tk.Label(self.master, text = "変換前")
        self.label2 = tk.Label(self.master, text = "変換先")
        self.label3 = tk.Label(self.master, text = "説明")
        self.input_box1 = tk.Entry(self.master, width=50)
        self.input_box2 = tk.Entry(self.master, width=50)
        self.input_box3 = tk.Entry(self.master, width=58)
        self.input_box1.insert(0, "MSHファイルを選択してください")
        self.input_box2.insert(0, "")
        self.input_box3.insert(0, datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9), 'JST')).strftime('%Y/%m/%d %H:%M:%S'))
        self.read_button1 = tk.Button(self.master, text='参照', command=lambda: self.file_select(self.input_box1), width=5)
        self.read_button2 = tk.Button(self.master, text='参照', command=lambda: self.file_select(self.input_box2), width=5)

        self.label1.place(x=5, y=10)
        self.label2.place(x=5, y=40)
        self.label3.place(x=5, y=70)
        self.input_box1.place(x=50, y=10)
        self.input_box2.place(x=50, y=40)
        self.input_box3.place(x=50, y=70)
        self.read_button1.place(x=360, y=10)
        self.read_button2.place(x=360, y=40)

        self.label = tk.Label(self.master, text = "ダミーデータの生成", font=("MSゴシック", "9", "bold"))
        self.label.place(x=5, y=105)

        self.labelframe1 = tk.LabelFrame(self.master, text = "浸透流だけ計算しますか？")
        self.radio_value1 = tk.IntVar(value = 0)
        self.radio1_1 = tk.Radiobutton(self.labelframe1, text = "浸透流だけ", variable = self.radio_value1, value = 1)
        self.radio1_2 = tk.Radiobutton(self.labelframe1, text = "変形解析", variable = self.radio_value1, value = 2)
        self.radio1_3 = tk.Radiobutton(self.labelframe1, text = "いいえ", variable = self.radio_value1, value = 0)
        self.radio1_1.grid(row=1, column=1)
        self.radio1_2.grid(row=1, column=2)
        self.radio1_3.grid(row=1, column=3)

        self.labelframe2 = tk.LabelFrame(self.master, text = "ジョイント要素を使用しますか？")
        self.radio_value2 = tk.IntVar(value = 0)
        self.radio2_1 = tk.Radiobutton(self.labelframe2, text = "はい", variable = self.radio_value2, value = 1)
        self.radio2_2 = tk.Radiobutton(self.labelframe2, text = "いいえ", variable = self.radio_value2, value = 0)
        self.radio2_1.grid(row=1, column=1)
        self.radio2_2.grid(row=1, column=2)

        self.labelframe3 = tk.LabelFrame(self.master, text = "EDGE CONDITIONを考慮しますか？")
        self.radio_value3 = tk.IntVar(value = 0)
        self.radio3_1 = tk.Radiobutton(self.labelframe3, text = "はい", variable = self.radio_value3, value = 1)
        self.radio3_2 = tk.Radiobutton(self.labelframe3, text = "いいえ", variable = self.radio_value3, value = 0)
        self.radio3_1.grid(row=1, column=1)
        self.radio3_2.grid(row=1, column=2)

        self.labelframe4 = tk.LabelFrame(self.master, text = "ビーム要素を使用しますか？")
        self.radio_value4 = tk.IntVar(value = 0)
        self.radio4_1 = tk.Radiobutton(self.labelframe4, text = "はい（ビーム要素のみ）", variable = self.radio_value4, value = 1)
        self.radio4_2 = tk.Radiobutton(self.labelframe4, text = "はい（ビーム要素＋ジョイント要素）", variable = self.radio_value4, value = 2)
        self.radio4_3 = tk.Radiobutton(self.labelframe4, text = "いいえ", variable = self.radio_value4, value = 0)
        self.radio4_1.grid(row=1, column=1)
        self.radio4_2.grid(row=1, column=2)
        self.radio4_3.grid(row=1, column=3)

        self.labelframe5 = tk.LabelFrame(self.master, text = "荷重を作用させますか？")
        self.radio_value5 = tk.IntVar(value = 0)
        self.radio5_1 = tk.Radiobutton(self.labelframe5, text = "はい（増加荷重）", variable = self.radio_value5, value = 1)
        self.radio5_2 = tk.Radiobutton(self.labelframe5, text = "はい（一定荷重）", variable = self.radio_value5, value = 2)
        self.radio5_3 = tk.Radiobutton(self.labelframe5, text = "いいえ", variable = self.radio_value5, value = 0)
        self.radio5_1.grid(row=1, column=1)
        self.radio5_2.grid(row=1, column=2)
        self.radio5_3.grid(row=1, column=3)

        self.labelframe6 = tk.LabelFrame(self.master, text = "水を考慮しますか？")
        self.radio_value6 = tk.IntVar(value = 0)
        self.radio6_1 = tk.Radiobutton(self.labelframe6, text = "はい", variable = self.radio_value6, value = 1)
        self.radio6_2 = tk.Radiobutton(self.labelframe6, text = "いいえ", variable = self.radio_value6, value = 0)
        self.radio6_1.grid(row=1, column=1)
        self.radio6_2.grid(row=1, column=2)

        self.labelframe1.place(x=5, y=130, width=410)
        self.labelframe2.place(x=5, y=180, width=410)
        self.labelframe3.place(x=5, y=230, width=410)
        self.labelframe4.place(x=5, y=280, width=410)
        self.labelframe5.place(x=5, y=330, width=410)
        self.labelframe6.place(x=5, y=380, width=410)

        self.excute_button = tk.Button(self, text="変換", command=lambda: self.file_read(
            self.input_box1.get(),
            self.input_box2.get(), 
            self.radio_value1.get(),
            self.radio_value2.get(),
            self.radio_value3.get(),
            self.radio_value4.get(),
            self.radio_value5.get(),
            self.radio_value6.get()), width=10)
        self.cancel_button = tk.Button(self, text='閉じる', command=self.quit, width=10)
        self.excute_button.place(x=120, y=440)
        self.cancel_button.place(x=220, y=440)

    def file_select(self, input_box):
        global file_path
        idir = 'C:\\python_test'
        filetype = [("メッシュファイル","*.MSH")]
        file_path = tkinter.filedialog.askopenfilename(filetypes = filetype, initialdir = idir)
        input_box.delete(0, tkinter.END)
        input_box.insert(tkinter.END, file_path)

        if input_box == self.input_box1:
            self.input_box2.delete(0, tkinter.END)
            self.input_box2.insert(tkinter.END, os.path.dirname(file_path)+"/2Dyouso.dat")
        return file_path


    def file_read(self, path, path_new, q_1, q_2, q_3, q_4, q_5, q_6):
        global lines
        if len(path) == 0:
            tkinter.messagebox.showwarning('確認', 'ファイルが選択されていません')
            return

        if os.path.basename(path).split('.')[-1] != 'MSH':
            tkinter.messagebox.showwarning('確認', 'MSHファイルが選択されていません')
            return
        else:
            with open(path, mode="r") as file:
                lines = file.read().splitlines()
            
            if not 'NODE' in lines:
                tkinter.messagebox.showwarning('確認', '節点の情報がありません')
                return
            elif not 'ELEMENT' in lines:
                tkinter.messagebox.showwarning('確認', '要素の情報がありません')
                return
            
            file_create(lines, path_new, dummy_text, q_1, q_2, q_3, q_4, q_5, q_6)
            tkinter.messagebox.showinfo('完了', 'ファイルが正しく変換されました')
            self.quit()    
            
    def quit(self):
       self.destroy()


def main():
    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main()
