"""
Author: Ido Karadi
Program Name: Cyber2.7
Desc: Server&Client sides of a 7 command server with a custom protocol
Date: 14/12/23
"""
import socket
import glob
import os
import shutil
import subprocess
import pyautogui


COMMAND_P = 4
QUEUE_LEN = 1
PARAMETER_P = 1024
BUFFER_SIZE = 2048
DEL_SUCCESS = 'successfully deleted file'
EXE_SUCCESS = 'successfully opened file on server'
COPY_SUCCESS = 'successfully copied source to destination on server'
DIRL_FAILURE = "Directory doesn't exist"
SS_SAVED = 'Screenshot saved.'


def dir_list(directory):
    """
     Function dir_list:
     receives parameter directory and returns list of files in directory.
     input: directory
     return: list of files in directory
    """
    files_list = glob.glob(directory[1::] + "/*")
    return files_list


def delete(file):
    """
     Function delete:
     receives parameter file and deletes file and returns success message.
     input: file(path)
     return: success message
    """
    try:
        os.remove(file)
        return DEL_SUCCESS
    except os.error as err:
        return str(err)


def copy(source, dest):
    """
     Function copy:
     receives parameter source and another parameter dest and copies source onto dest and returns success message.
     input: source(path), dest(path)
     return: success message
    """
    try:
        shutil.copy(source, dest)
        return COPY_SUCCESS
    except (shutil.Error, FileNotFoundError) as err:
        return str(err)


def execute(path):
    """
         Function execute:
         receives parameter path and executes file on path and returns success message
         input: path(path)
         return: success message
        """
    try:
        subprocess.run(path)
        return EXE_SUCCESS
    except subprocess.SubprocessError as err:
        return str(err)


def take_ss():
    """
         Function take_ss:
         takes screenshot and returns success message
         input: none
         return: success message
    """
    image = pyautogui.screenshot()
    image.save('screen.jpg')
    return SS_SAVED


def main():
    """
    Function main:
    Runs the server on an infinite loop, receives command and parameters and sends response to client, ready for
    another client after disconnection.
    """
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        my_socket.bind(('0.0.0.0', 1729))
        my_socket.listen(QUEUE_LEN)
        while True:
            client_socket, client_address = my_socket.accept()
            try:
                while True:
                    request = client_socket.recv(COMMAND_P).decode()
                    if request == 'dirl':
                        parameter = client_socket.recv(PARAMETER_P).decode()
                        while '~' not in parameter:
                            parameter += client_socket.recv(PARAMETER_P).decode()
                        dlist = dir_list(parameter[2::])
                        print(parameter[1::])
                        print(dlist)
                        newlist = '|| '.join(dlist)
                        sendlist = str(len(newlist)).rjust(8, '0') + '~' + newlist + '#'
                        client_socket.send(sendlist.encode())
                    elif request == 'delt':
                        parameter = client_socket.recv(PARAMETER_P).decode()
                        while '~' not in parameter:
                            parameter += client_socket.recv(PARAMETER_P).decode()
                        send_string = delete(parameter[1::])
                        print(send_string)
                        send2_string = str(len(send_string)).rjust(8, '0') + '~' + send_string + '#'
                        client_socket.send(send2_string.encode())
                    elif request == 'copy':
                        data = ''
                        while True:
                            part = client_socket.recv(1024).decode()
                            data += part
                            if '#' in part:
                                break
                        parameters = data[:-1].split('~')[1:]
                        print(parameters)
                        if len(parameters) >= 2:
                            parameter1 = parameters[0]
                            parameter2 = parameters[1]
                            print(request)
                            print(parameter1)
                            print(parameter2)
                            send_string = copy(parameter1, parameter2)
                            print(send_string)
                            send2_string = str(len(send_string)).rjust(8, '0') + '~' + send_string + '#'
                            client_socket.send(send2_string.encode())
                        else:
                            client_socket.send("Insufficient parameters received for 'copy' command.#".encode())

                    elif request == 'exec':
                        eparameter = client_socket.recv(PARAMETER_P).decode()
                        while '~' not in eparameter:
                            eparameter += client_socket.recv(PARAMETER_P).decode()
                        esend_string = execute(eparameter[1::])
                        print(esend_string)
                        esend2_string = str(len(esend_string)).rjust(8, '0') + '~' + esend_string + '#'
                        client_socket.send(esend2_string.encode())
                    elif request == 'shot':
                        shot_string = take_ss()
                        shot2_string = str(len(shot_string)).rjust(8, '0') + '~' + shot_string + '#'
                        client_socket.send(shot2_string.encode())
                    elif request == 'send':
                        img_path = 'screen.jpg'
                        try:
                            with open(img_path, 'rb') as img:
                                img_data = img.read(BUFFER_SIZE)
                                while img_data:
                                    client_socket.send(img_data)
                                    img_data = img.read(BUFFER_SIZE)
                                client_socket.send(b'#')
                                print('Upload finished.')
                        except FileNotFoundError:
                            print(f"Error: File '{img_path}' not found.")
                    elif request == 'exit':
                        estring = str(len('Disconnected.')) + '~' + 'Disconnected' + '#'
                        client_socket.send(estring.encode())
                        break
                    else:
                        client_socket.send('not a valid command'.encode())

            except socket.error as err:
                print('received socket error on client socket' + str(err))
            finally:
                client_socket.close()
    except socket.error as err:
        print('received socket error on server socket' + str(err))
    finally:
        my_socket.close()


if __name__ == '__main__':
    assert delete('not a file') != DEL_SUCCESS
    assert execute('notepad.exe') == EXE_SUCCESS
    assert copy('not a file', 'not a file2') != COPY_SUCCESS
    assert take_ss() == SS_SAVED
    delete('screen.jpg')
    main()
