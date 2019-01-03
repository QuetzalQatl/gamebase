from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit, send
from urllib.request import urlopen
#from codenames import game
import time
import random
import traceback
import socket
import sys

#this program needs:
#pip install flask flask-socketio eventlet

DefaultPort=5000
FlaskSecretKey='186758961935679815389671589390716774717446469994992999696'

CLIENTS = {} # dict to track active rooms
localIP='127.0.0.1'
LANIP='192.168.99.100'
WANIP=''

# initialize Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = FlaskSecretKey
socketio = SocketIO(app)

def getWideIpAdres():
    try:
        html = urlopen("https://whatsmyip.com/")
        lines=html.readlines()
        html = ''
        for l in lines:
            if l.find(b'Your IP') != -1 and l.find(b'is:') != -1:
                lines2=l.split(b'><')
                for l2 in lines2:
                    if l2.find(b'p class="h1 boldAndShadow">') !=-1 and l2.find(b'</p') !=-1:
                        return l2[27:-3].decode('ascii')
    except:
        traceback.print_exc()
        # perhaps try one or two others
    print ('OMG!!!! Could not find wide ip adres.... Is internet connected/working?')
    return ''

#@socketio.on('message')
#def handle_message(message):
    #print('received message: ' + message)

#@socketio.on('json')
#def handle_json(json):
    #print('received json: ' + str(json))

#@app.route('/favicon.png')
#def favicon():
    #return render_template('favicon.png')

def GetConnectTo(remote_address):
    if (remote_address==localIP):
        return localIP
    elif (remote_address[:4]=='192.'):
        return LANIP
    else:
        return WANIP

@app.route('/')
def app_index():
    a=render_template('index.html')
    a=a.replace('%%CONNECTTO%%',GetConnectTo(request.remote_addr))
    print (request.remote_addr, '/ --> /index.html')
    return a

@app.route('/color')
def app_color():
    a= render_template('color.html')
    a=a.replace('%%CONNECTTO%%',GetConnectTo(request.remote_addr))
    print (request.remote_addr, '/color --> /color.html')
    return a

@socketio.on('triggerColor', namespace='/colorlobbie')
def on_triggerColor():
    try:
        r,g,b=CLIENTS[request.sid]
        print (request.sid, 'triggerColor',r,g,b)
        socketio.emit('newColor', (r,g,b), namespace='/colorlobbie')
    except:
        print ('O shit in on_triggerColors')

@socketio.on('setColor', namespace='/colorlobbie')
def on_setColor(r,g,b):
    CLIENTS[request.sid]=(r,g,b)
    print (request.sid,'setColor -->', r,g,b)

def get1to255():
    random.seed()
    return random.randint(0, 255)

def getFreeColor():
    needWhite=True
    needBlack=True
    for c in CLIENTS:
        if CLIENTS[c]==(255,255,255):
            needWhite=False
        elif CLIENTS[c]==(0,0,0):
            needBlack=False
    if needWhite:
        return (255,255,255)
    if needBlack:
        return (0,0,0)
    r=get1to255()
    g=get1to255()
    b=get1to255()
    print ('getFreeColor',r,g,b)
    return (r,g,b)

@socketio.on('requestColor', namespace='/colorlobbie')
def on_requestColor():
    currentSocketId = request.sid
    r,g,b=CLIENTS[currentSocketId]
    print('requestColor -->',currentSocketId,r,g,b)
    socketio.emit('requestedColor', (currentSocketId,r,g,b), namespace='/colorlobbie')

@socketio.on('connect', namespace='/colorlobbie')
def on_connect():
    print('Client '+request.sid+' connected')
    currentSocketId = request.sid
    CLIENTS[currentSocketId]=getFreeColor()

@socketio.on('disconnect', namespace='/colorlobbie')
def on_disconnect():
    print('Client '+request.sid+' disconnected')
    currentSocketId = request.sid
    CLIENTS.pop(currentSocketId, None)

if __name__ == '__main__':
	if len(sys.argv)==2:
		try:
			DefaultPort=abs(int(sys.argv[1]))
		except:
			print ('Use a positive whole number as port number')
	elif len(sys.argv)==3:
		try:
			LANIP=sys.argv[1]
			#do some sanity checking?
		except:
			print ('not a valid ip addres')
		try:
			DefaultPort=abs(int(sys.argv[2]))
		except:
			print ('Use a positive whole number as port number')
	WANIP=getWideIpAdres()
	print (localIP)
	print (LANIP)
	print (WANIP)
	print (DefaultPort)
	socketio.run(app, debug=False, port=DefaultPort, host="0.0.0.0")
