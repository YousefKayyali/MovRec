import pathlib as pt
import pandas as pd
import os
p="images\\backdrops"
poster="images\\posters"
#po=os.listdir(poster)
#bc=os.listdir(p)
def change_data(x):
    number=['1','2','3','4','5','6','7','8','9','0']
    c=0
    for i in x:
        if i not in number:
            return x[:c]
        c+=1
        





 #   por.append(i[:x+1]+i[-10:])    
  #  bcr.append(i[:x+1]+i[-12:])
data=pd.read_csv(r"D:\project data\rating data\update_3\movie_2.csv")
print(data.head())
data.image_id=data.image_id.map(change_data)
print(data)
data.to_csv(r"D:\project data\rating data\update_3\movie_2.csv",index=False)

