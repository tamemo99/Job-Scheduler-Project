import os
from flask import Flask, request, jsonify, render_template, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:HuServerlessProject@localhost/JobTool"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

Bootstrap(app)

from models import Job, Queue, HistoricalData, HistoricalDataCluster


@app.route('/')
def hello_world():  # put application's code here
    return render_template('everywhere.html')


@app.route("/Job/add")
def add_job():
    job_id = request.args.get('job_id')
    name = request.args.get('name')
    description = request.args.get('description')
    description = request.args.get('description')
    try:
        job = Job(
            job_id=job_id,
            name=name,
            description=description
        )
        db.session.add(job)
        db.session.commit()
        return "Job added. Job id = {}".format(job.id)
    except Exception as e:
        return str(e)


@app.route("/Job/add/form", methods=['GET', 'POST'])
def add_job_form():
    if request.method == 'POST':
        job_id = request.form.get('job_id')
        name = request.form.get('name')
        description = request.form.get('description')
        try:
            job = Job(
                job_id=job_id,
                name=name,
                description=description,
            )
            db.session.add(job)
            db.session.commit()
            return all_jobs()
        except Exception as e:
            return str(e)
    return render_template("job-form.html")


@app.route("/Job/Update/<int:number>/form", methods=['GET', 'POST'])
def edit_job_form(number):
    job = Job.query.get_or_404(number)

    if request.method == 'POST':
        if len(request.form.get('name')) != 0:
            job.name = request.form.get('name')
        else:
            job.name = job.name
        if len(request.form.get('description')) != 0:
            job.description = request.form.get('description')
        else:
            job.description = job.description
        pass

        try:
            db.session.commit()
            return all_jobs()
        except:
            return "error"
    return render_template("job-edit-form.html")


@app.route("/Job/getall")
def get_all_jobs():
    try:
        jobs = Job.query.all()
        return jsonify([e.serialize() for e in jobs])
    except Exception as e:
        return str(e)


@app.route("/Job/alljobs", methods=['GET', 'POST'])
def all_jobs():
    jobs = Job.query.all()
    return render_template('view-all-jobs.html', jobs=jobs)


@app.route("/Job/get/<int:job_id>")
def get_job(job_id):
    try:
        job = Job.query.filter_by(job_id=job_id).first()
        return jsonify(job.serialize())
    except Exception as e:
        return str(e)


@app.route("/Job/delete/<int:job_id>")
def delete_job(job_id):
    job_record_to_delete = Job.query.get_or_404(job_id)
    try:
        db.session.delete(job_record_to_delete)
        db.session.commit()
        return all_jobs()
    except Exception as e:
        return all_jobs()


@app.route("/Job/Update/<int:number>/edit")
def update_job(number):
    job = Job.query.get_or_404(number)
    job.name = request.args.get('name')
    job.description = request.args.get('description')
    try:
        db.session.commit()
        return "it worked"
    except Exception as e:
        return "Error"


@app.route("/HistoricalData/add")
def add_historicaldata():
    historicaldata_id = request.args.get("id")
    date = request.args.get('date')
    runtime = request.args.get('runtime')
    containers = request.args.get('containers')
    job_status = request.args.get('job_status')

    try:
        historical_record = HistoricalData(
            historicaldata_id=historicaldata_id,
            date=date,
            runtime=runtime,
            containers=containers,
            job_status=job_status
        )
        db.session.add(historical_record)
        db.session.commit()
        return "Historical Record added id = {}".format(historical_record.id)
    except Exception as e:
        return str(e)


@app.route("/HistoricalData/add/form", methods=['GET', 'POST'])
def add_historicaldata_form():
    if request.method == 'POST':
        historicaldata_id = request.form.get('historicaldata_id')
        runtime = request.form.get('runtime')
        date = str(request.form.get('date'))
        containers = request.form.get('containers')
        job_status = request.form.get('job_status')
        try:
            historical_record = HistoricalData(
                historicaldata_id=historicaldata_id,
                runtime=runtime,
                date=date,
                containers=containers,
                job_status=job_status
            )
            db.session.add(historical_record)
            db.session.commit()
            return all_historical_records()
        except Exception as e:
            return str(e)
    return render_template("add-historical-data.html")


@app.route("/HistroricalData/get/<int:historicaldata_id>")
def get_historical_record(historicaldata_id):
    try:
        historical_record = HistoricalData.query.filter_by(HistoricalData_id=historicaldata_id).first()
        return jsonify(historical_record.serialize2())
    except Exception as e:
        return str(e)


@app.route("/HistoricalData/getall")
def get_all_historicaldata():
    try:
        historicalrecords = HistoricalData.query.all()
        return jsonify([e.serialize2() for e in historicalrecords])
    except Exception as e:
        return str(e)


@app.route("/HistoricalData/allRecords", methods=['GET', 'POST'])
def all_historical_records():
    records = HistoricalData.query.all()
    return render_template('view-all-historical-data.html', records=records)


@app.route("/HistoricalData/Update/<int:number>/edit")
def update_historicaldata(number):
    historicaldata = HistoricalData.query.get(number)
    historicaldata.date = request.args.get('date')
    historicaldata.runtime = request.args.get('runtime')
    historicaldata.containers = request.args.get('containers')
    historicaldata.job_status = request.args.get('job_status')
    try:
        db.session.commit()
        return "updating worked"
    except Exception as e:
        return "nope didnt work"


@app.route("/HistoricalData/<int:num>/Update", methods=['GET', 'POST'])
def update_historicaldata_form(num):
    record = HistoricalData.query.get_or_404(num)
    today = datetime.today()
    current_date = today.strftime("%d-%m-%Y")
    date_of_record = str(current_date)
    status = request.form.get('job_status')
    if request.method == 'POST':
        if len(request.form.get('containers')) != 0:
            record.containers = request.form.get('containers')
        else:
            record.containers = record.containers
        if len(request.form.get('runtime')) != 0:
            record.runtime = request.form.get('runtime')
        else:
            record.runtime = record.runtime
        if date_of_record != str(record.date):
            record.date = date_of_record
        else:
            h = record.date
            record.date = h
        if request.form.get('status') != record.job_status:
            record.job_status = request.form.get('status')
        else:
            record.job_status = record.job_status
        pass
        try:
            db.session.commit()
            return all_historical_records()
        except Exception as e:
            return "error"
    return render_template("edit-historical.html")


@app.route("/HistoricalData/delete/<int:historicaldata_id>")
def delete_historical_record(historicaldata_id):
    historical_data_record_to_delete = HistoricalData.query.get_or_404(historicaldata_id)
    try:
        db.session.delete(historical_data_record_to_delete)
        db.session.commit()
        return all_historical_records()
    except:
        return all_historical_records()


@app.route("/HistoricalData/deleteAll")
def delete_all_historic_records():
    try:
        HistoricalData.query.delete()
        db.session.commit()
        return all_historical_records()
    except Exception as e:
        return str(e)


@app.route("/Queue/add")
def add_to_queue():
    id_in_queue = request.args.get("id")
    deadline = request.args.get("deadline")
    time_of_entry = request.args.get("startTime")
    try:
        queue_record = Queue(
            id_in_queue=id_in_queue,
            deadline=deadline,
            time_of_entry=time_of_entry,
        )
        db.session.add(queue_record)
        db.session.commit()
        return "Added to Queue, id = {}".format(Queue.id)
    except Exception as e:
        return str(e)


@app.route("/Queue/add/form", methods=['GET', 'POST'])
def add_queue_form():
    current_time = datetime.now()
    if request.method == 'POST':
        id_in_queue = request.form.get('id_in_queue')
        deadline = request.form.get('deadline')
        time_of_entry = str(current_time)
        try:
            queue_record = Queue(
                id_in_queue=id_in_queue,
                deadline=deadline,
                time_of_entry=time_of_entry,
            )
            db.session.add(queue_record)
            db.session.commit()
            return all_queue_records()
        except Exception as e:
            return str(e)
    return render_template("add-queue-record.html")


@app.route("/Queue/Update/<int:number>/edit")
def update_record_queue(number):
    record_in_queue = Queue.query.get_or_404(number)
    record_in_queue.deadline = request.args.get('deadline')
    record_in_queue.time_of_entry = request.args.get('time_of_entry')
    try:
        db.session.commit()
        return "Queue updated"
    except:
        return "Updating Queue didnt work"


@app.route("/Queue/edit/<int:number>/update", methods=['GET', 'POST'])
def update_queue_form(number):
    current_time = datetime.now()
    queue_record = Queue.query.get_or_404(number)

    if request.method == 'POST':
        queue_record.time_of_entry = str(current_time)
        if request.form.get('deadline') != queue_record.deadline:
            queue_record.deadline = request.form.get('deadline')
        else:
            queue_record.deadline = queue_record.deadline
        try:
            db.session.commit()
            return all_queue_records()
        except Exception as e:
            return "error"
    return render_template("edit-queue.html")


@app.route("/Queue/get/<int:id_in_queue>")
def get_queue_record(id_in_queue):
    try:
        queue_record = Queue.query.filter_by(id_in_queue=id_in_queue).first()
        return jsonify(queue_record.serialize1())
    except Exception as e:
        return str(e)


@app.route("/Queue/getall")
def get_queue():
    try:
        entire_queue = Queue.query.all()
        return jsonify([e.serialize1() for e in entire_queue])
    except Exception as e:
        return str(e)


@app.route("/Queue/allRecords", methods=['GET', 'POST'])
def all_queue_records():
    records = Queue.query.all()
    return render_template('view-queue.html', records=records)


@app.route("/Queue/delete/<int:id_in_queue>")
def delete_queue(id_in_queue):
    queue_record_to_delete = Queue.query.get_or_404(id_in_queue)
    try:
        db.session.delete(queue_record_to_delete)
        db.session.commit()
        return all_queue_records()
    except:
        return all_queue_records()


@app.route("/HistoricCluster/getAll")
def get_historic_cluster_data():
    try:
        historic_cluster_data = HistoricalDataCluster.query.all()
        return jsonify([e.serialize4() for e in historic_cluster_data])
    except Exception as e:
        return str(e)


@app.route("/HistoricCluster/add")
def add_historic_cluster_data():
    data_index = request.args.get("data_index")
    percentage_load = request.args.get("percentage_load")
    full_load = request.args.get("full_load")
    job_load = request.args.get("job_load")
    try:
        historic_cluster_record = HistoricalDataCluster(
            data_index=data_index,
            percentage_load=percentage_load,
            full_load=full_load,
            job_load=job_load
        )
        db.session.add(historic_cluster_record)
        db.session.commit()
        return "Added to cluster load, index = {}".format(historic_cluster_record.data_index)
    except Exception as e:
        return str(e)


@app.route("/HistoricCluster/allRecords", methods=['GET', 'POST'])
def all_historic_cluster_records():
    records = HistoricalDataCluster.query.all()
    return render_template('view-cluster.html', records=records)


@app.route("/HistoricCluster/deleteAll")
def delete_historic_cluster_data():
    try:
        HistoricalDataCluster.query.delete()
        db.session.commit()
        return all_historic_cluster_records()
    except Exception as e:
        return str(e)


@app.route("/simulation/", methods=['Get', 'POST'])
def simulation():
    current_queue = Queue.query.all()
    historicaldata_records = HistoricalData.query.all()
    historic_cluster = HistoricalDataCluster.query.all()

    return render_template('simulation-second.html', current_queue=current_queue, historical_record=historicaldata_records,
                           historiccluster=historic_cluster)


if __name__ == '__main_':
    app.run()
