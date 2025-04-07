import pandas as pd
movie=pd.read_csv('cpdata3/movies.csv')
gener=pd.DataFrame(columns=['movie_id','genre'])
c=0
for index,row in movie.iterrows():
    for g in row.get("Genres").split(','):
        gener.loc[c]=[row.get("Movie ID"),g.replace(" ","")]
        c+=1
print(gener.head())
gener.to_csv('cpdata3/gener.csv',index=False)