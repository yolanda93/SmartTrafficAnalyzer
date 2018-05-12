#!/usr/bin/python

"""
Usage:
 demoEIT.py (forensic | realtime) -t <file> -n <file>
 demoEIT.py -h | --help

Options:
 -t <file>, --tstat <file>     # Tstat file to be processed
 -n <file>, --network <file>   # Machine Learning trained network
"""


from docopt import docopt, DocoptExit
import requests
import json
import time
import arrow
from datetime import datetime, tzinfo, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
from random import randint
from time import sleep
import numpy as np
import logging
import sys
import json
import signal
import warnings
import time

CONFIDENCE      = 0
TIME_START      = 1
TIME_END        = 2
IP_O            = 3
IP_D            = 4
PORT_O          = 5
PORT_D          = 6
PROTOCOL        = 7
TAG             = 8
TAG_NAME        = 9
tagNames=['Web',"Video","Cloud"]
number_packets_before_send = 4
percentage_threshold_change_alert=0.035
min_prob_confience = 0.75
i_pushed = 0
i_notpushed = 0


KIBANA_HOST = 'http://localhost'
KIBANA_PORT = '8081'

class Flow:
        def __init__(self,prob):
            number_of_tags=[0.,0.,0.]
            self.prob=np.array(number_of_tags)
            self.occurrences=np.array(number_of_tags)
            #value,occurrence,index(tag)
            self.last_send=np.array([0.,0.,0.])
            self.times_pushed = 0
            self.add_prob(prob)

            self.time_start = data[28]
            self.time_end = data[29]
            self.ip_o = data[0]
            self.ip_d = data[14]
            self.port_o = data[1]
            self.port_d = data[15]

        def get_number_packets(self):
            return sum(self.occurrences)

        def get_curr_prob(self):
            return np.nan_to_num(self.prob/self.occurrences).max()

        def get_curr_tag(self):
            return np.argmax(np.nan_to_num(self.prob/self.occurrences))

        def get_last_prob_sended(self):
            return self.last_send[0]

        def get_last_tag_sended(self):
            return self.last_send[2]

        def add_prob(self,prob):
            self.prob[np.argmax(prob)] += max(prob)
            self.occurrences[np.argmax(prob)] += 1

        def update_last_sended(self):
            self.last_send = np.array([self.get_curr_prob(), self.occurrences[np.argmax(np.nan_to_num(self.prob/self.occurrences))], np.argmax(np.nan_to_num(self.prob/self.occurrences))])
            self.times_pushed += 1

        def __str__(self):
            return '[{:<15}] {:<15}:{:<5} > {:<15}:{:<5}\tProb: [ {:<10.4}{:<10.4}{:<10.4} ]\t#Ocurrences: [ {:<6.4}{:<6.4}{:<4.4} ]\tLastSend: [ {:<6.4}{:<6.4}{:<4.4} ]\tTimes_Pushed: {}'.format(self.time_start,self.ip_o,self.port_o,self.ip_d,self.port_d, (self.prob/self.occurrences)[0], (self.prob/self.occurrences)[1], (self.prob/self.occurrences)[2],self.occurrences[0],self.occurrences[1],self.occurrences[2],self.last_send[0],self.last_send[1],self.last_send[2],self.times_pushed)

def get_output_message(flow):
    return "PREDICTION: {:<8}PROBABILITY: {:<8.4}TIMES_PUSHED: {:<8}ALL_PROBS: [ {:<6.4}{:<6.4}{:<4.4} ]\t\t[{}] {:<15}:{:<5} > {:<15}:{:<5} ({:<5})\tPushed: {:<7}Not Pushed: {}".format(flow.get_curr_tag(), flow.get_curr_prob(),int(flow.times_pushed),str(flow.prob[0]/flow.occurrences[0]),str(flow.prob[1]/flow.occurrences[1]),str(flow.prob[2]/flow.occurrences[2]),'%.0f'%float(data[28]),data[0],data[1],data[14],data[15],int(flow.get_number_packets()),i_pushed,i_notpushed)



def publish_flow_to_kibana(flow):
    """
    This function publish a new flow in the kibana dashboard
    """
    document = dict()

    if flow.get_curr_prob() < min_prob_confience:
        document['confidence']=float(flow.get_curr_prob())
        document['tag']=4
        document['tag_name']=str('Unclassified')
    else:
        document['confidence']=float(flow.get_curr_prob())
        document['tag']=int(flow.get_curr_tag())
        document['tag_name']=tagNames[flow.get_curr_tag()]
   
    document['flow_id']=data[0]+data[1]+data[14]+data[15]+'%.0f'%float(data[28])
    document['time_start']='%.0f'%float(data[28])
    document['time_end']='%.0f'%float(data[29])
    document['ip_o']=str(data[0])
    document['ip_d']=str(data[14])
    document['port_o']=str(data[1])
    document['port_d']=str(data[15])
    document['protocol']='TCP'
    document['@timestamp']=str(arrow.utcnow())
 
    print(str(document))
    requests.post(KIBANA_HOST + ":" + KIBANA_PORT + "/" + "eit_demoml-" + datetime.now().strftime("%Y-%m-%d") +"/logs/", data=json.dumps(document))

    flow.update_last_sended()

    if flow.times_pushed == 1 :
        print "(*NEW*)" + get_output_message(flow)
    else:
        print "       " + get_output_message(flow)


def follow(thefile):
    thefile.seek(0,2)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

def classificator(message, rf, bad_features, good_features, tstat_traces_dic):
    #for message in tstat_file:
    try:
        global data
        data = message.split()
        y = [data[i] for i in good_features]
        X = np.array(y).reshape(1,-1)
        
	try:
            prob = rf.predict_proba(X)
            prob = prob.tolist()[0]
            prediction = np.argmax(prob)
        except ValueError:
            print "Value Error"

        #key is ip_o,port_o,ip_d,port_d,timeStart
        key = data[0]+data[1]+data[14]+data[15]+'%.0f'%float(data[28])
        try:
            flow = tstat_traces_dic[key]
            flow.add_prob(prob)
            first_ocurrence = False
        except KeyError:
            flow = Flow(prob)
            first_ocurrence = True

        # For the real time mode
        if (flow.get_curr_prob() > flow.get_last_prob_sended() + percentage_threshold_change_alert) and flow.get_number_packets() >= number_packets_before_send :
       	    global i_pushed
            i_pushed += 1
            publish_flow_to_kibana(flow)
        else:
            global i_notpushed
            i_notpushed += 1 
        tstat_traces_dic[key] = flow
    except TypeError:
         print "IO ERROR"
    except IndexError:
         print "Index error"


def initialize(network):
    
    #Machine Learning Stuff
    #Load model
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        rf = joblib.load(network)

    bad_features = [0,1,11,14,15,17,28,29,37,38,39,40,42,49,50,56,57,58,59,60,61,62,63,64,65,66,67,68,69,73,74,79,80,81,83,85,86,87,88,89,90,91,96,97,101,102,103,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130]
    bad_features = [i for i in bad_features]
    good_features = [i for i in range(131) if i not in bad_features]

    tstat_traces_dic = { }

    return rf, bad_features, good_features, tstat_traces_dic

def forensicMode(arguments):
  
    # Get the parameters from the shell
    tstat_file = arguments['--tstat']
    network = arguments['--network']

    #Prepare to push data to kafka server
    isFirst = True
    initialTime = 0.0
    cicle = 1

    [rf, bad_features, good_features, tstat_traces_dic] = initialize(network)

    #Sending messages
    with open(tstat_file) as session_data:
        for line in session_data :
            line_split = line.split(" ")
            if "#" in line_split[0]:
                continue
            elif isFirst:
                initialTime = float(line.split()[29])
                isFirst = False
                lineTime = float(line.split()[29])
                timestamp = time.gmtime(lineTime/1000.)
            else:
                lineTime = float(line.split()[29])
               	while (lineTime > (initialTime + cicle * 2000.0)):
               	     time.sleep (2.0)
               	     cicle+=1
                timestamp = time.gmtime(lineTime/1000.)
                # Process the line with the classificator
                classificator(line, rf, bad_features, good_features, tstat_traces_dic)

def realTimeMode(arguments):
    # Get the parameters from the shell
    tstat_file = arguments['--tstat']
    network = arguments['--network']

    # Open tstat_file
    logfile = open(tstat_file,"r")
    loglines = follow(logfile)
    [rf, bad_features, good_features, tstat_traces_dic] = initialize(network)
    for line in loglines:
        classificator(line, rf, bad_features, good_features, tstat_traces_dic)

if __name__ == '__main__':

	try:
            args=sys.argv;
            args.pop(0)
            arguments = docopt(doc=__doc__, argv=args)

            if arguments['realtime'] == True:
                realTimeMode(arguments)
            elif arguments['forensic'] == True:
                forensicMode(arguments)

        except DocoptExit as e:
            print e.message
