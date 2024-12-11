import threading
import socket
import random
import time
import requests
from enum import Enum
import json

class ServerState(Enum):
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3

class RaftServer:
    def __init__(self, server_id, port, peers, manager_url):
        self.server_id = server_id
        self.port = port
        self.peers = peers
        self.manager_url = manager_url
        self.state = ServerState.FOLLOWER
        self.current_term = 0
        self.voted_for = None
        self.leader_id = None
        self.last_heartbeat = time.time()
        self.election_timeout = random.uniform(150, 300) / 1000  # 150-300ms

        # Setup UDP server
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(('localhost', port))

        # Start election timer
        self.election_timer = threading.Thread(target=self.run_election_timer)
        self.election_timer.daemon = True
        self.election_timer.start()

        # Start UDP listener
        self.udp_listener = threading.Thread(target=self.listen_udp)
        self.udp_listener.daemon = True
        self.udp_listener.start()

    def run_election_timer(self):
        while True:
            if self.state != ServerState.LEADER:
                if time.time() - self.last_heartbeat > self.election_timeout:
                    self.start_election()
            time.sleep(0.05)

    def start_election(self):
        self.state = ServerState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.server_id
        self.votes_received = 1  # Vote for self, make this an instance variable

        # Request votes from peers
        for peer in self.peers:
            try:
                message = {
                    'type': 'REQUEST_VOTE',
                    'term': self.current_term,
                    'candidate_id': self.server_id
                }
                self.udp_socket.sendto(json.dumps(message).encode(), ('localhost', peer))
            except Exception as e:
                print(f"Error sending vote request to peer {peer}: {e}")

        # Wait for responses
        time.sleep(self.election_timeout)

        # If we got majority votes and still a candidate, become leader
        if self.votes_received > len(self.peers) / 2 and self.state == ServerState.CANDIDATE:
            self.become_leader()

    def become_leader(self):
        self.state = ServerState.LEADER
        self.leader_id = self.server_id
        print(f"Server {self.server_id} became leader")

        try:
            requests.post(
                f"{self.manager_url}/update_leader",
                json={"leader_port": self.port}
            )
        except Exception as e:
            print(f"Error notifying manager: {e}")

        # Start sending heartbeats
        self.heartbeat_thread = threading.Thread(target=self.send_heartbeats)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()

    def send_heartbeats(self):
        while self.state == ServerState.LEADER:
            message = {
                'type': 'HEARTBEAT',
                'term': self.current_term,
                'leader_id': self.server_id
            }
            for peer in self.peers:
                try:
                    self.udp_socket.sendto(json.dumps(message).encode(), ('localhost', peer))
                except Exception as e:
                    print(f"Error sending heartbeat to peer {peer}: {e}")
            time.sleep(0.05)  # Send heartbeats every 50ms

    def listen_udp(self):
        while True:
            try:
                data, addr = self.udp_socket.recvfrom(1024)
                message = json.loads(data.decode())

                if message['type'] == 'REQUEST_VOTE':
                    if message['term'] > self.current_term:
                        self.current_term = message['term']
                        self.state = ServerState.FOLLOWER
                        self.voted_for = message['candidate_id']
                        # Send vote
                        response = {
                            'type': 'VOTE',
                            'term': self.current_term,
                            'vote_granted': True
                        }
                        self.udp_socket.sendto(json.dumps(response).encode(), addr)

                elif message['type'] == 'VOTE':  # Add handling for VOTE messages
                    if (message['term'] == self.current_term and
                            self.state == ServerState.CANDIDATE and
                            message['vote_granted']):
                        self.votes_received += 1
                        print(f"Server {self.server_id} received vote. Total votes: {self.votes_received}")

                elif message['type'] == 'HEARTBEAT':
                    if message['term'] >= self.current_term:
                        self.current_term = message['term']
                        self.state = ServerState.FOLLOWER
                        self.leader_id = message['leader_id']
                        self.last_heartbeat = time.time()

            except Exception as e:
                print(f"Error in UDP listener: {e}")
