import requests
import pandas as pd


def get_free_containers(current_cluster_load):
    return max_capacity - current_cluster_load


def trigger_execute_job(job_id, containers, start_index):
    urle = 'http://127.0.0.1:5005/eval/job_id=' + str(job_id) + '/start_time=' + str(start_index) + '/containers=' \
          + str(containers)
    return requests.put(urle).json()


def average_runtime(number_of_containers):
    dataframe = pd.read_csv('in/Fulldataset.csv')
    dataframe = dataframe[dataframe['container2'] == number_of_containers]
    return dataframe[['runtime']].mean().squeeze()


def job_check_up(timestamp):
    triggered_jobs = pd.read_csv('/Simulation/flaskProject'
                                 '/triggeredjobs.csv')
    for index, row in triggered_jobs.iterrows():
        job_id = int(row["job_id"].squeeze())
        urlw = 'http://127.0.0.1:5000/HistroricalData/get/' + str(job_id)
        trigger_info = requests.get(urlw).json()
        old_runtime = trigger_info["runtime"]
        if int(row['status'].squeeze()) == 0 and trigger_info["job_status"] == "running":
            urla = 'http://127.0.0.1:5000/HistoricalData/getall'
            triggered_job_list = requests.get(urla).json()
            execution_times = 1
            for trigger_runs in triggered_job_list:
                if trigger_runs["HistoricalData"] == job_id:
                    execution_times += 1
            new_runtime = old_runtime * (1 + (1 / execution_times))
            new_runtime = round(new_runtime)
            urlx = 'http://127.0.0.1:5000/HistoricalData/Update/' + str(job_id) + '/edit?runtime=' + str(new_runtime) \
                   + '&job_status=dropped' + '&date=' + str(trigger_info["date"]) + '&containers=' \
                   + str(trigger_info["containers"])
            requests.get(urlx)
        else:
            if int(row['status'].squeeze()) == 2 and trigger_info["job_status"] == "running":
                new_runtime = timestamp - trigger_info["date"]
                urly = 'http://127.0.0.1:5000/HistoricalData/Update/' + str(job_id) + '/edit?runtime=' \
                       + str(new_runtime) + '&job_status=finished' + '&date=' + str(trigger_info["date"]) \
                       + '&containers=' + str(trigger_info["containers"])
                requests.get(urly)
    pass


def job_historic_datapoint(job_id, timestamp, containers, runtime, status):
    urls = "http://127.0.0.1:5000/HistoricalData/add?id=" + str(job_id) + "&date=" + str(timestamp) + \
          "&containers=" + str(containers) + "&runtime=" + str(runtime) + "&job_status=" + str(status)
    requests.get(urls)
    pass


def cluster_historic_datapoint(timestamp, load, job_load, percentage):
    urld = "http://127.0.0.1:5000/HistoricCluster/add?data_index=" + str(timestamp) + "&percentage_load=" \
          + str(percentage) + "&full_load=" + str(load) + "&job_load=" + str(job_load)
    requests.get(urld)
    pass


def get_job_containers(run):
    job_containers = 0
    triggered_jobs = pd.read_csv('/Simulation/flaskProject'
                                 '/triggeredjobs.csv')
    for index, row in triggered_jobs.iterrows():
        job_status = int(row["status"].squeeze())
        if job_status == 1:
            job_containers = job_containers + int(row["containers"].squeeze())
    return job_containers


def idle_load(index):
    average_cluster_load = 0
    for run in range(index, max_index):
        # get current cluster load
        url = 'http://127.0.0.1:5005/cluster_load/time=' + str(run)
        current_cluster_load = requests.get(url).json()

        average_cluster_load = average_cluster_load + current_cluster_load["load"]

    # divide by time
    average_cluster_load = average_cluster_load / (max_index - min_index)
    percentage = average_cluster_load / max_capacity
    print("Idle average cluster load: " + str(percentage))
    pass


def greedy_basic(index):
    global wait_time, max_index, sim, phase, mode, max_capacity
    while True:
        for run in range(index, max_index):
            print("Index: " + str(run))

            # get current cluster load
            url = 'http://127.0.0.1:5005/cluster_load/time=' + str(run)
            current_cluster_load = requests.get(url).json()

            url = 'http://127.0.0.1:5000/Queue/getall'
            queue = requests.get(url).json()
            if queue:
                trigger_check = False
                for current_job in queue:
                    if trigger_check:
                        # skip rest of queue
                        break
                    else:
                        # get id for current job
                        job_id = current_job["idQueue"]
                        pload = {'JobId': job_id}

                        # get job estimation from csv
                        job_estimation = pd.read_csv('in/PredictedRuntimes.csv')

                        # extract lowest required number of containers
                        df = job_estimation[job_estimation["job_id"] == job_id]
                        container_min = int(df["containers"].squeeze())

                        # run trigger - if True at end of loop, we execute
                        run_trigger = True

                        # get current capacity
                        free_containers = get_free_containers(current_cluster_load["load"])

                        # save current cluster load as historic data
                        cluster_historic_datapoint(run, current_cluster_load["load"],
                                                   current_cluster_load["total load of jobs"],
                                                   current_cluster_load["load in percent"])

                        # check if job can fit with container requirement
                        if free_containers < container_min:
                            run_trigger = False

                        # check if we execute
                        if run_trigger:
                            trigger_check = not trigger_check
                            sim_response = trigger_execute_job(job_id, container_min, run)
                            print('Job ID: ' + str(sim_response["job_id"]) + ' | Message: '
                                  + str(sim_response["message"]))

                            wait_time = wait_time + (run - int(current_job["timeOfEntry"]))

                            # delete job from queue
                            urli = 'http://127.0.0.1:5000/Queue/delete/' + str(job_id)
                            update_queue = requests.get(urli)
                            print('Queue response: ' + update_queue.text)

                            # Update historical job table without estimation
                            job_historic_datapoint(job_id, run, container_min, 0, 'running')

            # check if any jobs failed/completed and need runtime adjusted
            job_check_up(run)

        # calculate all tracking values - average cluster load first
        avg_cluster_load = 0
        urlj = "http://127.0.0.1:5000/HistoricCluster/getAll"
        acc_cluster_load = requests.get(urlj).json()
        if acc_cluster_load:
            for entries in acc_cluster_load:
                avg_cluster_load = avg_cluster_load + int(entries["full_load"])
        avg_cluster_load = avg_cluster_load / (max_index - min_index)

        # average wait-time of jobs + num of triggered jobs
        triggered_jobs = pd.read_csv('/Simulation/flaskProject'
                                     '/triggeredjobs.csv')
        num_triggered_jobs = triggered_jobs.shape[0] + 1
        avg_wait_time = wait_time / num_triggered_jobs

        # number of dropped jobs
        num_dropped_jobs = triggered_jobs[triggered_jobs["status"] == 0].squeeze().count()

        # Final Output
        print("Simulation complete! Jobs triggered: " + str(num_triggered_jobs) + " | Jobs dropped: "
              + str(num_dropped_jobs) + " | Average cluster load: " + str(avg_cluster_load) + " | Average wait time: "
              + str(avg_wait_time))

        # check if simulation has been interrupted
        if not sim:
            break
        else:
            break
    pass


def greedy_improved(index):
    global wait_time, max_index, sim, phase, mode, max_capacity
    while True:
        for run in range(index, max_index):
            print("Index: " + str(run))

            # get current cluster load
            url = 'http://127.0.0.1:5005/cluster_load/time=' + str(run)
            current_cluster_load = requests.get(url).json()

            url = 'http://127.0.0.1:5000/Queue/getall'
            queue = requests.get(url).json()
            if queue:
                trigger_check = False
                for current_job in queue:
                    if trigger_check:
                        # skip rest of queue
                        break
                    else:
                        # get id for current job
                        job_id = current_job["idQueue"]
                        pload = {'JobId': job_id}

                        # get job estimation from csv
                        job_estimation = pd.read_csv('in/PredictedRuntimes.csv')

                        # extract lowest required number of containers
                        df = job_estimation[job_estimation["job_id"] == job_id]
                        container_min = int(df["containers"].squeeze())

                        # get runtime estimation by phase of job estimator
                        if phase == 1:
                            # get latest binary search estimate
                            url = 'http://127.0.0.1:5000/HistoricalData/getall'
                            historical_job_data = requests.get(url).json()

                            # find previous execution of the job
                            exists = False
                            status_runtime = 0
                            for entries in historical_job_data:
                                if entries["HistoricalData"] == job_id:
                                    exists = True
                                    status_runtime = entries["runtime"]

                            if exists:
                                run_est = status_runtime
                            else:
                                run_est = round(average_runtime(container_min))
                        else:
                            # extract predicted runtime for job in index steps
                            df = job_estimation[job_estimation["job_id"] == job_id]
                            run_est = int(df["predicted_runtime"].squeeze())

                        # run trigger - if True at end of loop, we execute
                        run_trigger = True

                        # get future cluster load estimation from csv
                        future_cluster_load_data = pd.read_csv('in/clusterLoad.csv')

                        free_containers = get_free_containers(current_cluster_load["load"])

                        # save current cluster load as historic data
                        cluster_historic_datapoint(run, current_cluster_load["load"],
                                                   current_cluster_load["total load of jobs"],
                                                   current_cluster_load["load in percent"])

                        # check if num of available containers decreases during runtime
                        if free_containers > container_min:

                            # check if its possible to run with simulation time left
                            min_runtime = run + run_est
                            if min_runtime > max_index:
                                break
                            else:
                                for i in range(run_est):
                                    load_index = run + i
                                    df = future_cluster_load_data[future_cluster_load_data["time"] == load_index]
                                    load = int(df["containers"].squeeze())
                                    job_containers = get_job_containers(run)
                                    future_load = get_free_containers(load + job_containers)
                                    if future_load < container_min:
                                        run_trigger = False

                        # check if we execute
                        if run_trigger:
                            trigger_check = not trigger_check
                            sim_response = trigger_execute_job(job_id, container_min, run)
                            print('Job ID: ' + str(sim_response["job_id"]) + ' | Message: '
                                  + str(sim_response["message"]))

                            wait_time = wait_time + (run - int(current_job["timeOfEntry"]))

                            # delete job from queue
                            url = 'http://127.0.0.1:5000/Queue/delete/' + str(job_id)
                            update_queue = requests.get(url)
                            print('Queue response: ' + update_queue.text)

                            # Update historical job table
                            job_historic_datapoint(job_id, run, container_min, run_est, 'running')

            # check if any jobs failed/completed and need runtime adjusted
            job_check_up(run)

        # calculate all tracking values - average cluster load first
        avg_cluster_load = 0
        url = "http://127.0.0.1:5000/HistoricCluster/getAll"
        acc_cluster_load = requests.get(url).json()
        if acc_cluster_load:
            for entries in acc_cluster_load:
                avg_cluster_load = avg_cluster_load + int(entries["full_load"])
        avg_cluster_load = avg_cluster_load / (max_index - min_index)

        # average wait-time of jobs + num of triggered jobs
        triggered_jobs = pd.read_csv('/Simulation/flaskProject'
                                     '/triggeredjobs.csv')
        num_triggered_jobs = triggered_jobs.shape[0] + 1
        avg_wait_time = wait_time / num_triggered_jobs

        # number of dropped jobs
        num_dropped_jobs = triggered_jobs[triggered_jobs["status"] == 0].squeeze().count()

        # Final Output
        print("Simulation complete! Jobs triggered: " + str(num_triggered_jobs) + " | Jobs dropped: "
              + str(num_dropped_jobs) + " | Average cluster load: " + str(avg_cluster_load) + " | Average wait time: "
              + str(avg_wait_time))

        # check if simulation has been interrupted
        if not sim:
            break
        else:
            break
    pass


def shortest_first(index):
    global wait_time, max_index, sim, phase, mode, max_capacity
    while True:
        for run in range(index, max_index):
            print("Index: " + str(run))

            # get current cluster load
            url = 'http://127.0.0.1:5005/cluster_load/time=' + str(run)
            current_cluster_load = requests.get(url).json()

            url = 'http://127.0.0.1:5000/Queue/getall'
            queue = requests.get(url).json()
            if queue:
                trigger_check = False
                job_id = ''

                # get job estimation from csv
                job_estimation = pd.read_csv('in/PredictedRuntimes.csv')

                # vars to find shortest job
                shortest_runtime = 0
                shortest_job_id = ''

                container_min = 0
                chosen_job = queue[0]

                for current_job in queue:
                    if trigger_check:
                        # skip rest of queue
                        break
                    else:
                        # get id for current job
                        job_id = current_job["idQueue"]
                        pload = {'JobId': job_id}

                        # extract lowest required number of containers
                        df = job_estimation[job_estimation["job_id"] == job_id]
                        container_min = int(df["containers"].squeeze())

                        # get runtime estimation by phase of job estimator
                        if phase == 1:
                            # get latest binary search estimate
                            urlf = 'http://127.0.0.1:5000/HistoricalData/getall'
                            historical_job_data = requests.get(urlf).json()

                            # find previous execution of the job
                            exists = False
                            status_runtime = 0
                            for entries in historical_job_data:
                                if entries["HistoricalData"] == job_id:
                                    exists = True
                                    status_runtime = entries["runtime"]

                            if exists:
                                run_est = status_runtime
                            else:
                                run_est = round(average_runtime(container_min))
                        else:
                            # extract predicted runtime for job in index steps
                            df = job_estimation[job_estimation["job_id"] == job_id]
                            run_est = int(df["predicted_runtime"].squeeze())

                        if run_est < shortest_runtime or shortest_runtime == 0:
                            shortest_runtime = run_est
                            shortest_job_id = job_id
                            chosen_job = current_job

                # run trigger - if True at end of loop, we execute
                run_trigger = True

                # get future cluster load estimation from csv
                future_cluster_load_data = pd.read_csv('in/clusterLoad.csv')

                free_containers = get_free_containers(current_cluster_load["load"])

                # save current cluster load as historic data
                cluster_historic_datapoint(run, current_cluster_load["load"],
                                           current_cluster_load["total load of jobs"],
                                           current_cluster_load["load in percent"])

                # check if num of available containers decreases during runtime
                if free_containers > container_min:

                    # check if its possible to run with simulation time left
                    min_runtime = run + shortest_runtime
                    if min_runtime > max_index:
                        break
                    else:
                        for i in range(shortest_runtime):
                            load_index = run + i
                            df = future_cluster_load_data[future_cluster_load_data["time"] == load_index]
                            load = int(df["containers"].squeeze())
                            job_containers = get_job_containers(run)
                            future_load = get_free_containers(load + job_containers)
                            if future_load < container_min:
                                run_trigger = False

                # check if we execute
                if run_trigger:
                    trigger_check = not trigger_check
                    sim_response = trigger_execute_job(shortest_job_id, container_min, run)
                    print('Job ID: ' + str(sim_response["job_id"]) + ' | Message: '
                          + str(sim_response["message"]))

                    wait_time = wait_time + (run - int(chosen_job["timeOfEntry"]))

                    # delete job from queue
                    urlp = 'http://127.0.0.1:5000/Queue/delete/' + str(shortest_job_id)
                    update_queue = requests.get(urlp)
                    print('Queue response: ' + update_queue.text)

                    # Update historical job table
                    job_historic_datapoint(shortest_job_id, run, container_min, shortest_runtime, 'running')

            # check if any jobs failed/completed and need runtime adjusted
            job_check_up(run)

        # calculate all tracking values - average cluster load first
        avg_cluster_load = 0
        urlt = "http://127.0.0.1:5000/HistoricCluster/getAll"
        acc_cluster_load = requests.get(urlt).json()
        if acc_cluster_load:
            for entries in acc_cluster_load:
                avg_cluster_load = avg_cluster_load + int(entries["full_load"])
        avg_cluster_load = avg_cluster_load / (max_index - min_index)

        # average wait-time of jobs + num of triggered jobs
        triggered_jobs = pd.read_csv('/Simulation/flaskProject'
                                     '/triggeredjobs.csv')
        num_triggered_jobs = triggered_jobs.shape[0] + 1
        avg_wait_time = wait_time / num_triggered_jobs

        # number of dropped jobs
        num_dropped_jobs = triggered_jobs[triggered_jobs["status"] == 0].squeeze().count()

        # Final Output
        print("Simulation complete! Jobs triggered: " + str(num_triggered_jobs) + " | Jobs dropped: "
              + str(num_dropped_jobs) + " | Average cluster load: " + str(avg_cluster_load) + " | Average wait time: "
              + str(avg_wait_time))

        # check if simulation has been interrupted
        if not sim:
            break
        else:
            break
    pass


def best_fit_optimized(index):
    global wait_time, max_index, sim, phase, mode, max_capacity
    while True:
        for run in range(index, max_index):
            print("Index: " + str(run))

            # get current cluster load
            url = 'http://127.0.0.1:5005/cluster_load/time=' + str(run)
            current_cluster_load = requests.get(url).json()

            # save current cluster load as historic data
            cluster_historic_datapoint(run, current_cluster_load["load"],
                                       current_cluster_load["total load of jobs"],
                                       current_cluster_load["load in percent"])

            # current capacity
            capacity = get_free_containers(current_cluster_load["load"])

            # get future cluster load estimation from csv
            future_cluster_load_data = pd.read_csv('in/clusterLoad.csv')

            # establish how long it will be available
            timeframe = 0
            for counter in range(index, max_index):
                df = future_cluster_load_data[future_cluster_load_data["time"] == counter]
                load = int(df["containers"].squeeze())
                job_containers = get_job_containers(run)
                future_load = get_free_containers(load + job_containers)
                if future_load < capacity:
                    timeframe = max_index - counter
                    break
                else:
                    timeframe = max_index - run

            urlo = 'http://127.0.0.1:5000/Queue/getall'
            queue = requests.get(urlo).json()
            chosen_job = queue[0]
            if queue:
                trigger_check = False

                # vars for best fit job and precision
                best_fit_id = ''
                best_fit_difference = 1000000

                for current_job in queue:
                    if trigger_check:
                        # skip rest of queue
                        break
                    else:

                        # get id for current job
                        job_id = current_job["idQueue"]
                        pload = {'JobId': job_id}

                        # get job estimation from csv
                        job_estimation = pd.read_csv('in/PredictedRuntimes.csv')

                        # extract lowest required number of containers
                        df = job_estimation[job_estimation["job_id"] == job_id]
                        container_min = int(df["containers"].squeeze())

                        # get runtime estimation by phase of job estimator
                        if phase == 1:
                            # get latest binary search estimate
                            url = 'http://127.0.0.1:5000/HistoricalData/getall'
                            historical_job_data = requests.get(url).json()

                            # find previous execution of the job
                            exists = False
                            status_runtime = 0
                            for entries in historical_job_data:
                                if entries["HistoricalData"] == job_id:
                                    exists = True
                                    status_runtime = entries["runtime"]

                            if exists:
                                run_est = status_runtime
                            else:
                                run_est = round(average_runtime(container_min))
                        else:
                            # extract predicted runtime for job in index steps
                            df = job_estimation[job_estimation["job_id"] == job_id]
                            run_est = int(df["predicted_runtime"].squeeze())

                        scale_run_est = 0

                        if capacity > container_min:
                            factor = capacity / container_min
                            scale_run_est = run_est / factor

                            # potential candidate check
                            if scale_run_est <= timeframe:
                                if (timeframe - scale_run_est) < best_fit_difference:
                                    best_fit_difference = timeframe - scale_run_est
                                    best_fit_id = job_id
                                    chosen_job = current_job

                if best_fit_id:
                    trigger_check = not trigger_check
                    sim_response = trigger_execute_job(best_fit_id, capacity, run)
                    print('Job ID: ' + str(sim_response["job_id"]) + ' | Message: '
                          + str(sim_response["message"]))

                    wait_time = wait_time + (run - int(chosen_job["timeOfEntry"]))

                    # delete job from queue
                    url = 'http://127.0.0.1:5000/Queue/delete/' + str(best_fit_id)
                    update_queue = requests.get(url)
                    print('Queue response: ' + update_queue.text)

                    # Update historical job table
                    job_historic_datapoint(best_fit_id, run, capacity, timeframe - best_fit_difference, 'running')

            # check if any jobs failed/completed and need runtime adjusted
            job_check_up(run)

        # calculate all tracking values - average cluster load first
        avg_cluster_load = 0
        url = "http://127.0.0.1:5000/HistoricCluster/getAll"
        acc_cluster_load = requests.get(url).json()
        if acc_cluster_load:
            for entries in acc_cluster_load:
                avg_cluster_load = avg_cluster_load + int(entries["full_load"])
        avg_cluster_load = avg_cluster_load / (max_index - min_index)

        # average wait-time of jobs + num of triggered jobs
        triggered_jobs = pd.read_csv('/Simulation/flaskProject'
                                     '/triggeredjobs.csv')
        num_triggered_jobs = triggered_jobs.shape[0] + 1
        avg_wait_time = wait_time / num_triggered_jobs

        # number of dropped jobs
        num_dropped_jobs = triggered_jobs[triggered_jobs["status"] == 0].squeeze().count()

        # Final Output
        print("Simulation complete! Jobs triggered: " + str(num_triggered_jobs) + " | Jobs dropped: "
              + str(num_dropped_jobs) + " | Average cluster load: " + str(avg_cluster_load) + " | Average wait time: "
              + str(avg_wait_time))

        # check if simulation has been interrupted
        if not sim:
            break
        else:
            break
    pass


# simulation toggle
sim = True

# phase of job estimation
phase = 1

# implement switch to chose operating mode
mode = 5

# static values
max_capacity = 880
min_index = 20031
max_index = 30030

# send start index to simulation
url = 'http://127.0.0.1:5005/start_time=' + str(min_index)
requests.put(url)

# tracking values for conclusion
wait_time = 0

if mode == 0:
    greedy_basic(min_index)
else:
    if mode == 1:
        greedy_improved(min_index)
    else:
        if mode == 2:
            shortest_first(min_index)
        else:
            if mode == 3:
                best_fit_optimized(min_index)
            else:
                idle_load(min_index)
