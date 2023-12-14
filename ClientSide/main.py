"""
Author: Ido Karadi
Program Name: Cyber2.7
Desc: Server&Client sides of a 7 command server with a custom protocol
Date: 14/12/23
"""
import socket

IP = '127.0.0.1'
PORT = 1729
LENGTH_P = 8
SUPPORTED_COMMANDS = ['dirl(directory)', 'delt(file)', 'copy(source, destination)',
                      'exec(.exe file)', 'shot()', 'send()', 'exit()']
FORMAT = "Format: command~parameter~s# (no # needed unless on copy function)"
VALID_COMMANDS = ['dirl', 'delt', 'copy', 'exec', 'shot', 'send', 'exit']
ONE_PARAMETER = ['dirl', 'exec', 'delt']
TWO_PARAMETERS = ['copy']
NO_PARAMETERS = ['shot', 'send', 'exit']
BUFFER_SIZE = 2048

my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def main():
    """
    Client main function: connects to server and receives user input for server command + parameter. Can send infinite
    commands until 'exit'.
    """
    print(SUPPORTED_COMMANDS)
    print(FORMAT)
    try:
        my_socket.connect((IP, PORT))
        while True:
            client_command = input('Choose a command: ').lower()
            if client_command in VALID_COMMANDS:
                if client_command in ONE_PARAMETER:
                    client_parameter = input('Enter a parameter: ')
                    client_input = client_command + '~' + client_parameter
                elif client_command in TWO_PARAMETERS:
                    client_parameter = input('Enter a parameter: ')
                    client_parameter2 = input('Enter a second parameter: ')
                    client_input = client_command + '~' + client_parameter + '~' + client_parameter2 + '#'
                else:
                    client_input = client_command
            else:
                print("Invalid command. Please enter a valid command.")
                continue
            if client_command == 'send':
                file_path = 'server_image.jpg'
                my_socket.send(client_input.encode())
                try:
                    with open(file_path, "wb") as file:
                        while True:
                            img_chunk = my_socket.recv(BUFFER_SIZE)
                            if img_chunk.endswith(b'#'):
                                file.write(img_chunk[:-1])  # Exclude the '#' from the written data
                                break  # Exit loop when the delimiter '#' is received
                            file.write(img_chunk)
                        print('Image received.')
                except IOError as e:
                    print(f"Error:" + str(e))
            else:
                my_socket.send(client_input.encode())
                response = my_socket.recv(LENGTH_P).decode()
                response2 = ''
                while '#' not in response2:
                    response2_part = my_socket.recv(2048).decode()
                    response2 += response2_part
                    if not response2_part:
                        break
                    if '#' in response2_part:
                        break
                print('Length: ' + response + 'Content:  ' + response2)
                if client_input == 'exit':
                    break
    except socket.error as err:
        print('received socket error ' + str(err))
    finally:
        my_socket.close()


if __name__ == '__main__':
    main()
