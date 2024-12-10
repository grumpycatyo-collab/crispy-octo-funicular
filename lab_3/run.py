#!/usr/bin/env python3
from pipe.manager import run_manager
from pipe.publisher import run_publisher
from ftp import feed_ftp
from multiprocessing import Process

if __name__ == "__main__":
    # publisher_process = Process(target=run_publisher)
    ftp_process = Process(target=feed_ftp)
    consumer_process = Process(target=run_manager)

    # publisher_process.start()
    ftp_process.start()
    consumer_process.start()

    # publisher_process.join()
    ftp_process.join()
    consumer_process.join()