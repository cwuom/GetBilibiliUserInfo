"""
bilibili用户信息爬取demo
只需要一个回车我要TA的所有信息！
by - im-cwuom
"""

import os
import random

import requests
import json
import time
import datetime
import logging
import http.client
import traceback

from wordcloud import WordCloud

http.client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig(filename='runlog.log', filemode='a+', level=logging.DEBUG)
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

CookiesAutocheck = True  # 启用cookies自动检测

# https://workers.vrp.moe/api/bilibili/user-info/UID
# https://workers.vrp.moe/api/bilibili/famous-fans/473400804

f = 0  # open temp

__version__ = "1.0b"  # version

user_agent_list = [
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) Gecko/20100101 Firefox/61.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",
]

headers = {'User-Agent': random.choice(user_agent_list)}

ef = open("runlog.log", "a+", encoding="utf-8")


def Major_err_log():
    ef.write("\n\n=========== Major_err ===========\n")
    ef.write(f"[*{get_date()}*] {traceback.format_exc()}\n")
    ef.write("=================================\n")


def err_log():
    ef.write(f"[{get_date()}*NormalErr] {traceback.format_exc()}\n")


# 输出分割线
def print_long_line(title="", no_title=False, longer=False, enter=False):
    """
    :param title: 标题
    :param no_title: 无标题模式，直接输出分割线
    :param longer: 更长的分割线
    :param enter: 是否在前面加上换行符
    :return:
    """
    global f
    if enter:
        print("\n")
        f.write("\n\n")

    if longer:
        print(f"============================ {title} ============================\n")
        f.write(f"============================ {title} ============================\n\n")
    elif no_title:
        print("========================================")
        f.write("========================================\n")
    else:
        print(f"================== {title} ==================")
        f.write(f"================== {title} ==================\n")


# 输出内容并同步输出到文件中
def output(msg):
    global f
    print(msg)
    f.write(str(msg) + "\n")


# 请求API时遇到问题
def get_err(msg="[E] 在Get API时遇到致命错误! 输入回车(Enter)/q 强制继续/直接退出"):
    command = input(msg)
    if command == "q":
        print("[STOP] 运行终止.. 用户取消了操作。")
        time.sleep(3)
        exit(0)
    else:
        return 0


# 解析并保存弹幕词云
def save_danmu_wordcloud(msg_list, name, mid):
    """
    :param msg_list: 弹幕列表
    :param name: 记录者昵称
    :param mid: 记录者UID
    :return:
    """
    result = ""
    for t in msg_list:
        result = result + " " + t

    print("[-]", result)
    try:
        wordcloud = WordCloud(background_color="white",
                              width=4000,
                              height=3000,
                              max_words=20000,
                              max_font_size=200,
                              contour_width=4,
                              contour_color='steelblue',
                              font_path="PingFang-Bold_0.ttf"
                              ).generate(result)
        wordcloud.to_file(f'wordcloud_data\\WordCloud_{name}_{mid}.png')
    except:
        err_log()
        print("[E] wordcloud 抛出了异常，请检查用户发言数量是否足以构成词云？")


# 将字符串cookies转换为字典
def convert_cookies_to_dict(cookies):
    cookies = dict([l.split("=", 1) for l in cookies.split("; ")])
    return cookies


# 更新cookies
def update_cookies(err_msg, tips, tips2):
    """
    :param err_msg: 错误信息
    :param tips: [input]提示
    :param tips2: [=]备用提示
    :return:
    """
    print("[E]", err_msg)
    if tips2 != "":
        print("[=]", tips2)
    new_cookies = input(f"{tips}> ")
    if new_cookies == "!c":
        print("[-] no change...")
        return -1
    with open("cookies.txt", "w") as w:
        new_cookies = w.write(new_cookies)
    return new_cookies


# ==========================================


# 获取日期
def get_date():
    curr_time = datetime.datetime.now()
    time_str = curr_time.strftime("%Y-%m-%d %H:%M:%S")
    return time_str


# ==========================================

# 输出主页信息 包含大会员，播放量，直播间等数据，顺便把请求和解析工作一并做了
def output_space_data(mid):
    global cookies
    while True:
        try:
            with open("cookies.txt", "r") as r:
                cookies = r.read()
            cookies = convert_cookies_to_dict(cookies)
            # https://api.bilibili.com/x/space/upstat?mid=102570170
            print("[/] Getting view data...")
            views = requests.get(f"https://api.bilibili.com/x/space/upstat?mid={mid}", cookies=cookies, headers=headers)
            print("[/] Getting vip data...")
            spaceInfo = requests.get(f"https://api.bilibili.com/x/space/acc/info?mid={mid}", cookies=cookies,
                                     headers=headers).text.replace(
                """{"code":-509,"message":"请求过于频繁，请稍后再试","ttl":1}""", "")

            try:
                views_data = json.loads(views.text)["data"]
                archive_view = views_data["archive"]["view"]
                article_view = views_data["article"]["view"]
            except:
                err_log()

                archive_view = "无"
                article_view = "无"

            space_data = json.loads(spaceInfo)["data"]
            vip_info = space_data["vip"]
            vip_due_date = vip_info["due_date"]
            vip_status_list = ["无", "有"]
            """
            0：无
            1：有
            """
            vip_status = vip_status_list[vip_info["status"]]

            vip_type_list = ["无会员", "月大会员", "年度及以上大会员"]
            """
            0：无
            1：月大会员
            2：年度及以上大会员
            """
            vip_type = vip_type_list[vip_info["type"]]

            tv_vip_status = vip_info["tv_vip_status"]
            if tv_vip_status == 0:
                tv_vip_status = "未开通电视大会员"
            else:
                tv_vip_status = "开通电视大会员"
            """
            1：月度大会员
            3：年度大会员
            7：十年大会员
            15：百年大会员
            """
            vip_role = vip_info["role"]
            if vip_role == 1:
                vip_role = "月度大会员"
            elif vip_role == 3:
                vip_role = "年度大会员"
            elif vip_role == 7:
                vip_role = "十年大会员"
            elif vip_role == 15:
                vip_role = "百年大会员"
            else:
                vip_role = "未知"

            print("[/] Getting live data...")
            try:
                live_room_info = space_data["live_room"]
                """
                0：无房间
                1：有房间
                """
                roomStatus = live_room_info["roomStatus"]
                if roomStatus == 1:
                    """
                    0：未开播
                    1：直播中
                    """
                    liveStatusList = ["未开播", "直播中"]
                    liveStatus = liveStatusList[live_room_info["liveStatus"]]
                    live_url = live_room_info["url"]
                    live_title = live_room_info["title"]
                    live_cover = live_room_info["cover"]
                    live_roomid = live_room_info["roomid"]
                    """
                    0：未轮播
                    1：轮播
                    """
                    live_roundStatusList = ["未轮播", "轮播"]
                    live_roundStatus = live_roundStatusList[live_room_info["roundStatus"]]
                    roomStatus = "有"
                else:
                    liveStatus = "无"
                    live_url = "无"
                    live_title = "无"
                    live_cover = "无"
                    live_roomid = "无"
                    live_roundStatus = "无"
                    roomStatus = "无"

            except:
                err_log()
                liveStatus = "无"
                live_url = "无"
                live_title = "无"
                live_cover = "无"
                live_roomid = "无"
                live_roundStatus = "无"
                roomStatus = "无"

            break
        except:
            Major_err_log()
            cookies = update_cookies("Something went wrong! "
                                     "please update your cookies or check your network setting...",
                                     "",
                                     "获取用户信息时遇到问题，你可以在此处更新你的cookies。"
                                     "若cookies没有问题，"
                                     "可输入'!c'进行重试或检查您的网络设置！")

    likes = views_data["likes"]
    timeArray = time.localtime(vip_due_date / 1000)

    print_long_line("View", enter=True)
    output(f"[视频总浏览] {archive_view}次")
    output(f"[文章总浏览] {article_view}次")
    output(f"[总播放] {article_view + archive_view}次")
    output(f"[总被赞数] {likes}个")
    try:
        output(f"[被赞率] {(likes / (article_view + archive_view)) * 100}%")
    except:
        err_log()
    print_long_line("VIP INFO")
    output(f"[会员状态] {vip_status}")
    output(f"[会员类型] {vip_type}")
    output(f"[到期时间] {time.strftime('%Y-%m-%d %H:%M:%S', timeArray)}")
    output(f"[电视大会员状态] {tv_vip_status}")
    output(f"[大会员角色] {vip_role}")

    print_long_line("Live INFO")
    output(f"[是否有房间] {roomStatus}")
    output(f"[开播状态] {liveStatus}")
    output(f"[直播间URL] {live_url}")
    output(f"[直播间标题] {live_title}")
    output(f"[直播间封面] {live_cover}")
    output(f"[大会员角色] {vip_role}")
    output(f"[直播间ID] {live_roomid}")
    output(f"[是否轮播] {live_roundStatus}")

    # 返回cookies，后续可能需要用到
    return cookies


# ==========================================

# 解析用户信息
def load_UserInfo(data):
    name = data["card"]["name"]  # 昵称
    sex = data["card"]["sex"]  # 性别
    rank = data["card"]["rank"]  # ..
    face = data["card"]["face"]  # 头像链接
    coins = data["card"]["coins"]  # 硬币数量
    DisplayRank = data["card"]["DisplayRank"]  # ..
    regtime = data["card"]["regtime"]  # 注册时间，时间戳, s
    birthday = data["card"]["birthday"]  # 生日
    sign = data["card"]["sign"]  # 个性签名
    fans = data["card"]["fans"]  # 粉丝数量
    friend = data["card"]["friend"]  # 关注数

    current_exp = data["card"]["level_info"]["current_exp"]  # 当前经验
    next_exp = data["card"]["level_info"]["next_exp"]  # 下一级经验所需(LV6为-1)
    current_level = data["card"]["level_info"]["current_level"]  # 当前等级
    current_min = data["card"]["level_info"]["current_min"]  # 当前等级所需

    pendant = data["card"]["pendant"]["pid"]  # 挂件PID
    pendant_name = data["card"]["pendant"]["name"]  # 挂件名称
    pendant_image = data["card"]["pendant"]["image"]  # 挂件图片链接

    timeArray = time.localtime(regtime)  # 注册时间，%Y-%m-%d %H:%M:%S
    timeArray = time.strftime('%Y-%m-%d %H:%M:%S', timeArray)

    return {"name": name, "sex": sex, "rank": rank, "face": face, "coins": coins,
            "DisplayRank": DisplayRank, "regtime": timeArray,
            "birthday": birthday, "sign": sign, "fans": fans, "friend": friend,
            "current_exp": current_exp, "next_exp": next_exp, "current_level": current_level,
            "current_min": current_min, "pendant": pendant, "pendant_name": pendant_name,
            "pendant_image": pendant_image}


# 解析直播间访问数据
def load_visit_data(live_data):
    print("[/] Loading data...")
    watch_num = len(live_data)
    watch_list = []
    for l in live_data:
        watch_list.append(f"UID:{l['uId']} - name:{l['name']}")

    # 通过从大到小排列所有数据
    watch_list_dict = dict([[i, watch_list.count(i)] for i in watch_list])
    watch_list_sorted = sorted(watch_list_dict.items(), reverse=True, key=lambda s: s[1])
    print("[!]", watch_list_sorted)

    return watch_num, watch_list_sorted


# 解析弹幕数据
def load_danmu_data(data_list):
    # 初始化所有列表
    show_list_danmu = []
    msg_list_danmu = []

    visit_list_danmu = []
    gift_list_danmu = []

    message = []
    gifts_danmu = []

    for data_danmu in data_list:
        data_danmu = json.loads(data_danmu)
        r = data_danmu["data"]["data"]
        for data2 in r:
            danmus = data2["danmakus"]
            channel = data2["channel"]
            for danmu in danmus:
                if danmu["type"] == 0:  # 发言事件
                    message.append(f"{channel['name']} - {channel['uId']}")
                    # 记录发言数据，便于生成词云图
                    msg_list_danmu.append(danmu['message'])
                    timeArray_danmu = time.localtime(danmu["sendDate"] / 1000)  # 格式化TIME

                    # 同上，便于输出
                    show_list_danmu.append(
                        f"发言: {danmu['message']}\n发送到{channel['name']} - {channel['uId']}\n发言时间: {time.strftime('%Y-%m-%d %H:%M:%S', timeArray_danmu)}")
                elif danmu["type"] == 4:  # 进入直播间事件
                    timeArray_danmu = time.localtime(danmu["sendDate"] / 1000)  # 同上
                    # 记录进入事件便于输出
                    visit_list_danmu.append(
                        f"访问主播ID: {channel['name']} - {channel['uId']}\n进入直播间日期: {time.strftime('%Y-%m-%d %H:%M:%S', timeArray_danmu)}")
                elif danmu["type"] == 1:  # 送礼事件
                    # 累加数据，便于统计和输出
                    gifts_danmu.append(f"{channel['name']} - {channel['uId']}")
                    gift_list_danmu.append(
                        f"主播ID{channel['name']} - {channel['uId']}\n送礼日期: {danmu['sendDate']}\n礼物内容: {danmu['message']}")

    return {"show_list_danmu": show_list_danmu, "msg_list_danmu": msg_list_danmu, "visit_list_danmu": visit_list_danmu,
            "gift_list_danmu": gift_list_danmu, "message": message, "gifts_danmu": gifts_danmu}


# ==========================================


# 获取直播间事件
def get_live_data():
    while True:
        try:
            live_data = requests.get(f"https://ukamnads.icu/api/search/user/channel?uid={mid}", headers=headers)
            return live_data
        except:
            Major_err_log()
            get_err()
            continue


# 获取与此用户有关的弹幕库
def get_danmu_data():
    pn = 0
    data_list = []

    while True:
        try:
            res = requests.get(f"https://ukamnads.icu/api/search/user/detail?uid={mid}&pagesize=100&pagenum={pn}")
            try:
                json.loads(res.text)["data"]["data"]
            except:
                err_log()
                break

            print("[Getting] pn =", pn)
            data_list.append(res.text)
            pn += 1
        except Exception as e:
            print("[E]", e)
            get_err()
            continue

    return data_list


# 获取用户信息（请求过多会无法访问）
def get_UserInfo():
    int(mid)  # 检测是否为整数
    # 获取用户数据
    userInfo = requests.get(f"https://workers.vrp.moe/api/bilibili/user-info/{mid}",
                            headers={'User-Agent': random.choice(user_agent_list)})
    # userInfo = """{"ts":1683812730,"code":0,"card":{"mid":"114514","name":"田所こうじ","approve":false,"sex":"保密","rank":"10000","face":"http://i1.hdslb.com/bfs/face/875eb66bb952f16afa9634081a820dea8e3fac96.jpg","coins":3920,"DisplayRank":"10000","regtime":1301713382,"spacesta":0,"place":"","birthday":"1919-08-10","sign":"？！","description":"","article":0,"attentions":[454765848,1955897084,382651856,476720460,1409863611,174501086,9617619,50329118,401742377,161775300,9429196,207704,888797,7676631,11357018,1537722,905975,367238,395],"fans":44847,"friend":19,"attention":19,"level_info":{"next_exp":-1,"current_level":6,"current_min":28800,"current_exp":35440},"pendant":{"pid":0,"name":"","image":"","expire":0},"official_verify":{"type":-1,"desc":""}}}"""

    # 获取此用户的知名粉丝
    famous_fans = requests.get(f"https://workers.vrp.moe/api/bilibili/famous-fans/{mid}",
                               headers={'User-Agent': random.choice(user_agent_list)})
    # famous_fans = """[{"name":"宵刑星-","mid":2087877804,"face":"https://i0.hdslb.com/bfs/face/27a753fe0844514874aad07588a07b14d981990d.jpg","fans":304367},{"name":"mc-末影小黑","mid":69720889,"face":"https://i1.hdslb.com/bfs/face/ddab29b7e5978cf98b1d2bd7400b6b63f28be4e6.jpg","fans":159873},{"name":"木下下下下下下下","mid":35239580,"face":"https://i2.hdslb.com/bfs/face/a3514187beba71aefcd4109f75992db4643d4fac.jpg","fans":98382},{"name":"来点然能量","mid":2135171763,"face":"https://i0.hdslb.com/bfs/face/5929871c359a859bbb5dae12b69bf217a836f022.jpg","fans":69419},{"name":"决心_Determination","mid":53291709,"face":"https://i0.hdslb.com/bfs/face/0d0992777f49793e8025c1f5db7e42e11ee96f16.jpg","fans":57958},{"name":"阿毛带你买橘子","mid":21310180,"face":"https://i1.hdslb.com/bfs/face/05438a7ac2881cedb313f0cdfb4094b7c3a3ea34.jpg","fans":55000},{"name":"无奈的甜瓜","mid":1321009337,"face":"http://i2.hdslb.com/bfs/face/4c39fe9655ed8e1544f265fc0260fa2fcf2c37de.jpg","fans":39465},{"name":"决心jx","mid":323900921,"face":"https://i2.hdslb.com/bfs/face/f15c12285aed6af82b5e3061ac5121037ff67414.jpg","fans":39402},{"name":"空条kujo_","mid":352738858,"face":"https://i1.hdslb.com/bfs/face/9600a1cdf9f2e256696d4244d53b6bb5ade9633e.jpg","fans":38974},{"name":"一号铁人粉","mid":294445293,"face":"https://i0.hdslb.com/bfs/face/e230cfd34211b70452dcb2db6007777a48a5424c.jpg","fans":35651},{"name":"A志坤","mid":294624876,"face":"http://i0.hdslb.com/bfs/face/af3ffb9fe4b8a95d09c80473000e303a0a7587a3.jpg","fans":32165},{"name":"黑木白bai","mid":503314683,"face":"https://i0.hdslb.com/bfs/face/4894183cbb1bc57bc04d361b05ad4c5a72a1512d.jpg","fans":29787},{"name":"零明","mid":3154865,"face":"https://i2.hdslb.com/bfs/face/ea9afa46521b5d790b194292906616fd6684c087.jpg","fans":25764},{"name":"我肯定是lsx","mid":486108822,"face":"https://i0.hdslb.com/bfs/face/65e3b590feeb1992984fecf304b3298648b33143.jpg","fans":25455},{"name":"CR训练师","mid":286572267,"face":"https://i0.hdslb.com/bfs/face/4c3fde9ede45aa9c998cb54687f09be88a69cc2e.jpg","fans":23095},{"name":"陨落之弓","mid":596105030,"face":"https://i2.hdslb.com/bfs/face/bfab9b09ef876294bcf3cb867ef8f3ad498d830d.jpg","fans":22831},{"name":"蜘蛛鸭","mid":38914323,"face":"https://i0.hdslb.com/bfs/face/6406fc563094803fb01f6363f6d35358dc1ac3e5.jpg","fans":20741},{"name":"戴夫邻居史蒂夫DFsteve","mid":381681555,"face":"https://i0.hdslb.com/bfs/face/aa51dd900a85a69ad3244cba7e9ce67fa21a066c.webp","fans":20624},{"name":"冬雨无痕","mid":913173,"face":"https://i0.hdslb.com/bfs/face/5ecb7527dd153a50207a346a608834335e95a4ec.gif","fans":19461},{"name":"取个难听de名字真难","mid":397463553,"face":"http://i0.hdslb.com/bfs/face/0d03998daf472ef9a1facc609fc6f008fe71087c.jpg","fans":17393}]"""

    data = json.loads(userInfo.text)  # 解析数据
    # data = json.loads(userInfo)

    print("[OK]", data)

    return data, famous_fans


def get_video_info(mid, headers, cookies):
    title_list = []  # 存放标题
    description_list = []  # 存放简介
    # https://api.bilibili.com/x/space/arc/search?mid=686127&order=click&ps=50
    res_list = []
    for p in range(3):
        try:
            print(f"[Getting] pn={p}")
            res = requests.get(f"https://api.bilibili.com/x/space/arc/search?mid={mid}&order=click&ps=50&pn={p + 1}",
                               headers=headers, cookies=cookies).text
            res_list.append(res.replace("""{"code":-509,"message":"请求过于频繁，请稍后再试","ttl":1}""", ""))
            for res in res_list:
                # print(res)
                data = json.loads(res)["data"]["list"]
                video_data = data["vlist"]
                for video in video_data:
                    title_list.append(video["title"])
                    description_list.append(video["description"])
        except:
            err_log()
            print(f"[Getting] Over, Got {len(res_list)} pages")
            break

    print("[title_list]", title_list)
    print("[description_list]", description_list)

    return title_list, description_list


def makedirs(folder):
    if not os.path.exists(folder):  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(folder)
        print(f"[{folder}] created!")


# ============================================


if __name__ == '__main__':
    print(
        "========================================\n"
        f"GetBilibiliUserInfo - {__version__}\n"
        "github > https://github.com/cwuom/GetBilibiliUserInfo\n"
        "bilibili@im-cwuom > https://space.bilibili.com/473400804\n"
        "========================================")

    while True:
        if CookiesAutocheck:
            # 检查COOKIES
            try:
                with open("cookies.txt", "r") as r:
                    cookies = r.read()
            except:
                Major_err_log()
                cookies = update_cookies("'cookies.txt' not found!", "cookies",
                                         "please input your cookies first and try again...")

            try:
                cookies = convert_cookies_to_dict(cookies)

                check_cookie = requests.get("https://api.bilibili.com/x/space/upstat?mid=102570170", cookies=cookies,
                                            headers=headers).text
                if check_cookie == """{"code":0,"message":"0","ttl":1,"data":{}}""":
                    cookies = update_cookies("Something went wrong, please update your cookies....", "cookies", "")
                    continue
            except:
                Major_err_log()
                cookies = update_cookies("Something went wrong, please check your cookies or input new cookies here!",
                                         "cookies", "")
                continue

        CookiesAutocheck = False  # 关闭cookies审查，避免重复

        # 创建必要文件夹
        makedirs("datas")
        makedirs("gpt_datas")
        makedirs("wordcloud_data")
        try:
            mid = input("\nmid> ")
            if mid == "exit":
                exit(0)  # 直接退出

            print("[/] Getting info, please wait...")
            all_data = get_UserInfo()
            data, famous_fans = all_data[0], all_data[1]

            print("[!] Loading data...")

            print(data)
            all_info = load_UserInfo(data)
            f = open(f"datas\\{all_info['name']}_{mid}.txt", "w", encoding="utf-8")  # 记录获取到的信息

            # 输出主要信息，此接口可突破官方API限制
            output(
                f"=============================\nWarning: 以下数据截止到{get_date()}\n被收集者UID: {mid}，请勿用于非法用途\nFrom - https://workers.vrp.moe/\n=============================\n")
            print_long_line("UserInfo", enter=True)
            output(f"[昵称] {all_info['name']}")
            output(f"[性别] {all_info['sex']}")
            output(f"[rank] {all_info['rank']}")
            output(f"[头像链接] {all_info['face']}")
            output(f"[硬币数量] {all_info['coins']}")
            output(f"[DisplayRank] {all_info['DisplayRank']}")
            output(f"[注册时间] {all_info['regtime']}")
            output(f"[生日] {all_info['birthday']}")
            output(f"[个性签名] {all_info['sign']}")
            output(f"[粉丝数量] {all_info['fans']}")
            output(f"[关注数] {all_info['friend']}")

            print_long_line("XP")

            output(f"当前exp -> {all_info['current_exp']}exp")
            output(f"等级 -> LV{all_info['current_level']}")
            output(f"下一级所需 -> {all_info['next_exp']}exp")
            output(f"当前等级门槛 -> {all_info['current_min']}exp")
            if all_info['next_exp'] != -1:
                output(
                    f"升级进度 -> 还差{all_info['next_exp'] - all_info['current_exp']}exp可升级，当前进度为{(all_info['current_exp'] / all_info['next_exp']) * 100}%")
            else:
                output(
                    f"升级进度 -> 此人等级已经爆表！超出LV6 {all_info['current_exp'] - all_info['current_min']}exp")
            print_long_line("FamousFans")

            output(f"- 以下为关注{all_info['name']}的知名UP，为空则无 -")
            # 遍历关注TA的知名粉丝
            try:
                for fan in json.loads(famous_fans.text):
                    print_long_line(no_title=True)
                    output(f"昵称: {fan['name']}")
                    output(f"粉丝数: {fan['fans']}")
                    output(
                        f"跟UP的差距: {fan['fans'] - all_info['fans']} ({fan['name']}的粉丝数 - {all_info['name']}的粉丝数)")
                    output(f"UID: {fan['mid']}")
            except:
                err_log()

            print_long_line(no_title=True)

            input("[-] 以上内容为访客方式获取，按下回车加载更多数据。（请注意，以下内容需要使用您的cookies）")
            break
        except:
            Major_err_log()
            print("[E] Error, please check your input or network settings and try again")
            continue
    # ====================================================================================================
    try:
        cookies = output_space_data(mid)
    except:
        Major_err_log()
        output("[E] 在解析view/vip/live data时部分环节出现了致命问题。这可能是风控导致，若此问题持续出现请联系开发者！")

    output("\n\n")
    print_long_line(no_title=True)
    output(f"Warning: 以下数据截止到{get_date()}，20年以后\n"
           f"被收集者UID: {mid}，下列数据仅供参考，部分直播间未被监听则为空\n"
           f"From - https://ukamnads.icu/\n"
           f"=============================\n\n")

    # =============================================================

    input("按下回车载入直播间数据，此项不需要cookies。")

    print_long_line("直播间数据统计", longer=True, enter=True)
    print("[/] Getting more data, please wait...")

    # 获取直播间访问数据
    live_data = get_live_data()

    live_data = json.loads(live_data.text)["data"]
    visit_data = load_visit_data(live_data)

    try:
        watch_num, watch_list_sorted = visit_data[0], visit_data[1]

        input("按下回车展示观看直播排行，此过程无需请求任何内容。")
        n_ = 0
        #  展示观看排行，通过进入直播间数据来排列
        for w in watch_list_sorted:
            print_long_line(no_title=True)
            output(f"{w[0]} - 观看{w[1]}次")
            n_ += 1

        output(f"[主播统计] 共观看了{n_}名主播。")
        output(f"[观看直播次数] {watch_num}次\n")
    except:
        Major_err_log()
        output("[E] 在解析'观看排行'时部分环节出现了致命问题。这可能是风控导致，若此问题持续出现请联系开发者！")

    # =============================================================

    input("按下回车收集此用户在直播间的发言数据(非全部，20年之后)。 此过程不需要您的cookies")

    data_list = get_danmu_data()
    print("[/] Loading data...")
    try:
        danmu_data = load_danmu_data(data_list)
    except:
        Major_err_log()
        output("[E] 在解析'发言数据'时遇到问题。此问题可能是风控导致，若持续出现请联系开发者")

    # =============================================================

    input("按下回车展示此用户的发言数据，此过程无需请求任何信息。")

    print_long_line("直播间发言数据", longer=True)

    # 获取所有解析完的数据
    show_list, msg_list, visit_list, gift_list = danmu_data['show_list_danmu'], danmu_data['msg_list_danmu'], \
        danmu_data['visit_list_danmu'], danmu_data['gift_list_danmu']
    message, gifts = danmu_data['message'], danmu_data['gifts_danmu']

    n = 0  # 记录弹幕数量
    for p in show_list:
        print_long_line(no_title=True)
        output(f"{p}")
        n += 1

    output(f"[发言统计] 共发言{n}次")

    # =============================================================

    input("按下回车展示此用户访问直播间的数据，此过程无需请求任何信息。")
    print_long_line("访问直播间数据 ", longer=True, enter=True)
    for p in visit_list:
        print_long_line(no_title=True)
        output(f"{p}")
    try:
        output(f"\n\n\n[最后一次访问数据] {visit_list[0]}")
        output(f"[自统计最早访问数据] {visit_list[-1]}")
    except:
        err_log()
        output("[NULL] 无发言数据...")

    # =============================================================

    input("按下回车展示送礼数据 / 发言数据统计，此过程无需请求任何信息。")
    # 对所需数据进行排序处理 reverse=True为从大到小排列
    d_gifts = dict([[i, gifts.count(i)] for i in gifts])
    d_send = dict([[i, message.count(i)] for i in message])
    d_gifts = sorted(d_gifts.items(), reverse=True, key=lambda s: s[1])
    d_send = sorted(d_send.items(), reverse=True, key=lambda s: s[1])

    print_long_line("直播间送礼数据", longer=True, enter=True)

    # 写入并输出送礼数据
    for gift in gift_list:
        print_long_line(no_title=True)
        output(f"{gift}")

    print_long_line("直播间送礼次数统计", longer=True, enter=True)
    gt = 0  # 记录送礼次数
    for g in d_gifts:
        print_long_line(no_title=True)
        gt = gt + g[1]
        output(f"送给{g[0]} - 送出{g[1]}次")

    print_long_line(no_title=True)
    output(f"\n[送礼统计] 共送出{gt}个礼物")

    print_long_line("直播间发言统计", longer=True, enter=True)
    for g in d_send:
        print_long_line(no_title=True)
        output(f"在{g[0]} - 发言了{g[1]}次")

    print_long_line(no_title=True)
    output("\n\n")

    try:
        f.write("======================== 最终统计 ========================\n")
        f.write(f"[送礼统计] 共送出{gt}个礼物\n")
        f.write(f"[观看直播次数] {watch_num}次\n")
        f.write(f"[最后一次访问数据] {visit_list[0]}\n")
        f.write(f"[自统计最早访问数据] {visit_list[-1]}\n")
    except:
        err_log()
        f.write("[-] 数据过少，部分统计无法显示。")

    f.write("======================================================\n")

    f.write(f"\n\n统计结束 - {get_date()}")
    f.close()  # 解除占用并保存写入

    # =============================================================

    if input("按下回车生成词云图，此过程无需请求任何信息。 输入'n'取消... ") != "n":
        save_danmu_wordcloud(msg_list, mid=mid, name=all_info['name'])

    # =============================================================

    print(f"[OK] 用户{mid}的成分已经保存到datas文件夹，请查收。")

    # =============================================================

    if input("是否需要保存数据文件来提供给ChatGPT，这可能需要爬取更多信息。\n注意，此过程需要你的cookies\nn/*>") == "n":
        print("[EXIT] 用户取消了操作")
        exit(0)

    f = open(f"gpt_datas\\gpt_{mid}_{all_info['name']}.txt", "w", encoding="utf-8")
    f.write(
        f"{all_info['name']}的B站基本信息: \n昵称: {all_info['name']}\n简介: {all_info['sign']}\n粉丝数量: {all_info['fans']}\n关注数: {all_info['friend']}")
    result = ""
    f.write(f"\n\n以下是{all_info['name']}在各大直播间的发言:")
    for t in range(250):
        try:
            result = result + f"\n" + random.choice(msg_list)
        except:
            err_log()
            break

    f.write(result)

    video_data = get_video_info(mid, headers, cookies)
    title_list, description_list = video_data[0], video_data[1]

    n_ = 0
    f.write("\n\n")
    for w in watch_list_sorted:
        if n_ > 4:
            break
        f.write(f"他看了主播{w[0].split('name:')[1]}一共{w[1]}次\n")
        n_ += 1

    if len(title_list) != 0:
        f.write(f"\n\n以下是{all_info['name']}的视频信息，分割线左边为标题右边为简介\n")
        for x in range(20):
            try:
                f.write(f"{title_list[x]} | {description_list[x]}\n")
            except:
                err_log()
                break

    print(f"[OK] 文件保存在gpt_datas\\gpt_{mid}_{all_info['name']}.txt，请注意查看，您可删改文件的内容")
