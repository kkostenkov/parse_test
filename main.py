import threading
from queue import Queue
import time
import database.interface as db
from search import cat_search
from test import tester
from report import emailer, filemaker
from settings import CONN_SETTINGS, SEARCHPATH, TESTING_THREADS_ALLOWED, \
                     EXTENTION_TO_FIND, ALLOWED_APP_RUNTIME, MAIL_SETTINGS, \
                     DB_WATCHDOG_TIME

conn_data = CONN_SETTINGS.copy()
unique_info = []
size_of_executables = []

def start_search(test_continues, size_of_executables):
    """Composes catalog tree and dynamically uploads it to database.
    Calculates total size of files with specified extentions."""
    connection = db.connect(conn_data)
    print('Preparing database...\n')
    db.prepare(connection, conn_data["database"], conn_data["table_name"])
    print('Composing catalog tree...\n')
    cat_search.compose_tree(connection, conn_data["table_name"], SEARCHPATH)
    print('Tree composed and loaded to database.\n')
    print('Calculating total size of searched files...\n')
    size_of_executables.append(db.get_total_size(connection, \
                                                 conn_data["table_name"],
                                                 EXTENTION_TO_FIND))
    print("Calculated.\n start_search() finished working\n ")
    connection.close()
    test_continues.get()
    test_continues.task_done()

def start_testing(unique_info, test_continues):
    """Multithreaded testing of files fetched from database.
    Reports first buttons found. Composes list of unique files with
    specified extentions."""
    worker_threads = Queue(TESTING_THREADS_ALLOWED)
    print("starting ", TESTING_THREADS_ALLOWED, " threads\n")
    test_thread_id = 0
    all_files_tested = False
    while time.time() - db.time_of_update[0] < DB_WATCHDOG_TIME \
           and (not all_files_tested) :
        """ Spawn threads to fetch, test files and update database until
        all files uploaded to DB and tested or no changes happened to DB
        for DB_WATCHDOG_TIME seconds."""
        print(time.time() - db.time_of_update[0])
        if worker_threads.qsize() < TESTING_THREADS_ALLOWED:
            worker_threads.put(test_thread_id)
            worker = threading.Thread(target=tester.tester, \
                                      args=(worker_threads, \
                                      conn_data, \
                                      unique_info,
                                      EXTENTION_TO_FIND,
                                      ALLOWED_APP_RUNTIME
                                      ))
            worker.setDaemon(True)
            worker.start()
            test_thread_id += 1
            time.sleep(0.01)
            if test_continues.qsize() < 2: #  tree composed and uploaded
                all_files_tested = db.check_test_completion(conn_data,
                                                        EXTENTION_TO_FIND)
    print ("Testing thread waiting for all worker-threads to complete\n")
    worker_threads.join()
    print ("Testing Thread Checked all unique ",EXTENTION_TO_FIND, " files\n")
    test_continues.get()
    test_continues.task_done()

# start of first thread
test_continues = Queue()
test_continues.put("token")
threading.Thread(target=start_search, \
                 args=(test_continues, size_of_executables)).start()
#start of second thread
test_continues.put("token")
threading.Thread(target=start_testing, \
                 args=(unique_info, test_continues)).start()
print("Main is waiting for start_search() and start_testing() to complete.\n")
test_continues.join()
print("Main thread unlocked. Composing report.\n")

html_text =  filemaker.list_to_file(unique_info, size_of_executables.pop())
emailer.send_email(html_text, MAIL_SETTINGS)
