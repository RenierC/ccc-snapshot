import pandas as pd
import random as rn
import numpy as np

wallets = pd.read_csv('snap.csv',usecols=[0]).values
hold_cnt = pd.read_csv('snap.csv',usecols=[1]).values

wallet_flat = np.array([item for sublist in wallets for item in sublist])
hold_list = np.array([item for sublist in hold_cnt for item in sublist])

# normalize
hold_list = (hold_list)/float(sum(hold_list))

winners = np.random.choice(wallet_flat, 1000, p=hold_list, replace=False)
print(winners)
pd.DataFrame(winners).to_csv("winners_white_wolf.csv")

