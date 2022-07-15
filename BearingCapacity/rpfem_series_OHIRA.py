# coding: UTF-8


"""
【プログラムの設計】
1.RPFEM
・連続して解析するフォルダがあるディレクトリをインプットデータとして入力する
・ディレクトリ内の解析フォルダを全て取得してリストに追加する
・リストに追加したフォルダに順番にパスを通していき，RPFEMを実行する
・解析が終わりresult.dが生成されたら，解析値と実行時間を結果を集計するそれぞれのリストに追加していく．また，このとき，フォルダの名前（解析の条件）もリストに追加する
・１つの解析が終わったら，リスト内の次の解析フォルダにパスが移動する
・実行→結果の追加を繰り返す
・最初に取得した解析フォルダの全ての解析が終了したら，結果を追加した３つのリスト（値，時間，名前）をCSVファイルに保存する

2. グラフの作成
・[1. RPFEM]で作成した3つのリスト（値，時間，名前）を使って，グラフを作成する．（レイアウトは好みで）
※あくまで，解析結果の傾向を簡単に見るためのものなので，このグラフを論文に貼ることは絶対にない．

3. LINEの通知
・[1. RPFEM]，[2. グラフの作成]で作成したリストおよびグラフをLINEに送信する．
※あくまで，次の解析を実行するまでの時間短縮，および，グラフ傾向の傾向を簡単に確認するためのものである．
※この機能を使用する場合は，自分のLINEにLINE Notifyを追加して，アクセストークンを取得して，該当箇所を書き換えてください．


【このプログラムを作成した背景】
    卒研(2019)において，膨大な解析を実行し，それが大変だった．また，水野先生から連続して解析ができるバッチファイルは作れんか，と言われた．
    今後の研究の効率化のためにと，Pythonを用いてプログラムを書くことにした．
    また，今後，このプログラムがブラックボックス化しないように，以下に，このプログラムの中身について書く．
【プログラムの中身】
    このプログラムは３つの関数（rpfem_repeat, graph, send_line_notify）を作成し，それぞれを順番に実行していく．

● rpfem_repeat
    主となる関数．
    最初にインプットしたディレクトリの下にある解析フォルダ内のRPFEMを順番に実行していく．
    ※このとき解析フォルダの他に別のファイルやフォルダがあると，エラーが起きる．
    そのため，連続して解析を実行する前にresult.csvの存在確認をIF文で分岐し，実行者の入力するキーによって処理が変更する．
    また，後に作成されるgraph.pngの存在確認を行い，存在すれば削除する．
    解析した結果を取得するため，解析後に生成されたresult.dのから，結果部分のみを抽出する．
    それらを，１つ１つの解析が終わる毎にリスト（list_value, list_time, list_dir）に追加されるようになっている．

    また，全ての解析が終了したあと，追加されたリストはCSVファイル（result.csv）に保存される（pandas使用）．

    このプログラムで実行するRPFEMのexeファイルは，解析が終わった時に4つのresultファイルが生成される．
    浸透流解析を実行しないなら，result.dのファイル以外は不要であるため，削除するようにしてある．
    浸透流解析を想定して，このプログラムは作成してないが，使う場合は削除するコ―ドを削除する（os.remove(os.path.join～～～)）

● graph
    グラフ化では，リストに追加した値を使って，グラフを作成し，保存する．（例：縦軸：list_vale，横軸：list_dirの数字部分（"c=10"→10））
    グラフの縦軸，横軸，タイトルまたそのサイズや色など自由に変更可能である．詳しくはググって．


● send_line_notify
    RPFEMは解析いつ終わるのか，またいつ終わったかどうかわからない．そのため，解析が終わった時にLINEに通知する機能を導入した．（LINE Notifyを使用）
    これにより，無駄なく解析を実行できる．
    この通知は解析の終了を知らせるためのものだが，解析値とグラフも送信されるようになっている．
    解析値には，rpfem_repeatで追加したリストを使用している．
    グラフには，graph関数で保存した画像をそのまま送信されるようになっている．



200930に修正
【修正内容】
・修正前は，result.csvとgraph.pngがそれぞれのフォルダの中に生成していたが，集計の際に１つ１つのフォルダを開かないといけないので，いつのフォルダに保存するようにする．

210114に修正
・解析が値の小さい順番に行われるように，sorterの追加，その他コードの修正

"""

#修正箇所の変数

line_notify_token = "6KIyVw4wK3PEjRm5IhtqqLZzWELPJJIoedxJm4EYuuw"

"""
    #####################################################RPFEM連続解析の関数#############################################################
"""
import os
import sys
import time
import glob
import subprocess as sp
import re
import pandas as pd
from natsort import natsorted
def rpfem_repeat():
    global curr_dir
    global graph_dir
    global graph_name
    global csv_dir
    global csv_name
    global exe_name
    global txt_rpfem

    # 解析を実施するフォルダを入力させる
    curr_dir = str(input("解析を実施するフォルダがあるディレクトリを入力："))
    # RPFEMの実行ファイル（プログラミング言語：Fortran）を指定する　※最後に[PAUSE]がないプログラム（分からなければ水野先生に）
    # exe_name = "RPFEM_OHIRA.exe"

    count = 0
    txt_rpfem = "a"
    while len(txt_rpfem) < 10:

        if count != 0:
            print("""
========================
    解析内容が短いです．
========================
            """)
        txt_rpfem = str(input("解析を実施する内容を簡単に入力："))
        count += 1

    folder_name_get = os.path.split(curr_dir)
    graph_dir = os.path.join(folder_name_get[0], "graph_list")
    csv_dir = os.path.join(folder_name_get[0], "csv_list")

    # 保存するCSVファイル，PNGファイルの名前を指定
    graph_name = folder_name_get[1] + ".png"
    csv_name = folder_name_get[1] + ".csv"

    # CSVファイアおよびPNGファイルを保存するフォルダを作成
    if not os.path.exists(graph_dir):
        os.makedirs(graph_dir)
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)

    # 関数の外でも変数を使うためにグローバル関数にする
    global list_value
    global list_time
    global list_dir
    global list_rpfem

    # 空リストを定義する
    ##　解析結果を格納
    list_value = []
    list_time = []
    list_dir = []
    ##　使用したRPFEMプログラム（RPFEM~~~.exe: 言語 Fortran）を格納
    list_rpfem = []

    # 解析するフォルダ内の解析フォルダをリストに格納
    sub_dirs = [d for d in os.listdir(curr_dir)]
    sub_dirs = [d for d in sub_dirs if ".txt" not in d]
    # リストをきれいに並び替え
    sub_dirs = natsorted(sub_dirs)



    #　解析フォルダを頭から順番にfor文で実行していく
    for sub_dir in sub_dirs:
        # カレントディレクトリを変更する
        os.chdir(os.path.join(curr_dir, sub_dir))

        # 実行するRPFEMプログラムの名前を取得
        exa_dir = glob.glob(curr_dir + "\\" + sub_dir + "\\*.exe")
        exa_dir = [d for d in exa_dir if "RPFEM" in os.path.basename(d)]
        if len(exa_dir)!=1:
            print("""
        ========================================
        ※ RPFEMの実行ファイルが正しくありません．
        ========================================""")
            sys.exit()
        exe_name = os.path.basename(exa_dir[0])
        list_rpfem.append(exe_name)
        # RPFEMの実行ファイルを実行
        print("Excuse : ", sub_dir)
        sp.call(exe_name)
        #### 以下，RPFEMの実行ファイルが終えたら始める #########
        # 解析が終わったら作成されるresult.dの読込
        with open("result.d", "r") as ff:
            # 全ての行を読取
            lines = ff.read().splitlines()
            # 解析値が書かれている行を取得（下から3行目）
            res_value = re.compile("\d+\.\d+").findall(lines[-3])
            # 解析時間が書かれている行を取得（下から1行目）
            res_time = re.compile("\d+\.\d+").findall(lines[-1])
            # 解析結果および解析時間，条件（例：phai=10）を定義した空リストに格納
            list_value.append(res_value[0])
            list_time.append(res_time[0])
            list_dir.append(sub_dir)

        # 解析が実行したときに生成される不要なファイルを削除

        remove_files = ["out_seepage_element.d", "out_seepage_node.d", "resultseepage.d", "fem-change_data.exe", "libiomp5md.dll"]
        for remove_file in remove_files:
            if os.path.exists(remove_file):
                os.remove(remove_file)
        os.remove(exe_name)



    # 格納し終わったリストをからDataFrameを作成（pattern, Analysis Valuem, Analysis TimeはCSVファイルのヘッダーとなる）
    df_result = pd.DataFrame.from_dict({"Pattern":list_dir,"Analysis Value":list_value, "Analysis Time":list_time})
    # 作成したDataFrameをCSVファイルとして保存
    df_result.to_csv(os.path.join(csv_dir, csv_name), index=False)

    print(curr_dir)
    # 解析が終了したことをコマンドプロンプトに表示
    print("""
    =======================
            解析終了
    =======================""")



"""
    ################################################################グラフ化の関数##################################################################
"""

import matplotlib.pyplot as plt
def graph():
    # 横軸のデータを格納する空リストを定義
    x = []
    # list_dirから数字だけを抽出（例：phai=10であれば10を）
    for i in list_dir:
        x.append(re.findall(r"([+-]?[0-9]+\.?[0-9]*)", i))

    # 抽出された数字を数に変更
    x = [float(i) for j in x for i in j]

    # yに格納されているデータを数字に変更
    y = [float(i) for i in list_value]

    # グラフを描写するキャンパスを用意（figsizeで画像のサイズを指定）
    fig = plt.figure(figsize=(9, 9))
    ax = fig.add_subplot(111)

    # 軸ラベルの設定
    ax.set_xlabel("x", font="Times New Roman", fontsize = 20)
    ax.set_ylabel("Analysis value", font="Times New Roman", fontsize = 20)

    # フォントの設定
    plt.rcParams['font.size'] = 30
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

    # RPFEMの解析値をプロットと折れ線
    ax.scatter(x, y, label="RPFEM", s=300, color="black")
    ax.plot(x, y, label="RPFEM", color="black", linestyle="-")

    # グラフを保存
    plt.savefig(os.path.join(graph_dir, graph_name))


"""
    ##################################################################LINEに通知する関数###############################################################################
"""
import requests
# LINE通知の関数を定義
# ※ [line_notify_token]の変数にあるLINE APIを設定する（LINE Notifyのサイトより取得）
# 複数人にLINEを通知したい場合は，その人数分の関数を作成する
def send_line_notify(message, line_notify_token):
    line_notify_token = line_notify_token
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {line_notify_token}'}
    data = {'message': message}
    files = {'imageFile': open(os.path.join(graph_dir, graph_name), "rb")}
    requests.post(line_notify_api, headers = headers, data = data, files = files)



"""
    ####################################################################フォルダを整理する関数###########################################################################
"""
import datetime
def clean_folder(curr_dir, txt_content):
    with open(curr_dir + "\\analysis.txt", "a") as file:
        file.write(txt_content)
"""
    ###################################################################解析履歴を集計する関数###########################################################################
"""
history_csv_dir = r"\\10.27.1.2\mizuno_lab\cal-temp_R2\Ohira\rpfem_history.csv"

import csv
def analysis_history(history_csv_dir, curr_dir, time, txt_rpfem):

    if os.path.exists(history_csv_dir):
        with open(history_csv_dir, "a", newline="") as file:
            w = csv.DictWriter(file, fieldnames=["Analysis date", "Analysis directory", "Analysis summary"])
            w.writerow({"Analysis date": time, "Analysis directory": curr_dir, "Analysis summary": txt_rpfem})
    else:
        with open(history_csv_dir, "a", newline="") as file:
            w = csv.DictWriter(file, fieldnames=["Analysis date", "Analysis directory", "Analysis summary"])
            w.writeheader()
            w.writerow({"Analysis date": time, "Analysis directory": curr_dir, "Analysis summary": txt_rpfem})





"""
    #######################################################################連続で解析をする##############################################################################
"""
rpfem_repeat()


"""
    ######################################################################解析値をグラフ化する#########################################################################
"""
graph()


"""
    #############################################################解析値および，そのグラフをLINE　Notify に送信する#########################################################
"""
result_notify = [(str(i) + "：" + str(j)) for (i, j) in zip(list_dir, list_value)]
result_notify = '\n'.join(result_notify)
message = "\n 【{curr_dir}】\n=======結果=======\n {result_notify}\n======解析内容======\n{txt}".format(curr_dir=curr_dir, result_notify=result_notify,txt=txt_rpfem)
send_line_notify(message, line_notify_token)




"""
    #############################################################プログラムの詳細を記載したテキストファイルの作成################################################################
"""
result_clean = [(str(i) + "：" + str(j)) for (i, j) in zip(list_dir, list_value)]
result_clean = [(str(i) + "：" + str(j)) for (i, j) in zip(result_clean, list_rpfem)]
result_clean = '\n'.join(result_clean)

date_now = datetime.datetime.now()
date_now = date_now.strftime('%Y年%m月%d日 %H:%M:%S')
txt_content = """
##############################
####### プログラムの詳細 #######
##############################

このファイルの作成日時：{date_now}

解析内容
{txt_rpfem}

解析結果
{result_clean}

""".format(date_now=date_now, result_clean=result_clean, txt_rpfem=txt_rpfem)


clean_folder(curr_dir, txt_content)


"""
    一連のプログラムが終わったら，txtを表示させて，黒い画面で止まるようにする
"""
print(txt_content)

analysis_history(history_csv_dir, curr_dir, date_now, txt_rpfem)
os.system("PAUSE")
