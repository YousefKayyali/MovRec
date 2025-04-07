import pandas as pd
import os 
os.makedirs('cpdata4',exist_ok=True)
destination = r"D:\project data\rating data\cpdata4\rating_with_adj.csv"
source = r"D:\project data\rating data\cpdata3\rating.csv"
data = pd.read_csv(source)
print( len(data))
movie = {}
new_rows = [] 
size = len(data)
for i in range(size):
    movie_id= data.iloc[i, 1]
    if movie_id not in movie:
        new_rows.append([-3, movie_id, 2.5])
        new_rows.append([0, movie_id, 2.5])
        movie[movie_id] = True
        if len(movie.keys())==7616:
            break
if new_rows:
    new_data = pd.DataFrame(new_rows, columns=[data.columns[0], data.columns[1], 'rating'])
    data = pd.concat([data, new_data], ignore_index=True)
print( len(data))
data.to_csv(destination, index=False)
