import pathlib as pt
import pandas as pd
import os
p="images\backdrops"
poster="images\posters"
po=os.listdir(poster)
bc=os.listdir(p)
number=['1','2','3','4','5','6','7','8','9','0']
#print(po[0][:4]+po[0][-10:])
por=[]

for i in po:
    x=0
    for j in i:
        if j in number :
            x+=1
        else :
            break
    por.append(i[:x+1]+i[-10:])
print(len(por))
bcr=[]
for i in bc:
    x=0
    for j in i:
        if j in number :
            x+=1
        else :
            break
    bcr.append(i[:x+1]+i[-12:])
for i in range(len(por)):
    os.rename(os.path.join(poster, po[i]), os.path.join(poster, por[i]))
for i in range(len(bcr)):
    os.rename(os.path.join(p, bc[i]), os.path.join(p, bcr[i]))