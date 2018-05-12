# SmartTrafficAnalyzer
Smart Network Traffic Analyzer (STA)


project tree
=================

This repository is organised in the following way:

<pre>
   SmartTrafficAnalyzer
   ├── utilities/           : some functionalities to compute some statistics and perform some post-processing operations 
   ├── checker/             : rule-based checker to ensure data quality 
   ├── jupyter-notebooks/   : scripts used to train ml algorithms
   ├── deployment/          : scripts and procedures used to deploy the trained ml algorithm on a real scenario
   └── README               : this file

</pre>

## Requirements


This project uses:

*  pyspark to perform massive distributed processing over resilient sets of data
*  tensorflow and scickit-learn for machine learning
*  jupyter notebook 

###### (1) Install pySpark

To install Spark, make sure first that you have Java 8 or higher

```
$ tar -xzf spark-2.3.0-bin-hadoop2.7

$ mv spark-2.3.0-bin-hadoop2.7 /opt/spark-2.3.0

$ ln -s /opt/spark-2.3.0 /opt/spark̀2

$ export SPARK_HOME=/opt/spark2

$ export PATH=$SPARK_HOME/bin:$PATH
```

###### (2) Install Jupyter Notebook

```
$ pip install jupyter
```

###### (3) Install FindSpark package

```
$ pip install findspark
```


