#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

__AUTHOR__ = "Yiqian Zhang"    # author's name
__STUDENT_NUMBER__ = "18722082"    # author's student ID
__DATE__ = "01/10/2020"    # update date

import socket
import os
import struct
import time
import select

ICMP_ECHO_REQUEST = 8  # ICMP type code for echo request messages
ICMP_ECHO_REPLY = 0  # ICMP type code for echo reply messages


def checksum(string):
    """
    :param string: the string which will be checked
    :return: the string which has been checked is return
    """
    c_sum = 0  # initialise the sum to 0
    countTo = (len(string) // 2) * 2  # take the upper boundary of the number of loops
    count = 0  # the counter is used to compute how many times the loop is executed

    while count < countTo:
        thisVal = ((string[count + 1]) << 8) + string[count]
        c_sum = c_sum + thisVal
        count = count + 2  # Add 2 to the counter

    if len(string) % 2:
        c_sum = c_sum + string[-1]  # If the length of string is odd, then add the last element

    c_sum = (c_sum >> 16) + (c_sum & 0xffff)
    c_sum = c_sum + (c_sum >> 16)
    answer = ~c_sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)

    return answer


def receive(icmpSocket, timeout, delay, IPAddress, tries):
    """
    :param icmpSocket: the socket which is used to receive packet
    :param timeout: time interval for listening to coming message
    :param delay: the array used to store the delays
    :param IPAddress: the host to which the packet is sent
    :param tries: times of loop for which TTL packet is sent
    :return: delay and IPAddress is returned
    """
    # compute time for receiving data
    startTime = time.time()
    select.select([icmpSocket], [], [], timeout)    # accept packet from socket
    endTime = time.time()
    period = endTime - startTime    # calculate the period used

    if period > 2:  # timed out
        delay.insert(tries, -1)    # delay is set to -1
        if IPAddress is None:
            IPAddress = "Request timed out"
    else:
        # received successfully, retrieve the address and check dataType
        packet, IPAddress = icmpSocket.recvfrom(1024)   # receive the packet
        IPAddress = IPAddress[0]    # get address
        header = packet[20: 28]    # get header
        dataType, dataCode, dataChecksum, ID, sequence = struct.unpack('>bbHHh', header)
        if dataType == 0 or dataType == 11:  # record the delay
            delay.insert(tries, period * 1000)
        else:  # lost
            delay.insert(tries, -1)    # delay is set to -1

    return delay, IPAddress


def send(icmpSocket, host, mySequence=1):
    """
    :param icmpSocket: the socket which is used to send packet
    :param host: the host to which the packet is sent
    :param mySequence: the sequence of the packet
    :return: nothing is returned
    """
    myID = os.getpid()  # get the id of current process
    # create an icmpHeader and a packet
    icmpHeader = struct.pack(">bbHHh", ICMP_ECHO_REQUEST, 0, 0, myID, mySequence)
    myData = struct.pack("d", time.time())
    packet = icmpHeader + myData

    # checksum and repack the header
    myChecksum = checksum(packet)
    icmpHeader = struct.pack(">bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myID, mySequence)
    icmpPacket = icmpHeader + myData

    icmpSocket.sendto(icmpPacket, (host, 80))   # send the packet to destination


def getName(address):
    """
    :param address: address that will be turned into name
    :return: name of address will be return
    """
    try:
        hostName = socket.gethostbyaddr(address)[0]    # try to find its name
    except socket.error:
        hostName = 'Name not found'    # no name found

    return hostName


def traceroute(host, timesDesired=1, timeout=2):
    """
    :param host: to which packet will be sent
    :param timesDesired: maximum of TTL
    :param timeout: period for listening for packet
    :return: nothing is returned
    """
    print("Traceroute: %s" % host)
    for TTL in range(1, timesDesired + 1):
        delay = []  # 3 delays
        IPAddress = None  # initialise router's address

        for tries in range(3):  # try 3 traces for each TTL
            # initialise the icmpSocket
            icmpSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))

            icmpSocket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, struct.pack("I", TTL))
            icmpSocket.settimeout(timeout)

            # create a packet with given function and send it to destination
            send(icmpSocket, host, TTL)

            # receive info with given function
            delay, IPAddress = receive(icmpSocket, timeout, delay, IPAddress, tries)

            icmpSocket.close()  # close the socket

        # print out three delays and the address and name for router
        print("TTL: %d\t" % TTL, end='')
        for i in range(3):     # 3 delays are displayed in turn
            if delay[i] == -1 or delay[i] == 0.0:
                print("\t\t*\t", end='')    # packet lost or timeout
            else:
                print("\t%.2fms\t" % delay[i], end='')     # delay is printed
        hostName = getName(IPAddress)
        print("\taddress: (%s)\tname: %s" % (IPAddress, hostName))     # print information of host

    print("\n")  # turn to new line


""" 
main is where your program starts
it is a good habit to include main
"""
if __name__ == "__main__":
    while True:
        hostInput = input("Input a host or IP address: ")   # ask user to input host

        if not hostInput:  # if nothing input, terminate
            print("Program terminates\n")
            break   # program terminates

        try:
            hostInput = socket.gethostbyname(hostInput)
        except socket.gaierror as e:  # invalid host input
            print("Error: %s\nPlease input valid host" % e)
            continue    # re-input the host

        while True:
            times = input("Input value of TTL: ")  # ask user to input TTL
            try:
                times = int(times)
                if times < 1:  # TTL should be greater than or equal to 1
                    print("Please input integer greater than or equal to 1")
                    continue
            except ValueError:  # input is not integer, error
                print("Please input value greater than or equal to 1")
                continue
            break

        while True:
            TIMEOUT = input("Input value of timeout: ")  # ask user to input timeout
            try:
                TIMEOUT = int(TIMEOUT)
                if TIMEOUT < 0:  # timeout should be greater than 0
                    print("Please input integer greater than 0")
                    continue
            except ValueError:  # input is not integer, error
                print("Please input integer greater than 0")
                continue
            break

        traceroute(hostInput, times, TIMEOUT)  # function call of traceroute()
