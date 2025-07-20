from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from base64 import b64encode
from XTUWebAuth import load_credentials_from_json

# RSA加密类实现
class RSAUtils:
    def __init__(self, public_key_exponent, public_key_modulus):
        self.key = self.get_key(public_key_exponent, public_key_modulus)

    @staticmethod
    def get_key(public_key_exponent, public_key_modulus):
        # 构建RSA_PUBLIC_KEY对象
        n = int(public_key_modulus, 16)
        e = int(public_key_exponent, 16)
        return RSA.construct((n, e))

    def encrypted_string(self, plaintext):
        cipher = PKCS1_v1_5.new(self.key)
        # 密码先进行反转加密
        reversed_text = plaintext[::-1]
        encrypted_text = cipher.encrypt(reversed_text.encode())
        # 使用Base64编码以便输出
        return b64encode(encrypted_text).decode()


# 实现加密逻辑
def encrypted_password(password, public_key_exponent, public_key_modulus):
    # 初始化加密工具
    rsa_util = RSAUtils(public_key_exponent, public_key_modulus)
    # 调用加密方法
    return rsa_util.encrypted_string(password)


if __name__ == "__main__":
    # JSON文件路径
    json_file_path = 'password.json'
    # 第一次进入程序，检查是否存在JSON文件
    credentials = load_credentials_from_json(json_file_path)
    password = credentials["password"]  # 明文密码

    # 公钥指数和模数需要从后端或相关配置中获取
    public_key_exponent = "10001"  # 公钥指数
    public_key_modulus = (
        "94dd2a8675fb779e6b9f7103698634cd400f27a154afa67af6166a43fc26417222a79506d34cacc7641946abda1785b7acf9910ad6a0978c91ec84d40b71d2891379af19ffb333e7517e390bd26ac312fe940c340466b4a5d4af1d65c3b5944078f96a1a51a5a53e4bc302818b7c9f63c4a1b07bd7d874cef1c3d4b2f5eb7871"
    )  # 公钥模数

    # 获取加密密码
    encrypted_pwd = encrypted_password(password, public_key_exponent, public_key_modulus)
    print(f"加密后的密码：{encrypted_pwd}")
