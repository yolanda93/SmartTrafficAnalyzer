# SmartTrafficAnalyzer
Smart Network Traffic Analyzer


project tree
=================

This repository is organised in the following way:

<pre>
   SmartTraficcAnalyzer
   ├── post-processing/     : some functionalities to perform some post-processing operations 
   ├── checker/             : rule-based checker to ensure data quality 
   ├── statistics/          : compute some statistics over the datasets
   ├── jupyter-notebooks/   : scripts with different experiments used to train ml algorithms
   └── README               : this file

</pre>

## Requirements

This project uses pyspark to perform massive distributed processing over resilient sets of data

###### (1) Install pySpark

To install Spark, make sure first that you have Java 8 or higher

```
$ tar -xzf spark-2.3.0-bin-hadoop2.7

$ mv spark-2.3.0-bin-hadoop2.7 /opt/spark-2.3.0

$ ln -s /opt/spark-2.3.0 /opt/spark̀

$ export SPARK_HOME=/opt/spark

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


