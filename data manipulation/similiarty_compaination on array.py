import pandas as pd
from  typing  import Dict
path=r'D:\movrec\update_4\movie_similarities (1).csv'
df=pd.read_csv(path)
# similerity_as_arr:dict[int,list]=dict()
# for idx,row in df.iterrows():
#     try:
#         similerity_as_arr[int(row[0])].append(int(row[1]))
#     except KeyError as e:
#         similerity_as_arr[int(row[0])]=[int(row[1])]
#     if idx+1 %100000==0:
#         print(f'done {idx}')
# processed_df=pd.DataFrame(similerity_as_arr.items(),columns=['movie_id','similer_movie_id'])
# processed_df.to_csv(r'D:\movrec\update_4\processed_movie_similarities.csv',index=False)
df.drop(['score'],axis=1,inplace=True)
df.to_csv(r'D:\movrec\update_4\processed_movie_similarities_drop_score.csv',index=False)