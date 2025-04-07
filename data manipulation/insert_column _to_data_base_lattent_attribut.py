import psycopg2 as psy2
import sys
# with psy2.connect(dbname='movrec',user='postgres',password='postgres',port='5432',host='localhost') as connect:
#     with connect.cursor() as cur:
#         try:
#             for i in range(16,76,1):
#                 query=f'ALTER TABLE model.movie_latent_attributs ADD COLUMN l{i} numeric;'
#                 cur.execute(query)
#             for i in range(16,76,1):
#                 query=f"ALTER TABLE model.user_latent_attributs ADD COLUMN l{i} numeric;"
#                 cur.execute(query)
#         except psy2.Error as e:
#             connect.rollback()
#             print(f"the process go wrong\n{e}")
#             sys.exit()

        