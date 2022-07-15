import os
import numpy as np


file_name = "result.d"

with open(file_name, "r", encoding='CP932') as file:
    lines = file.read().splitlines()

"""
    モデルの情報を読込
"""
model_data_info = lines[[i for i, line in enumerate(lines) if '[Model data]' in line][0] + 1]
npm = int(model_data_info.split()[1]) # 接点（ノード）の数
nem = int(model_data_info.split()[3]) # 要素（エレメント）の数
nbm = int(model_data_info.split()[5]) # 拘束の数

nod = 4 # 1つの要素を構成する接点の数（マップド4コーナー）

node = np.zeros([nod+1, nem], dtype=np.int64)
x = np.zeros(npm, dtype=np.float64)
y = np.zeros(npm, dtype=np.float64)
disx = np.zeros(npm, dtype=np.float64)
disy= np.zeros(npm, dtype=np.float64)
strx=np.zeros(nem, dtype=np.float64)
stry=np.zeros(nem, dtype=np.float64)
angl=np.zeros(npm, dtype=np.float64)
sig=np.zeros(nem, dtype=np.float64)

"""
    座標の情報を読込
"""
coord_data_initRow = int([i for i, line in enumerate(lines) if 'node location' in line][0]) + 2

for i, num in enumerate(range(coord_data_initRow, coord_data_initRow+npm, 1)):
    x[i] = float(lines[num].split()[-2])
    y[i] = float(lines[num].split()[-1])

"""
    要素を構成する接点の情報を読込
"""
element_data_initRow = int([i for i, line in enumerate(lines) if 'node condition(local-total)' in line][0]) + 2

for i, num in enumerate(range(element_data_initRow, element_data_initRow+nem, 1)):
    node[0,i] = int(lines[num].split()[-5]) #node_1
    node[1,i] = int(lines[num].split()[-4]) #node_2
    node[2,i] = int(lines[num].split()[-3]) #node_3
    node[3,i] = int(lines[num].split()[-2]) #node_4
    node[4,i] = int(lines[num].split()[-6]) #section number


"""
    displacementの情報を読込
"""
displacement_data_initRow = int([i for i, line in enumerate(lines) if 'Total velocity displacement' in line][0]) + 2

for i, num in enumerate(range(displacement_data_initRow, displacement_data_initRow+npm, 1)):
    disx[i] = float(lines[num].split()[-2])
    disy[i] = float(lines[num].split()[-1])


"""
    応力stressおよび歪みstrainの情報を読込
"""
strain_data_initRow = int([i for i, line in enumerate(lines) if 'No   strain-x-      -y-        -z-        -xy-' in line][0]) + 1

for i, num in enumerate(range(strain_data_initRow, strain_data_initRow+nem, 1)):
    strx[i] = float(lines[num][5:17])
    stry[i] = float(lines[num][17:29])
    strxy = float(lines[num][41:53])
    sig[i] = (strx[i]**2 + stry[i]**2 + 0.5*strxy**2)**(1/2)
    
    

file_name = "rpfem_to_txt.dat"


file = open(file_name, "w", encoding='CP932')

file.write("#TPTMS10\n\n")

# file.write("[ATTRIBUTE]\n")

file.write("[ITEM]\n")
file.write("  X方向変位={-1, 1}\n")
file.write("  Y方向変位={-1, 2}\n")
file.write("  応力={0, 0}\n")

file.write("[NODE]\n")
for i in range(npm):
    file.write("  {node}={{{x}, {y}}}\n".format(node=i+1, x=x[i], y=y[i]))

file.write("[ELEMENT]\n")

for i in range(nem):
    file.write("  {node}={{{x1}, {x2}, {x3}, {x4}}}\n".format(node=node[4][i], x1=node[0][i], x2=node[1][i], x3=node[2][i], x4=node[3][i]))

file.write("[STEP]\n")
file.write("time=0.0\n")
file.write('procname="最終"\n')
file.write("X方向変位={{{}}}\n".format(",".join([str(i) for i in disx])))
file.write("Y方向変位={{{}}}\n".format(",".join([str(i) for i in disy])))
file.write("応力={{{}}}\n".format(",".join([str(i) for i in sig])))

file.close()
