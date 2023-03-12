import pandas as pd
import math
import numpy as np
from sklearn import linear_model
from sklearn.model_selection import train_test_split
import statsmodels.api as sm

pd.set_option("display.max_columns", None)

df = pd.read_csv('jobdata.csv')

x = df[['container0', 'container1', 'container2']]
y = df['runtime']

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.4, random_state = 100)
model = sm.OLS.from_formula("runtime ~ container0 + container1 + container2", data = df)
result = model.fit()
#print(result.summary()) /print summary result of the algorithm
regr = linear_model.LinearRegression()
regr.fit(x_train, y_train)
y_pred_regr = regr.predict(x_test)

regr_diff = pd.DataFrame({'Actual value': y_test, 'predicted value': y_pred_regr})