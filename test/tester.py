import os
import time
import mysql.connector
from shlex import split as splitsh
import subprocess
import ctypes, win32gui, win32process, win32api, win32con
from database.interface import connect, fetch_next_file, report_button

def tester(queue, conn_data, unique_info, file_extention, app_runtime):
    '''Get file from database, run it, lookup any buttons,
    send buttonname to DB. '''
    thread_id = queue.get()
    connection = connect(conn_data)
    if connection == None:
        print("Tester thread №", thread_id, "encountered" + err +"\n")
        connection.close()
        queue.task_done()
        return
    table_name = conn_data["table_name"]
    file_to_find = fetch_next_file(connection, table_name, file_extention)
    connection.commit()
    if len(file_to_find) == 0:
        #print(thread_id, " didn't fetch any file\n")
        connection.close()
        queue.task_done()
        return
    path_to_run = file_to_find["path"]
    md5 = file_to_find["md5"]
    button_name = _execute_file(path_to_run, app_runtime)
    file_to_find["description"] = button_name
    unique_info.append(file_to_find)
    report_success = False
    while not report_success:
        report_success = report_button(connection, table_name, md5, button_name)
        time.sleep(0.01) # repeat upload after pause
    print(file_to_find["path"], " tested.\n")
    connection.close()
    queue.task_done()

def _execute_file(path, app_runtime):
    ''' Starts file on provided path, searches for buttons with
    name in it for specified time.'''
    cmd = splitsh(path)
    try:
        proc = subprocess.Popen(cmd)
    except WindowsError as err:
        print (err.errno)
        if err.errno == 22:
            print(path, "No rights to run file.")
            test_result = "No rights to run file."
            return test_result
        else:
            print(err)
            return "Unhandled Popen exception"
    pid = proc.pid
    end_time = int(time.time() + app_runtime)
    time.sleep(0.5) # time for process to create window
    #print("search for process " + str(pid)+ "\n")
    app_hwnd = None
    btn_hwnd = None
    test_result = "Buttons not found"
    button_name = ""
    import pywintypes
    while (button_name == "") & (time.time() <= end_time):
        # either found button name or hit timelimit
        if app_hwnd == None:
            app_hwnd = _find_window_for_pid(pid)
        if app_hwnd != None:
            app_name = win32gui.GetWindowText(app_hwnd)
            #print("Name of app found: " + app_name + "\n")
            try:
                win32gui.SetActiveWindow(app_hwnd)
                btn_hwnd = _find_button_child(app_hwnd)
                #win32gui.FindWindowEx(app_hwnd, 0, "Button", None)
            except Exception as  err:
                #if err.errno == 1400:
                #print("window handler changed")
                button_name = "Unhandled button hwnd Exception"
                print(str(err))
                break
            #EnumChildWindow enumerates recursively while FindWindowEx does not.
            if btn_hwnd:
                button_name = win32gui.GetWindowText(btn_hwnd)
                # press button
                win32api.PostMessage(btn_hwnd, win32con.WM_LBUTTONDOWN, 0, 0)
                win32api.PostMessage(btn_hwnd, win32con.WM_LBUTTONUP, 0, 0)
                print("Name of button found: " + test_result + "\n")
    test_result = button_name
    if time.time() >= end_time:
        # Time exceeded. Mark file as "Trouble"
        test_result = "Trouble. No buttons found"
    #import pdb; pdb.set_trace()
    #pdb.set_trace()
    proc.kill()
    return test_result

def _find_button_child(parent_hwnd):
    ''' Recursively search provided window handler for child-handler
    with "Button" class, that has name. Gets parent window handler.
    Returns button window handler.'''
    button_hwnd = None
    def button_searcher(hwnd, _):
        nonlocal button_hwnd
        if win32gui.GetClassName(hwnd) != "Button":
            return True
        if win32gui.IsWindowVisible( hwnd ):
            length = win32gui.GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
            button_hwnd = hwnd
            if buff.value != "":
                #print(buff.value)
                return False
        return True
    try:
        win32gui.EnumChildWindows(parent_hwnd, button_searcher, None)
    except:
        #print("Find child exception")
        pass
    return button_hwnd

def _find_window_for_pid(pid):
    ''' Compare process ID with processes that currently is up
    to find window handler. Gets process ID. Returns handler.'''
    result = None
    def callback(hwnd, _):
        nonlocal result
        ctid, cpid = win32process.GetWindowThreadProcessId(hwnd)
        if cpid == pid:
            result = hwnd
            return False
        return True
    try:
        win32gui.EnumWindows(callback, None)
    except:
        #print("Find hwnd exception")
        pass
    return result
