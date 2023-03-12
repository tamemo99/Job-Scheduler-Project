from app import db


class Job(db.Model):
    __tablename__ = 'job'

    job_id = db.Column(db.Integer, primary_key= True, autoincrement=False)
    name = db.Column(db.String())
    description = db.Column(db.String())

    def __init__(self, job_id, name, description):
        self.job_id = job_id
        self.name = name
        self.description = description,

    def __repr__(self):
        return '<job_id {}>'.format(self.jobidid)

    def serialize(self):
        return{
            'job_id': self.job_id,
            'name': self.name,
            'description': self.description,
        }


class Queue(db.Model):

    __tablename__ = 'Queue'

    id_in_queue = db.Column(db.Integer, db.ForeignKey('job.job_id'), primary_key=True)
    deadline = db.Column(db.String())
    time_of_entry = db.Column(db.String)

    def __init__(self, id_in_queue, deadline, time_of_entry):
        self.id_in_queue = id_in_queue
        self.deadline = deadline,
        self.time_of_entry = time_of_entry

    def serialize1(self):
        return{
            'id_in_queue': self.id_in_queue,
            'deadline': self.deadline,
            'time_of_entry': self.time_of_entry
        }


class HistoricalData(db.Model):
    __tablename__= 'Historical Data'

    historical_data_id = db.Column(db.Integer, db.ForeignKey('job.job_id'), primary_key=True)
    runtime = db.Column(db.Integer)
    date = db.Column(db.String)
    containers = db.Column(db.Integer)
    job_status = db.Column(db.String)

    def __int__(self, historical_data_id, runtime, containers, date, job_status):
        self.historical_data_id = historical_data_id,
        self.runtime = runtime,
        self.date = date,
        self.containers = containers,
        self.job_status = job_status

    def serialize2(self):
        return{
            'historicaldata_id': self.historical_data_id,
            'runtime': self.runtime,
            'date': self.date,
            'containers': self.containers,
            'job_status': self.job_status
        }


class simulationstabelle(db.Model):
    __tablename__ = 'simulationstabelle'

    id_of_job = db.Column(db.Integer, db.ForeignKey('job.job_id'), primary_key=True)
    number_of_containers = db.Column(db.Integer)
    end_time = db.Column(db.Integer)
    start_time =db.column(db.Integer)
    status = db.Column(db.Integer)

    def __int__(self, id_of_job, number_of_container, end_time, start_time, status):
        self.id_of_job = id_of_job,
        self.number_of_containers = number_of_container,
        self.end_time = end_time,
        self.start_time = start_time,
        self.status = status

    def serialize3(self):
        return {
            'id_of_job': self.historicaldata_id,
            'number_of_containers': self.number_of_containers,
            'end_time': self.end_time,
            'start_time': self.start_time,
            'status': self.status
        }


class HistoricalDataCluster(db.Model):
    __tablename__ = 'Historical Data Cluster'

    data_index = db.Column(db.Integer, primary_key=True, autoincrement=False)
    percentage_load = db.Column(db.FLOAT())
    full_load = db.Column(db.Integer)
    job_load = db.Column(db.Integer)

    def __int__(self, data_index, percentage_load, full_load, job_load):
        self.data_index = data_index,
        self.percentage_load = percentage_load,
        self.full_load = full_load,
        self.job_load = job_load

    def serialize4(self):
        return{
            'data_index': self.data_index,
            'percentage_load': self.percentage_load,
            'full_load': self.full_load,
            'job_load': self.job_load
        }
