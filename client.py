from socket import *
import sys
import traceback
def do_history(s):
	while True:
		data = s.recv(1024).decode()
		if data == '##':
			break
		print(data)
def words(s):
	word = input("请输入您要搜索的单词:")
	s.send(word.encode())
	data = s.recv(2048).decode()
	return data
def do_login(s):
	print("""==========================
			4:查单词，5:历史记录,6:退出
			===========================""")
	while True:
		try:
			data = input("请输入选项")
			s.send(data.encode())
			if data == '4':
				w = words(s)
				if not w:
					print("您输入的单词不存在")
					continue
				l = w.split(' ')
				word = l[0]
				interpret = ' '.join(l[1:])
				print(word,'   ',interpret)
			elif data == '5':
				do_history(s)
			elif data == '6':
				return
			else:
				print("请输入正确的选项")
				continue
		except KeyboardInterrupt:
			return
def do_register(s):
	while True:
		root = input('请输入您要创建的账号')
		secret = input('请输入密码')
		secret1 = input("请再次输入密码")
		if secret != secret1:
			print('两次输入的密码不一致，请重新输入')
			continue
		s.send((root+' '+secret).encode())
		data = s.recv(1024).decode()
		if data == 'exits':
			return 1
		elif data == 'ok':
			return 0
		elif data == 'false':
			return 2
def main():
	if len(sys.argv)<3:
		return
	else:
		host = sys.argv[1]
		port = int(sys.argv[2])
		addr = (host,port)
	s = socket()
	try:
		s.connect(addr)
	except:
		traceback.print_exc()
		return
	while True:
		print("""=======welceome=========
			--1:注册，2:登录,3:退出--
			=============================
			""")
		try:
			data = int(input('请输入选择内容'))
		except KeyboardInterrupt:
			s.send("q".encode())
			sys.exit("退出啦")
		except Exception as e:
			print(e)
			continue
		if data == 1:
			s.send('r'.encode())
			r = do_register(s)
			if r == 0:
				print("注册成功")
			elif r == 1:
				print("已有用户注册")
			elif r == 2:
				print("注册失败")
		elif data == 2:
			while True:
				s.send('l'.encode())
				root = input('请输入您的账号')
				secret = input("请输入您的密码")
				s.send((root+" "+secret).encode())
				data = s.recv(1024).decode()
				if data == "ok":
					print("登录成功")
					break
				elif data == "failed":
					print("用户名和密码不一致，请重新输入:")
					continue
			d = do_login(s)
		elif data == 3:
			s.send('q'.encode())
			return
		else:
			print('请输入正确选项')
			sys.stdin.flush()
			continue
if __name__ == "__main__":
	main()

