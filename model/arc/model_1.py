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
    def __init__(self,user_size,user_in_out:list,movie_in_out:list,in_out_list:list,activation_model,activation_user,activation_movie):
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
        self.layer_user=torch.nn.ModuleList()
        self.layer_movie=torch.nn.ModuleList()
        #buildeing a models 
        in_f=user_in_out[-1]
        in_u=100
        in_m=100
        #to prevent error of input  dim not same for concatenated model her we make sure of that

        for idx,out_f in enumerate(in_out_list):
            self.layers.append(torch.nn.Linear(in_f,out_f))
            if (idx+1)%6==0:
                self.layers.append(torch.nn.BatchNorm1d(out_f))
            if (idx+1)%3==1:
             self.layers.append(activation_model)
            if (idx+1)%3==2:
                self.layer_user.append(activation_user)
            if (idx+1)%3==0:
             self.layer_movie.append(activation_movie)

            

                
            in_f=out_f
        for idx,u_out in enumerate(user_in_out):
            self.layer_user.append(torch.nn.Linear(in_u,u_out))
            if (idx+1)%6==0:
                self.layers.append(torch.nn.BatchNorm1d(u_out))
            if (idx+1)%3==1:
             self.layers.append(activation_model)
            if (idx+1)%3==2:
                self.layer_user.append(activation_user)
            if (idx+1)%3==0:
             self.layer_movie.append(activation_movie)

            in_u=u_out
        for idx,m_out in enumerate(movie_in_out):
            self.layer_movie.append(torch.nn.Linear(in_m,m_out))
            if (idx+1)%6==0:
                self.layer_movie.append(torch.nn.BatchNorm1d(m_out))
            if (idx+1)%3==1:
             self.layers.append(activation_model)
            if (idx+1)%3==2:
                self.layer_user.append(activation_user)
            if (idx+1)%3==0:
             self.layer_movie.append(activation_movie)

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
        num  = numeric_movie_data[idx]
        movie = torch.cat([tit, ovrv, dire, ct, gn, pc, pr, num], dim=-1)
        movie = self.model_movie(movie)
        user  = self.model_user(user)
        x     = self.model(user*movie)
        return self.output(x).squeeze()

path_of_base=r'D:\movrec\model\hybrid model\hybird_base_model\base_model_MAE_0.6602.pth'
base_model=FunctionalModel(user_num)
base_model.load_state_dict(torch.load(path_of_base))
model=Model(user_num,[128,150],[128,150],[256,128],torch.nn.ReLU(),torch.nn.LeakyReLU(),torch.nn.LeakyReLU())