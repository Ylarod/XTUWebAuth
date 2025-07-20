import json
import os
import re
import requests
from pip._internal.network import session


def save_credentials_to_json(file_path, user_id, password):
    """将学号和密码保存到JSON文件"""
    data = {
        "user_id": user_id,
        "password": password
    }
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_credentials_from_json(file_path):
    """从JSON文件中读取学号和密码"""
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return None


def testInternet():
    try:
        html = requests.get('http://baidu.com')
        userip = re.findall(r'wlanuserip=(.*?)&wlan', html.text)[0]
    except Exception:
        return True
    return False


def encryptedPassword(
        password,
        publicKeyExponent="10001",
        publicKeyModulus="94dd2a8675fb779e6b9f7103698634cd400f27a154afa67af6166a43fc26417222a79506d34cacc7641946abda1785b7acf9910ad6a0978c91ec84d40b71d2891379af19ffb333e7517e390bd26ac312fe940c340466b4a5d4af1d65c3b5944078f96a1a51a5a53e4bc302818b7c9f63c4a1b07bd7d874cef1c3d4b2f5eb7871"
):
    """ RSA加密逻辑 """
    # 将公钥参数从十六进制转为整数
    e = int(publicKeyExponent, 16)
    n = int(publicKeyModulus, 16)

    # 根据模数长度计算 chunkSize（此处模拟 JavaScript 中的 2 * biHighIndex(m) 行为）
    byte_length = len(publicKeyModulus) // 2  # 模数的字节长度
    digit_num = (byte_length + 1) // 2  # 模数按 16 位数字（digit）计算的位数
    high_index = digit_num - 1  # 最高的非零位索引（假设模数为完整长度）
    chunk_size = 2 * high_index  # 每个加密块的字节数，匹配 JavaScript

    # 反转密码字符串（模拟 password.split("").reverse().join("") 行为）
    password_encode = password[::-1]

    # 将密码字符串转为字节数组（使用 ASCII 编码）
    byte_array = [ord(c) for c in password_encode]

    # 如果字节数组长度不是 chunk_size 的倍数，则使用 0 进行填充
    while len(byte_array) % chunk_size != 0:
        byte_array.append(0)

    # 对每个分块进行加密
    encrypted_blocks = []
    for i in range(0, len(byte_array), chunk_size):
        # 提取块数据，并将其转为小端字节序的整数
        block_bytes = byte_array[i:i + chunk_size]
        block_int = int.from_bytes(block_bytes, 'little')

        # 使用 RSA 加密逻辑：block_int^e mod n
        crypt_int = pow(block_int, e, n)

        # 将加密后的整数转为十六进制字符串（去掉 '0x' 前缀）
        crypt_hex = hex(crypt_int)[2:]
        encrypted_blocks.append(crypt_hex)

    # 通过空格连接加密的块并返回
    return ' '.join(encrypted_blocks)


class XTUWebAuth():
    def __init__(self, userId, password, isInitLogin=True):
        self.userId = userId
        self.password = password
        self.linkRoot = "http://172.16.0.32:8080"
        self.linkRedirect = "http://123.123.123.123"
        self.linkLogin = "http://172.16.0.32:8080/eportal/InterFace.do?method=login"
        self.linkLogout = "http://172.16.0.32:8080/eportal/InterFace.do?method=logout"
        self.linkOnlineUseerInfo = "http://172.16.0.32:8080/eportal/InterFace.do?method=getOnlineUserInfo"
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.1 Safari/605.1.15',
            'Content-Type': 'text/html;charset=utf-8'
        }
        self.userIndex = ""
        if isInitLogin == True:
            requests.session()
            self.authUrl = self.getWebAuthUrl()
            self.queryString = self.getQueryString()
            self.formDataLogin = self.makeFormData()
            self.headersLogin = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.1 Safari/605.1.15',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Referer': self.authUrl
            }

    def makeFormData(self):
        tmp = "userId={userId}&password={password}&service=&queryString={queryString}&operatorPwd=&operatorUserId=&validcode=&passwordEncrypt=true"
        tmp = tmp.replace("{userId}", self.userId)
        tmp = tmp.replace("{password}", self.password)
        tmp = tmp.replace("{queryString}", self.queryString)
        return tmp

    def getQueryString(self):
        r = requests.get(self.linkRedirect, headers=self.headers, timeout=5)
        queryString = r.text.replace("<script>top.self.location.href='http://172.16.0.32:8080/eportal/index.jsp?", "")
        queryString = queryString.replace("'</script>", "")
        queryString = queryString.replace("=", "%253D")
        queryString = queryString.replace("&", "%2526")
        queryString = queryString.replace("/", "%252F")
        queryString = queryString.replace(":", "%253A")
        return queryString.replace("\r\n", "")

    def getWebAuthUrl(self):  # use when not online
        r = requests.get(self.linkRedirect, headers=self.headers, timeout=5)
        accessUrl = r.text.replace("<script>top.self.location.href='", "")
        accessUrl = accessUrl.replace("'</script>", "").replace("\r\n", "")
        return accessUrl

    def getOnlineUserInfo(self):  # use when online
        r = requests.get(self.linkOnlineUseerInfo, timeout=5)
        r.encoding = 'utf-8'
        return r.text

    def getCookie(self):
        return requests.utils.dict_from_cookiejar(session.cookies)

    def login(self):
        self.headersLogin['Referer'] = self.authUrl
        # print(self.headersLogin)
        # print(self.formDataLogin)
        r = requests.post(self.linkLogin, headers=self.headersLogin, data=self.formDataLogin, timeout=5)
        r.encoding = 'utf-8'
        if "success" in r.text:
            return True, r.text
        else:
            return False, r.text

    def logout(self):
        r = requests.post(self.linkOut, headers=self.headersLogin, data="userIndex=" + self.userIndex, timeout=5)
        if "success" in r.text:
            return True, r.text
        else:
            return False, r.text


if __name__ == "__main__":
    # JSON文件路径
    json_file_path = 'password.json'
    # 第一次进入程序，检查是否存在JSON文件
    credentials = load_credentials_from_json(json_file_path)
    if credentials is None:
        user_id = input("请输入学号: ")
        password = input("请输入密码: ")
        save_credentials_to_json(json_file_path, user_id, password)
    else:
        user_id = credentials["user_id"]
        password = credentials["password"]

    encrypted = encryptedPassword(password)

    # 测试是否已经在线
    if not testInternet():
        obj = XTUWebAuth(user_id, encrypted)
        status, msg = obj.login()
        print("登录状态:", status)
        print("登录信息:", msg)
    else:
        print("已在线状态:")
        obj = XTUWebAuth(user_id, encrypted, False)
        print(obj.getOnlineUserInfo())
