import pandas as pd
import random
import authorization
import numpy as np

class moodSongs():
    
    def __init__(self):
        self.df = pd.read_csv("cleanedDataset_Spotify.csv")
        self.df["mood_vec"] = self.df[["valence", "sqenergy"]].values.tolist()
        self.sp = authorization.authorize()
        
    def recommend(self,happy,energy):
        happy=float(happy)
        energy=float(energy)
        happy/=10
        energy/=10
        happy=happy+random.random()/20
        energy=energy+random.random()/20

        if happy>1: happy=1-random.random()/20
        if happy<0: happy=0+random.random()/20
        if energy>1: energy=1-random.random()/20
        if energy<0: energy=0+random.random()/20
        
        print(happy,energy)
        ref_df=self.df
        track_moodvec = np.array([happy, energy])
        ref_df["distances"] = ref_df["mood_vec"].apply(lambda x: np.linalg.norm(track_moodvec-np.array(x)))
        print(ref_df.sort_values(by = "distances", ascending = True).head(1))  
        return ref_df.sort_values(by = "distances", ascending = True).head(1)
