import requests
import json
import socket

class APIIntegration:

    def connection(self, url):
        """
        :param url: get the url to connect to api
        :return: status code
        """
        try:
            # see if we can resolve the host name -- tells us if there is
            # a DNS listening
            host = socket.gethostbyname("www.google.com")
            # connect to the host -- tells us if the host is actually
            # reachable
            s = socket.create_connection((host, 80), 2)
            response = requests.post(url)
            return response.status_code
        except:
            pass
        return False

    def set_payload(self, url, payload, sign):
        """
        :param payload: The information That Must be go with the request
        to get the response
        :param url: get the url to connect to api
        :param follow_id: Patient follow request number
        :param sign: it’s a keyed hash for incoming HTTP requests authentication
        :return response object
        """
        headers = {
            'Content-Type': "application/json",
            'Cache-Control': "no-cache",
            'Token': sign
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        result = json.loads(response.text)
        return result

################################################
# WCF request based on json response
##############################################

    def wcf_connection(self, url):
        """
        :Windows Communication Foundation - send get request
        :param url: get the url to connect to api
        :return: status code
        """
        try:
            # see if we can resolve the host name -- tells us if there is
            # a DNS listening
            host = socket.gethostbyname("www.google.com")
            # connect to the host -- tells us if the host is actually
            # reachable
            s = socket.create_connection((host, 80), 2)
            response = requests.get(url)
            return response.status_code
        except:
            pass
        return False

    def wcf_get(self, url ):
        """
        :get request of url 
        :return response text body
        """
        response = requests.get(url)
        return response.text
