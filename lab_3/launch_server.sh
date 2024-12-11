#!/bin/bash


DEFAULT_PORT=5000
DEFAULT_SERVER_ID=1

# Help function
show_help() {
    echo "Usage: ./launch_server.sh [OPTIONS]"
    echo "Launch a single RAFT server instance"
    echo ""
    echo "Options:"
    echo "  -i, --id SERVER_ID    Server ID (default: 1)"
    echo "  -p, --port PORT       Server port (default: 5000)"
    echo "  -r, --peers PEERS     Comma-separated list of peer ports (e.g., 5001,5002)"
    echo "  -h, --help           Show this help message"
    echo ""
    echo "Example:"
    echo "  ./launch_server.sh -i 1 -p 5000 -r 5001,5002"
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--id)
            SERVER_ID="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -r|--peers)
            PEERS="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done


SERVER_ID=${SERVER_ID:-$DEFAULT_SERVER_ID}
PORT=${PORT:-$DEFAULT_PORT}
PEERS=${PEERS:-""}


export SERVER_ID
export PORT
export PEERS
export PYTHONUNBUFFERED=1

python app/app.py


#./launch_server.sh -i 1 -p 5000 -r 5001,5002
#./launch_server.sh -i 2 -p 5001 -r 5000,5002
#./launch_server.sh -i 3 -p 5002 -r 5000,5001