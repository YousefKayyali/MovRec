import torch 
import numpy as np
import psycopg2 as psy
import pandas as pd
num_user=151967+1
num_movie=9447
path=r'D:\movrec\model\hybrid model\hybird_base_model\base_model_MAE_0.6602.pth'
title=torch.load(r'D:\movrec\model\toknized_tensor\title.pt')
cast=torch.load(r'D:\movrec\model\toknized_tensor\cast.pt')
director=torch.load(r'D:\movrec\model\toknized_tensor\director.pt')
genre=torch.load(r'D:\movrec\model\toknized_tensor\genre.pt')
overrview=torch.load(r'D:\movrec\model\toknized_tensor\overrview.pt')
numeric_movie_data=torch.load(r'D:\movrec\model\toknized_tensor\numeric_movie_data.pt')
production_countries=torch.load(r'D:\movrec\model\toknized_tensor\production_countries.pt')
production_compaines=torch.load(r'D:\movrec\model\toknized_tensor\production_compaines.pt')
class FunctionalModel(torch.nn.Module):
    def __init__(self, user_size):
        super(FunctionalModel, self).__init__()
        self.user_emb = torch.nn.Embedding(user_size, 100)
        self.title_emb=torch.nn.Embedding(torch.max(title)+1,20)
        self.overreview_emb=torch.nn.Embedding(torch.max(overrview)+1,20)
        self.director_emb=torch.nn.Embedding(torch.max(director)+1,8)
        self.cast_emb=torch.nn.Embedding(torch.max(cast)+1,10)
        self.genre_emb=torch.nn.Embedding(torch.max(genre)+1,15)
        self.prod_comp_emb=torch.nn.Embedding(torch.max(production_compaines)+1,10)
        self.prod_count_emb=torch.nn.Embedding(torch.max(production_countries)+1,10)
        self.dropout=torch.nn.Dropout(0.2)
    def forward(self, user_ids, movie_ids):
        #because index of tokenized data start from 0 not one 
        movie_ids=movie_ids-1 
        user =self.user_emb(user_ids)
        tit=self.title_emb(title[movie_ids])
        ovrv=self.overreview_emb(overrview[movie_ids])
        dire=self.director_emb(director[movie_ids])
        ct=self.cast_emb(cast[movie_ids])
        gn=self.genre_emb(genre[movie_ids])
        pd_cmp=self.prod_comp_emb(production_compaines[movie_ids])
        pd_count=self.prod_count_emb(production_countries[movie_ids])
        num_data=numeric_movie_data[movie_ids]
        #because the diff of sequence  we must reduce the dim without lossing of data
        ovrv_vec=ovrv.mean(dim=1)
        ct_vec=ct.mean(dim=1)
        gn_vec=gn.mean(dim=1)
        pd_cmp_vec=pd_cmp.mean(dim=1)
        pd_count_vec=pd_count.mean(dim=1) 
        movie=torch.cat((tit,ovrv_vec,dire,ct_vec,gn_vec,pd_cmp_vec,pd_count_vec,num_data),dim=-1)
        movie=self.dropout(movie)
        user=self.dropout(user)
        x = torch.sum(user * movie, dim=-1, keepdim=True)
        return x.squeeze()

model=FunctionalModel(num_user)
model.load_state_dict(torch.load(path))
parameters=list()
name=list()
for n,par in model.named_parameters():
    parameters.append(par)
    name.append(n)
print(parameters[0].shape)
print(torch.mean(parameters[0][1:],dim=0))
# i add it to database as trigger