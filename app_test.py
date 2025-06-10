import json
from json import JSONDecodeError

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

json_str='''{
    "view": "**【认识保罗】**保罗是基督教历史上极为重要的人物，对福音的传播贡献巨大。

**默想**：
1. **蒙召转变**：保罗起初迫害教会，却在前往大马士革的路上蒙主光照，从此成为福音的有力传播者。这显示了上帝奇妙的拣选与改变人的大能。正如《加拉太书》1:15 - 16所说：\\“然而那把我从母腹里分别出来，又施恩召我的神，既>然乐意将他儿子启示在我心里，叫我把他传在外邦人中。\\”
2. **坚定信念**：保罗一生历经苦难，被囚禁、遭鞭打，但始终坚守信仰，传扬福音。

**祷告**：主啊，求你让我们有保罗那样蒙召转变的经历，认识到你的救恩。也赐给我们坚定的信念，像保罗一样无论面对何种艰难，都能持守信仰，勇敢传扬你的福音。

**实际应用**：在生活中，当我们遭遇困境，要像保罗一样依靠主的力量。积极传扬福音，用行动见证信仰，即便面对反对和挫折，也不退缩。",
    "explore": [
        "保罗的传教经历对我们当今传福音有哪些具体启示？",
        "保罗书信对基督教教义的形成有怎样的重要影响？"
    ]
}
'''


msg_feedback = '''你要在基督教正统教义范围内对下面输入提供祷告和默想建议: \n\n1.\xa0 view:针对用户上一个输入内容，提供与之相关的祷告和默想，以及返回一段符合基督教新教原则的实际应用建议，字数在800字以内。分为以下三部分:默想，祷告，实际应用。请围绕【具体主题】进行回答，要求：\n \nA.\xa0标题加粗（用【】标注主题），首句先提炼核心结论；\n\u200b\nB.\xa0分点回答时使用 1. 2. 3. … 有序列表，每点前用简短关键词加粗（如 核心优势：），内容简洁清晰；\n\u200b\nC.\xa0避免‘首先/然后’等过渡词，直接按逻辑顺序分点，每点控制在2-3句话，便于快速阅读。\n\nD.在段与段之间要空一行\n\n2.\xa0 explore:给出2个和用户输入内容密切相关的，引导基督教新教教义范围内进一步展开讨论的话题，话题的形式可以是问题或者指令。推荐你能回答的问题或话题。 \n\n3.\xa0 严格按json格式返回。{view:<view>,explore:<explore>} \n\n4.\xa0 对于给出的圣经经文，以及具体圣经出处，都用加粗字体来展示。 \n\n5.\xa0 严格按照用户输入的语言返回。 以下是用户的输入内容： \n\n    保罗是一个怎么样的人？
                '''

if __name__ == '__main__':

    try:
        # print(repr(json_str))
        print(json.loads('{\n    "view": "**【认识保罗】**保罗是基督教历史上极为重要的人物，对福音的传播贡献巨大。\\n\\n**默想**"\n}\n'))
    except JSONDecodeError as e:
        print(f"Error occurred: {e}")
        # 获取出错位置信息
        line = e.lineno
        column = e.colno
        pos = e.pos

        # 打印原始字符串的片段（前后各20个字符）
        start = max(0, pos - 20)
        end = min(len(json_str), pos + 20)
        context = json_str[start:end]

        print(f"\nError context (char {pos}):")
        print(f"Line {line}, Column {column}")
        print(f"Surrounding text: {repr(context)}")

        # 标记出错位置
        if pos - start > 0:
            marker = ' ' * (pos - start) + '^'
            print(f"Error position:  {marker}")
    # token = login("user2")
    # # get_conf(token)
    # # new_session(token)
    # get_message(token)
    # r = my_session(token)
    # print(extract_test(r.get("data").get("feedback")[0:200],[0,0,0,0]))