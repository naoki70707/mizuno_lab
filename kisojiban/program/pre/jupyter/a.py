import sys
import numpy as np


"""
    配列から指定した文字列を含む行のインデックスを返す関数
"""

def get_index(l, x):
    idx = [i for i, j in enumerate(l) if x in j]
    if len(idx) == 1:
        return idx[0]
    elif len(idx) == 0:
        print("ファイル内に［{}］を確認できませんでした".format(x))
        sys.exit()
    else:
        print("ファイルの中身が正しくありません。［{}］を確認してください。".format(x))
        sys.exit()

    

"""
    全要素数，全節点数，ファイルの中身を返す関数
"""
def get_data(file_name):
    global npm
    global nem
    global lines
    with open(file_name, mode="r") as file:
        lines = file.read().splitlines()


    node_row = get_index(lines, "NODE")
    element_row = get_index(lines, "ELEMENT")

    npm = element_row - node_row - 1

    nem = get_index(lines, "LINE") - element_row - 1 # <---------------要修正

    print(npm)
    return npm, nem, lines



"""
    座標取得
    0: 接点番号
    1: x座標値
    2: y座標値
    
"""
def read_data(npm, nem, lines):
    global node
    global element
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
    element = sorted(element.tolist(), key=lambda x:(x[1]))
    element = np.array(element)
    return node, element

    """
        1要素を構成する接点の並びを確認および修正するプログラム
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
    2Dyouso.dat作成のための質問
"""
def question():
    global q_1, q_2, q_3, q_4, q_5, q_6
    q_1 = int(input("ARE YOU CALCULATE ONLY SEEPAGE?\n ONLY SEEPAGE FLOW=1  +DEFORMATION ANALYSIS=2  +NO=0 \n >>>"))

    q_2 = int(input("ARE YOU CONSIDER JOINT ELEMENT?\n YES=1  NO=0 \n >>>"))#5
    q_3 = int(input("ARE YOU CONSIDER EDGE CONDITION?\n YES=1  NO=0 \n >>>")) #7
    q_4 = int(input("ARE YOU CONSIDER BEAM ELEMENT?\n BEAM ONLY=1  BEAM & JOINT=2  NO=0 \n >>>"))#8
    q_5 = int(input("   ARE YOU CONSIDER LOADING?\n YES(INCREASE LOAD)=1  YES(CONSTANT LOAD )=2  NO=0 \n >>>"))#4
    q_6 = int(input("ARE YOU CONSIDER WATER?\n YES=1  NO=0 \n >>>>>"))#6

    return q_1, q_2, q_3, q_4, q_5, q_6

"""
    関数create_dataを実行して作成したデータから2Dyouso.datを作成
"""
def create_file(npm, nem, node, element, dummy_text):
    file = open("2Dyouso.dat", "w", encoding='CP932')

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
    file.write("E    1    10000.00000        0.49999   0.00000    0.0000    50000.00000   0.00000\n")


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

def main():
    question()
    file_name = "sample2.MSH"
    get_data(file_name)
    read_data(npm, nem, lines)
    devise_data(node, element)
    create_file(npm, nem, node, element, dummy_text)

if __name__ == "__main__":
    main()