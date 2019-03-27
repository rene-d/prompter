#! /usr/bin/env python3

"""
SUB example
"""

import zmq
import datetime


def main():
    """ main method """

    # Prepare our context and publisher
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.bind("ipc://./.log.sock")
    subscriber.setsockopt(zmq.SUBSCRIBE, b"LOG")

    while True:
        # Read envelope with address
        address, contents = subscriber.recv_multipart()
        now = datetime.datetime.now().strftime("%H:%M:%S.%f")
        print("[{}] {}".format(now, contents.decode()))

    # We never get here but clean up anyhow
    subscriber.close()
    context.term()


if __name__ == "__main__":
    main()
