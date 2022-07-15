"""
#######################################################
#######################################################
#####　　支持力曲線および支持力曲面のためのプログラム　####
#######################################################
###########　　　作成日時：2020年12月25日　　　　#########
###########　　　作成者：大平 尚輝（専攻科1年）　 ########
#######################################################


【使用言語】
・Python


【本プログラムの目的】
・土圧計算の作業の効率化

【本プログラムの概要】
・土圧計算は作用位置を変化させて，土圧が最小値となる作用位置を探す
・従来は，１つ１つ，2Dyouso.datを打ち換え，実行，result.dを確認するといった繰り返しだった．
・このプログラムは，初期作用位置を設定したフォルダを用意すれば，自動的に土圧が最小値を認識し，その後，3つ分の解析をする．
・細かい解説は，以下にあるコードの上に書いてある．


※注意点
・2Dyouso.dat内の作用位置を設定する行はプログラムを手打ちで変更しなければいけない．
・LINE通知のプログラムを実行する場合，自分のアクセストークンを発行して変更する．（https://notify-bot.line.me/ja/）
・解析フォルダ内にあるRPFEMの実行ファイルは，１つだけにする（RPFEMが含まれるexeファイルを１つだけ検出するため）
・解析が発散した場合，対処できない（途中で解析が止まってしまったら，それまでに作成されたフォルダを別フォルダに移動させて，途中から実行してください．
・汎用性を高めるため，用意する解析フォルダの名前は作用位置のみ（例えば，「1.5」）としてください．（最初の解析フォルダを初期作用位置とするため，余分な文字列があるとエラーとなります）



【ディレクトリ階層例】
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
C:.
└─1.5 <-----------------------------------------------初期作用位置
        2D.neu
        2Dyouso.dat　<--------------------------------初期作用位置となるようにしてください
        analysis output.exe　
        libiomp5md.dll　
        RPFEM_OHIRA.exe　<----------------------------解析終了時のPAUSEをなくしたRPFEM実行ファイル
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



"""


"""
    以下の内容が書かれている行を2Dyouso.datを見て打ち換える

    E 3443　　　　　　　　　　　　　　　　　　　　　　　　　　　　　<-----------作用位置
    E 3443       -1.00000        0.00000        0.00000　　　　 <-----------作用量
"""
changedRow_1 = 214
changedRow_2 = 215



import os
import glob
import shutil
import re
import sys
import pandas as pd
import subprocess as sp

#　解析を実施するディレクトリの設定
curr_dir = str(input("解析を実施するフォルダがあるディレクトリを入力："))

initial_folder_list = glob.glob(curr_dir + "\\*")
initial_dir = initial_folder_list[0]

# RPFEMプログラムを取得する（名前はRPFEMから始まるものとする）
rpfem_dir = glob.glob(initial_folder_list[0] + "\\*.exe")
rpfem_dir = [d for d in rpfem_dir if "RPFEM" in os.path.basename(d)]
# RPFEMの解析フォルダが1つかどうかを判別（取得した際に，その数が１つでないなら，プログラムを終了させる）
if len(rpfem_dir) != 1:
    print("""
---------- ERROR ----------)
RPFEMプログラムが{}個、存在します。
正しいフォルダを用意してください。
---------------------------"""
.format(len(rpfem_dir)))
    sys.exit()

# RPFEMの実行ファイルの名前"RPFE_○○○○○.exe"を取得
rpfem_exe = os.path.basename(rpfem_dir[0])
"""
    最初のフォルダの個数をカウント．１以外ならプログラムを中止．
"""
# 余分なファイル・フォルダが存在するかを判別
if len(initial_folder_list) != 1:
    print("""
---------- ERROR ----------)
余分なファイル・フォルダが存在します。
正しいフォルダを用意してください。
---------------------------"""
.format(len(initial_folder_list)))
    sys.exit()

# フォルダの名前から初期作用位置を取得
height = float(os.path.basename(initial_dir))


# 解析結果を集計するための空リストおよび，2Dyouso.dat内の番号を変更するための変数を設定

list_value = []
list_height = []
list_time = []
node_number_count = 0
def remove_file():
    remove_files = ["out_seepage_element.d", "out_seepage_node.d", "resultseepage.d", "fem-change_data.exe", "libiomp5md.dll"]
    for remove_file in remove_files:
        if os.path.exists(remove_file):
            os.remove(remove_file)
    os.remove(rpfem_dir[0])
    
"""
    初期高さの土圧計算（１周目）
"""
def rpfem(dir, height):

    # 解析を行う解析フォルダにカレントディレクトリを変更
    os.chdir(dir)
    # RPFEMの実行ファイルを実行
    sp.call(rpfem_exe)

    # 解析中．．．．．．解析が終われば[result.d]が生成される
    # 解析結果を取得するため，result.dを読み込む
    with open("result.d", "r") as ff:
        lines = ff.read().splitlines()
        # RPFEM値（主働土圧合力）の取得
        res_value = "res_value_{}".format(height)
        res_value = re.compile("\d+\.\d+").findall(lines[-3])
        # 解析時間を取得
        res_time = re.compile("\d+\.\d+").findall(lines[-1])

    # 取得した解析結果と，作用位置をリストに格納
    list_value.append(res_value[0])
    list_time.append(res_time[0])
    list_height.append(round(height, 2))
    
    # 初期作用位置の解析が終了
    print(dir, ": END")
    # remove_file()


"""
    土圧計算（２周目以降，前の解析結果との差が＋になるまで）
"""
def rpfem_while(dir, height, changedRow_1, changedRow_2):
    global node_number_count

    # 初期作用地位の解析フォルダをもとに，解析フォルダを複製
    shutil.copytree(initial_dir, dir)

    #複製した解析フォルダにカレントディレクトリを変更
    os.chdir(dir)

    # 以下の[row1], [row2]で，2Dyouso.dat内の作用位置を変更する）
    # ========================row1=============================
    with open("2Dyouso.dat", "r", encoding="cp932") as file:
        data_lines = file.read()
        row1 = data_lines.splitlines()[changedRow_1 - 1][0:]
    sep = row1.split()
    node_number_count += 1
    node_number = int(sep[1]) + node_number_count
    data_line1 = data_lines.replace(row1, "E "+ str(node_number))

    with open("2Dyouso.dat", mode="w", encoding="cp932") as file:
        file.write(data_line1)

    # ========================row2=============================


    with open("2Dyouso.dat", "r", encoding="cp932") as file:
        data_lines = file.read()
        row2 = data_lines.splitlines()[changedRow_2 - 1][0:]

    data_line2 = data_lines.replace(row2, "E "+str(node_number)+"       -1.00000        0.00000        0.00000")

    with open("2Dyouso.dat", mode="w", encoding="cp932") as file:
        file.write(data_line2)

    # 2Dyouso.datを変更したら，RPFEMの実行ファイルを実行
    sp.call(rpfem_exe)
    # remove_file()


    with open("result.d", "r") as ff:
        lines = ff.read().splitlines()
        res_value = "res_value_{}".format(height)
        res_value = re.compile("\d+\.\d+").findall(lines[-3])
        #print(res_value)
        #print(diff_value)

    res_time = re.compile("\d+\.\d+").findall(lines[-1])

    list_value.append(res_value[0])
    list_time.append(res_time[0])
    list_height.append(round(height, 2))

    print(dir, ": END")


"""
    グラフ化の関数
"""
import matplotlib.pyplot as plt
import numpy as np
def graph():
    #y = list_height
    #x = list_value
    #x = [float(i) for j in x for i in j]
    #y = [float(i) for i in y]

    os.chdir(curr_dir)
    #  作成したresult.csvのデータを読込
    data = np.loadtxt(
        fname = "result.csv",
        dtype = "float",
        delimiter = ",",
        skiprows = 1
    )

    # グラフを描くためのxおよびyのリストを設定
    x = data[:, 1]
    y = data[:, 0]

    fig = plt.figure(figsize=(9, 9))
    ax = fig.add_subplot(111)

    # 軸の幅をxおよびyの最小値と最大値に変更
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min(y), max(y))

    # 軸ラベルの設定
    ax.set_xlabel("Active Earth Pressure Pa [kN/m]", font="Times New Roman", fontsize = 20)
    ax.set_ylabel("Earth Pressure Acting Point h [m]", font="Times New Roman", fontsize = 20)
    #ax.set_title(sep_list)

    # フォントの設定
    plt.rcParams['font.size'] = 14
    plt.rcParams['font.family'] = 'Times New Roman'

    # 目盛の設定（内側）
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'

    # 目盛り線の設定（グラフの上下左右）
    ax.yaxis.set_ticks_position('both')
    ax.xaxis.set_ticks_position('both')

    # x軸に補助目盛線を設定
    ax.grid(which = "major", axis = "x", color = "black", alpha = 0.5, linestyle = "--", linewidth = 1)

    # y軸に目盛線を設定
    ax.grid(which = "major", axis = "y", color = "black", alpha = 0.5, linestyle = "--", linewidth = 1)

    # RPFEMの解析値をプロット（縦軸に作用位置，横軸に土圧合力）
    ax.scatter(x, y, label="RPFEM", s=300, color="black")

    # プロットした点を線で結ぶ（折れ線グラフ）
    ax.plot(x, y, label="RPFEM", color="black")

    # 作用位置が最小値となる箇所に赤い横線を描写
    ax.plot([min(x), max(x)],[min_height, min_height], "red", linestyle='-')

    # 解析フォルダがあるディレクトリにグラフを"graph.png"として保存
    fig.savefig(curr_dir+ "//graph.png")

"""
    LINEに通知する関数
"""
import requests
def send_line_notify_ohira(message):
    line_notify_token = '6KIyVw4wK3PEjRm5IhtqqLZzWELPJJIoedxJm4EYuuw'######<---------ここがアクセストークンで，自分のものに変える．詳しくはググる，ohira
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {line_notify_token}'}
    data = {'message': message}
    files = {'imageFile': open(os.path.join(curr_dir, "graph.png"), "rb")}
    requests.post(line_notify_api, headers = headers, data = data, files = files)



"""
    フォルダを整理する関数
"""
import os
import glob

remove_files = ["out_seepage_element.d", "out_seepage_node.d", "resultseepage.d", "fem-change_data.exe", "libiomp5md.dll"]
def cleaning_folder(curr_dir, rpfem_exe):
    file_dirs = glob.glob(curr_dir + "\\*")
    for file_dir in file_dirs:
        os.chdir(file_dir)
        for remove_file in remove_files:
            if os.path.exists(remove_file):
                os.remove(remove_file)

        if os.path.exists(rpfem_exe):
            os.remove(rpfem_exe)



"""
    以下，プログラムの実行
"""

# diffの初期値の設定
diff = 1

#1つ目のRPFEMを実行
rpfem(initial_dir, height)
# プラスならwhile文続行し，マイナスならwhile文を抜け出す


while diff > 0:
    height += 0.1
    # 解析するディレクトリの設定
    dir = curr_dir + "\\" + str(round(height, 2))

    # RPFEMの実行（ここに，解析フォルダの準備，2Dyouso.datの書換などが含まれる）
    rpfem_while(dir, height, changedRow_1, changedRow_2)

    # 1つ前の作用位置で求めたRPFEMとの差分を算出
    diff = float(list_value[-2]) - float(list_value[-1])

# while文が終了したときの最後から2つ目の値が最小値となる
min_value = list_value[-2]
min_height = list_height[-2]


"""
    土圧が最小値になった後，2周分の解析をする
"""
# while文での作業を2回分行う．
height += 0.1
dir = curr_dir + "\\" + str(round(height, 2))
rpfem_while(dir, height, changedRow_1, changedRow_2)

height += 0.1
dir = curr_dir + "\\" + str(round(height, 2))
rpfem_while(dir, height, changedRow_1, changedRow_2)



if min_value > list_value[-1]:
    height += 0.1
    dir = curr_dir + "\\" + str(round(height, 2))
    rpfem_while(dir, height, changedRow_1, changedRow_2)
    height += 0.1
    dir = curr_dir + "\\" + str(round(height, 2))
    rpfem_while(dir, height, changedRow_1, changedRow_2)
    height += 0.1
    dir = curr_dir + "\\" + str(round(height, 2))
    rpfem_while(dir, height, changedRow_1, changedRow_2)


if min_value > list_value[-2]:
    height += 0.1
    dir = curr_dir + "\\" + str(round(height, 2))
    rpfem_while(dir, height, changedRow_1, changedRow_2)
    height += 0.1
    dir = curr_dir + "\\" + str(round(height, 2))
    rpfem_while(dir, height, changedRow_1, changedRow_2)

min_value = min(list_value)
index = list_value.index(min(list_value))
min_height = list_height[index]



cleaning_folder(curr_dir, rpfem_exe)

"""
    解析結果が格納されているリストをCSVに集計
"""
df_result = pd.DataFrame.from_dict({"Height":list_height,"Analysis Value":list_value, "Analysis Time":list_time})
df_result.to_csv(os.path.join(curr_dir, "result.csv"), index=False)



graph()

print("""
=====================================================
    解析フォルダ：{folder}
    土圧の最小値：{min_value}
    その作用位置：{min_height}
=====================================================
""".format(folder=curr_dir, min_value=min_value, min_height=min_height)
)


"""
    解析値および，そのグラフをLINE　Notify に送信する
"""
result_notify = [(str(i) + "：" + str(j)) for (i, j) in zip(list_height, list_value)]
result_notify = '\n'.join(result_notify)
message = "\n 【{curr_dir}】\n=======結果=======\n {result_notify}\n================".format(curr_dir=curr_dir, result_notify=result_notify)
send_line_notify_ohira(message)
os.system("PAUSE")
