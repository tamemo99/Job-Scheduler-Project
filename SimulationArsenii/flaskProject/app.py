from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
import pandas as pd

app = Flask(__name__)
api = Api(app)

'''
Time between 20031 and 30030 in minutes 
theres 880 containers 
440 machines
'''


max_capacity = 880
trace_start = 20031
trace_end = 30030
jobs_been_submitted = False
# initialize the start and end time of the simulation
sim_time = pd.read_csv('simtime.csv')
# initialize the dataframe and .csv file with submitted jobs
h = {'job_id': [],
     'containers': [],
     'runtime': [],
     'start_time': [],
     'end_time': [],
     'status': []
     }
jobs_triggered = pd.DataFrame(h, dtype=int)
jobs_triggered.to_csv("triggeredjobs.csv", index=False)
# initialize the cluster trace dataframe
sim_trace = pd.read_csv('trace.csv')
# initialize the dataframe with jobs data
jobs_trace = pd.read_csv('PredictedRuntimes.csv')


class SimTime(Resource):
    # set simulation time interval
    def put(self, stime, etime=30030):
        global sim_trace, sim_time, jobs_triggered
        # job_id,containers,actual_runtime,predicted_runtime
        # check if provided time is valid
        if stime in range(trace_start, trace_end+1) and etime in range(trace_start, trace_end+1) and stime < etime:

            # save the times in the dataframe
            sim_time.loc[0, 'start_time'] = stime
            sim_time.loc[0, 'end_time'] = etime

            # trim the trace to only include the provided time interval
            sim_trace = sim_trace[stime <= sim_trace['time']]
            sim_trace = sim_trace[sim_trace['time'] <= etime]

            # update the .csv files
            sim_trace.to_csv("simtrace.csv", index=False)
            sim_time.to_csv("simtime.csv", index=False)
            h = {'job_id': [],
                 'containers': [],
                 'runtime': [],
                 'start_time': [],
                 'end_time': [],
                 'status': []
                 }
            jobs_triggered = pd.DataFrame(h, dtype=int)
            jobs_triggered.to_csv("triggeredjobs.csv", index=False)

            return jsonify({'start_time': stime, 'end_time': etime})
        else:
            return jsonify({'start_time': stime, 'end_time': etime, 'message': 'invalid time interval'})


class JobEvaluator(Resource):
    def __init__(self):
        self.sim_trace = sim_trace.copy()

    # Get new job triggered starting from start_time with containers
    def put(self, job_id, start_time, containers):

        global jobs_trace, jobs_triggered, sim_trace, jobs_been_submitted
        jobs_been_submitted = True
        # find job in csv file based on id
        if (jobs_trace['job_id'] == job_id).any():

            # check if the job is already running
            if not ((jobs_triggered['job_id'] == job_id) & (jobs_triggered['status'] == 1)).any():

                # extract the row with the provided job from the dataframe with jobs data
                found_job = jobs_trace.loc[jobs_trace['job_id'] == job_id]

                # set values for job start time and end time
                job_start = start_time

                # calculate load when considering containers
                runtime = found_job.iloc[0]['actual_runtime'] * int(found_job.iloc[0]['containers'] / containers)
                job_runtime = runtime if runtime > 0 else 1
                job_end = job_runtime + job_start

                found_job.iloc[0]['actual_runtime'] = job_runtime
                found_job = found_job.rename(columns={'actual_runtime': 'runtime'})

                job_load = containers
                found_job.iloc[0]['containers'] = job_load

                found_job.insert(len(found_job.columns), "start_time", [job_start])
                found_job.insert(len(found_job.columns), "end_time", [job_end])

                # set jobs status to 1 (running)
                found_job.insert(len(found_job.columns), "status", [1])
                found_job.drop('predicted_runtime', axis=1, inplace=True)

                # create a dataframe with trace of 1 jobs load for the simulation period
                job = self.sim_trace['time'].transform(lambda x: job_load if job_start <= x < job_end else 0)
                job = job.rename(f"{job_id}@{start_time}", inplace=True)

                # append the column to the simulation dataframe and update the .csv file
                self.sim_trace = pd.concat([self.sim_trace, job], axis=1)
                sim_trace = self.sim_trace.copy()
                sim_trace.to_csv("simtrace.csv", index=False)

                # create entry in the triggered jobs dataframe with status running
                jobs_triggered = pd.concat([jobs_triggered, found_job], ignore_index=True)
                jobs_triggered.to_csv("triggeredjobs.csv", index=False)

                return jsonify({'job_id': job_id, 'message': 'job found and triggered'})
            else:
                return jsonify({'job_id': job_id, 'message': 'job is already running'})
        else:
            return jsonify({'job_id': job_id, 'message': 'job_id doesnt exist in the simulation trace'})


def drop_excessive_jobs():
    global sim_trace, jobs_triggered
    dropped_jobs = {}
    for ind in sim_trace.index:
        row = sim_trace.iloc[ind]
        if row.drop("time").sum() >= max_capacity:
            # drop jobs starting with ones with the biggest load
            while row.drop("time").sum() >= max_capacity and (jobs_triggered['status'] == 1).any():
                job_id = row.drop(["containers", "time"]).idxmax()

                # set jobs load to zero after drop
                sim_trace.loc[ind:, '%s' % job_id] = 0
                row.drop('%s' % job_id, inplace=True)

                # set the job status to 0(dropped) in the triggered jobs dataframe
                # set end_time
                job_dropped_at_time = row.squeeze()['time']
                jobs_triggered.loc[jobs_triggered['job_id'] == int(job_id), ['end_time']] = job_dropped_at_time
                jobs_triggered.loc[jobs_triggered['job_id'] == int(job_id), ['status']] = 0

                dropped_jobs[int(job_id)] = int(job_dropped_at_time)

    # update corresponding .csv files
    jobs_triggered.to_csv("triggeredjobs.csv", index=False)
    sim_trace.to_csv("simtrace.csv", index=False)
    return dropped_jobs


def drop_excessive_jobs_per_call(time):
    global sim_trace, jobs_triggered
    ind = sim_trace.index[sim_trace['time'] == time].tolist()[0]
    row = sim_trace.iloc[ind]
    if row.drop("time").sum() >= max_capacity:
        # drop jobs starting with ones with the biggest load
        while row.drop("time").sum() >= max_capacity and (jobs_triggered['status'] == 1).any():
            job_id = row.drop(["containers", "time"]).idxmax()

            # set jobs load to zero after drop
            sim_trace.loc[ind:, str(job_id)] = 0
            # sim_trace.drop(str(job_id), axis=1, inplace=True)
            row.drop(str(job_id), inplace=True)

            # set the job status to 0(dropped) in the triggered jobs dataframe
            # set end_time
            job_dropped_at_time = row.squeeze()['time']
            job_id = job_id.split('@')[0]

            a = (jobs_triggered['end_time'] > time) & (jobs_triggered['start_time'] <= time)
            b = (jobs_triggered['job_id'] == int(job_id)) & a
            jobs_triggered.loc[b, ['status']] = 0
            jobs_triggered.loc[b, ['end_time']] = job_dropped_at_time

    # update corresponding .csv files
    jobs_triggered.to_csv("triggeredjobs.csv", index=False)
    sim_trace.to_csv("simtrace.csv", index=False)
    pass


class ClusterLoad(Resource):

    # get simulated cluster load at time
    def get(self, time):
        # drop excessive jobs
        # dropped_jobs = {}
        global jobs_been_submitted, jobs_triggered
        if jobs_been_submitted:
            drop_excessive_jobs_per_call(time)
            jobs_been_submitted = False

        if (jobs_triggered['end_time'] == time).any():
            # dropped_jobs = jobs_triggered[(jobs_triggered['status'] == 0) & (jobs_triggered['end_time'] == time)]
            # dropped_jobs = dict(zip(dropped_jobs.job_id, dropped_jobs.end_time))
            jobs_triggered.loc[(jobs_triggered['status'] == 1) & (jobs_triggered['end_time'] == time), ['status']] = 2
            jobs_triggered.to_csv("triggeredjobs.csv", index=False)

        # sum over cluster load and all jobs load that are running at time
        load = sim_trace.loc[sim_trace['time'] == time].drop(['time'], axis=1).squeeze().sum()
        load_jobs = sim_trace.loc[sim_trace['time'] == time].drop(['time', 'containers'], axis=1).squeeze().sum()
        return jsonify({'load': int(load), 'load in percent': int((load/max_capacity)*100),
                        'total load of jobs': int(load_jobs)})


api.add_resource(ClusterLoad, '/cluster_load/time=<int:time>')
api.add_resource(JobEvaluator, '/eval/job_id=<int:job_id>/start_time=<int:start_time>/containers=<int:containers>')
api.add_resource(SimTime, '/start_time=<int:stime>')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5005, debug=True)
