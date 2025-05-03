import pandas as pd
import os
lpath=r'cpdata2v2'
rating=pd.read_csv(lpath+'\\ratings.csv')
movies=pd.read_csv(lpath+'\\movies.csv')
links=pd.read_csv(lpath+'\\links.csv')
print(rating.shape)
temp=rating.groupby('movieId').filter(lambda x:len(x)>=50)
print(temp.shape)
temp=temp.groupby('userId').filter(lambda x:len(x)>=35)
print(temp.shape)
rating=temp
links=links[links['movieId'].isin(rating['movieId'])]
movies=movies[movies['Movie ID'].isin(links['tmdbId'])]
print('movie: ',len(movies['Movie ID'].unique()),'rating movie :',len(rating['movieId'].unique()))
r2t=dict({})
t2m=dict({})
x=1
for index,row in movies.iterrows():
    if t2m.get(row["Movie ID"])==None:
        t2m[row["Movie ID"]]=x
        x+=1
    else:
        print("there is redundancy")
        break
for index,row in links.iterrows():
    if r2t.get(row["movieId"])==None:
        r2t[row["movieId"]]=row['tmdbId']
    else:
        print("there is redundancy")
rating['movieId'] = rating['movieId'].map(lambda x: t2m[r2t[x]])
movies['Movie ID']=movies['Movie ID'].map(lambda x:t2m[x])
rating=rating.drop(labels=['timestamp'],axis=1)
rating['userId'] =pd.factorize(rating['userId'])[0]+1
len(rating['userId'].unique()),len(rating['movieId'].unique())
lpath=r'cpdata3v2'
os.makedirs(lpath,exist_ok=True)
links.to_csv(lpath+'\\links.csv',index=False)
rating.to_csv(lpath+'\\ratings.csv',index=False)
movies.to_csv(lpath+'\\movies.csv',index=False)