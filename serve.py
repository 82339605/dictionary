from multiprocessing import Process
from socket import *
from signal import *
import traceback
import sys
import time
import pymysql
import re
import time
def do_select(conn,db,name):
	vocabulary = conn.recv(1024).decode()
	cur = db.cursor()
	sql = "select  * from words where word = '%s'"%(vocabulary)
	try:
		cur.execute(sql)
		t = cur.fetchone()
		if not t:
			conn.send("没有查到这个单词".encode())
		word = t[1]
		interpret = t[2]
		sql = 'insert into history(name,word,time) values("%s","%s","%s")'%(name,word,time.asctime())
		try:
			cur.execute(sql)
			db.commit()
		except:
			db.rollback()
			traceback.print_exc()
			return
		conn.send((word+' '+interpret).encode())
	except:
		traceback.print_exc()
		db.rollback()
		return
def hand(conn,db):
	print('connect from ',conn.getpeername())
	while True:
		try:
			data = conn.recv(1024).decode()
			if data == 'l':
				do_login(conn,db)
			elif data == 'r':
				d = do_register(conn,db)
			elif data == 'q':
				sys.exit("客户端%s退出"%(conn.getpeername()))
			elif data == 'h':
				do_history()
		except Exception as e:
			print(e)
			continue
def do_login(conn,db):
	print("等待用户输入账号密码")
	data = conn.recv(1024).decode()
	l = data.split(' ')
	name = l[0]
	passwd = " ".join(l[1:])
	cur = db.cursor()
	sql = "select * from user where name='%s' and passwd ='%s'" %(name,passwd)
	cur.execute(sql)
	k = cur.fetchone()
	if k == None:
		print("failed")
		conn.send("failed".encode())
		return
	if passwd == k[2]:
		print("登录成功")
		conn.send("ok".encode())
	while True:
		order = conn.recv(1024).decode()
		if order == '4':
			do_select(conn,db,name)
		elif order =='5':
			do_history(conn,db)
		elif order =='6':
			return
def do_register(conn,db):
	cur = db.cursor()
	print("wait a minute")
	data = conn.recv(1024).decode()
	l = data.split(" ")
	name = l[0]
	secret = ' '.join(l[1:])
	sql = 'select * from user where name = "%s"'%(name)
	try:
		cur.execute(sql)
		r = cur.fetchone()
	except:
		traceback.print_exc()
		db.rollback()
		conn.send(b"false")
	else:
		if r != None:
			conn.send(b"exits")
			return
	string = 'insert into user (name,passwd) values ("%s","%s")'%(name,secret)
	try:
		cur.execute(string)
		db.commit()
		conn.send(b"ok")
	except:
		db.rollback()
		conn.send(b'false')
	else:
		print("'%s'注册成功"%name)
def do_history(conn,db):
	cur = db.cursor()
	data = 'select * from history'
	try:
		cur.execute(data)
		document = cur.fetchall()
		for i in document:
			name = i[1]
			word = i[2]
			time = i[3]
			conn.send((name+' '+word+' '+time).encode())
		conn.send('##'.encode())
	except:
		conn.send("failed".encode())
		traceback.print_exc()
		return
def main():
	db = pymysql.connect('localhost','root','123456','project')
	host = '0.0.0.0'
	port = 8000
	addr = (host,port)
	s = socket(AF_INET,SOCK_STREAM)
	s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
	s.bind(addr)
	s.listen(5)
	signal(SIGCHLD,SIG_IGN)
	while True:
		try:
			conn,addr = s.accept()
		except KeyboardInterrupt:
			s.close()
			conn.close()
			sys.exit('退出啦')
		except:
			traceback.print_exc()
			continue
		p = Process(target = hand,args = (conn,db))
		p.daemon = True
		p.start()
if __name__ == '__main__':
	main()
