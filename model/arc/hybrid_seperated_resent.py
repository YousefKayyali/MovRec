class FunctionalModel(torch.nn.Module):
    def __init__(self, user_size):
        super(FunctionalModel, self).__init__()
        self.user_emb = torch.nn.Embedding(user_size, 75)
        self.title_emb=torch.nn.Embedding(torch.max(title)+1,15)
        self.overreview_emb=torch.nn.Embedding(torch.max(overrview)+1,15)
        self.director_emb=torch.nn.Embedding(torch.max(director)+1,5)
        self.cast_emb=torch.nn.Embedding(torch.max(cast)+1,12)
        self.genre_emb=torch.nn.Embedding(torch.max(genre)+1,11)
        self.prod_comp_emb=torch.nn.Embedding(torch.max(production_compaines)+1,5)
        self.prod_count_emb=torch.nn.Embedding(torch.max(production_countries)+1,5)
    def forward(self, user_ids, movie_ids):
        #because index of tokenized data start from 0 not one 
        movie_ids=movie_ids-1 
        user = self.user(user_ids)
        tit=self.title(title[movie_ids])
        ovrv=self.overreview(overrview[movie_ids])
        dire=self.director(director[movie_ids])
        ct=self.cast(cast[movie_ids])
        gn=self.genre(genre[movie_ids])
        pd_cmp=self.prod_comp(production_compaines[movie_ids])
        pd_count=self.prod_count(production_countries[movie_ids])
        num_data=self.numeric_movie_data[movie_ids]
        #because the diff of sequence  we must reduce the dim without loesing of data
        ovrv_vec=ovrv.mean(dim=1)
        ct_vec=ct.mean(dim=1)
        gn_vec=gn.mean(dim=1)
        pd_cmp_vec=pd_cmp.mean(dim=1)
        pd_count_vec=pd_count.mean(dim=1) 
        movie=torch.cat((tit,ovrv_vec,dire,ct_vec,gn_vec,pd_cmp_vec,pd_count_vec,num_data),dim=-1)
        x = torch.sum(user * movie, dim=-1, keepdim=True)
        return x.squeeze()
class ResNetBlock(torch.nn.Module):
    def __init__(self,in_f,out_f,activation=torch.nn.ELU()):
        super(ResNetBlock,self).__init__()
        self.f1=torch.nn.Linear(in_f,out_f)
        self.f2=torch.nn.Linear(out_f,out_f)
        self.res=torch.nn.Linear(in_f,out_f)
        self.batchNorm1=torch.nn.LayerNorm(out_f)
        self.batchNorm2=torch.nn.LayerNorm(out_f)
        self.activation=activation
        
    def forward(self,x):
        shortcut=self.res(x)
        x=self.f1(x)
        x=self.batchNorm1(x)
        x=self.activation(x)
        x=self.f2(x)
        x=self.batchNorm2(x)
        x=x+shortcut
        x=self.activation(x)
        return x
class Model(torch.nn.Module):
    def __init__(self,user_size,user_in_out:list,movie_in_out:list,in_out_list:list,activation_model,activation_user,activation_movie):
        super(Model,self).__init__()
        self.user_emb = torch.nn.Embedding(user_size, 75)
        self.title_emb=torch.nn.Embedding(torch.max(title)+1,15)
        self.overreview_emb=torch.nn.Embedding(torch.max(overrview)+1,15)
        self.director_emb=torch.nn.Embedding(torch.max(director)+1,5)
        self.cast_emb=torch.nn.Embedding(torch.max(cast)+1,12)
        self.genre_emb=torch.nn.Embedding(torch.max(genre)+1,11)
        self.prod_comp_emb=torch.nn.Embedding(torch.max(production_compaines)+1,5)
        self.prod_count_emb=torch.nn.Embedding(torch.max(production_countries)+1,5)
        self.numeric_movie_data=numeric_movie_data
        self.layers=torch.nn.ModuleList() 
        self.layer_user=torch.nn.ModuleList()
        self.layer_movie=torch.nn.ModuleList()
        #buildeing a models 
        in_f=user_in_out[-1]+movie_in_out[-1]
        in_u=75
        in_m=75
        #to prevent error of input  dim not same for concatenated model her we make sure of that

        for out_f in in_out_list:
            self.layers.append(ResNetBlock(in_f,out_f,activation_model))
            in_f=out_f
        for u_out in user_in_out:
            self.layer_user.append(ResNetBlock(in_u,u_out,activation_user))
            in_u=u_out
        for m_out in movie_in_out:
            self.layer_movie.append(ResNetBlock(in_m,m_out,activation_movie))
            in_m=m_out
        self.output=torch.nn.Linear(in_out_list[-1],1)
        self.model=torch.nn.Sequential(*self.layers)
        self.model_user=torch.nn.Sequential(*self.layer_user)
        self.model_movie=torch.nn.Sequential(*self.layer_movie)
    def forward(self,user_ids,movie_ids):
        movie_ids = movie_ids - 1
        idx = movie_ids  
        user = self.user_emb(user_ids)
        tit  = self.title_emb(title[idx])      
        ovrv = self.overreview_emb(overrview[idx]).mean(1)
        dire = self.director_emb(director[idx])
        ct   = self.cast_emb(cast[idx]).mean(1)
        gn   = self.genre_emb(genre[idx]).mean(1)
        pc   = self.prod_comp_emb(production_compaines[idx]).mean(1)
        pr   = self.prod_count_emb(production_countries[idx]).mean(1)
        num  = self.numeric_movie_data[idx]
        movie = torch.cat([tit, ovrv, dire, ct, gn, pc, pr, num], dim=-1)
        movie = self.model_movie(movie)
        user  = self.model_user(user)
        x     = self.model(torch.cat([user, movie], dim=1))
        return self.output(x).squeeze()

path_of_base=r'D:\movrec\model\hybrid model\hybird_base_model_adj_data\base_model_adj_4_stratif_user.pth'
base_model=FunctionalModel(user_num)
base_model.load_state_dict(torch.load(path_of_base))
model=Model(user_num,[128,144,256],[128,144,256],[1024,2048,512,1024],torch.nn.ReLU(),torch.nn.LeakyReLU(),torch.nn.LeakyReLU())