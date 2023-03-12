## Set up
1. Install all dependencies in app.py


2. Run app.py


3. Simulation api will run on localhost


4. Carefully read documentation of enpoints

## Endpoints of the simulation api:

1. put request to `/start_time=<int:stime>/end_time=<int:etime>`

+ sets the start time for the simulation and resets files
+ Returns {'start_time': ___, 'end_time': ___}

2. put request to `/eval/job_id=<int:job_id>/start_time=<int:start_time>`

+ finds a record with real data for the job in simulatedjobs file, creates an entry in triggeredjobs file, sets the jobs status to 1(running or completed). Creates a column in the simtrace file corresponding to jobs load on the cluster for the specified time interval. simtrace is a table indexed by time in minutes: time(minutes), clusterload(containers), job0(containers), job1(containers), job2(containers)..
+ Returns {'job_id': ___, 'message': ___}

3. get request to `/cluster_load/time=<int:time>`

+ calculates cumulative loat at the time. Drops jobs starting with the job with most containers until the load is below maxcapacity. Returns a dict with jobs dropped (if any) at the specified time.
+ Returns {'load': ___, 'load in percent': ___, 'dropped jobs': ___}

max_capacity = 880 \
trace_start = 20031 \
trace_end = 30030

4. PredictedRuntimes.csv contains only the jobs that run for more than 1 minute, times are converted to minutes and rounded