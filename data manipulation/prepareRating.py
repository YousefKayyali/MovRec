import pandas as pd
data=pd.read_csv(r"D:\project data\rating data\update_3\rating_2.csv")
data.drop(['timestamp'],axis=1,inplace=True)
print(data)
data.to_csv(r"D:\project data\rating data\update_3\rating_3.csv",index=False,)

