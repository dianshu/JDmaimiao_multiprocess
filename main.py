from JDmaimiao import main_jd
from WeiChat import main_itchat
import multiprocessing


if __name__ == '__main__':
    send_pipe = multiprocessing.Pipe()
    receive_pipe = multiprocessing.Pipe()
    weichat = multiprocessing.Process(target=main_itchat, args=(send_pipe[1], receive_pipe[1]), name='weichat')
    weichat.daemon = True
    jd_p = multiprocessing.Process(target=main_jd, args=(send_pipe[0], receive_pipe[0]), name='jd')
    jd_p.daemon = True
    while 1:
        try:
            weichat.start()
            jd_p.start()
            jd_p.join()
        except Exception:
            continue

