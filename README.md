# Semesterproject

Welcome to the WS 21/22 Semesterproject repository

Humboldt University of Berlin

Semesterprojekt 6: Serverless Distributed Data Processing Project

This Project included a group of 5 members, each of them had a certain task/part to focus on.

*NOTE*: My part of this project focuses on the database and its interface. however I helped the other group members in other parts of the projects where ever they needed

# Navigation

Structuring a software project is something we still need to learn.

There are three important directories:
- DatabaseInterface
- Scheduler 
- Simulation

To run experiments with the scheduler you need to set up the other 
components first. 

There are guides once you open each directory. Good luck!

# APIs & Database

Manage and test APIs: Use "Postman"

View Database with "pgAdmin4"
Interact with datatables through API 


# Load Estimator

To run the load Estimater script, you need "R version 4.1.2" with the packages 'forecast', 'stats', and 'utils'.

"trainingData.csv" file and "LoadEstimaterScript.R" script must be in the same folder.

Run the R script by typing :

```console
Rscript LoadEstimaterScript.R
```

The output will be the "EstimatedClusterLoad.csv" file.



