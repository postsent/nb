#!/usr/bin/env python
# coding: utf-8

# # Crypto Prediction

# Question
# 1. how to handle missing value?

# # TODO

# In[ ]:


# impute non zero y
# tune ICA


# #Notes

# 1. This is a regression / prediction problem

# In[ ]:


# gpu_info = !nvidia-smi
# gpu_info = '\n'.join(gpu_info)
# if gpu_info.find('failed') >= 0:
#   print('Not connected to a GPU')
# else:
#   print(gpu_info)


# In[ ]:


# # # # Load the Drive helper and mount
# from google.colab import drive
# drive.mount('/content/drive')


# In[ ]:


#!unzip "/content/drive/My Drive/crypto_prediction/data.zip" -d "/content"


# In[ ]:


# Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from google.colab import files


# In[ ]:


# Load files
train = pd.read_csv('Train.csv')
test = pd.read_csv('Test.csv')
ss = pd.read_csv('SampleSubmission.csv')


# In[ ]:


# check data shapes
train.shape, test.shape, ss.shape


# In[ ]:


# Preview train
train.head()


# In[ ]:


test.head()


# In[ ]:


ss.head()


# In[ ]:


# Check if there any missing values in train set
ax = train.isna().sum().sort_values().plot(kind = 'barh', figsize = (9, 10))
plt.title('Percentage of Missing Values Per Column in Train Set', fontdict={'size':15})
for p in ax.patches:
    percentage ='{:,.0f}%'.format((p.get_width()/train.shape[0])*100)
    width, height =p.get_width(),p.get_height()
    x=p.get_x()+width+0.02
    y=p.get_y()+height/2
    ax.annotate(percentage,(x,y))


# In[ ]:


# Check if there missing values in test set
ax = test.isna().sum().sort_values().plot(kind = 'barh', figsize = (9, 10))
plt.title('Percentage of Missing Values Per Column in Test Set', fontdict={'size':15})

for p in ax.patches:
    percentage ='{:,.1f}%'.format((p.get_width()/test.shape[0])*100)
    width, height =p.get_width(),p.get_height()
    x=p.get_x()+width+0.02
    y=p.get_y()+height/2
    ax.annotate(percentage,(x,y))


# In[ ]:


# fill missing values
train = train.fillna(0)
test = test.fillna(0)


# In[ ]:


train.head()


# In[ ]:


# Check for duplicates
train.duplicated().any(), test.duplicated().any()


# In[ ]:


SEED = 23
# Select main columns to be used in training
main_cols = train.columns.difference(['id', 'close','medium','asset_id', 'social_volume_24h_rank', 'volume_24h_rank', 'market_cap_rank', 'social_score_24h_rank', 'tweet_followers']) # assert_id exclude since all 1, volatility, 'youtube', 

X = train[main_cols]
y = train.close.astype(float)

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.1, random_state=42)


# # Final

# In[ ]:


from sklearn.model_selection import RepeatedKFold

from sklearn.tree import ExtraTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.linear_model import Ridge


from sklearn.model_selection import cross_val_score
from numpy import mean, std


# In[ ]:


# y_cleaned = y_train[y_train != 0]
# y_cleaned.index
# X_cleaned = X_train[X_train.index.isin(list(y_cleaned.index))]
# print(X_cleaned.shape)
# print(y_cleaned.shape)
# y_test_cleaned = y_test[y_test != 0]
# X_test_cleaned = X_test[X_test.index.isin(list(y_test_cleaned.index))]
# print(X_test_cleaned.shape)
# print(y_test_cleaned.shape)


# In[ ]:


# used on X_train instead of X_delete as above

from sklearn.ensemble import IsolationForest

iso = IsolationForest(random_state=SEED, contamination=0.1)
y_pred = iso.fit_predict(X_train)
X_train_cleaned = X_train[np.where(y_pred == 1, True, False)]
y_train_cleaned = y_train[np.where(y_pred == 1, True, False)]

# summarize the shape of the updated training dataset
print(X_train_cleaned.shape, y_train_cleaned.shape)
cleaned,_ = X_train_cleaned.shape

total, _ = X_train.shape
print("number of outlier row removed: ", total - cleaned)
print("percentage of outliers removed: ", (total-cleaned) / total)


# In[ ]:


#submission
ridge_rg = Ridge(alpha=1, solver="auto", random_state=SEED)

#ridge_rg.fit(X_train_cleaned, y_train_cleaned) # 81

ridge_rg.fit(X_train, y_train) # 77

y_pred = ridge_rg.predict(X_test)

#ridge_rg.fit(X_delete_cleaned, y_delete_cleaned) # 81
#ridge_rg.fit(X_reduced, y_delete)x # 81
#y_pred = ridge_rg.predict(X_test_reduced)

#y_pred = ridge_rg.predict(X_test_imputed)

from sklearn.metrics import mean_squared_error
mean_squared_error(y_pred, y_test, squared=False)


# In[ ]:


# evaluate the model

ridge_rg = Ridge(alpha=1, solver="auto", random_state=SEED)

cv = RepeatedKFold(n_splits=10, n_repeats=1, random_state=SEED)
#n_scores = cross_val_score(ridge_rg, X_train, y_train, scoring='neg_root_mean_squared_error', cv=cv, n_jobs=-1, error_score='raise')
n_scores = cross_val_score(ext, X_cleaned, y_cleaned, scoring='neg_root_mean_squared_error', cv=cv, n_jobs=-1, error_score='raise')

print('RMSE: %.3f (%.3f)' % (mean(n_scores), std(n_scores))) # ['id', 'close', 'asset_id'] -> RMSE: -61.251 (11.243)


# In[ ]:


# evaluate the model

ext = ExtraTreesRegressor(random_state=SEED, n_estimators=130, max_depth=39, min_samples_split=2)  # 39->RMSE: -56.458 (8.914)


cv = RepeatedKFold(n_splits=10, n_repeats=1, random_state=SEED)
n_scores = cross_val_score(ext, X_train, y_train, scoring='neg_root_mean_squared_error', cv=cv, n_jobs=-1, error_score='raise')
#n_scores = cross_val_score(ext, X_cleaned, y_cleaned, scoring='neg_root_mean_squared_error', cv=cv, n_jobs=-1, error_score='raise')

print('RMSE: %.3f (%.3f)' % (mean(n_scores), std(n_scores))) # ['id', 'close', 'asset_id'] -> RMSE: -61.251 (11.243)


# In[ ]:


def fit_model(model, X_given=X_train, y_given=y_train, X_test_given=X_test):
    # # Fit Model
    model.fit(X_given, y_given)
    # Predict
    y_pred = model.predict(X_test_given)
    from sklearn.metrics import mean_squared_error
    print(mean_squared_error(y_pred, y_test, squared=False))


# In[ ]:



from sklearn.ensemble import ExtraTreesRegressor

ext = ExtraTreesRegressor(random_state=SEED, n_estimators=130, max_depth=39, min_samples_split=2)  

fit_model(ext, X_train, y_train, X_test)# 59.632469543757274

#fit_model(ext, X_cleaned, y_cleaned, X_test)
#fit_model(ext, X_delete, y_delete)
# 83
#fit_model(ext, X_train_scaled, y_train, X_test_scaled) #worse
#fit_model(ext, X_train_imp_mean, y_train, X_test_imp_mean) 137.67830689850263
#fit_model(ext, X_reduced, y_train, X_test_reduced)


# ## Pre-processing

# ## delete

# In[ ]:


print(len(X_train))
n_zeros_allow =39  #(X_train.shape[1])//6, 41, 39(77)
#print("number of half columns",n_zeros_th)

X_delete = X_train[X_train.eq(0).sum(1) < n_zeros_allow] #X_train[(X_train != 0).all(1)]
print(len(X_delete))
X_delete.head()
y_delete = y_train[y_train.index.isin(list(X_delete.index))]


# ## isoforest

# ### x_delete

# In[ ]:


# # used on X_train instead of X_delete as above

# from sklearn.ensemble import IsolationForest
# from sklearn.metrics import make_scorer, f1_score
# from sklearn import model_selection
# from sklearn.datasets import make_classification

# iso = IsolationForest(random_state=SEED, contamination=0.1)
# y_pred = iso.fit_predict(X_delete)
# X_delete_cleaned = X_delete[np.where(y_pred == 1, True, False)]
# y_delete_cleaned = y_delete[np.where(y_pred == 1, True, False)]

# # summarize the shape of the updated training dataset
# print(X_delete_cleaned.shape, y_delete_cleaned.shape)
# cleaned,_ = X_delete_cleaned.shape

# total, _ = X_delete.shape
# print("number of outlier row removed: ", total - cleaned)
# print("percentage of outliers removed: ", (total-cleaned) / total)


# ### x_train

# In[ ]:


# used on X_train instead of X_delete as above

from sklearn.ensemble import IsolationForest
from sklearn.metrics import make_scorer, f1_score
from sklearn import model_selection
from sklearn.datasets import make_classification

iso = IsolationForest(random_state=SEED, contamination=0.05)
y_pred = iso.fit_predict(X_train)
X_train_cleaned = X_train[np.where(y_pred == 1, True, False)]
y_train_cleaned = y_train[np.where(y_pred == 1, True, False)]

# summarize the shape of the updated training dataset
print(X_train_cleaned.shape, y_train_cleaned.shape)
cleaned,_ = X_train_cleaned.shape

total, _ = X_train.shape
print("number of outlier row removed: ", total - cleaned)
print("percentage of outliers removed: ", (total-cleaned) / total)


# ## standardised (bad)

# In[ ]:


from sklearn import preprocessing
scaler = preprocessing.StandardScaler().fit(X_train)
X_delete_scaled = scaler.transform(X_delete)


# In[ ]:


from sklearn import preprocessing
scaler = preprocessing.StandardScaler().fit(X_test)
X_test_scaled = scaler.transform(X_test)


# ## robust scaler (bad result)

# In[ ]:


from sklearn.preprocessing import RobustScaler
transformer = RobustScaler().fit(X_delete)
X_delete_robust = transformer.transform(X_delete)

transformer = RobustScaler().fit(X_test)
X_test_robust = transformer.transform(X_test)


# ## remove nans,zeros trial

# remove rows contain half nan

# In[ ]:


# np.random.seed([SEED])
# df = pd.DataFrame(np.random.choice([1, np.nan], size=(5, 10)))

# df


# In[ ]:


df.shape


# In[ ]:


# n_not_empty = 6 #df.shape[1]/2
# print(th)
# df.dropna(thresh = n_not_empty, axis = 0, inplace = True)
# df


# remove rows contain half zeros

# In[ ]:


# np.random.seed([SEED])
# df = pd.DataFrame(np.random.choice([1, 0], size=(5, 10)))

# df


# In[ ]:


# df.eq(0).sum(axis=1)


# In[ ]:


# n_zeros =(df.shape[1])//2
# print(n_zeros)
# df[df.eq(0).sum(1) < n_zeros]


# remove rows that contain at least one zero's

# In[ ]:


print(len(X_train))
X_delete = X_train[(X_train != 0).all(1)]
print(len(X_delete))
X_delete.head()
y_delete = y_train[y_train.index.isin(list(X_delete.index))]


# ## remove half zeros

# In[ ]:


# print(len(X_train))
# n_zeros_allow = 42  #(X_train.shape[1])//6
# #print("number of half columns",n_zeros_th)

# X_delete = X_train[X_train.eq(0).sum(1) < n_zeros_allow] #X_train[(X_train != 0).all(1)]
# print(len(X_delete))
# X_delete.head()
# y_delete = y_train[y_train.index.isin(list(X_delete.index))]


# ## iso forest on X_delete

# In[ ]:


from sklearn.ensemble import IsolationForest
from sklearn.metrics import make_scorer, f1_score
from sklearn import model_selection
from sklearn.datasets import make_classification

iso = IsolationForest(random_state=SEED)
y_pred = iso.fit_predict(X_delete)
X_delete_cleaned = X_delete[np.where(y_pred == 1, True, False)]
y_delete_cleaned = y_delete[np.where(y_pred == 1, True, False)]

# summarize the shape of the updated training dataset
print(X_delete_cleaned.shape, y_delete_cleaned.shape)
cleaned,_ = X_delete_cleaned.shape

total, _ = X_delete.shape
print("number of outlier row removed: ", total - cleaned)
print("percentage of outliers removed: ", (total-cleaned) / total)


# In[ ]:


# from sklearn.cluster import DBSCAN, not working

# db = DBSCAN(eps=0.0001, min_samples=100).fit(X_delete)
# X_delete_cleaned = X_delete[db.labels_ != -1]
# y_delete_cleaned = y_delete[db.labels_ != -1]

# # summarize the shape of the updated training dataset
# print(X_delete_cleaned.shape, y_delete_cleaned.shape)
# cleaned,_ = X_delete_cleaned.shape

# total, _ = X_delete.shape
# print("number of outlier row removed: ", total - cleaned)
# print("percentage of outliers removed: ", (total-cleaned) / total)


# In[ ]:


# from sklearn.ensemble import IsolationForest
# from sklearn.metrics import make_scorer, f1_score
# from sklearn import model_selection
# from sklearn.datasets import make_classification

# iso = IsolationForest(random_state=SEED, contamination=0.1)
# y_pred = iso.fit_predict(X_train)
# X_train_cleaned = X_train[np.where(y_pred == 1, True, False)]
# y_train_cleaned = y_train[np.where(y_pred == 1, True, False)]

# # summarize the shape of the updated training dataset
# print(X_train_cleaned.shape, y_train_cleaned.shape)
# cleaned,_ = X_train_cleaned.shape

# total, _ = X_train.shape
# print("number of outlier row removed: ", total - cleaned)
# print("percentage of outliers removed: ", (total-cleaned) / total)


# ## imputation

# ### univariate (bad result)

# In[ ]:


from sklearn.impute import SimpleImputer
X_imp_median = SimpleImputer(missing_values=0, strategy='median')
X_imp_median = X_imp_median.fit_transform(X_train)

import pandas as pd
X_imp_median = pd.DataFrame(X_imp_median, columns = list(X_train.columns))

# dont impute row contain zero, thes outlier should be learnt to predict the missing value as in the final test set
X_cleaned_zero = X_train[X_train.index.isin(list(y_train[y_train.close ==0].index))]

cols = list(X_cleaned_zero.columns)
X_imp_median.loc[X_imp_median.index.isin(X_cleaned_zero.index), cols] = X_cleaned_zero[cols] # replace row from one dataframe to another


# In[ ]:


from sklearn.impute import SimpleImputer
X_test_imp_median = SimpleImputer(missing_values=0, strategy='median')
X_test_imp_median = X_test_imp_median.fit_transform(X_test)

import pandas as pd
X_test_imp_median = pd.DataFrame(X_test_imp_median, columns = list(X_test.columns))

X_test_cleaned_zero = X_test[X_test.index.isin(list(y_test[y_test==0].index))]

cols = list(X_test_cleaned_zero.columns)
X_test_imp_median.loc[X_test_imp_median.index.isin(X_test_cleaned_zero.index), cols] = X_test_cleaned_zero[cols] # replace row from one dataframe to another


# In[ ]:


#len(list(y_test[y_test==0].index))


# In[ ]:


# # zeros
# y_cleaned_zero = y_train[y_train.close.astype(int) == 0]
# X_cleaned_zero = X_train[X_train.index.isin(list(y_cleaned_zero.index))]

# print(X_train.shape)
# print(y_train.shape)
# print()
# print(X_cleaned_zero.shape)
# print(y_cleaned_zero.shape)


# In[ ]:





# In[ ]:


# #(y_train==0).sum()
# # y_train[y_train.close == 0]
# X_cleaned_zero


# In[ ]:


(X_imp_mean==0).astype(int).sum().sort_values()/len(X_imp_mean)*100


# In[ ]:


(X_train==0).astype(int).sum().sort_values()/len(X_train)*100


# In[ ]:


(X_test_imp_median==0).astype(int).sum().sort_values()/len(X_test_imp_median)*100


# In[ ]:


(X_test==0).astype(int).sum().sort_values()/len(X_test)*100


# ### multivariate 

# #### convert numpy to pandas

# In[ ]:


# no zeros
y_cleaned = y_train[y_train != 0]
y_cleaned.index
X_cleaned = X_train[X_train.index.isin(list(y_cleaned.index))]
print(X_cleaned.shape)
print(y_cleaned.shape)

y_test_cleaned = y_test[y_test != 0]
X_test_cleaned = X_test[X_test.index.isin(list(y_test_cleaned.index))]
print(X_test_cleaned.shape)
print(y_test_cleaned.shape)


# In[ ]:


# zeros
y_cleaned_zero = y_train[y_train == 0]
X_cleaned_zero = X_train[X_train.index.isin(list(y_cleaned_zero.index))]
print(X_cleaned_zero.shape)
print(y_cleaned_zero.shape)


# In[ ]:


import numpy as np
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
imp_mean = IterativeImputer(random_state=SEED, missing_values=0) # here the missing value is instead 0 since we fill nan with zeros beforehand

X_imputed = imp_mean.fit_transform(X_cleaned)

import pandas as pd
X_imputed = pd.DataFrame(X_imputed, columns = list(X_cleaned.columns))


# In[ ]:


X_new = X_imputed.append(X_cleaned_zero, ignore_index=True)


# In[ ]:


X_new.head()


# In[ ]:


X_train.head()


# In[ ]:


X_imputed.head()


# In[ ]:


# print(len(X_train))
# X_no_zeros = X_train[(X_train != 0).all(1)]
# print(len(X_no_zeros))
# X_no_zeros.head()
# y_no_zeros = y_train[y_train.index.isin(list(X_no_zeros.index))]


# In[ ]:


# import numpy as np
# from sklearn.experimental import enable_iterative_imputer
# from sklearn.impute import IterativeImputer
# imp_mean = IterativeImputer(random_state=SEED, missing_values=0, max_iter=100) # here the missing value is instead 0 since we fill nan with zeros beforehand

# X_imputed = imp_mean.fit_transform(X_delete)

# import pandas as pd
# X_imputed = pd.DataFrame(X_imputed, columns = list(X_delete.columns))


# In[ ]:


#impute on x_delete
import numpy as np
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
imp_mean = IterativeImputer(random_state=SEED, missing_values=0, sample_posterior=True) # here the missing value is instead 0 since we fill nan with zeros beforehand

X_delete_imputed = imp_mean.fit_transform(X_delete)

import pandas as pd
X_delete_imputed = pd.DataFrame(X_delete_imputed, columns = list(X_delete.columns))


# In[ ]:


X_train.head()


# In[ ]:


X_imputed.head()


# In[ ]:


a = X_delete.describe().loc[['std']]
b = a[a<=1]
b.dropna(axis=1) # drop column contains nan


# In[ ]:


X_train.describe()


# In[ ]:


X_imputed.describe()


# In[ ]:


# Check if there missing values in test set
ax = X_imputed.isna().sum().sort_values().plot(kind = 'barh', figsize = (9, 10))
plt.title('Percentage of Missing Values Per Column in Test Set', fontdict={'size':15})

for p in ax.patches:
    percentage ='{:,.1f}%'.format((p.get_width()/test.shape[0])*100)
    width, height =p.get_width(),p.get_height()
    x=p.get_x()+width+0.02
    y=p.get_y()+height/2
    ax.annotate(percentage,(x,y))


# ### Knn imputer (bad result)

# In[ ]:


from sklearn.impute import KNNImputer

imputer = KNNImputer(n_neighbors=2, weights="uniform", missing_values=0)
X_imp_knn = imputer.fit_transform(X_delete)


# ## Log transform

# In[ ]:


# convert all 0 to 1
X_delete_one = X_delete.replace(0, 1)


# In[ ]:


# Check if there missing values in test set
ax = X_delete_one.isna().sum().sort_values().plot(kind = 'barh', figsize = (9, 10))
plt.title('Percentage of Missing Values Per Column in X_delete_one Set', fontdict={'size':15})

for p in ax.patches:
    percentage ='{:,.1f}%'.format((p.get_width()/X_delete_one.shape[0])*100)
    width, height =p.get_width(),p.get_height()
    x=p.get_x()+width+0.02
    y=p.get_y()+height/2
    ax.annotate(percentage,(x,y))


# In[ ]:


for c in [c for c in X_delete_one.columns if c != 'percent_change_24h']:
    X_delete_one[c] = np.log(X_delete_one[c])


# In[ ]:


X_delete_one.describe()


# In[ ]:


np.log(20)


# # feature selection

# ## FeatureAgglomeration

# In[ ]:


import numpy as np
from sklearn import datasets, cluster

agglo = cluster.FeatureAgglomeration(affinity="euclidean", linkage="average", pooling_func=np.median, n_clusters=44) # , n_clusters=361)
agglo.fit(X_delete)

X_reduced = agglo.transform(X_delete)
X_reduced.shape


# In[ ]:


import numpy as np
from sklearn import datasets, cluster

agglo = cluster.FeatureAgglomeration(affinity="euclidean", linkage="average", pooling_func=np.median, n_clusters=44) # , n_clusters=361)
agglo.fit(X_test)

X_test_reduced = agglo.transform(X_test)
X_test_reduced.shape


# In[ ]:


'feature_preprocessor:feature_agglomeration:affinity': 'euclidean', 'feature_preprocessor:feature_agglomeration:linkage': 'average', 'feature_preprocessor:feature_agglomeration:n_clusters': 361, 'feature_preprocessor:feature_agglomeration:pooling_func': 'median', 


# #PCA

# In[ ]:


from sklearn.decomposition import PCA

pca = PCA().fit(X_train)
plt.figure(figsize=(8,4))
plt.plot(np.cumsum(pca.explained_variance_ratio_))

plt.xlabel('PCA - number of components')
plt.ylabel('cumulative explained variance')


# ##performance compare using PCA

# In[ ]:


for n_features in range(15,46,2):
    print("# features", n_features, end=" ")
    pca = PCA(n_components=n_features)
    pca.fit(X_train)
    X_pca = pca.transform(X_train)
    ridge_rg(X_pca)


# In[ ]:


for n_features in range(1,46,2):
    print("# features", n_features, end=" ")
    pca = PCA(n_components=n_features)
    pca.fit(X_train)
    X_pca = pca.transform(X_train)
    #ext_rg(X_pca)
    ext_rg(X_pca)


# In[ ]:


# for n_features in range(15,46,5):
#     print("# features", n_features, end=" ")
#     pca = PCA(n_components=n_features)
#     pca.fit(X_train)
#     X_pca = pca.transform(X_train)
#     X_pca_test = pca.transform(X_test)
#     #submission
#     ext_model = ExtraTreeRegressor(random_state=SEED, max_depth=21, splitter="best")

#     #ext_model.fit(X_train_cleaned, y_train_cleaned)
#     ext_model.fit(X_pca, y_train)

#     y_pred = ext_model.predict(X_pca_test)

#     from sklearn.metrics import mean_squared_error
#     a = mean_squared_error(y_pred, y_test, squared=False)
#     print(a)


# #Baseline score

# In[ ]:


# Load libraries

from pandas import set_option
#from pandas.tools.plotting import scatter_matrix
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_val_score # scoring - https://scikit-learn.org/stable/modules/model_evaluation.html
from sklearn.model_selection import GridSearchCV

from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score

from sklearn.pipeline import Pipeline

from sklearn import metrics

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


# #TabNet

# In[ ]:


#!pip install pytorch-tabnet


# In[ ]:


from pytorch_tabnet.tab_model import TabNetRegressor
import torch.nn as nn
import torch

#criterion = torch.nn.MSELoss()
criterion = nn.L1Loss()

# class RMSELoss(nn.Module):
#     def __init__(self, eps=1e-8):
#         super().__init__()
#         self.mse = nn.MSELoss()
#         self.eps = eps
        
#     def forward(self,yhat,y):
#         loss = torch.sqrt(self.mse(yhat,y) + self.eps)
#         return loss

# criterion = RMSELoss()

clf = TabNetRegressor(
    optimizer_fn=torch.optim.SGD,
    optimizer_params=dict(lr=9e-1, momentum=0.9, weight_decay=5e-4, nesterov =True), # 7 -> 250
    scheduler_params={"patience":10, "factor":0.7}, # 5, 0.7
    #n_steps=3,
    lambda_sparse=1e-4,
    scheduler_fn=torch.optim.lr_scheduler.ReduceLROnPlateau, mask_type='entmax' 
    #scheduler_fn=torch.optim.lr_scheduler.StepLR, mask_type='entmax' # StepLR
)  

# scheduler_params={"step_size":10, # how to use learning rate scheduler
#                     "gamma":0.7},

# y_train_net = y_delete.values.reshape(-1, 1)
# X_train_net = X_delete.values

y_train_net = y_delete.values.reshape(-1, 1)
X_train_net = X_scaled

# y_train_net = y_train.values.reshape(-1, 1)
# X_train_net = X_train.values

clf.fit(
  X_train_net, y_train_net,
  eval_set=[(X_train_net, y_train_net)],
  eval_metric=['rmse'],
  max_epochs=2000,
  batch_size=1024*2, virtual_batch_size=128,
  drop_last=False,
  patience=500,
  loss_fn=criterion
)


# In[ ]:


clf


# In[ ]:


# save tabnet model
saving_path_name = "./tabnet_model_test_1"
saved_filepath = clf.save_model(saving_path_name)

# define new model with basic parameters and load state dict weights
loaded_clf = TabNetRegressor(
    optimizer_params=dict(lr=7e-2), # 7 -> 250
    scheduler_params={"patience":5, "factor":0.5}, # 0.7
    #n_steps=3,
    lambda_sparse=1e-4,
    scheduler_fn=torch.optim.lr_scheduler.ReduceLROnPlateau, mask_type='entmax' 
    #scheduler_fn=torch.optim.lr_scheduler.StepLR, mask_type='entmax' # StepLR
)  

loaded_clf.load_model(saved_filepath)


# In[ ]:


preds = clf.predict(X_test.values)

from sklearn.metrics import mean_squared_error
mean_squared_error(preds, y_test.values, squared=False)


# In[ ]:


# from pytorch_tabnet.pretraining import TabNetPretrainer
# from pytorch_tabnet.tab_model import TabNetRegressor
# import torch

# unsupervised_model = TabNetPretrainer(
#     optimizer_fn=torch.optim.Adam,
   
#     mask_type='entmax', # "sparsemax",
    
    
# )

# unsupervised_model.fit(
#     X_train=X_train_net,
#     eval_set=[X_train_net],
#     pretraining_ratio=0.8,
#     drop_last=False,
#     batch_size=2048, virtual_batch_size=128,
# )

# clf = TabNetRegressor()  

# clf.fit(
#   X_train_net, y_train_net,
#   eval_set=[(X_train_net, y_train_net)],
#   eval_metric=['rmse'],
#   from_unsupervised=unsupervised_model,
#    max_epochs=2000
# )


# In[ ]:


unsupervised_model.predict(X_test.values)


# In[ ]:


preds = clf.predict(X_test)


# 
# #Model selection

# In[ ]:


from sklearn.model_selection import RepeatedKFold
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.tree import ExtraTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import RobustScaler

from sklearn.linear_model import Ridge
from sklearn.kernel_ridge import KernelRidge

from sklearn.model_selection import cross_val_score
from numpy import mean, std


# ##GradientBoostingRegressor

# In[ ]:


# evaluate the model
model = GradientBoostingRegressor()
cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=SEED)
n_scores = cross_val_score(model, X_train, y_train, scoring='neg_root_mean_squared_error', cv=cv, n_jobs=-1, error_score='raise')


# In[ ]:


print('RMSE: %.3f (%.3f)' % (mean(n_scores), std(n_scores))) # RMSE: -89.512 (8.465)


# ##*ExtraTreeRegressor*

# ### iso

# In[ ]:


# used on X_train instead of X_delete as above

from sklearn.ensemble import IsolationForest
from sklearn.metrics import make_scorer, f1_score
from sklearn import model_selection
from sklearn.datasets import make_classification

iso = IsolationForest(random_state=SEED, contamination=0.1)
y_pred = iso.fit_predict(X_train)
X_train_cleaned = X_train[np.where(y_pred == 1, True, False)]
y_train_cleaned = y_train[np.where(y_pred == 1, True, False)]

# summarize the shape of the updated training dataset
print(X_train_cleaned.shape, y_train_cleaned.shape)
cleaned,_ = X_train_cleaned.shape

total, _ = X_train.shape
print("number of outlier row removed: ", total - cleaned)
print("percentage of outliers removed: ", (total-cleaned) / total)


# In[ ]:


# # used on X_train instead of X_delete as above

# from sklearn.ensemble import IsolationForest
# from sklearn.metrics import make_scorer, f1_score
# from sklearn import model_selection
# from sklearn.datasets import make_classification

# iso = IsolationForest(random_state=SEED, contamination=0.3)
# y_pred = iso.fit_predict(X_imputed)
# X_imputed_cleaned = X_imputed[np.where(y_pred == 1, True, False)]
# y_imputed_cleaned = y_train[np.where(y_pred == 1, True, False)]

# # summarize the shape of the updated training dataset
# print(X_imputed_cleaned.shape, y_imputed_cleaned.shape)
# cleaned,_ = X_imputed_cleaned.shape

# total, _ = X_imputed.shape
# print("number of outlier row removed: ", total - cleaned)
# print("percentage of outliers removed: ", (total-cleaned) / total)


# ### evaluate the model

# In[ ]:


def ext_rg(X_given,y_given=y_train):
  model = ExtraTreeRegressor(random_state=SEED, max_depth=21, splitter="best") #ExtraTreeRegressor(random_state=SEED, max_depth=26)
  #model = ExtraTreeRegressor(random_state=SEED, criterion="friedman_mse", max_depth=None, max_features=0.7929825166874074, max_leaf_nodes=None, min_impurity_decrease=0, min_samples_leaf=2, min_samples_split=6, min_weight_fraction_leaf=0)
  #model = SimpleRegressionPipeline({'data_preprocessing:categorical_transformer:categorical_encoding:__choice__': 'no_encoding', 'data_preprocessing:categorical_transformer:category_coalescence:__choice__': 'minority_coalescer', 'data_preprocessing:numerical_transformer:imputation:strategy': 'mean', 'data_preprocessing:numerical_transformer:rescaling:__choice__': 'minmax', 'feature_preprocessor:__choice__': 'feature_agglomeration', 'regressor:__choice__': 'extra_trees', 'data_preprocessing:categorical_transformer:category_coalescence:minority_coalescer:minimum_fraction': 0.013555629780288401, 'feature_preprocessor:feature_agglomeration:affinity': 'euclidean', 'feature_preprocessor:feature_agglomeration:linkage': 'average', 'feature_preprocessor:feature_agglomeration:n_clusters': 361, 'feature_preprocessor:feature_agglomeration:pooling_func': 'median', 'regressor:extra_trees:bootstrap': 'False', 'regressor:extra_trees:criterion': 'friedman_mse', 'regressor:extra_trees:max_depth': 'None', 'regressor:extra_trees:max_features': 0.7929825166874074, 'regressor:extra_trees:max_leaf_nodes': 'None', 'regressor:extra_trees:min_impurity_decrease': 0.0, 'regressor:extra_trees:min_samples_leaf': 2, 'regressor:extra_trees:min_samples_split': 6, 'regressor:extra_trees:min_weight_fraction_leaf': 0.0})
  
  cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=SEED)
  n_scores = cross_val_score(model, X_given, y_given, scoring='neg_root_mean_squared_error', cv=cv)
  print('RMSE: %.3f (%.3f)' % (mean(n_scores), std(n_scores))) # RMSE: -104.756 (33.902), X_train_cleaned -> RMSE: -39.699 (14.663)

#ext_rg(X_train) # current: RMSE: -82.658 (14.536), without youtube, medium columns -> RMSE: -80.446 (18.064)
#ext_rg(X_train_cleaned, y_train_cleaned)
ext_rg(X_delete, y_delete)
#ext_rg(X_imp_mean, y_delete)
#ext_rg(X_reduced, y_delete)


# In[ ]:


'regressor:extra_trees:bootstrap': 'False', 'regressor:extra_trees:criterion': 'friedman_mse', 'regressor:extra_trees:max_depth': 'None', 'regressor:extra_trees:max_features': 0.7929825166874074, 'regressor:extra_trees:max_leaf_nodes': 'None', 'regressor:extra_trees:min_impurity_decrease': 0.0, 'regressor:extra_trees:min_samples_leaf': 2, 'regressor:extra_trees:min_samples_split': 6, 'regressor:extra_trees:min_weight_fraction_leaf': 0.0},


# ## submission

# In[ ]:


#submission
ext_model = ExtraTreeRegressor(random_state=SEED, max_depth=21, splitter="best")

#ext_model.fit(X_train_cleaned, y_train_cleaned)
#ext_model.fit(X_train, y_train) # 103.01549008547863, 104.76005740251006 - remove highly missing cols

#ext_model.fit(X_no_zeros, y_no_zeros) worse
#ext_model.fit(X_imputed, y_train)

ext_model.fit(X_delete, y_delete) 
y_pred = ext_model.predict(X_test)

#ext_model.fit(X_scaled, y_delete) # zero mean worse
#y_pred = ext_model.predict(X_test_scaled)

from sklearn.metrics import mean_squared_error
mean_squared_error(y_pred, y_test, squared=False)


# In[ ]:


clf = ExtraTreeRegressor(random_state=SEED)
clf.fit(X_delete, y_delete.values.ravel())

# #############################################################################
# Plot feature importance
feature_importance = clf.feature_importances_
# make importances relative to max importance
feature_importance = 100.0 * (feature_importance / feature_importance.max())
sorted_idx = np.argsort(feature_importance)

pos = np.arange(sorted_idx.shape[0]) + 1 # start from 1
plt.figure(figsize=(60,15))
plt.subplot(1, 2, 2)
plt.barh(pos, feature_importance[sorted_idx], align='center')
plt.yticks(pos, X_delete.columns[sorted_idx])#boston.feature_names[sorted_idx])
plt.xlabel('Relative Importance')
plt.title('Variable Importance')
plt.show()


# ##random tree

# In[ ]:


# evaluate the model
model = RandomForestRegressor()
cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=SEED)
#n_scores = cross_val_score(model, X_train_cleaned, y_train_cleaned, scoring='neg_root_mean_squared_error', cv=cv, n_jobs=-1, error_score='raise')
n_scores = cross_val_score(model, X_train, y_train, scoring='neg_root_mean_squared_error', cv=cv, n_jobs=-1, error_score='raise')
from numpy import mean, std
print('RMSE: %.3f (%.3f)' % (mean(n_scores), std(n_scores))) # RMSE: -57.897 (6.050), x_trained_clean -> RMSE: -55.651 (21.680), X_delete -> -124.312 (30.900)


# In[ ]:


#submission
rand_tree_model = RandomForestRegressor(random_state=SEED) # , max_depth=21

#rand_tree_model.fit(X_train_cleaned, y_train_cleaned)
#rand_tree_model.fit(X_train, y_train)
rand_tree_model.fit(X_delete, y_delete)

y_pred = rand_tree_model.predict(X_test)

from sklearn.metrics import mean_squared_error
mean_squared_error(y_pred, y_test, squared=False)


# ## bayeisan regressor

# In[ ]:


from sklearn.preprocessing import PolynomialFeatures
poly = PolynomialFeatures(2, interaction_only=True)
X_poly = poly.fit_transform(X_train)

X_test_poly = poly.fit_transform(X_test)


# In[ ]:


X_train.shape


# In[ ]:


X_poly.shape


# ## add features

# In[ ]:


SEED = 23
# Select main columns to be used in training
main_cols = train.columns.difference(['id', 'close','medium','asset_id', 'social_volume_24h_rank', 'volume_24h_rank', 'market_cap_rank', 'social_score_24h_rank', 'tweet_followers']) # assert_id exclude since all 1, volatility, 'youtube', 
#main_cols = train.columns.difference(['id', 'close','medium','asset_id'])

X = train[main_cols]
y = train.close.astype(float)

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.1, random_state=42)
#X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2, random_state=23)

X_train = X_train.reset_index().drop("index", 1)
y_train = y_train.reset_index().drop("index", 1)


# In[ ]:


y_train.head()


# In[ ]:


from sklearn.decomposition import PCA, TruncatedSVD, FastICA
from sklearn.random_projection import GaussianRandomProjection, SparseRandomProjection

N_COMP = 40  # 30 PCA - 53, ICA: 40 - 49.5, 35 - 50

print("\nStart decomposition process...")

print("ICA")
ica = FastICA(n_components=40, random_state=17)
ica_results_train = ica.fit_transform(X_train)
ica_results_test = ica.transform(X_test)


print("Append decomposition components to datasets...")
for i in range(1, 40 + 1):


    X_train['ica_' + str(i)] = ica_results_train[:, i - 1]
    X_test['ica_' + str(i)] = ica_results_test[:, i - 1]

   
print('\nTrain shape: {}\nTest shape: {}'.format(X_train.shape, X_test.shape))


# In[ ]:


# from sklearn.decomposition import PCA, TruncatedSVD, FastICA
# from sklearn.random_projection import GaussianRandomProjection, SparseRandomProjection

# N_COMP = 40  # 30 PCA - 53, ICA: 40 - 49.5, 35 - 50

# print("\nStart decomposition process...")
# # print("PCA")
# # pca = PCA(n_components=N_COMP, random_state=17)
# # pca_results_train = pca.fit_transform(X_train)
# # pca_results_test = pca.transform(X_test)
# # print(pca.explained_variance_ratio_)

# # print("tSVD")
# # tsvd = TruncatedSVD(n_components=N_COMP, random_state=17)
# # tsvd_results_train = tsvd.fit_transform(X_train)
# # tsvd_results_test = tsvd.transform(X_test)

# print("ICA")
# ica = FastICA(n_components=40, random_state=17)
# ica_results_train = ica.fit_transform(X_train)
# ica_results_test = ica.transform(X_test)

# # print("GRP") # to be reduced
# # grp = GaussianRandomProjection(n_components=N_COMP, eps=0.1, random_state=17)
# # grp_results_train = grp.fit_transform(X_train)
# # grp_results_test = grp.transform(X_test)

# # print("SRP")
# # srp = SparseRandomProjection(n_components=N_COMP, dense_output=True, random_state=17)
# # srp_results_train = srp.fit_transform(X_train)
# # srp_results_test = srp.transform(X_test)

# print("Append decomposition components to datasets...")
# for i in range(1, N_COMP + 1):
#     # X_train['pca_' + str(i)] = pca_results_train[:, i - 1]
#     # X_test['pca_' + str(i)] = pca_results_test[:, i - 1]
    
   
#     # X_train['tsvd_' + str(i)] = tsvd_results_train[:, i - 1]
#     # X_test['tsvd_' + str(i)] = tsvd_results_test[:, i - 1]

#     X_train['ica_' + str(i)] = ica_results_train[:, i - 1]
#     X_test['ica_' + str(i)] = ica_results_test[:, i - 1]


#     # X_train['grp_' + str(i)] = grp_results_train[:, i - 1]
#     # X_test['grp_' + str(i)] = grp_results_test[:, i - 1]

#     # X_train['srp_' + str(i)] = srp_results_train[:, i - 1]
#     # X_test['srp_' + str(i)] = srp_results_test[:, i - 1]

# print('\nTrain shape: {}\nTest shape: {}'.format(X_train.shape, X_test.shape))


# In[ ]:


# from sklearn import linear_model

# reg = linear_model.BayesianRidge(compute_score=True)
# #submission

# reg.fit(X_poly, y_train)

# y_pred = reg.predict(X_test_poly)

# from sklearn.metrics import mean_squared_error
# mean_squared_error(y_pred, y_test, squared=False)


# In[ ]:


from sklearn import linear_model

reg = linear_model.BayesianRidge(compute_score=True)
#submission

reg.fit(X_train, y_train)

y_pred = reg.predict(X_test)

from sklearn.metrics import mean_squared_error
mean_squared_error(y_pred, y_test, squared=False)


# ##kNN regressor

# In[ ]:


from sklearn.neighbors import KNeighborsRegressor
neigh = KNeighborsRegressor(n_neighbors=20)
cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=SEED)
n_scores = cross_val_score(neigh, X_train_cleaned, y_train_cleaned, scoring='neg_root_mean_squared_error', cv=cv, n_jobs=-1, error_score='raise')
from numpy import mean, std
print('RMSE: %.3f (%.3f)' % (mean(n_scores), std(n_scores))) 


# ##xgboost

# In[ ]:


#!pip install xgboost


# In[ ]:


X_t = X_train[:-1000]
X_t.shape


# In[ ]:


#submission
SEED = 104
model = XGBRegressor(objective='reg:squarederror', max_depth=16, n_estimators=150, #16
                     learning_rate= 0.0764, random_state=SEED, gamma=0, booster="gbtree", # , subsample=0.90,
                      tree_method='auto', # gpu_hist
                      subsample=1,
                      colsample_bytree=1,
                      reg_alpha=0.5, # 52.96502463981406:0.5 without those added columns
                      reg_lambda=1 
                     # min_child_weight, TODO
                     ) #54.14->0.0765
# cut_off = -1000
# X_t = X_train[:cut_off]
# y_t = y_train[:cut_off]
# X_c = X_train[cut_off:]
# y_c = y_train[cut_off:]

#model.fit(X_t, y_t, eval_metric="rmse",  eval_set=[(X_t, y_t), (X_c, y_c)], verbose=True) # 49.51422068156787

#model.fit(X_log, y_train)
#model.fit(X_poly, y_train)
#model.fit(X_train_cleaned, y_train_cleaned)
#model.fit(X_imp_median, y_train)

model.fit(X_train, y_train) # 49.51422068156787
y_pred = model.predict(X_test)


#y_pred = model.predict(X_test_imp_median)


from sklearn.metrics import mean_squared_error
mean_squared_error(y_pred, y_test, squared=False)


# In[ ]:


y_pred[(y_pred<2000)] = 0
from sklearn.metrics import mean_squared_error
mean_squared_error(y_pred, y_test, squared=False)


# In[ ]:


y_pred[y_pred < 0.01]


# In[ ]:


y_pred[y_pred < 0.01] = 0

from sklearn.metrics import mean_squared_error
mean_squared_error(y_pred, y_test, squared=False)


# In[ ]:



# model = XGBRegressor(objective='reg:squarederror', max_depth=16, n_estimators=150, #16
#                      learning_rate=0.0764, random_state=SEED, gamma=0, booster="gbtree", # , subsample=0.90,
#                       tree_method='auto', # gpu_hist
#                       subsample=1,
#                       colsample_bytree=1,
#                       reg_alpha=0.5, # 52.96502463981406:0.5 without those added columns
#                       reg_lambda=1
#                      ) #54.14->0.0765


# cv = RepeatedKFold(n_splits=10, n_repeats=1, random_state=SEED)
# #n_scores = cross_val_score(model, X_train, y_train, scoring='neg_root_mean_squared_error', cv=cv, n_jobs=-1, error_score='raise')
# #n_scores = cross_val_score(model, X_cleaned, y_cleaned, scoring='neg_root_mean_squared_error', cv=cv, n_jobs=-1, error_score='raise')
# n_scores = cross_val_score(model, X_log, y_train, scoring='neg_root_mean_squared_error', cv=cv, n_jobs=-1, error_score='raise')

# print('RMSE: %.3f (%.3f)' % (mean(n_scores), std(n_scores))) # RMSEE: -63.467 (4.710)


# In[ ]:


# model = XGBRegressor(objective='reg:squarederror', max_depth=16, n_estimators=200, 
#                      learning_rate=0.07, random_state=SEED, gamma=0, booster="gbtree", # , subsample=0.90,
#                       tree_method='auto', # gpu_hist
#                       subsample=1,
#                       colsample_bytree=1,
#                       reg_alpha=0.5, # 52.96502463981406:0.5 without those added columns
#                       reg_lambda=1
#                      ) #54.14->0.0765

# model.fit(X_cleaned, y_cleaned) #61.3

# y_pred = model.predict(X_test_cleaned)

# from sklearn.metrics import mean_squared_error
# mean_squared_error(y_pred, y_test_cleaned, squared=False)


# In[ ]:


a = X_train.skew(axis = 0, skipna = True)
X_log = X_train.copy()
for s in list(a[abs(a)>0.5].index):
  X_log[s] = X_log[s].replace(0, 1)
  X_log[s] = np.log(X_log[s])


# In[ ]:


X_log.skew(axis = 0, skipna = True)

#X_train['high'].iloc(10337)
#X_train['high'].loc[[10337]]


# In[ ]:


b = X_test.skew(axis = 0, skipna = True)
X_test_log = X_test.copy()
for s in list(b[abs(b)>0.5].index):
  X_test_log[s] = X_test_log[s].replace(0, 1)
  X_test_log[s] = np.log(X_test_log[s])


# In[ ]:


X_test_log.skew(axis = 0, skipna = True)


# ### importance

# In[ ]:


from xgboost import plot_importance
import matplotlib.pyplot as plt

#print(model.feature_importances_)
# plot feature importance
fig, ax = plt.subplots(figsize=(15, 15))
plot_importance(model, ax=ax)
plt.show()


# ## submit

# In[ ]:


from sklearn.decomposition import FastICA

test_submit = test[main_cols].copy()
print("\nStart decomposition process...")

print("ICA")
submit_ica_test = ica.transform(test_submit)

print("Append decomposition components to datasets...")
for i in range(1, N_COMP + 1):

    test_submit['ica_' + str(i)] = submit_ica_test[:, i - 1]


print('\nTrain shape: {}\nTest shape: {}'.format(X_train.shape, test_submit.shape))


# In[ ]:


# Make predictions in test set and prepare submission file
predictions = model.predict(test_submit) # test[main_cols]
sub_file = ss.copy()
sub_file.close = predictions
sub_file.to_csv('Baseline.csv', index = False)


# In[ ]:


sub_file.head()


# In[ ]:


files.download('Baseline.csv') 


# In[ ]:


import xgboost as xgb

dmatrix = xgb.DMatrix(data=X_train, label=y_train)
params={ 'objective':'reg:squarederror',
         'max_depth': 6, 
         'colsample_bylevel':0.5,
         'learning_rate':0.5, # 0.5,
        'n_estimators':200,
        #'alpha ':2,
        'lambda ':1.5,
         'random_state':SEED}
cv_results = xgb.cv(dtrain=dmatrix, params=params, nfold=10, metrics={'rmse'}, as_pandas=True, seed=SEED)
print('RMSE: %.2f' % cv_results['test-rmse-mean'].min())


# In[ ]:


from sklearn.model_selection import RandomizedSearchCV

params = {
          'max_depth': [3, 5, 6, 10, 15, 20],
           'learning_rate': [0.01, 0.1, 0.2, 0.3],
           'subsample': np.arange(0.5, 1.0, 0.1),
           'colsample_bytree': np.arange(0.4, 1.0, 0.1),
           'colsample_bylevel': np.arange(0.4, 1.0, 0.1),
           'n_estimators': [100, 500, 1000]}
xgbr = xgb.XGBRegressor(seed = SEED, objective='reg:squarederror')

clf = RandomizedSearchCV(estimator=xgbr,
                         param_distributions=params,
                         scoring='neg_root_mean_squared_error',
                         n_iter=25,
                         verbose=1)

clf.fit(X_train, y_train)

print("Best parameters:", clf.best_params_)
print("Lowest RMSE: ", (-clf.best_score_)**(1/2.0))


# ##LGBM

# In[ ]:


#!pip install lightgbm
from lightgbm import LGBMRegressor
model = LGBMRegressor()
cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=SEED)
n_scores = cross_val_score(model, X_train, y_train, scoring='neg_root_mean_squared_error', cv=cv, n_jobs=-1, error_score='raise')
print('MAE: %.3f (%.3f)' % (mean(n_scores), std(n_scores))) # MAE: -107.906 (15.543)


# ##catboost

# In[ ]:


#!pip install catboost


# In[ ]:


from catboost import CatBoostRegressor
model = CatBoostRegressor(verbose=0, n_estimators=100)
cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=SEED)
n_scores = cross_val_score(model, X_train, y_train, scoring='neg_root_mean_squared_error', cv=cv, n_jobs=-1, error_score='raise')
print('MAE: %.3f (%.3f)' % (mean(n_scores), std(n_scores))) # MAE: -227.432 (38.044)


# In[ ]:


from catboost import CatBoostRegressor

model = CatBoostRegressor(verbose=0, iterations=200, depth=5, learning_rate=0.365, l2_leaf_reg=1, loss_function="RMSE") # 5-193

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

from sklearn.metrics import mean_squared_error
mean_squared_error(y_pred, y_test, squared=False)


# ##SVR

# In[ ]:


from sklearn.svm import SVR
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

#regr = make_pipeline(StandardScaler(), SVR(C=1.0, epsilon=0.2))
regr = SVR(C=1.0, epsilon=0.2)

cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=SEED)
n_scores = cross_val_score(regr, X_train, y_train, scoring='neg_root_mean_squared_error', cv=cv, n_jobs=-1, error_score='raise')
print('MAE: %.3f (%.3f)' % (mean(n_scores), std(n_scores)))


# ##ridge

# ### test

# In[ ]:


#ridge_rg = make_pipeline(StandardScaler(), Ridge(alpha=1.0))
def ridge_rg(X_given, y_given=y_train):
  ridge_rg = Ridge(alpha=1, solver="auto") # 52
  #ridge_rg = make_pipeline(RobustScaler(), Ridge(alpha=1.0)) # 77
  #ridge_rg = KernelRidge(alpha=1.0)

  cv = RepeatedKFold(n_splits=10, n_repeats=5, random_state=SEED)
  n_scores = cross_val_score(ridge_rg, X_given, y_given, scoring='neg_root_mean_squared_error', cv=cv, n_jobs=-1, error_score='raise')
  print('RMSE: %.3f (%.3f)' % (mean(n_scores), std(n_scores)))

#ridge_rg(X_imp_mean,y_delete) 
#ridge_rg(X_cleaned,y_cleaned) # RMSE: -63.052 (6.967)
#ridge_rg(X_delete_cleaned,y_delete_cleaned) # RMSE: -32.634 (56.319)
#ridge_rg(X_train_cleaned,y_train_cleaned) # RMSE: -19.272 (11.371), alpha = 100 -> RMSE: -17.142 (2.080)
#ridge_rg(X_train, y_train) 
#ridge_rg(X_imputed, y_delete)
#ridge_rg(X_delete_cleaned, y_delete_cleaned)
#ridge_rg(X_delete_robust, y_delete)
#ridge_rg(X_imp_knn, y_delete)
#ridge_rg(X_reduced, y_delete)
ridge_rg(X_imp_median, y_train)


# In[ ]:


#submission
ridge_rg = Ridge(alpha=1, solver="auto",random_state=SEED)

ridge_rg.fit(X_train_cleaned, y_train_cleaned) # 81
#ridge_rg.fit(X_train, y_train) # 77
#ridge_rg.fit(X_delete, y_delete) # 81
y_pred = ridge_rg.predict(X_test)

#ridge_rg.fit(X_delete_cleaned, y_delete_cleaned) # 81
#ridge_rg.fit(X_reduced, y_delete)x # 81
#y_pred = ridge_rg.predict(X_test_reduced)

#y_pred = ridge_rg.predict(X_test_imputed)

from sklearn.metrics import mean_squared_error
mean_squared_error(y_pred, y_test, squared=False)


# In[ ]:


#y_pred[y_pred<0] = 0
y_pred[(y_pred<100)] = 0

from sklearn.metrics import mean_squared_error
mean_squared_error(y_pred, y_test, squared=False)
#X_train_cleaned.describe()


# In[ ]:


y_pred[y_pred<100]


# In[ ]:


# Make predictions in test set and prepare submission file
predictions = ridge_rg.predict(test[main_cols])
sub_file = ss.copy()
sub_file.close = predictions
sub_file.to_csv('Baseline.csv', index = False)


# In[ ]:


sub_file.head()


# In[ ]:


files.download('Baseline.csv') 


# ### formal

# In[ ]:


#submission
ridge_rg = Ridge(alpha=10, solver="auto")


#ridge_rg = make_pipeline(StandardScaler(), Ridge(alpha=10.0)) # 77
#ridge_rg.fit(X_train_cleaned, y_train_cleaned)
#ridge_rg.fit(X_train, y_train) # 77.54780979871404
#ridge_rg.fit(X_imputed, y_train)
#ridge_rg.fit(X_delete, y_delete) # 77.58237723128258
#ridge_rg.fit(X_delete_cleaned, y_delete_cleaned) # 83.99180726695666
#ridge_rg.fit(X_delete_imputed, y_delete) # 83.99180726695666
# ridge_rg.fit(X_delete, y_delete) 

# y_pred = ridge_rg.predict(X_test)


# ridge_rg.fit(X_delete_robust, y_delete) 
# y_pred = ridge_rg.predict(X_test_robust) 222


ridge_rg.fit(X_delete_robust, y_delete) 
y_pred = ridge_rg.predict(X_test_robust) 222


from sklearn.metrics import mean_squared_error
mean_squared_error(y_pred, y_test, squared=False)


# ## used on X_train instead of X_delete as above

# In[ ]:


# used on X_train instead of X_delete as above

from sklearn.ensemble import IsolationForest
from sklearn.metrics import make_scorer, f1_score
from sklearn import model_selection
from sklearn.datasets import make_classification

iso = IsolationForest(random_state=SEED, contamination=0.05)
y_pred = iso.fit_predict(X_train)
X_train_cleaned = X_train[np.where(y_pred == 1, True, False)]
y_train_cleaned = y_train[np.where(y_pred == 1, True, False)]

# summarize the shape of the updated training dataset
print(X_train_cleaned.shape, y_train_cleaned.shape)
cleaned,_ = X_train_cleaned.shape

total, _ = X_train.shape
print("number of outlier row removed: ", total - cleaned)
print("percentage of outliers removed: ", (total-cleaned) / total)


# ### param tuning

# In[ ]:


ridge_rg = Ridge()
# define grid
grid = dict()
grid['alpha'] = np.arange(0, 4, 0.05)
# define search
search = GridSearchCV(ridge_rg, grid, scoring='neg_root_mean_squared_error', cv=cv, n_jobs=-1)
# perform the search
results = search.fit(X_train, y_train)
# summarize
print('RMSE: %.3f' % results.best_score_)
print('Config: %s' % results.best_params_)


# In[ ]:


results


# In[ ]:


scores = [x[1] for x in clf.grid_scores_]
scores = np.array(scores).reshape(len(Cs), len(Gammas))

for ind, i in enumerate(Cs):
    plt.plot(Gammas, scores[ind], label='C: ' + str(i))
plt.legend()
plt.xlabel('Gamma')
plt.ylabel('Mean score')
plt.show()


# ##Lasso reg

# In[ ]:


from sklearn import linear_model
lasso_rg = linear_model.Lasso(alpha=0.1)
cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=SEED)
n_scores = cross_val_score(lasso_rg, X_train, y_train, scoring='neg_root_mean_squared_error', cv=cv, n_jobs=-1, error_score='raise')
print('MAE: %.3f (%.3f)' % (mean(n_scores), std(n_scores)))


# ##Elasticnet

# In[ ]:


from sklearn.linear_model import ElasticNet
elastic = ElasticNet()
cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=SEED)
n_scores = cross_val_score(elastic, X_train_cleaned, y_train_cleaned, scoring='neg_root_mean_squared_error', cv=cv, n_jobs=-1, error_score='raise')
print('MAE: %.3f (%.3f)' % (mean(n_scores), std(n_scores)))


# In[ ]:


#submission
elastic = ElasticNet()
#ridge_rg = make_pipeline(StandardScaler(), Ridge(alpha=0.8))
elastic.fit(X_train_cleaned, y_train_cleaned)
#elastic.fit(X_train, y_train)

y_pred = elastic.predict(X_test)

from sklearn.metrics import mean_squared_error
mean_squared_error(y_pred, y_test, squared=False)


# ##RGF regression

# In[ ]:


get_ipython().system('pip install rgf_python')


# In[ ]:



from rgf.sklearn import RGFRegressor
rgf_rg = RGFRegressor(max_leaf=300, algorithm="RGF_Sib", test_interval=100, loss="LS")

cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=SEED)
n_scores = cross_val_score(rgf_rg, X_train, y_train, scoring='neg_root_mean_squared_error', cv=cv, n_jobs=-1, error_score='raise')
print('MAE: %.3f (%.3f)' % (mean(n_scores), std(n_scores))) # MAE: -473.728 (29.295)


# ## linear regression

# In[ ]:


# Instantiate model
lm2 = LinearRegression()
# Fit Model
lm2.fit(X_train, y_train)
# Predict
y_pred = lm2.predict(X_test)
from sklearn.metrics import mean_squared_error
mean_squared_error(y_pred, y_test, squared=False)


# ## autosklearn

# In[ ]:


#!pip install auto-sklearn


# In[ ]:


import autosklearn.regression
from autosklearn.metrics import root_mean_squared_error 
n_mins = 90
automl = autosklearn.regression.AutoSklearnRegressor(
    time_left_for_this_task=n_mins*60,
    #include_preprocessors=["no_preprocessing"], exclude_preprocessors=None,
    exclude_estimators=["sgd", "gaussian_process", "ard_regression", "liblinear_svr"], #,
    per_run_time_limit=30,
    ensemble_size=6,
    metric=root_mean_squared_error 
#    n_jobs=4
)
automl.fit(X_delete, y_delete)
print(automl.leaderboard())
print(automl.show_models())

train_predictions = automl.predict(X_test)
#submission

from sklearn.metrics import mean_squared_error
mean_squared_error(train_predictions, y_test, squared=False)


# In[ ]:


automl.leaderboard(detailed=True, ensemble_only=False)#.loc[228] # , top_k=8


# In[ ]:


automl.get_models_with_weights()


# In[ ]:


automl.cv_results_.keys()


# In[ ]:


#np.argmax(automl.cv_results_['mean_test_score'])
automl.cv_results_['mean_test_score'].argsort()[:10]#[::-1]


# In[ ]:


automl.cv_results_['mean_test_score'][288]


# In[ ]:


automl.cv_results_['params'][288]


# ### save result

# In[ ]:


import pickle
# x = automl.show_models()
# results = autml # the classifier/regressor itself
# pickle.dump(results, open('file.pickle','wb'))
x = automl
results = automl # the classifier/regressor itself
pickle.dump(results, open('file.pickle','wb'))


# ##old

# In[ ]:


import autosklearn.regression
from autosklearn.metrics import mean_squared_error

automl = autosklearn.regression.AutoSklearnRegressor(
    time_left_for_this_task=30*60,
    per_run_time_limit=30,
    metric=mean_squared_error
)
automl.fit(X_delete, y_delete)
print(automl.leaderboard())
train_predictions = automl.predict(X_test)
#submission

from sklearn.metrics import mean_squared_error
mean_squared_error(train_predictions, y_test, squared=False)


# In[ ]:


print(automl.leaderboard())


# In[ ]:


train_predictions = automl.predict(X_test)
#submission

from sklearn.metrics import mean_squared_error
mean_squared_error(train_predictions, y_test, squared=False)


# In[ ]:


print(automl.show_models())

