import pandas as pd
import numpy as np


#test = pd.DataFrame(1, index=np.arange(1, 10000), columns=np.arange(880))
# number_of_containers = 1
'''
df1 = pd.read_csv('Predict.csv')
# df2 = pd.read_csv('Predicted Values.csv')
df2 = df1[df1['actual_runtime'] >= 60]
print(df2)
df2['actual_runtime'] = df2['actual_runtime'].transform(lambda x: int(x/60))
df2['predicted_runtime'] = df2['predicted_runtime'].transform(lambda x: int(x/60))
df2['containers'] = df2['containers'].transform(lambda x: int(x))
print(df2)
print(df1.nunique())
print(df2.nunique())
df2.to_csv("PredictedRuntimes.csv", index=False)
# print(df2)

# df3 = df2.join(df1[['container2', 'runtime']])
# print(df3)


def average_runtime(number_of_containers, dataframe):
    dataframe = dataframe[dataframe['container2'] == number_of_containers]
    return dataframe[['runtime']].mean().squeeze()


time = 25000
row = sim_trace.loc[sim_trace['time'] == time]
ind = sim_trace.index[sim_trace['time'] == time].tolist()[0]
print(ind)

print(average_runtime(number_of_containers, dataframe))

sim_trace = pd.read_csv('trace.csv')
sim_time = pd.read_csv('simtime.csv')

stime = 20031
etime = 25000

sim_time.loc[0, 'start_time'] = stime
sim_time.loc[0, 'end_time'] = etime

# trim the trace to only include the provided time interval
sim_trace = sim_trace[stime <= sim_trace['time']]
sim_trace = sim_trace[sim_trace['time'] <= etime]

# update the .csv files
sim_trace.to_csv("simtrace.csv", index=False)
sim_time.to_csv("simtime.csv", index=False)
'''

df = pd.read_csv('trace.csv')
print(df)



#test.to_csv("testtrace.csv", index=False)



