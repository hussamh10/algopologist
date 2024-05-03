import socket
import uuid
import core.constants as constants

def request_id(server_address, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Connecting to server at {server_address}:{server_port}...")
    try:
        client_socket.connect((server_address, server_port))
        assigned_id = client_socket.recv(1024).decode()  # Receive the response (ID) from the server
        print(f"Received assigned ID: {assigned_id}")
    except Exception as e:
        print(f"Error connecting to the server: {e}")
    finally:
        client_socket.close()

    return assigned_id

def getId():
    SERVER_ADDRESS = 'toutatis.cs.uiowa.edu' 
    SERVER_PORT = constants.SERVER_PORT
    id = request_id_mac(SERVER_ADDRESS, SERVER_PORT)
    print(f"Assigned ID: {id}")
    return id

def request_id_mac(server_address, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Connecting to server at {server_address}:{server_port}...")
    try:
        client_socket.connect((server_address, server_port))
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)][::-1])
        print(f"Sending MAC address: {mac_address}")
        client_socket.send(mac_address.encode())
        assigned_id = client_socket.recv(1024).decode()  # Receive the response (ID) from the server
        print(f"Received assigned ID: {assigned_id}")
    except Exception as e:
        print(f"Error connecting to the server: {e}")
    finally:
        client_socket.close()

    return assigned_id