import pandas  as pd
import torch
movies=pd.read_csv(r'D:\movrec\data_preprocessing\cpdata3v2\movies.csv')
movies.drop(labels=['Movie ID','Poster Path','Backdrop Path','Keywords','Similar Movies','Movie Homepage'],axis=1,inplace=True)
movies['Release Date']=pd.to_datetime(movies['Release Date'])
numeric_movie_data=movies.select_dtypes(include=['number','bool','datetime'])
movies.drop(labels=numeric_movie_data.columns,axis=1,inplace=True)
numeric_movie_data['year']=numeric_movie_data['Release Date'].dt.year
numeric_movie_data['month']=numeric_movie_data['Release Date'].dt.month
numeric_movie_data['day']=numeric_movie_data['Release Date'].dt.day
numeric_movie_data.drop(labels=['Release Date','Average Rating','Vote Count'],axis=1,inplace=True)
class Tokenizer:
    def __init__(self,split,max_seq_len):
        self.tokn=list()
        self.vocab=list()
        self.index=dict()
        self.num=list()
        self.max_len=max_seq_len
        self.split=split
    def standerization(self,data:str,split:str):
        data=str(data)
        data=data.lower()
        data=re.sub('[\.@#%^&*()!:;\\\$\'"]*',"",data)
        if split != None:
            data=re.split(split,data)
            data=list(map(lambda x:re.sub(' ',"",x),data))
        else:
            data=re.sub(r' ',"",data)
        return data
    def add_to_vocab(self,row):
        if isinstance(row, list):
            for word in row:
                if word not in self.vocab:
                    self.vocab.append(word)
        elif isinstance(row,str):
            if row not in self.vocab:
                self.vocab.append(row)
    def build_vocab(self):
        for li in self.tokn: 
            self.add_to_vocab(li)
    def maper(self):

        self.index={word : idx+2 for idx,word in enumerate(self.vocab)}
        for idx,li in enumerate(self.tokn):
            if isinstance(li, list):
                self.num.append(list())
                for word in li:
                    self.num[idx].append(self.index[word])
            else:
                self.num.append(self.index[li])
    def padding(self):

        for i in self.num:
            if not isinstance(i, list):
                break
            while len(i)>self.max_len:
                i.pop(-1)
            while len(i)<self.max_len:
                i.append(1)
    def transform(self,data):
        self.tokn=list(map(lambda word:self.standerization(word,self.split),data))
        self.build_vocab()
        self.maper()
        self.padding()
        return  self.num
title=torch.tensor(Tokenizer(max_seq_len=1,split=None).transform(movies['Title']),device=device,dtype=torch.long)
cast=torch.tensor(Tokenizer(max_seq_len=3,split=',').transform(movies['Cast'].to_list()),device=device,dtype=torch.long)
genre=torch.tensor(Tokenizer(max_seq_len=4,split=',').transform(movies['Genres'].to_list()),device=device,dtype=torch.long)
overrview=torch.tensor(Tokenizer(max_seq_len=50,split=' ').transform(movies['Overview'].to_list()),device=device,dtype=torch.long)
director=torch.tensor(Tokenizer(max_seq_len=1,split=',').transform(movies['Director'].to_list()),device=device,dtype=torch.long).squeeze()
production_compaines=torch.tensor(Tokenizer(max_seq_len=3,split=',').transform(movies['Production Companies'].to_list()),device=device,dtype=torch.long)
production_countries=torch.tensor(Tokenizer(max_seq_len=2,split=',').transform(movies['Production Countries'].to_list()),device=device,dtype=torch.long)
path=r'D:\movrec\model\toknized_tensor'
torch.save(title,path+"\\title.pt")
torch.save(overrview,path+"\\overrview.pt")
torch.save(director,path+"\\director.pt")
torch.save(cast,path+"\\cast.pt")
torch.save(production_compaines,path+'\\production_compaines.pt')
torch.save(production_countries,path+'\\production_countries.pt')
torch.save(genre,path+'\\genre.pt')
torch.save(numeric_movie_data,path+'\\numeric_movie_data.pt')