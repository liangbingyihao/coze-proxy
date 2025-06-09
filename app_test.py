import json
import requests



def register():
    url = "http://8.217.172.116:5000/api/auth/register"
    data = {
        "username": "user2",
        "email": "user2@163.com",
        "password": "123456"
    }

    response = requests.post(url, json=data)
    print(response.text)


def login(user_name):
    url = "http://8.217.172.116:5000/api/auth/login"
    data = {
        "guest": "81863ba6-abf8-340f-892a-683e6896a23f",
        "password": "123456"
    }

    response = requests.post(url, json=data)
    print(response.text)
    token = response.json().get("data").get("access_token")
    return token


def new_session(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "session_name": "session_name2",
        "robot_id": "1"
    }

    response = requests.post("http://8.217.172.116:5000/api/session", headers=headers, json=data)
    print(response.text)


def my_session(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "page": 1,
        "limit": 50
    }

    response = requests.get("http://8.217.172.116:5000/api/session", headers=headers, params=data)
    sessions = response.json().get("data")
    for s in sessions.get("items"):
        print(s)

def get_conf(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "page": 1,
        "limit": 50
    }

    response = requests.get("http://8.217.172.116:5000/api/system/conf", headers=headers, params=data)
    data = response.json().get("data")
    print(data)


def add_message(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "text": "今天和邻居聊了一个上午，但还没有解开大家的心结",
        "context_id": "2",
        "prompt":"test"
    }
#     data = {
#         "text": '''✨嗨，你好🙌欢迎来到恩语~！
# 我可以为你记录你的每一件感恩小事💝、圣灵感动🔥、真实感受，甚至讲道亮光🌟哦，
# 帮助你在信仰路上，不断看到上帝的恩典🌈！
# 📝文字或🎤语音转文字，就能快速记录，我们会帮你整理⏳~
# 每天的记录都是我们跟神互动的印记💌，
# 坚持记录，你很快会发现，上帝如何奇妙地与我们同行👣哦！
# 快来开始记录吧~🎉
# ''',
#     }
    # data = {
    #     "text":1
    # }

    response = requests.post("http://8.217.172.116:5000/api/message", headers=headers, json=data)
    print(response.text)


def my_message(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "session_id": 12,
        # "context_id":21,
        # "page":1,
        # "limit":1
    }
    response = requests.get("http://8.217.172.116:5000/api/message", headers=headers, params=data)
    print(response.json())


def get_message(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "session_id": 2,
        "context_id": 21,
        # "page":1,
        # "limit":1
    }
    response = requests.get("http://8.217.172.116:5000/api/message/7bd9b8e4-f904-4fde-9464-38ab62212446", headers=headers)
    r = response.json()
    print(json.dumps(r.get("data"), indent=4,ensure_ascii=False))
    return r

def update_summary(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "summary": "心结难解"
    }
    response = requests.post("http://8.217.172.116:5000/api/message/c198b09d-2ac7-4f6a-8f2b-9511d78c7049", headers=headers,json=data)
    r = response.json()
    print(r)
    return r

def _extract_content(content, s):
    print(content)
    s1, s2, s3 = s
    if not s1:
        s[0] = s1 = content.find("\"bible\":")
    if s1 and not s2:
        s[1] = s2 = content.find("\"feed")
    if s2 and not s3:
        s[2] = s3 = content.find("\"exp")
    bible, detail = content[s1 + 8:s2 if s2 > 0 else -1], content[s2 + 11:s3 if s3 > 0 else -1]
    return bible, detail


def extract_test(text, s):
    import re
    s1, e1, s2, e2 = s
    bible, detail = "", ""

    if not s1:
        match = re.search(r"(\"bible\"\s*:\s*)", text)
        if match:
            s[0] = s1 = match.end()

    if not s2:
        match = re.search(r"(\"feedback\"\s*:\s*)", text)
        if match:
            s[1] = e1 = match.start()
            s[2] = s2 = match.end()

    if not e2:
        match = re.search(r"(\"explore\"\s*:\s*)", text)
        if match:
            s[3] = e2 = match.start()
    if s1:
        bible = text[s1:e1 if e1 > 0 else -1]
    if s2:
        detail = text[s2:e2 if e2 > 0 else -1]
    return bible, detail

x='''
'你要先识别用户是在问问题还是在记录。\n\n如果用户是在问问题，他通常会用问句来做结尾，或者语义是一个具体的问题呈现。\n\n接收到问题后，先回复一段共情用户
输入内容的开头，在基督教新教的框架内容上，去回答他的问题。回答问题时，请围绕【具体主题】进行回答，要求：\n \nA.\xa0标题加粗（用【】标注主题），首句先提炼核心结论；\n\u200b\nB.\xa0分点回答时使用 1. 2. 3. … 有序>列表，每点前用简短关键词加粗（如 核心优势：），内容简洁清晰；\n\u200b\nC.\xa0避免‘首先/然后’等过渡词，直接按逻辑顺序分点，每点控制在2-3句话，便于快速阅读，\n\nD.在段与段之间要空一行。\n\n字数在1000字以内。这一>类的内容，全部都归类到【信仰问答】的主题分类中。\n\n如果问题超出了基督教新教的原则，或者有不确定之处，要写清楚这个观点来源，并提醒用户观点仅供参考。鼓励他可以把问题记录或收藏下来，日后在生活实践中，持续用这个恩
语app来记录，可能有新的亮光发现。\n\n最后，推荐他一条与之相关的新教圣经中的经文作为结尾，标明经文的出处。\n\n如果用户的问题涉及到政治，自杀，黄赌毒等敏感话题，温馨告知这类问题无法回答，可以帮他记录下来到一个新>的时间轴主题中，并给予一段积极正面的经文作为鼓励，让他知道无论经历多难的事情，上帝依然爱他，对他的生命有一个美好的计划。\n\n如果用户是记录内容，不是问问题，无论是感恩小事，圣灵感动，亮光发现，讲道笔记等信息，进
行以下反馈: \n\n1.\xa0 bible:先用共情的语言回应用户的记录内容，再返回一段基督教新教的圣经中的相关经文进行回应 \n\n2.\xa0 view:针对用户的记录以及结合该经文内容，反馈一段500字以内的内容，可以讲解经文的经典人物背>景，也可以讲这段经文对这个记录事件有什么实际应用的参考价值。回答问题时，尽量用清晰的结构来陈述，有结论，论点，论据。如果涉及到多内容，那就先说观点，再分开几点来陈述，确保用户可以清晰知道你的观点，便于阅读者阅读
。 \n\n3.\xa0 topic1:为输入内容从["压力倾诉","开心感恩","分享信仰问题","主祷文探讨","考试失利","处理妹妹问题","考试进步感恩","大卫的故事","赞美见异象","讲道感悟",]里选出一个主题分类，若无法选取则为“” \n\n3. topic2:无法选出topic1时，新增一个6个字以内的主题分类 \n\n4.\xa0 tag:对用户输入的内容先根据内容的情绪，简单按照喜怒哀惧四种情绪来分类，并且按照喜-红色，怒（包括烦恼）-黄色，哀（包括痛苦）-蓝色，惧（包含焦虑）-绿色>的规则来作为记录的背景颜色。同时根据返回的圣经经文打标签，标签只能从信靠，盼望，刚强，光明，慈爱，喜乐，安慰，永恒，平安，恩典选择最接近的一个。 \n\n5.\xa0 summary:给出8个字以内的重点小结，总结要结合用户记录的>内容本身，尽量不要跟上文的summary有太多雷同，体现出同一个大的主题下，事情发展的具体变化\n\n6.\xa0 explore:给出2个和用户输入内容密切相关的，引导基督教新教教义范围内进一步展开讨论的话题，话题的形式可以是问题或者>指令。推荐你能回答的问题或话题。 \n\n7.\xa0 严格按json格式返回。{bible:<bible>,view:<view>,explore:<explore>,topic1:<topic1>,topic2:<topic2>,tag:<tag>,summary:<summary>} \n\n8.\xa0 对于所有给出的圣经经文，以及>具体圣经出处，都用加粗字体来展示。\n\n9.\xa0 严格按照用户输入的语言返回。 以下是用户的输入内容： \n\n我今天又很没耐心，看到孩子一直磨蹭功课，很难受，忍不住批评他了。'
'''


msg_feedback = '''你要帮助基督徒用户记录的感恩小事，圣灵感动，亮光发现、回答用户关于信仰的问题，请进行以下反馈:
                1.view: 用户查看的回应文本,必须是**Markdown 格式的字符串**（支持标题、列表、代码块等语法）。详细说明见后面view字段的详细要求。
                2.bible:view字段回应中主要的一段圣经经文文本。
                3.topic1:如果用户输入是关于信仰的问题，返回"信仰问答"，否则从${event}里选出一个主题分类,无法选取则为""
                3.topic2:无法选出topic1时，新增一个6个字以内的主题分类
                4.tag:对用户输入的内容返回的圣经经文打标签，标签只能从"信靠，盼望，刚强，光明，慈爱，喜乐，安慰，永恒，平安，恩典"选择最接近的一个。
                5.summary:给出8个字以内的重点小结
                6.explore:给出1个和用户输入内容密切相关的，引导基督教新教教义范围内进一步展开讨论的话题，话题的形式可以是问题或者指令。
                7.严格按json格式返回。{"view":<view>,"bible":<bible>,"explore":<explore>,"topic1":<topic1>,"topic2":<topic2>,"tag":<tag>,"summary":<summary>}
                8.对于跟信仰，圣经无关任何输入，如吃喝玩乐推荐、或者毫无意义的文本，只需要回复""。
                9.严格按照用户输入的语言返回。
                
                ###以下是view字段的详细要求：
                你要先识别用户是在问问题还是在记录。
如果用户是在问问题，他通常会用问句来做结尾，或者语义是一个具体的问题呈现。
接收到问题后，先回复一段共情用户
输入内容的开头，在基督教新教的框架内容上，去回答他的问题。回答问题时，请围绕【具体主题】进行回答，要求：
A. 标题加粗（用【】标注主题），首句先提炼核心结论；
​
B. 分点回答时使用 1. 2. 3. … 有序>列表，每点前用简短关键词加粗（如 核心优势：），内容简洁清晰；
​
C. 避免‘首先/然后’等过渡词，直接按逻辑顺序分点，每点控制在2-3句话，便于快速阅读，
D.在段与段之间要空一行。
字数在1000字以内。这一>类的内容，全部都归类到【信仰问答】的主题分类中。
如果问题超出了基督教新教的原则，或者有不确定之处，要写清楚这个观点来源，并提醒用户观点仅供参考。鼓励他可以把问题记录或收藏下来，日后在生活实践中，持续用这个恩
语app来记录，可能有新的亮光发现。
最后，推荐他一条与之相关的新教圣经中的经文作为结尾，标明经文的出处。
如果用户的问题涉及到政治，自杀，黄赌毒等敏感话题，温馨告知这类问题无法回答，可以帮他记录下来到一个新>的时间轴主题中，并给予一段积极正面的经文作为鼓励，让他知道无论经历多难的事情，上帝依然爱他，对他的生命有一个美好的计划。
如果用户是记录内容，不是问问题，无论是感恩小事，圣灵感动，亮光发现，讲道笔记等信息，
先用共情的语言回应用户的记录内容，再返回一段基督教新教的圣经中的相关经文进行鼓励。然后针对该经文予一段500字以内的内容拓展，可以说经文的经典人物背景，也可以讲这段经文的实际应用。如果用户是问圣经相关的问题，先回复一段共情用户输入内容的开头，再根据用户的问题进行回答，回答的内容要符合基督教新教的教义，或者基于圣经的常识性问题。如果用户的问题存在不同的观点，那就要列明这些都只是观点，仅供参考。回答的内容在800字以内。
圣经经文要高亮显示，要合理分段方便在手机查看，段落要分明。如有需要可以分点来回答，便于阅读者来阅读。
                
                ###以下是用户的输入内容：
                '''

if __name__ == '__main__':
    print(x)
    # token = login("user2")
    # # get_conf(token)
    # # new_session(token)
    # get_message(token)
    # r = my_session(token)
    # print(extract_test(r.get("data").get("feedback")[0:200],[0,0,0,0]))