import requests
import re
import os

def testInternet():
	try:
		html = requests.get('http://baidu.com')
		userip = re.findall(r'wlanuserip=(.*?)&wlan', html.text)[0]
	except:
		return True
	return False
	
class XTUWebAuth():
	def __init__(self,userId,password,isInitLogin = True):
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
		tmp = tmp.replace("{password}" , self.password)
		tmp = tmp.replace("{queryString}", self.queryString)
		return tmp
		
	
	def getQueryString(self):
		r = requests.get(self.linkRedirect,headers= self.headers ,timeout= 5)
		queryString = r.text.replace("<script>top.self.location.href='http://172.16.0.32:8080/eportal/index.jsp?","")
		queryString = queryString.replace("'</script>","")
		queryString = queryString.replace("=","%253D")
		queryString = queryString.replace("&","%2526")
		queryString = queryString.replace("/","%252F")
		queryString = queryString.replace(":","%253A")
		return queryString.replace("\r\n","")
	
	def getWebAuthUrl(self): #use when not online
		r = requests.get(self.linkRedirect,headers= self.headers ,timeout= 5)
		accessUrl = r.text.replace("<script>top.self.location.href='","")
		accessUrl = accessUrl.replace("'</script>","").replace("\r\n","")
		return accessUrl
	
	
	def getOnlineUserInfo(self):  #use when online 
		r = requests.get(self.linkOnlineUseerInfo,timeout= 5)
		r.encoding='utf-8'
		return r.text
	
	def getCookie():
		return requests.utils.dict_from_cookiejar(session.cookies)
	
	def login(self):
		self.headersLogin['Referer'] = self.authUrl
		#print(self.headersLogin)
		#print(self.formDataLogin)
		r = requests.post(self.linkLogin,headers= self.headersLogin,data= self.formDataLogin,timeout= 5)
		r.encoding='utf-8'
		if "success" in r.text:
			return True,r.text
		else:
			return False,r.text
			
	def logout(self):
		r = requests.post(self.linkOut,headers= self.headersLogin,data= "userIndex=" + self.userIndex,timeout= 5)
		if "success" in r.text:
			return True,r.text
		else:
			return False,r.text

if __name__ == "__main__":
	if testInternet() == False:
		obj = XTUWebAuth("[学号]" ,"[RSA加密后的密码]")
		status,msg = obj.login()
		print(status)
		print(msg)
	else:
		print("Already online:")
		obj = XTUWebAuth("[学号]" ,"[RSA加密后的密码]",False)
		print(obj.getOnlineUserInfo())
