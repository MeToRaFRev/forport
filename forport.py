#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
from difflib import get_close_matches

VALID_ACTIONS = ["list", "remove", "delete", "delete all"]

def forward_port(source_port, destination_port):
    os_name = platform.system()

    if os_name == "Windows":
        command = f'netsh interface portproxy add v4tov4 listenport={source_port} listenaddress=0.0.0.0 connectport={destination_port} connectaddress=127.0.0.1'
    elif os_name == "Linux":
        command = f'sudo iptables -t nat -A PREROUTING -p tcp --dport {source_port} -j REDIRECT --to-port {destination_port}'
    else:
        print(f"Unsupported OS: {os_name}")
        sys.exit(1)

    print(f"Running command: {command}")
    result = os.system(command)

    if result != 0:
        print(f"Failed to create port forwarding from {source_port} to {destination_port}.")
    else:
        print(f"Port forwarding from {source_port} to {destination_port} successfully created.")

def list_ports():
    os_name = platform.system()
    forwarding_rules = []

    if os_name == "Windows":
        command = 'netsh interface portproxy show all'
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        rules = result.stdout.strip().splitlines()

        # Parsing netsh output for port forwarding rules
        for line in rules:
            if line.startswith("Listen on IP"):
                continue  # Skip headers
            parts = line.split()
            if len(parts) >= 4 and parts[1].isdigit() and parts[3].isdigit():
                listen_port = parts[1]
                connect_port = parts[3]
                forwarding_rules.append((listen_port, connect_port))
    
    elif os_name == "Linux":
        command = 'sudo iptables -t nat -L PREROUTING --line-numbers'
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        rules = result.stdout.strip().splitlines()

        # Debugging iptables output
        for line in rules:
            if "REDIRECT" in line:
                parts = line.split()
                # print(f"Parts: {parts}")  # Debugging print
                source_port = None
                destination_port = None

                # Extract source port from 'tcp dpt:<port>'
                for part in parts:
                    if "dpt:" in part:
                        source_port = part.split("dpt:")[1]
                
                # Extract destination port from 'ports <port>' (last part)
                destination_port = parts[-1]  # Last element holds the destination port
                
                if source_port and destination_port:
                    # print(f"Source Port: {source_port}, Destination Port: {destination_port}")  # Debugging print
                    forwarding_rules.append((source_port, destination_port))
    
    else:
        print(f"Unsupported OS: {os_name}")
        sys.exit(1)

    if not forwarding_rules:
        print("No port forwarding rules found.")
    else:
        print("Port forwarding rules:")
        for i, rule in enumerate(forwarding_rules, 1):
            print(f"{i}. {rule[0]}->{rule[1]}")

    return forwarding_rules



def remove_port(index):
    os_name = platform.system()

    if os_name == "Windows":
        # Fetch the current forwarding rules
        forwarding_rules = list_ports()

        # Get the forwarding rule by index
        try:
            rule = forwarding_rules[int(index) - 1]
        except IndexError:
            print(f"Invalid index: {index}")
            sys.exit(1)

        listen_port, connect_port = rule

        # Use netsh to remove the forwarding rule
        command = f'netsh interface portproxy delete v4tov4 listenport={listen_port} listenaddress=0.0.0.0'
        print(f"Removing port forwarding rule: {listen_port}->{connect_port}")
        result = os.system(command)

        if result != 0:
            print(f"Failed to remove port forwarding rule with index {index}.")
        else:
            print(f"Successfully removed port forwarding rule: {listen_port}->{connect_port}.")
    
    elif os_name == "Linux":
        # On Linux, removing the port forwarding rule by its index
        command = f'sudo iptables -t nat -D PREROUTING {index}'
        result = os.system(command)

        if result != 0:
            print(f"Failed to remove port forwarding rule with index {index}.")
        else:
            print(f"Successfully removed port forwarding rule with index {index}.")
    else:
        print(f"Unsupported OS: {os_name}")
        sys.exit(1)

def remove_all():
    os_name = platform.system()

    if os_name == "Windows":
        # Fetch the current forwarding rules
        forwarding_rules = list_ports()

        for listen_port, _ in forwarding_rules:
            # Use netsh to remove each forwarding rule
            command = f'netsh interface portproxy delete v4tov4 listenport={listen_port} listenaddress=0.0.0.0'
            print(f"Removing port forwarding rule for port {listen_port}")
            result = os.system(command)
            if result != 0:
                print(f"Failed to remove port forwarding rule for port {listen_port}")
            else:
                print(f"Successfully removed port forwarding rule for port {listen_port}")

    elif os_name == "Linux":
        # Remove all iptables rules under PREROUTING
        command = 'sudo iptables -t nat -F PREROUTING'
        result = os.system(command)

        if result != 0:
            print(f"Failed to remove all port forwarding rules.")
        else:
            print(f"Successfully removed all port forwarding rules.")
    else:
        print(f"Unsupported OS: {os_name}")
        sys.exit(1)

def handle_port_range(source_ports, destination_ports):
    # Handling different combinations of source and destination ranges
    if len(source_ports) > 1 and len(destination_ports) == 1:
        # If there are multiple source ports and one destination port, forward all to the same destination
        for source_port in source_ports:
            forward_port(source_port, destination_ports[0])
    elif len(source_ports) == 1 and len(destination_ports) > 1:
        # If there is one source port and multiple destination ports, forward the same source to all destinations
        for destination_port in destination_ports:
            forward_port(source_ports[0], destination_port)
    elif len(source_ports) == len(destination_ports):
        # If both source and destination are ranges of the same length, forward each source to the corresponding destination
        for source_port, destination_port in zip(source_ports, destination_ports):
            forward_port(source_port, destination_port)
    else:
        print("Invalid range combination. Source and destination ranges must either have the same number of ports or one side must be a single port.")
        sys.exit(1)

def parse_port_range(port_str):
    if '-' in port_str:
        start, end = map(int, port_str.split('-'))
        return list(range(start, end + 1))
    else:
        return [int(port_str)]

def suggest_command(unknown_command):
    """Suggest a close match for an unknown command."""
    close_command = get_close_matches(unknown_command, VALID_ACTIONS, n=1)
    if close_command:
        print(f"Did you mean '{close_command[0]}'?")
    else:
        print("Available actions are: list, remove, delete, delete all")

def parse_and_run(args):
    if len(args) < 2:
        print("Usage: forport <source_port>:<destination_port> | list | delete <id> | delete all")
        sys.exit(1)

    action = args[1].lower()

    # Handle port forwarding directly as <source_port>:<destination_port>
    if ':' in action:
        ports = action.split(":")
        if len(ports) != 2:
            print("Invalid format. Usage: forport <source_port>:<destination_port>")
            sys.exit(1)
        try:
            source_ports = parse_port_range(ports[0])
            destination_ports = parse_port_range(ports[1])
        except ValueError:
            print("Ports must be valid integers or ranges.")
            sys.exit(1)
        handle_port_range(source_ports, destination_ports)
        return

    # Handle actions like list, remove, delete
    if action == "list":
        list_ports()
    elif action == "remove" or action == "delete":
        if len(args) == 3:
            if args[2].lower() == "all":
                remove_all()
            else:
                remove_port(args[2])
        else:
            print("Usage: forport delete <id> | delete all")
            sys.exit(1)
    else:
        suggest_command(action)

if __name__ == "__main__":
    parse_and_run(sys.argv)
