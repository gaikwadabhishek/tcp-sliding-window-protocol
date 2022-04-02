# import socket programming library
import socket

# import thread module
from _thread import *
import threading

print_lock = threading.Lock()

# thread function
def threaded(c):
	while True:

		# data received from client
		data = c.recv(1024)
		if not data:
			print('Bye')
			
			# lock released on exit
			print_lock.release()
			break
		print(data)
		# send back reversed string to client
		c.send(data)

	# connection closed
	c.close()


def Main():
	host = ""

	# reverse a port on your computer
	# in our case it is 12345 but it
	# can be anything
	port = 50053
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((host, port))
	print("socket binded to port", port)

	# put the socket into listening mode
	s.listen()
	print("socket is listening")

	# a forever loop until client wants to exit
	while True:

		# establish connection with client
		c, addr = s.accept()

		# lock acquired by client
		print_lock.acquire()
		print('Connected to :', addr[0], ':', addr[1])
		
		if c.recv(1024).decode('utf-8') == "network":
			print("Received network sending success")
			c.send("SUCCESS".encode('utf-8'))
			# Start a new thread and return its identifier
			start_new_thread(threaded, (c,))
	s.close()


if __name__ == '__main__':
	Main()
