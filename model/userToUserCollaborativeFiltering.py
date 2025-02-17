import psycopg2 as psy
import numpy as np
from sortedcontainers import SortedList
USER_NUMBER=200948
ri=0
rj=0
movie_rating_data=list()
movie_rating_data_j=list()
ratings=list()
rating_j=list()
sig_i=list()
sig_j=list()
movie_rating_dict=dict()
movie_rating_dict_j=dict()
dev_rating_dict_i=dict()
dev_rating_dict_j=dict()
non_rated_movie_dict=dict()
sij=dict()
movie_i=set()
movie_j=set()
non_rated_movie=set()
pcsl=SortedList()
predication=SortedList()
def pearson_correlation(common_movie_ij:set,dev_rating_i:dict,dev_rating_j:dict,sigma_i,sigma_j):
    numerator =np.sum([dev_rating_i[k]*dev_rating_j[k] for k in common_movie_ij])
    denominator=sigma_i*sigma_j
    return float(numerator)/(float(denominator)+(1e-10))
with psy.connect(dbname='movrec',user='postgres',password='postgres',port='5432',host='localhost') as connect:
    with connect.cursor() as cur:
        #the ratings table will convert to watchevents table 
        #the user_id will send from API
        query=f'''
            SELECT movie_id,
                rating 
                FROM ratings
                WHERE user_id={1}
        '''  
        cur.execute(query)
        movie_rating_data=cur.fetchall()
        movie_i={k[0]for k in movie_rating_data}
        movie_rating_dict={k[0]:k[1] for k in movie_rating_data}
        for j in range(2,USER_NUMBER,1):
            query=f'''
                    SELECT movie_id,
                            rating
                    FROM ratings
                    WHERE user_id={j}
                    '''  
            cur.execute(query)
            movie_rating_data_j=cur.fetchall()
            movie_j={k[0] for k in movie_rating_data_j}
            common_movie=movie_i.intersection(movie_j)
            if len(common_movie)>=5:
                ratings=[k[1]for k in movie_rating_data if k[0] in common_movie]
                ri=np.mean(ratings)
                dev_rating_dict_i={mov:(rat-ri) for mov,rat in movie_rating_dict.items() if mov in common_movie}
                rating_j=[k[1] for k in movie_rating_data_j if k[0] in common_movie]
                movie_rating_dict_j={k[0]:k[1] for k in movie_rating_data_j if k[0] in common_movie }
                rj=np.mean(rating_j)
                dev_rating_dict_j={mov:(rat-rj) for mov,rat in movie_rating_dict_j.items()}
                sig_i=np.sqrt(np.sum([ rat**2 for mov,rat in dev_rating_dict_i.items()]))
                sig_j=np.sqrt(np.sum([ rat**2 for mov,rat in dev_rating_dict_j.items()]))
                peasron_result=pearson_correlation(common_movie,dev_rating_dict_i,dev_rating_dict_j,sig_i,sig_j)
                pcsl.add((peasron_result,j))
                if(len(pcsl)>=25):
                    if(pcsl[0][0]>=0.80):
                        break
                    del pcsl[0]     
        z=24  
        while z>=0:
            query=f'''
            SELECT movie_id,
                    rating
            FROM ratings
            WHERE user_id={pcsl[z][1]}
            '''  
            cur.execute(query)
            movie_rating_data_j=cur.fetchall()
            non_rated_movie={k[0] for k in movie_rating_data_j}-movie_i
            non_rated_movie_dict={k[0]:k[1] for k in movie_rating_data_j if k[0]in non_rated_movie}
            for k in non_rated_movie:
                if k in sij.keys():
                    continue
                query=f'''
                    SELECT 
                        avg_rating
                    FROM ratings_summary
                    WHERE movie_id={k}
                    '''  
                cur.execute(query)
                rj=float(cur.fetchall()[0][0])
                result=(float(pcsl[z][0])*(float(non_rated_movie_dict[k])-float(rj)))/np.abs(float(pcsl[z][0])+1e-10)+rj
                if result>=3:
                    sij[k]=result
            z-=1
for mov,rat in sij.items():
    predication.add((rat,mov))   
i=len(sij.keys())-1
while i >=0:
    print(f"movie id : {predication[i][1]}, movie prdcated rating: {predication[i][0]} ")
    i-=1