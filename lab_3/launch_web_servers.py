# launch_servers.py
import subprocess
import sys
import time
import os
import signal
import threading

def log_output(process, server_id):
    # Capture both stdout and stderr
    for line in iter(process.stdout.readline, b''):
        print(f"[Server {server_id}] {line.strip()}")
    for line in iter(process.stderr.readline, b''):
        print(f"[Server {server_id} ERROR] {line.strip()}")
    process.stdout.close()
    process.stderr.close()

def shutdown_gracefully(processes):
    print("\nShutting down all servers gracefully...")
    for process in processes:
        if process.poll() is None:  # If still running
            process.send_signal(signal.SIGINT)  # Send SIGINT for graceful shutdown

    for process in processes:
        process.wait()

    print("All servers have been stopped.")

def launch_servers(num_servers=3, base_port=5000):
    processes = []

    try:
        print("Launching RAFT web servers...")
        for i in range(num_servers):
            server_id = i + 1
            port = base_port + i

            peers = [base_port + j for j in range(num_servers) if j != i]
            peers_str = ",".join(map(str, peers))

            env = os.environ.copy()
            env.update({
                'SERVER_ID': str(server_id),
                'PORT': str(port),
                'PEERS': peers_str,
                'PYTHONUNBUFFERED': '1',
            })

            process = subprocess.Popen(
                [sys.executable, 'app/app.py'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            processes.append(process)
            print(f"Started server {server_id} on port {port} with peers: {peers_str}")
            time.sleep(1)

            log_thread = threading.Thread(target=log_output, args=(process, server_id))
            log_thread.start()
            time.sleep(1)
        print("\nAll servers are running. Press Ctrl+C to stop all servers.\n")

        while True:
            for i, process in enumerate(processes):
                if process.poll() is not None:
                        print(f"Server {i+1} has stopped unexpectedly!")
            time.sleep(1)

    except KeyboardInterrupt:
        shutdown_gracefully(processes)

if __name__ == "__main__":
    # You can specify the number of servers as a command line argument
    num_servers = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    launch_servers(num_servers)