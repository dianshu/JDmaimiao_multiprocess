# coding:utf-8
import itchat
from http.client import RemoteDisconnected

def main_itchat(send_pipe, receive_pipe):
    @itchat.msg_register(itchat.content.TEXT, isFriendChat=True)
    def reply(msg):
        try:
            if msg.fromUserName == to:
                receive_pipe.send(int(msg.text))
                itchat.send('%s reveived' % msg.text, to)
        except RemoteDisconnected as e:
            print('RemoteDisconnected from reply')
            return
    print('Weichat start')
    itchat.auto_login(hotReload=True)
    to = itchat.search_friends(nickName=u'金牛')[0].userName
    itchat.run(blockThread=False)
    while 1:
        try:
            itchat.send(send_pipe.recv(), to)
        except RemoteDisconnected as e:
            print('RemoteDisconnected from send')
