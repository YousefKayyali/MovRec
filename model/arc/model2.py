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

class Model(torch.nn.Module):
    def __init__(self,user_size,in_out_list:list,activation):
        super(Model,self).__init__()
        self.user_emb = torch.nn.Embedding(user_size, 100)
        self.title_emb=torch.nn.Embedding(torch.max(title)+1,20)
        self.overreview_emb=torch.nn.Embedding(torch.max(overrview)+1,20)
        self.director_emb=torch.nn.Embedding(torch.max(director)+1,8)
        self.cast_emb=torch.nn.Embedding(torch.max(cast)+1,10)
        self.genre_emb=torch.nn.Embedding(torch.max(genre)+1,15)
        self.prod_comp_emb=torch.nn.Embedding(torch.max(production_compaines)+1,10)
        self.prod_count_emb=torch.nn.Embedding(torch.max(production_countries)+1,10)
        self.layers=torch.nn.ModuleList() 
        in_f=100
        for idx,out_f in enumerate(in_out_list):
            self.layers.append(torch.nn.Linear(in_f,out_f))
            if (idx+1)%3==0:
                self.layers.append(torch.batch_norm())
            self.layers.append(activation)
            in_f=out_f
        self.output=torch.nn.Linear(in_out_list[-1],1)
        self.model=torch.nn.Sequential(*self.layers)
    def forward(self,user_ids,movie_ids):
        movie_ids=movie_ids-1 
        user = self.user_emb(user_ids)
        tit=self.title_emb(title[movie_ids])
        ovrv=self.overreview_emb(overrview[movie_ids])
        dire=self.director_emb(director[movie_ids])
        ct=self.cast_emb(cast[movie_ids])
        gn=self.genre_emb(genre[movie_ids])
        pd_cmp=self.prod_comp_emb(production_compaines[movie_ids])
        pd_count=self.prod_count_emb(production_countries[movie_ids])
        ovrv_vec=ovrv.mean(dim=1)
        ct_vec=ct.mean(dim=1)
        gn_vec=gn.mean(dim=1)
        pd_cmp_vec=pd_cmp.mean(dim=1)
        pd_count_vec=pd_count.mean(dim=1) 
        num_data=numeric_movie_data[movie_ids]
        movie=torch.cat((tit,ovrv_vec,dire,ct_vec,gn_vec,pd_cmp_vec,pd_count_vec,num_data),dim=-1)
        result=movie*user
        x=self.model(result)
        x=self.output(x)
        return x.squeeze()
model=Model(user_num,[256,128],torch.nn.ReLU())