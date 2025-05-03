import psycopg2 
import sys
import numpy as np
from sortedcontainers import SortedList
import pandas as pd
user_id=sys.argv[1]
connection_sting= "postgres://postgres:postgres@localhost:5432/movrec"
def persen_correlation(i:dict,i_prim:dict,avg_rate:dict,common_set):
    i_diff=np.array([(float(i[movie_id])-float(avg_rate[movie_id])) for movie_id in  common_set])
    i_prim_diff=np.array([float(i_prim[movie_id])-float(avg_rate[movie_id]) for movie_id in  common_set])
    numerator=np.dot(i_diff,i_prim_diff)
    denomerator=np.sqrt((i_diff**2).sum())*np.sqrt((i_prim_diff**2).sum() )+1e-31
    return numerator/denomerator
def uset_to_user(user_id):
    with psycopg2.connect(connection_sting) as connect:
        cursor= connect.cursor() 
        query='''
                select movie_id,rating from watch_events WHERE user_id=%s;
                '''
        cursor.execute(query,(user_id,))
        i_movie_rating_map= dict(cursor.fetchall())
        user_movies_set=set(i_movie_rating_map)
        s=SortedList()
        rating1 = pd.read_csv(r'D:\movrec\data_preprocessing\cpdata3v2\ratings.csv')
        data = {}
        for uid, mid, r in zip(rating1['userId'], rating1['movieId'], rating1['rating']):
            data.setdefault(uid, {})[mid] = r
        query='''
        select movie_id,avg from model.ratings_summary1;
            '''
        cursor.execute(query)
        common_movie_rating=dict(cursor.fetchall())
        for u,rating in data.items():
            common_set=user_movies_set & rating.keys()
            if len(common_set)<=14:
                continue
            else:
                result=persen_correlation(i_movie_rating_map,rating,common_movie_rating,common_set)                     
                if result>=0.65:
                    if len(s)<20:
                        s.add((result,u))
                    else:
                        if result>s[0][0]:
                            del s[0]
                            s.add((result,u))
        users=tuple([i[1] for i in s])
        movies_tuple = tuple(user_movies_set)
        if len(users) ==0:
            return 0
        query='''SELECT DISTINCT movie_id,avg_rate FROM model.rating1 WHERE user_id in %s AND movie_id not in %s and movie_id not in (SELECT movie_id FROM model.model_recommendation WHERE user_id=%s)'''
        cursor.execute(query,(users,movies_tuple,user_id))
        size=len(s)
        if size==0:
            return 0
        i=size-1
        non_seen_movie=dict(cursor.fetchall())
        if len(non_seen_movie)>35:
            query='''DELETE FROM  model.user_recommendation WHERE user_id=%s'''
            cursor.execute(query,(user_id,))
        rec_set=dict()
        temp=False
        while i>-1:
            for movie,rat in non_seen_movie.items():
                try:
                    u_r=data[s[i][1]][movie]
                    corr=s[i][0]
                    result=corr*(u_r-rat)/corr+rat
                    if  result>=3.5:
                        rec_set[movie]=result
                        if len(rec_set)>=150:
                            temp=True
                            break
                except KeyError as e:
                    continue
            if temp:
                break
            i=-1
        if len(rec_set)==0:
            return 0
        query='''INSERT INTO model.user_recommendation
                VALUES (%s,%s,%s);'''
        for m,r in rec_set.items():
            try:
                cursor.execute(query,(user_id,m,r))
            except Exception as e:
                connect.rollback()
                continue
        return 1
output=uset_to_user(user_id)