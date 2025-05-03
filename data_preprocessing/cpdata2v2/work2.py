import pandas as pd
import os
links=pd.read_csv(lpath+'\\links.csv')
rating=pd.read_csv(lpath+'\\ratings.csv')
movies=pd.read_csv(lpath+'\\movies_data.csv')
print(links.shape,rating.shape,movies.shape)
print(rating[rating.duplicated()])
print(rating.isna().sum())
print(movies.shape)
print('check duplication\n',movies[movies.duplicated()],'\n-----------------------------------')
print('check duplication\n',movies[movies['Movie ID'].duplicated()],'\n-----------------------------------')
print('check missing value in each column\n',movies.isna().sum(),'\n-----------------------------------')
movies.dropna(axis=0,subset=['Cast','Director','Overview','Genres','Poster Path','Backdrop Path','Release Date'],inplace=True)
print(links.shape)
links=links[links['tmdbId'].isin(movies['Movie ID'])]
links=links[links['movieId'].isin(rating['movieId'])]
print(links.shape)
movies=movies[movies['Movie ID'].isin(links['tmdbId'])]
rating=rating[rating['movieId'].isin(links['movieId'])]
print(len(rating['movieId'].unique()),len(rating['userId'].unique()))
print('check duplication\n',movies[movies.duplicated()],'\n-----------------------------------')
print('check missing value in each column\n',movies.isna().sum(),'\n-----------------------------------')
lpath=r'cpdata2v2'
os.makedirs(lpath,exist_ok=True)
links.to_csv(lpath+'\\links.csv',index=False)
rating.to_csv(lpath+'\\ratings.csv',index=False)
movies.to_csv(lpath+'\\movies.csv',index=False)