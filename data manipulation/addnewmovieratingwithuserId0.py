import pandas as pd
destination = r"D:\project data\rating data\update_4\rating_4.csv"
source = r"D:\project data\rating data\update_3\rating_3.csv"
data = pd.read_csv(source)
print( len(data))
movie = {}
new_rows = [] 
size = len(data)
for i in range(size):
    movie_name = data.iloc[i, 1]
    if movie_name not in movie:
        new_rows.append([0, movie_name, 2.5])
        movie[movie_name] = True
if new_rows:
    new_data = pd.DataFrame(new_rows, columns=[data.columns[0], data.columns[1], 'rating'])
    data = pd.concat([data, new_data], ignore_index=True)
print( len(data))
data.to_csv(destination, index=False)
