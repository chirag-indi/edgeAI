# !/usr/local/lib/python3.8 -Es
from datetime import time
from flask import Flask, request, jsonify, make_response
import requests
from flask_cors import CORS
import random
from datetime import datetime
import os
import logging 
from kubernetes import client, config


app = Flask(__name__)
CORS(app)


def node_discovery():
    '''
    This function returns a dictionary of active Pod's in all namespaces which have an external IP assigned to them.
    
    '''

    #load a Kubernetes config from within a cluster. This script must be run within a pod. 
    config.load_incluster_config()
    dynamic_pods = {}

    #Initialize the Python Kubernetes client
    v1 = client.CoreV1Api()

    logging.info("Listing pods with their IPs:")
    
    #List of pods of all namespaces
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        
        #If the pod has a external IP add it to the Output dictionary
        if i.status.pod_ip:
            logging.info("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
            dynamic_pods[i.status.pod_ip] = i.metadata.name
    
    return dynamic_pods


@app.route('/', methods=["POST"])
def base_case():
    '''
    This function defines a base endpoint which returns a JSON containing the list of runnings pods with external IPs

    '''
    try:
        node_list = node_discovery()
        return make_response(jsonify(node_list), 200)
    except requests.exceptions.HTTPError as err:
        return err.response.text, err.response.status_code
    except Exception as e:
        logging.error(e)
        return str(e), 500


@app.route('/continue', methods=["POST"])
def check_cont():
    try:

        logging.info("It enters continue!")

        #get the current Pod IP from the environment variable mentioned in the Kubernetes yaml file
        node_ip = os.environ.get('NODE_IP')
        logging.info("NODE_IP= " + str(node_ip))
        
        # Get the query json table passed to this pod
        query_param = request.get_json()
        logging.info("Query param= " + str(query_param))

        #Check if the current node is in the node_list arguement, if not, exit.
        node_list = query_param['node_list']
        if node_ip not in node_list:
            raise Exception("node not in node list")

        #Mark the current pod as visited
        del node_list[node_ip]

        #If there are no pods to visit after the current pod
        if len(node_list) == 0:

            #Append the current node IP and the time to the table of the query parameter
            query_param['table'].append(
            {
                "node_ip": node_ip,
                "time": str(datetime.now().strftime("%H:%M:%S:%f"))
                }
            )

            logging.info("New Query param= " + str(query_param))
            return make_response(jsonify(query_param), 200)
        
        #If there are more nodes to visit
        logging.info("New Node list= " + str(node_list))
        
        #Pick the next node/pod randomly
        next_node = random.choice(list(node_list.keys()))
        logging.info("Next Node= " + str(next_node))
        
        #Update the node_list
        query_param['node_list'] = node_list

        #Append the current node IP and the time to the table of the query parameter
        query_param['table'].append(
            {
                "node_ip": node_ip,
                "time": str(datetime.now().strftime("%H:%M:%S:%f"))
                }
        )
        
        logging.info("New Query param= " + str(query_param))

        #Pass the current table to the new pod picked in the previous step
        response = requests.post(f'http://{next_node}:12000/continue', json=query_param)
        logging.info("Response= " + str(response))
        response.raise_for_status()

        #Extract the received response
        data = response.json()
        logging.info("Data= " + str(data))

        #Return the updated table 
        return make_response(jsonify(data), 200)
    except requests.exceptions.HTTPError as err:
        return err.response.text, err.response.status_code
    except Exception as e:
        logging.error(e)
        return str(e), 500




@app.route('/start', methods=["GET"])
def check_start():
    try:
        logging.info("It enters start!")

        #get the current Pod IP from the environment variable mentioned in the Kubernetes yaml file
        node_ip = os.environ.get('NODE_IP')
        logging.info("NODE_IP= " + str(node_ip))
        
        #Get the list of currently active pods with an external IP
        node_list = node_discovery()

        #Check if the current node is in the node_list arguement, if not, exit.
        if node_ip not in node_list:
            raise Exception("node not in node list")

        #Mark the current pod as visited
        del node_list[node_ip]
        logging.info("New Node list= " + str(node_list))

        #Pick the next node/pod randomly
        next_node = random.choice(list(node_list.keys()))
        logging.info("Next Node= " + str(next_node))

        #Create a table with the current node IP and the time to the table of the query parameter
        table = { 'node_list': node_list,
        'table':
            [
                {
                "node_ip": node_ip,
                "time": str(datetime.now().strftime("%H:%M:%S:%f"))
                }
            ]
        }
        logging.info("New Query param= " + str(table))

        #Pass the current table to the new pod picked in the previous step
        response = requests.post(f'http://{next_node}:12000/continue', json=table)
        response.raise_for_status()

        #Extract the received response
        data = response.json() 
        logging.info("Data= " + str(data))

        #Return the updated table 
        return make_response(jsonify(data['table']), 200)
    except requests.exceptions.HTTPError as err:
        return err.response.text, err.response.status_code
    except Exception as e:
        logging.error(e)
        return str(e), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=12000)

