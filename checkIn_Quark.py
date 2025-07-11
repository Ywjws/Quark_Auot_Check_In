import os 
import re 
import sys 
import requests 
import httpx
import re
import urllib.parse
import time
import os
import sys
from bs4 import BeautifulSoup

cookie_list = os.getenv("COOKIE_QUARK").split('\n|&&')
# 直接从环境变量获取配置
COOKIE = os.environ['TSDM_COOKIE']

# 替代 notify 功能
def send(title, message):
    print(f"{title}: {message}")

# 获取环境变量 
def get_env(): 
    # 判断 COOKIE_QUARK是否存在于环境变量 
    if "COOKIE_QUARK" in os.environ: 
        # 读取系统变量以 \n 或 && 分割变量 
        cookie_list = re.split('\n|&&', os.environ.get('COOKIE_QUARK')) 
    else: 
        # 标准日志输出 
        print('❌未添加COOKIE_QUARK变量') 
        send('夸克自动签到', '❌未添加COOKIE_QUARK变量') 
        # 脚本退出 
        sys.exit(0) 

    return cookie_list 

# 其他代码...

class Quark:
    '''
    Quark类封装了签到、领取签到奖励的方法
    '''
    def __init__(self, user_data):
        '''
        初始化方法
        :param user_data: 用户信息，用于后续的请求
        '''
        self.param = user_data

    def convert_bytes(self, b):
        '''
        将字节转换为 MB GB TB
        :param b: 字节数
        :return: 返回 MB GB TB
        '''
        units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = 0
        while b >= 1024 and i < len(units) - 1:
            b /= 1024
            i += 1
        return f"{b:.2f} {units[i]}"

    def get_growth_info(self):
        '''
        获取用户当前的签到信息
        :return: 返回一个字典，包含用户当前的签到信息
        '''
        url = "https://drive-m.quark.cn/1/clouddrive/capacity/growth/info"
        querystring = {
            "pr": "ucpro",
            "fr": "android",
            "kps": self.param.get('kps'),
            "sign": self.param.get('sign'),
            "vcode": self.param.get('vcode')
        }
        response = requests.get(url=url, params=querystring).json()
        #print(response)
        if response.get("data"):
            return response["data"]
        else:
            return False

    def get_growth_sign(self):
        '''
        获取用户当前的签到信息
        :return: 返回一个字典，包含用户当前的签到信息
        '''
        url = "https://drive-m.quark.cn/1/clouddrive/capacity/growth/sign"
        querystring = {
            "pr": "ucpro",
            "fr": "android",
            "kps": self.param.get('kps'),
            "sign": self.param.get('sign'),
            "vcode": self.param.get('vcode')
        }
        data = {"sign_cyclic": True}
        response = requests.post(url=url, json=data, params=querystring).json()
        #print(response)
        if response.get("data"):
            return True, response["data"]["sign_daily_reward"]
        else:
            return False, response["message"]

    def queryBalance(self):
        '''
        查询抽奖余额
        '''
        url = "https://coral2.quark.cn/currency/v1/queryBalance"
        querystring = {
            "moduleCode": "1f3563d38896438db994f118d4ff53cb",
            "kps": self.param.get('kps'),
        }
        response = requests.get(url=url, params=querystring).json()
        # print(response)
        if response.get("data"):
            return response["data"]["balance"]
        else:
            return response["msg"]

    def do_sign(self):
        '''
        执行签到任务
        :return: 返回一个字符串，包含签到结果
        '''
        log = ""
        # 每日领空间
        growth_info = self.get_growth_info()
        if growth_info:
            log += (
                f" {'88VIP' if growth_info['88VIP'] else '普通用户'} {self.param.get('user')}\n"
                f"💾 网盘总容量：{self.convert_bytes(growth_info['total_capacity'])}，"
                f"签到累计容量：")
            if "sign_reward" in growth_info['cap_composition']:
                log += f"{self.convert_bytes(growth_info['cap_composition']['sign_reward'])}\n"
            else:
                log += "0 MB\n"
            if growth_info["cap_sign"]["sign_daily"]:
                log += (
                    f"✅ 签到日志: 今日已签到+{self.convert_bytes(growth_info['cap_sign']['sign_daily_reward'])}，"
                    f"连签进度({growth_info['cap_sign']['sign_progress']}/{growth_info['cap_sign']['sign_target']})\n"
                )
            else:
                sign, sign_return = self.get_growth_sign()
                if sign:
                    log += (
                        f"✅ 执行签到: 今日签到+{self.convert_bytes(sign_return)}，"
                        f"连签进度({growth_info['cap_sign']['sign_progress'] + 1}/{growth_info['cap_sign']['sign_target']})\n"
                    )
    """日志报告函数"""
    print(f"【{title}】{message}")

def tsdm_check_in():
    log = ""
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Cookie": COOKIE,
        "Referer": "https://www.tsdm39.com/forum.php",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }

    with httpx.Client(headers=headers) as client:
        try:
            # 获得formhash
            response = client.get("https://www.tsdm39.com/forum.php")
            pattern = r'formhash=(.+?)"'
            match = re.search(pattern, response.text)
            if match:
                formhash_value = match.group(1)
                encoded_formhash = urllib.parse.quote(formhash_value)

                # 签到
                payload = {"formhash": encoded_formhash, "qdxq": "kx", "qdmode": "3", "todaysay": "", "fastreply": "1"}
                response = client.post(
                    "https://www.tsdm39.com/plugin.php?id=dsu_paulsign%3Asign&operation=qiandao&infloat=1&sign_as=1&inajax=1",
                    data=payload)
                
                if "签到成功" in response.text:
                    log = "✅ 签到成功"
                else:
                    log += f"❌ 签到异常: {sign_return}\n"
        else:
            log += f"❌ 签到异常: 获取成长信息失败\n"

                    log = "❌ 签到异常: 未知响应"
            else:
                log = "❌ 签到异常: 获取formhash失败"
        except Exception as e:
            log = f"❌ 签到异常: {str(e)}"
        
        send("签到结果", log)
        return log

def tsdm_work():
    log = ""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'cookie': COOKIE,
        'connection': 'Keep-Alive',
        'x-requested-with': 'XMLHttpRequest',
        'referer': 'https://www.tsdm39.net/plugin.php?id=np_cliworkdz:work',
        'content-type': 'application/x-www-form-urlencoded'
    }

    with httpx.Client(headers=headers) as client:
        try:
            # 查询是否可以打工
            response = client.get("https://www.tsdm39.com/plugin.php?id=np_cliworkdz%3Awork&inajax=1", headers=headers)
            pattern = r"您需要等待\d+小时\d+分钟\d+秒后即可进行。"
            match = re.search(pattern, response.text)
            if match:
                log = f"⏳ 打工冷却中: {match.group()}"
            else:
                # 必须连续6次！
                for i in range(6):
                    response = client.post("https://www.tsdm39.com/plugin.php?id=np_cliworkdz:work", 
                                        headers=headers, 
                                        data={"act": "clickad"})
                    time.sleep(3)

                # 获取奖励
                response = client.post("https://www.tsdm39.com/plugin.php?id=np_cliworkdz:work", 
                                    headers=headers, 
                                    data={"act": "getcre"})
                log = "✅ 打工完成"
        except Exception as e:
            log = f"❌ 打工异常: {str(e)}"
        
        send("打工结果", log)
        return log

def main():
    '''
    主函数
    :return: 返回一个字符串，包含签到结果
    '''
    msg = ""
    global cookie_quark
    cookie_quark = get_env()

    print("✅ 检测到共", len(cookie_quark), "个夸克账号\n")

    i = 0
    while i < len(cookie_quark):
        # 获取user_data参数
        user_data = {}  # 用户信息
        for a in cookie_quark[i].replace(" ", "").split(';'):
            if not a == '':
                user_data.update({a[0:a.index('=')]: a[a.index('=') + 1:]})
        # print(user_data)
        # 开始任务
        log = f"🙍🏻‍♂️ 第{i + 1}个账号"
        msg += log
        # 登录
        log = Quark(user_data).do_sign()
        msg += log + "\n"

        i += 1

    # print(msg)

def get_score():
    try:
        send('夸克自动签到', msg)
    except Exception as err:
        print('%s\n❌ 错误，请查看运行日志！' % err)

    return msg[:-1]

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": COOKIE,
            "Referer": "https://www.tsdm39.com/forum.php",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        }
        with httpx.Client(headers=headers) as client:
            response = client.get("https://www.tsdm39.com/home.php?mod=spacecp&ac=credit&showcredit=1")
            soup = BeautifulSoup(response.text, 'html.parser')
            ul_element = soup.find('ul', class_='creditl')
            li_element = ul_element.find('li', class_='xi1')
            angel_coins = li_element.get_text(strip=True).replace("天使币:", "").strip()
            return angel_coins
    except Exception as e:
        send("查询异常", f"❌ 获取天使币失败: {str(e)}")
        return "未知"

def run_checkin():
    checkin_log = tsdm_check_in()
    score = get_score()
    send("签到完成", f"{checkin_log} | 当前天使币: {score}")

def run_work():
    work_log = tsdm_work()
    score = get_score()
    send("打工完成", f"{work_log} | 当前天使币: {score}")

if __name__ == "__main__":
    print("----------夸克网盘开始签到----------")
    main()
    print("----------夸克网盘签到完毕----------")
    if len(sys.argv) > 1:
        if sys.argv[1] == "checkin":
            run_checkin()
        elif sys.argv[1] == "work":
            run_work()
        else:
            print("Invalid command. Use 'checkin' or 'work'")
    else:
        run_checkin()
        run_work()
