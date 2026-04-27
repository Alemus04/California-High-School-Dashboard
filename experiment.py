from numpy import int64
from grad_data_creation import combined_df
import pandas as pd
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import numpy as np
import matplotlib.pyplot as plt


df = combined_df.dropna(subset=['SchoolName', 'DistrictName'])

#Converting to float
df["Regular HS Diploma Graduates (Count)"] = (df["Regular HS Diploma Graduates (Count)"].str.extract('(\d+)').astype(float))
df = df.dropna()
#print(df[['Regular HS Diploma Graduates (Count)']].head(5))

df["Dropout (Count)"] = (df["Dropout (Count)"].str.extract('(\d+)').astype(float))


df["CPP Completer (Rate)"] = (df["CPP Completer (Rate)"].str.extract('(\d+\.\d+)').astype(float))


df["CohortStudents"] = (df["CohortStudents"].str.extract('(\d+)').astype(float))
# Impute missing values with school-year mean, then round and cast
#print(type(df['Regular HS Diploma Graduates (Count)'].iloc[0]))
""""
 df['Regular HS Diploma Graduates (Count)'] = ( 
    df['Regular HS Diploma Graduates (Count)']
    .fillna(df.groupby(['SchoolName', 'AcademicYear'])['Regular HS Diploma Graduates (Count)'].transform('mean'))
    .round()
    .astype(int64)
) """

print('This worked')
"""
df['Regular HS Diploma Graduates (Rate)'] = (
    df['Regular HS Diploma Graduates (Rate)']
    .astype(str)
    .str.extract('(\d+\.\d+)')  # Extract first float only
    .astype(float)
)
df['Regular HS Diploma Graduates (Rate)'] = (
    df['Regular HS Diploma Graduates (Rate)']
    .fillna(df.groupby(['SchoolName', 'AcademicYear'])['Regular HS Diploma Graduates (Rate)'].transform('mean'))
    .round(2)
)
"""

## -- MODEL CREATION -- ##

features = ['Dropout (Count)'
            , 'Dropout (Rate)'
            , 'Regular HS Diploma Graduates (Rate)'
            ,'CPP Completer (Rate)'
            ]

label = ['Regular HS Diploma Graduates (Count)']

df[features] = df[features].apply(pd.to_numeric, errors = 'coerce')

for feature in features:
    # 1st: fill with school-level median
    df[feature] = df[feature].fillna(
        df.groupby('SchoolName')[feature].transform('median')
    )
    # 2nd: fill remaining with district-level median
    df[feature] = df[feature].fillna(
        df.groupby('DistrictName')[feature].transform('median')
    )
    # 3rd: fill anything still missing with global median
    df[feature] = df[feature].fillna(df[feature].median())
 
X = df[features].values
Y = df[label].values


X_train, X_test, Y_train, Y_test = train_test_split(X, Y, train_size = 0.7, shuffle= True)

X_train = torch.tensor(X_train, dtype=torch.float32)
Y_train = torch.tensor(Y_train, dtype=torch.float32)
X_test = torch.tensor(X_test, dtype=torch.float32)
Y_test = torch.tensor(Y_test, dtype=torch.float32)

model = nn.Linear(in_features=4, out_features=1)

loss_function = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr =0.01)

for epoch in range(500):
    preds = model(X_train)
    loss = loss_function(preds,Y_train)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if epoch % 50 == 0:
        print(epoch, loss.item())
 
model.eval()

with torch.no_grad():
    train_preds = model(X_train)
    test_preds = model(X_test)
    test_loss = loss_function(test_preds, Y_test)
    print(f"Test Loss: {test_loss.item()}")

"""
plt.scatter(X_train[:, 0].numpy(), Y_train.numpy(), color='blue', label='Training Data')
plt.plot(X_train[:, 0].numpy(), train_preds.numpy(), color='red', label='Fitted Line')
plt.legend()
plt.show()
"""

# Convert to numpy for sklearn metrics
test_preds_np = test_preds.numpy()
Y_test_np = Y_test.numpy()
train_preds_np = train_preds.numpy()
Y_train_np = Y_train.numpy()


# Metrics
train_mae = mean_absolute_error(Y_train_np, train_preds_np)
test_mae = mean_absolute_error(Y_test_np, test_preds_np)
train_r2 = r2_score(Y_train_np, train_preds_np)
test_r2 = r2_score(Y_test_np, test_preds_np)

print(f"Train MAE: {train_mae:.2f}")
print(f"Test  MAE: {test_mae:.2f}")
print(f"Train R²:  {train_r2:.4f}")
print(f"Test  R²:  {test_r2:.4f}")