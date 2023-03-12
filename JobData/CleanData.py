
import pandas as pd
import numpy as np

pd.set_option("display.max_columns", None)

df = pd.read_csv('mustang_release_v0.2.0.csv', index_col=False)
df.reset_index(drop=True, inplace=True)
df = df.loc[df["node_count"] != 0]
df = df.loc[df["job_status"] != "CANCELLED"]
df = df.loc[df["job_status"] != "TIMEOUT"]

df.shape

df['end_time'] = pd.to_datetime(df['end_time'])
df['start_time'] = pd.to_datetime(df['start_time'])
df['runtime'] = df['end_time'] - df['start_time']
df['runtime'] = df['runtime'].map(lambda x: x.total_seconds())

data = df['user_ID'], df['group_ID'], df['runtime'], round(1/(df['node_count']), 5), round(np.log(df['node_count']), 5), df['node_count']
headers = ["user_ID", "group_ID", "runtime", "container0", "container1", "container2"]
df2 = pd.concat(data, axis=1, keys=headers)
df2["runtime"] = pd.to_numeric(df2["runtime"], downcast="float")
df2["container2"] = pd.to_numeric(df2["container2"], downcast="float")
df2 = df2.dropna(how='any', axis=0)
df2.to_csv(r'C:\Users\IBM 5100\Desktop\df\jobdata.csv')


