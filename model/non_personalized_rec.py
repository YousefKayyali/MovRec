import psycopg2 as psy2
import math
import pandas as pd 
import numpy as np
data=0
with psy2.connect(dbname='movrec',user='postgres',password='postgres',port='5432',host='localhost') as conn:
    with conn.cursor() as cu:
        cu.execute('''
        SELECT * 
        FROM model.ratings_summary1
        ''')
        data=cu.fetchall()
rating=[]
for i in range(len(data)):
    row=data[i]
    r=float(row[2])-1.96*math.sqrt(float(row[3]))/math.sqrt(float(row[1]))
    rating.append((row[0],row[1],r))
df=pd.DataFrame(rating,columns=['movie_id','count_rating','rating'])
#This process done just one time 
with psy2.connect(dbname='movrec',user='postgres',password='postgres',port='5432',host='localhost') as conn:
    with conn.cursor() as cu:
        try:
            query='''
            INsERT INTO  non_personalize_recommenadation
            VALUES(%s,%s,%s)
            '''
            for i in df.itertuples(index=False):
              cu.execute(query,(i[0],i[1],i[2]))
        except Exception:
            print("the prosses is already done ")