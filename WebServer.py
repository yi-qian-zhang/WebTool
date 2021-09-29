#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

__AUTHOR__ = "Yiqian Zhang"    # author's name
__STUDENT_NUMBER__ = "18722082"    # author's student ID
__DATE__ = "06/10/2020"    # update date

import socket
import sys
import re
import multiprocessing


def handleRequest(tcpSocket):
    """
    :param tcpSocket: socket which connects with the client
    :return: nothing is returned
    """
    requestMessage = tcpSocket.recv(1024)   # receive request message from the client on connection socket

    try:
        request = requestMessage.splitlines()[0]
    except IndexError: 
        request = b''

    # extract the path of the requested object from the message (second part of the HTTP header)
    fileName = re.match(r"\w+ +(/[^ ]*) ", request.decode()).group(1)

    try:
        a = fileName[1]    # check whether fileName is null
    except IndexError:
        fileName = ''
    else:
        if fileName[0: 11] == '/index.html':
            fileName = 'index.html'    # file name
        else:
            fileName = ''

    try:
        file = open(fileName, 'rb')   # read the corresponding file from disk
    except FileNotFoundError:
        responseHeader = "HTTP/1.1 404 Not Found\r\n" + \
            "Server: 127.0.0.1\r\n" + "\r\n"

        responseData = responseHeader + "No such file\nCheck your input\n"

        response = responseHeader + responseData    # send the correct HTTP response error
    else:
        content = file.read()    # store in temporary buffer
        file.close()

        response = "HTTP/1.1 200 OK\r\n" + "Server: 127.0.0.1\r\n" + "\r\n" \
            + content.decode()  # send the correct HTTP response

    tcpSocket.send(response.encode())    # send the content of the file to the socket

    tcpSocket.close()   # close the connection socket


def startServer(serverAddress, serverPort):
    """
    :param serverAddress: to which the request is sent
    :param serverPort: the port that listens for request
    :return: nothing is returned
    """
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind((serverAddress, serverPort))  # bind the server socket to server address and server port

    serverSocket.listen(0)     # continuously listen for connections to server socket

    while True:    # when a connection is accepted, call handleRequest function, passing new connection socket
        try:
            print("Waiting for connection...\n")

            connectSocket, address = serverSocket.accept()  # accept connection request
            print("Connected successfully\nHandling requests...\n")

            handleProcess = multiprocessing.Process(target=handleRequest, args=(connectSocket, ))
            handleProcess.start()   # handle request
        except KeyboardInterrupt:
            break


""" 
main is where your program starts
it is a good habit to include main
"""
if __name__ == "__main__":
    while True:
        port = input("Please input a port number over 1024: ")  # prompt use to choose a port

        try:
            port = int(port)    # convert str into int
        except ValueError:
            print("You should input integers\n")    # input is not integer
            continue
        else:
            if port < 1024:
                print("I do not recommend you to use port 0 to 1024\n")    # port should be over 1024
                continue
            else:
                break   # OK

    try:
        startServer("", port)   # call function startServer
    except KeyboardInterrupt:
        sys.exit(1)
