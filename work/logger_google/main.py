import time
import sys
# print(sys.path)

from logger import ProcessManager

def do_basic_operations():
    def poll(process_manager: ProcessManager):
        poll_time = time.time()
        res = process_manager.poll()
        print(f"Time: {poll_time}, pulled process:: {res}")


    def no_process_added():
        process_manager = ProcessManager()
        poll(process_manager)
        poll(process_manager)

    def two_process_ended_in_same_order():
        process_manager = ProcessManager()
        process_manager.start(pid=1)
        process_manager.start(pid=2)
        time.sleep(2)
        poll(process_manager=process_manager)
        poll(process_manager=process_manager)

        process_manager.end(2)

        poll(process_manager=process_manager)
        poll(process_manager=process_manager)

        process_manager.end(1)

        poll(process_manager=process_manager)
        poll(process_manager=process_manager)
        poll(process_manager=process_manager)
        poll(process_manager=process_manager)

        # TODO

    # no_process_added()
    two_process_ended_in_same_order()



def run_logger():
    do_basic_operations()

if __name__ == "__main__":
    run_logger()
