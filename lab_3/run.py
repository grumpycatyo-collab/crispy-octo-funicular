#!/usr/bin/env python3
from pipe.consumer import run_consumer
from pipe.publisher import run_publisher

from multiprocessing import Process

if __name__ == "__main__":
    publisher_process = Process(target=run_publisher)
    consumer_process = Process(target=run_consumer)

    publisher_process.start()
    consumer_process.start()

    publisher_process.join()
    consumer_process.join()