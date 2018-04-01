# coding:utf-8
from params import *
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time
from bs4 import BeautifulSoup
import sys


class JDmaimiao(object):
    def __init__(self):
        # 计数
        self.refresh_count = 0
        # 新建浏览器驱动
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(20)
        # 有效任务
        self.valid_tasks = []

    def main(self, send_pipe, receive_pipe):
        self.login()
        self.clear_alert()
        self.set_task_filter()
        print(time.strftime('%H:%M:%S') + ': Finding task...')
        while 1:
            self.refresh()
            self.refresh_count += 1
            print('%s: Page refreshed %d times' % (time.strftime('%H:%M:%S'), self.refresh_count))
            if self.refresh_count % 50 == 0:
                msg = 'Page refreshed %d times' % self.refresh_count
                send_pipe.send(msg)
            if self.notify():
                print(time.strftime('%H:%M:%S') + ': Task found.')
                if self.auto_take_order(self.valid_tasks):
                    msg = 'Take order successfully. ' + 'Script is waiting for sleep time input within 60 seconds' + '(input 999 to end script).'
                    print(time.strftime('%H:%M:%S') + ':' + msg)
                    send_pipe.send(msg)
                # self.driver.execute_script('window.scrollTo(0, 700)')
                    time_in_minute = int(receive_pipe.recv())
                    if time_in_minute == 999:
                        self.driver.quit()
                        sys.exit()
                    print(time.strftime('%H:%M:%S') + ': Sleep %d minutes' % time_in_minute)
                    time.sleep(time_in_minute * 60)
                else:
                    msg = 'Fail to take order.'
                    print(time.strftime('%H:%M:%S') + ': ' + msg)
            time.sleep(20)


    def login(self):
        self.driver.get(login_url)
        self.driver.find_element_by_id(id_input_username).send_keys(username)
        self.driver.find_element_by_id(id_input_passwd).send_keys(passwd)
        self.driver.find_element_by_id(id_button_submit).click()

    def clear_alert(self):
        try:
            self.driver.find_element_by_class_name(class_a_known).click()
        except:
            pass

    def set_task_filter(self):
        self.driver.get(task_filter_url)

    def refresh(self):
        self.driver.find_element_by_class_name(class_a_refresh).click()

    def get_valid_task_number(self):
        return int(self.driver.page_source.count('qcrw taskTask'))

    def task_constructor(self, task_btns):
        # 根据找到的抢此任务按钮，构造任务，每个任务都为一个字典，包含任务的各个属性
        tasks = []
        for task in task_btns:
            temp = {}
            temp['taskItem'] = task.parent.parent
            temp['lang'] = task.get('lang')
            temp['coin'] = float(task.parent.find(attrs={'title': '完成任务后，您能获得的任务奖励，可兑换成RMB'}).span.string.strip())
            temp['money'] = float(task.parent.find(attrs={'title': '平台担保：此任务卖家已缴纳全额担保存款，接手可放心购买，任务完成后，买家平台账号自动获得相应存款'}).span.string.strip())
            temp['account_need'] = 0 if task.parent.parent.find(attrs={'class': 'BuyerJifen'}) is None else 1
            tasks.append(temp)
        return tasks

    def notify(self):
        if self.get_valid_task_number() > 0:
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            task_btns = soup.find_all(attrs={'class': 'qcrw taskTask'})
            tasks = self.task_constructor(task_btns)
            self.valid_tasks = tasks if len(tasks) < 3 else tasks[:3]
            # 去除有等级要求, 垫付金额大于500, 金币数小于5的任务
            # self.valid_tasks = [task for task in tasks if task['account_need'] == 0 and task['money'] < 500 and task['coin'] > 5]
            if len(self.valid_tasks) > 0:
                return True
        return False

    def auto_take_order(self, valid_tasks):
        # 对valid_tasks按照金币与垫付金额的比值进行递减排序
        valid_tasks.sort(key=lambda x: x['money'] / x['coin'])

        for task in valid_tasks:
            # 点击抢此任务
            self.driver.find_elements_by_css_selector('[lang=\"%s\"]' % task['lang'])[0].click()
            # 判断跳出来的div标签是否包含'当前任务金额超出您的垫付立反额度'
            div_text = self.driver.find_element_by_class_name(class_div_content).text
            if partial_confirm_content1 in div_text:
                self.driver.find_element_by_class_name(class_a_btn).click()
            # 判断跳出来的div标签是否包含'选择接此任务的买号'
            div_text = self.driver.find_element_by_class_name(class_div_content).text
            if partial_confirm_content2 in div_text:
                self.driver.find_element_by_class_name(class_a_btn).click()
            else:
                self.driver.find_element_by_class_name(class_a_btn).click()
            # 判断跳出来的div标签是否包含'您已经成功接手此任务'
            try:
                div_text = self.driver.find_element_by_class_name(class_div_content).text
                if partial_confirm_content3 in div_text:
                    self.driver.find_element_by_class_name(class_a_btn).click()
                    return True
                else:
                    self.driver.find_element_by_class_name(class_a_btn).click()
            except NoSuchElementException:
                pass
        return False


def main_jd(send_pipe, receive_pipe):
    try:
        jd = JDmaimiao()
        jd.main(send_pipe, receive_pipe)
    finally:
        print('jd fail')
        jd.driver.quit()
        sys.exit()


if __name__ == '__main__':
    jd = JDmaimiao()
    jd.main(None, None)
