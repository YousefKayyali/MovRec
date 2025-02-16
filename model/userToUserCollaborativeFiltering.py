import psycopg2 as psy
import numpy as np
movie_rating_data=[]
USER_NUMBER=200948
with psy.connect(dbname='movrec',user='postgres',password='postgres',port='5432',host='localhost') as connect:
    with connect.cursor() as cur:
        query=f'''
            SELECT movie_id,
                rating
                FROM ratings
                WHERE user_id={1}
        '''  
        cur.execute(query)
        movie_rating_data=cur.fetchall()
movies=[]
ratings=[]
movie_rating_dict={}
for i in movie_rating_data:
    j,k=i 
    movies.append(j)
    ratings.append(k)
    movie_rating_dict[j]=k
movie_rating_data=None
ri=np.mean(ratings)
dev_rating_dict_i={movie:(rating-ri) for movie,rating in movie_rating_dict.items()}