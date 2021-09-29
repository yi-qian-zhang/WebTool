#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

__AUTHOR__ = "Yiqian Zhang"    # author's name
__STUDENT_NUMBER__ = "18722082"    # author's student ID
__DATE__ = "01/10/2020"    # update date

import socket
import struct
import time
import select
import random

ICMP_ECHO_REQUEST = 8  # ICMP type code for echo request messages
ICMP_ECHO_REPLY = 0  # ICMP type code for echo reply messages


def checksum(string):
    """
    :param string: the string which will be checked
    :return: the string which has been checked is return
    """
    c_sum = 0    # initialise the sum to 0
    countTo = (len(string) // 2) * 2    # take the upper boundary of the number of loops
    count = 0   # the counter is used to compute how many times the loop is executed

    while count < countTo:
        thisVal = ((string[count + 1]) << 8) + string[count]
        c_sum = c_sum + thisVal
        count = count + 2   # Add 2 to the counter

    if len(string) % 2:
        c_sum = c_sum + string[-1]    # If the length of string is odd, then add the last element

    c_sum = (c_sum >> 16) + (c_sum & 0xffff)
    c_sum = c_sum + (c_sum >> 16)
    answer = ~c_sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)

    return answer


def receiveOnePing(icmpSocket, destinationAddress, ID, timeout):
    """
    :param icmpSocket: the socket used to receive the ping
    :param destinationAddress: the host to which the ping is sent
    :param ID: packet ID, justifying whether received packet is the one sent
    :param timeout: time interval for listening to coming message
    :return: time when ping arrived is returned
    """
    startTime = time.time()    # record the start time
    msg = select.select([icmpSocket], [], [], timeout)  # wait for the socket to receive a reply
    timeReceived = time.time()  # once received, record time of receipt

    # unpack the packet header for useful information, including the ID
    receivePacket, address = icmpSocket.recvfrom(1024)
    icmpHeader = receivePacket[20: 28]
    dataType, dataCode, checkSum, packetID, sequence = struct.unpack(">BBHHH", icmpHeader)

    # check that the ID matches between the request and reply
    if dataType == ICMP_ECHO_REPLY and packetID == ID and timeReceived != startTime:
        return timeReceived    # return total network delay
    else:
        return -1


def sendOnePing(icmpSocket, destinationAddress, ID):
    """
    :param icmpSocket: the socket used to send the ping
    :param destinationAddress: the host to which the ping is sent
    :param ID: packet ID, justifying whether received packet is the one sent
    :return: time when the packet is sent is returned
    """
    icmpPacket = struct.pack('>BBHHH32s', ICMP_ECHO_REQUEST, 0, 0, ID, 1, b'Don')
    icmpChecksum = checksum(icmpPacket)
    icmpPacket = struct.pack('>BBHHH32s', ICMP_ECHO_REQUEST, 0, icmpChecksum, ID, 1, b'Don')
    """ build ICMP header
        checksum ICMP use giving function
        insert checksum into packet """

    icmpSocket.sendto(icmpPacket, (destinationAddress, 80))    # send packet using socket
    timeSend = time.time()  # record time of sending

    return timeSend    # return the time of sending


def doOnePing(destinationAddress, timeout):
    """
    :param destinationAddress: the host to which the ping is sent
    :param timeout: time interval for listening to coming message
    :return: period used to receive the ping is returned
    """
    ICMP = socket.getprotobyname("icmp")    # ICMP protocol
    icmpSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, ICMP)   # create ICMP socket

    ID = random.randint(0, 10)  # raise a random integer for packet ID
    timeSend = sendOnePing(icmpSocket, destinationAddress, ID)  # call sendOnePing function
    timeReceive = receiveOnePing(icmpSocket, destinationAddress, ID, timeout)   # call receiveOnePing function

    icmpSocket.close()  # close ICMP socket

    if timeReceive == -1:   # timeout
        return timeReceive
    return timeReceive - timeSend   # return total network delay


def ping(host, timeout=1, n=0):
    """
    :param host: the host to which ping is sent
    :param timeout: time interval for listening to coming message
    :param n: times of loop for which ping is sent
    :return: nothing is returned
    """
    delayArray = []    # create an array to store the results
    print('\n')
    for i in range(n):
        print("Requesting ping from %s." % host)
        delay = doOnePing(host, timeout)*1000   # call doOnePing function, approximately every second

        if delay == -1:    # timeout
            print("Reply timeout. (timeout within %ssec.)" % timeout)
        else:
            delayArray.insert(i, delay)    # insert daley into array
            print("Reply ping in %.4fms." % delay)    # print out the returned delay

            time.sleep(1 - delay/1000)
    # continue this process until stopped
    if len(delayArray) > 0:    # if the array is not null, execute following statements
        delayArray.sort()   # sort the array
        print("\nThe minimum is: %.4fms." % delayArray[0])    # get the minimum
        print("The maximum is: %.4fms." % delayArray[-1])  # get the maximum
        delaySum = sum(delayArray)   # get the sum of array
        print("The average is: %.4fms." % (delaySum/len(delayArray)))  # get the average
    else:
        print("\nNo delay is gained.")     # delayArray is empty


""" 
main is where your program starts
it is a good habit to include main
"""
if __name__ == '__main__':
    while True:
        hostInput = input('Input an IP or host name: ')  # prompt user to input
        if not hostInput:
            print("\nProgram terminates.\n")    # if nothing is input, program terminates
            break
        try:
            hostInput = socket.gethostbyname(hostInput)
        except socket.gaierror as e:
            print("\nException occurs: %s" % e)
            print("Please input valid address.\n")
            continue

        while True:
            try:
                desiredTimeout = int(input("The desired timeout: "))    # input value of timeout
                times = int(input("The desired times for loop: "))  # input number of loop
            except ValueError as er:
                print("\nYou need to input integers.\n")    # input is not integer
                continue
            if desiredTimeout <= 0 or times < 0:
                print("\nYou should input positive integers.\n")
                continue    # continue to input proper information
            break
        ping(hostInput, desiredTimeout, times)  # call function ping
        print('\n')
