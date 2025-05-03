import pandas as pd
import os
links=pd.read_csv("ml-32m/links.csv")
print(links.head(),links.shape)
links.drop(labels='imdbId',axis=1,inplace=True)#,'movieId'
print('number of duplicated recored in each column\n',links[links.duplicated('tmdbId')].count(),links[links.duplicated('movieId')].count())
links.drop_duplicates(subset=['movieId'],inplace=True)
links.drop_duplicates(subset=['tmdbId'],inplace=True)
print(links[links.duplicated()])
print('work on duplincation ends \n------------------------------------------------')
print('count na data \n',links.isna().sum())
links.dropna(inplace=True)
print('count na data after drop\n',links.isna().sum(),'\n------------------------------------------------')
lpath=r'cpdata1v2'
os.makedirs(lpath,exist_ok=True)
links.to_csv(lpath+'\\links.csv',index=False)
