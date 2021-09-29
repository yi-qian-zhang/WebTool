#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

__AUTHOR__ = "Yiqian Zhang"    # author's name
__STUDENT_NUMBER__ = "18722082"    # author's student ID
__DATE__ = "06/10/2020"    # update date

import os
import sys
import socket


def handleRequest(clientSocket):
    """
    :param clientSocket: the socket connecting to client
    :return: nothing is returned
    """
    # receive request information from client and read the file name
    requestMessage = clientSocket.recv(4096).decode()
    fileName = requestMessage.split()[1].partition("//")[2].replace('/', '_')

    # try to find file on the proxy and send it to client
    try:
        file = open(fileName, 'rb')
        responseMessage = file.readlines()     # if file is found, read the contents

        # send all the data in file to client
        for i in range(0, len(responseMessage)):
            clientSocket.send(responseMessage[i])

        print("File is found in proxy server.\n")
    # file is not found on proxy
    except FileNotFoundError:
        # try to send request to target server
        try:
            print("Try to send request to server.")
            sendSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     # create a tcp socket

            # find the server name
            serverName = requestMessage.split()[1].partition("//")[2].partition(':')[0]

            # connect with the server and send request to it
            sendSocket.connect((serverName, 80))
            sendSocket.sendall(requestMessage.encode())
            print("Send successfully.")    # request has been sent successfully

            responseMessage = sendSocket.recv(4096)    # receive response from server
            clientSocket.sendall(responseMessage)    # send response to client
            print("File found in server.")

            # cache the file on proxy
            cache = open("./" + fileName, 'w')
            cache.writelines(responseMessage.decode().replace('\r\n', '\n'))
            cache.close()
            print("File cached in proxy.\n")
        # request sent failed
        except socket.gaierror:
            print("Failed to send request to server.\n")


def proxyServer(port):
    """
    :param port: the port that listens for request
    :return: nothing is returned
    """
    # create a tcp socket and listen constantly
    proxySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxySocket.bind(("", port))    # bind to the given port
    proxySocket.listen(0)

    while True:
        try:
            print("Proxy is waiting for connection...")

            clientSocket, address = proxySocket.accept()    # request from client arrives
            print("Connected successfully.\n")

            handleRequest(clientSocket)    # call handleRequest function to handle request

        except KeyboardInterrupt:
            break

    proxySocket.close()    # close the proxy


""" 
main is where your program starts
it is a good habit to include main
"""
if __name__ == '__main__':
    while True:
        # ask user to choose a port that will be used
        try:
            port = int(input("Choose a port number over 1024: "))
        except ValueError:
            print("You should input integer.\n")    # input is not an integer
            continue
        else:
            if port > 1024:    # OK
                break
            else:
                print("You should input integer greater than 1024")    # port is chosen improperly
                continue

    try:
        proxyServer(port)   # call proxyServer function to start
    except KeyboardInterrupt:
        sys.exit(1)
