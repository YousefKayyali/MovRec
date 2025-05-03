class FunctionalModel(torch.nn.Module):
    def __init__(self, user_size,numeric_movie_data):
        super(FunctionalModel, self).__init__()
        self.user = torch.nn.Embedding(user_size, 75)
        self.title=torch.nn.Embedding(torch.max(title)+1,15)
        self.overreview=torch.nn.Embedding(torch.max(overrview)+1,15)
        self.director=torch.nn.Embedding(torch.max(director)+1,5)
        self.cast=torch.nn.Embedding(torch.max(cast)+1,12)
        self.genre=torch.nn.Embedding(torch.max(genre)+1,11)
        self.prod_comp=torch.nn.Embedding(torch.max(production_compaines)+1,5)
        self.prod_count=torch.nn.Embedding(torch.max(production_countries)+1,5)
        self.user_baies = torch.nn.Embedding(user_size, 1)
        self.numeric_movie_data=numeric_movie_data   
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
        #because the diff of sequence  we must reduce the dim without lossing of data
        ovrv_vec=ovrv.mean(dim=1)
        ct_vec=ct.mean(dim=1)
        gn_vec=gn.mean(dim=1)
        pd_cmp_vec=pd_cmp.mean(dim=1)
        pd_count_vec=pd_count.mean(dim=1) 
        movie=torch.cat((tit,ovrv_vec,dire,ct_vec,gn_vec,pd_cmp_vec,pd_count_vec,num_data),dim=-1)
        x = torch.sum(user * movie, dim=-1, keepdim=True)
        x = x + self.user_baies(user_ids)
        return x.squeeze()
class ResNetBlock(torch.nn.Module):
    def __init__(self,in_f,out_f,activation=torch.nn.ELU()):
        super(ResNetBlock,self).__init__()
        self.f1=torch.nn.Linear(in_f,out_f)
        self.f2=torch.nn.Linear(out_f,out_f)
        self.res=torch.nn.Linear(in_f,out_f)
        self.batchNorm1=torch.nn.BatchNorm1d(out_f, momentum=0.3)
        self.batchNorm2=torch.nn.BatchNorm1d(out_f,momentum=0.3)
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
    def __init__(self,user_size,numeric_movie_data,in_out_list:list,activation):
        super(Model,self).__init__()
        self.user = torch.nn.Embedding(user_size, 75)
        self.title=torch.nn.Embedding(torch.max(title)+1,15)
        self.overreview=torch.nn.Embedding(torch.max(overrview)+1,15)
        self.director=torch.nn.Embedding(torch.max(director)+1,5)
        self.cast=torch.nn.Embedding(torch.max(cast)+1,12)
        self.genre=torch.nn.Embedding(torch.max(genre)+1,11)
        self.prod_comp=torch.nn.Embedding(torch.max(production_compaines)+1,5)
        self.prod_count=torch.nn.Embedding(torch.max(production_countries)+1,5)
        self.user_baies = torch.nn.Embedding(user_size, 1)
        self.numeric_movie_data=numeric_movie_data
        self.layers=torch.nn.ModuleList() 
        in_f=151
        for out_f in in_out_list:
            self.layers.append(ResNetBlock(in_f,out_f,activation))
            in_f=out_f
        self.output=torch.nn.Linear(in_out_list[-1],1)

        self.model=torch.nn.Sequential(*self.layers)
    def forward(self,user_ids,movie_ids):
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
        ovrv_vec=ovrv.mean(dim=1)
        ct_vec=ct.mean(dim=1)
        gn_vec=gn.mean(dim=1)
        pd_cmp_vec=pd_cmp.mean(dim=1)
        pd_count_vec=pd_count.mean(dim=1) 
        movie=torch.cat((tit,ovrv_vec,dire,ct_vec,gn_vec,pd_cmp_vec,pd_count_vec,num_data),dim=-1)
        cat_latent_att=torch.cat((self.user(user_ids),self.user_baies(user_ids),movie),dim=1)
        x=self.model(cat_latent_att)
        x=self.output(x)
        return x.squeeze()
path_of_base=r'D:\movrec\model\hybrid model\base model\base_model_1.pth'
base_model=FunctionalModel(user_num,numeric_movie_data)
base_model.load_state_dict(torch.load(path_of_base))
model=Model(user_num,numeric_movie_data,[256,512,1024,2048],torch.nn.ReLU())