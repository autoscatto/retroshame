#!/usr/bin/python

# Number 5 bot.
# thanks John Badham <3

import pyrs.comms
import pyrs.rpc
import pyrs.msgs
import pyrs.test.auth

from pyrs.proto import core_pb2
from pyrs.proto import peers_pb2
from pyrs.proto import system_pb2
from pyrs.proto import chat_pb2
import html2text

import time
import re
import datetime

auth = pyrs.test.auth.Auth()

def register_command(regexp, handler):
        commandos.append((re.compile(regexp), handler))

def process_message(message,lob):
    if message:
            for r, callback in commandos:
                match = r.search(message.replace('@'+NICKNAME,'')) #strippo via se c'e' il nickname dal messaggio
                if match:
                    try:
                        return callback(match,lob)
                    except Exception as e:
                        print 'Exception: ' + str(e).replace('\n', ' - ')
                        return False
                        continue
            return False
    else:
        return False



#----------------------------------------------------------------------------
#### nickname del joinino
NICKNAME="N5"

### tempo d'attesa tra un check di chat event e l'altro 
TIMEOUT=10

### se whitelist e' diversa da [] joina solo quelle, altrimenti controlla blacklist
WHITELIST=["bot_test"]

#### le lobbies blacklistate non verranno joinate
BLACKLIST=["casapau"]



#----------------------------------------------------------------------------
commandos=[]
LASTMID=0 #conterra' sempre l'ultimo message id ricevuto
CHANINFO={} #info varie sulle varie lobbies
MCHANINFO={}

def foibe(b,lob):
    return u"e allora le foibe?"

def lastact(b,lob):
    return "Last chan activity: %s"%datetime.datetime.fromtimestamp(lob.last_activity).strftime('%Y-%m-%d %H:%M:%S')

def helpa(b,lob):
    s= '<table border="0">'
    s=s+ '<tr><td>%s:</td><td></td><td>%s</td></tr>'%("!help","print this help instructions")
    s=s+ '<tr><td>%s:</td><td></td><td>%s</td></tr>'%("!maxuser","print the maximum of users reached by the channel")
    s=s+ '<tr><td>%s:</td><td></td><td>%s</td></tr>'%("!lastactivity","print last lobbie activity")
    s=s+ '</table>'
    return s
    
def maxpeer(b,lob):
    return "Max user on chan: %d" %MCHANINFO[lob.lobby_id]
    
#### Registra gli hook regexmatch -> funzione
#### le funzioni vengono chiamate con 2 parametri (per ora): il messaggio completo
#### che ha matchato e il lobbie object di pyrs (id,name,topic,user ...)  

register_command('e allora\\?$', foibe)
register_command('!lastactivity$', lastact)
register_command('!maxuser$', maxpeer)
register_command('!help$', helpa)


# Construct a Msg Parser.
parser = pyrs.msgs.RpcMsgs();

# create comms object.
comms = pyrs.comms.SSHcomms(auth.user, auth.pwd, auth.host, auth.port)
comms.connect();

rs = pyrs.rpc.RsRpc(comms); 


timeout = 0.5
requests = [];
# Firstly we subscribe to Chat Events.

# Request for Chat Lobbies.
rp = chat_pb2.RequestChatLobbies();
rp.lobby_set = chat_pb2.RequestChatLobbies.LOBBYSET_ALL;

msg_id = pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.CHAT, chat_pb2.MsgId_RequestRegisterEvents, False);
print "Sending Register for Chat Events:"
chat_register_id = rs.request(msg_id, rp)
requests.append(chat_register_id);

# change the default nickname to PyChatBot.
rp = chat_pb2.RequestSetLobbyNickname();
rp.nickname = NICKNAME;

msg_id = pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.CHAT, chat_pb2.MsgId_RequestSetLobbyNickname, False);
print "Sending PyEchoBot Nickname:"
req_id = rs.request(msg_id, rp)
requests.append(req_id);


# wait for responses for initial commands.
for peer_req_id in requests:
  ans = rs.response(peer_req_id, timeout);
  if ans:
      (msg_id, msg_body) = ans;
      print "Received Response: msg_id: %d" % (msg_id);
      resp = parser.construct(msg_id, msg_body);
      if resp:
        print "Parsed Msg:";
        print resp;
      else:
        print "Unable to Parse Response";
  else:
      print "No Response!";
  
requests = [];

# Reference Msg IDs.
chatevent_msg_id = pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.CHAT, chat_pb2.MsgId_EventChatMessage, True);

bldict={}
for blr in BLACKLIST:
    bldict[blr]=True
time.sleep(10);

# This script only logs in once!
while(True): # for more cycles.

  print "Starting new fetch cycle";
  # Create some requests....
  # Send all your Requests first.

  # Get List of Peers and System Info First.
  rp = peers_pb2.RequestPeers();
  rp.set = peers_pb2.RequestPeers.CONNECTED;
  rp.info = peers_pb2.RequestPeers.ALLINFO;

  msg_id = pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.PEERS, peers_pb2.MsgId_RequestPeers, False);

  print "Sending Request for Peers:";
  req_id = rs.request(msg_id, rp)
  requests.append(req_id);

  # 
  rp = system_pb2.RequestSystemStatus();
  msg_id = pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.SYSTEM, system_pb2.MsgId_RequestSystemStatus, False);
  print "Sending Request for SystemStatus:";
  req_id = rs.request(msg_id, rp)
  requests.append(req_id);

  # Request for Chat Lobbies.
  rp = chat_pb2.RequestChatLobbies();
  rp.lobby_set = chat_pb2.RequestChatLobbies.LOBBYSET_ALL;

  msg_id = pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.CHAT, chat_pb2.MsgId_RequestChatLobbies, False);
  print "Sending Request for ChatLobbies:";
  chat_listing_id = rs.request(msg_id, rp)

  requests.append(chat_listing_id);

  # Now iterate through all the responses.
  next_req_cycle = [];
  for peer_req_id in requests:

    # wait for responses.

    ans = rs.response(peer_req_id, timeout);
    if ans:
      (msg_id, msg_body) = ans;
      print "Received Response: msg_id: %d" % (msg_id);
      resp = parser.construct(msg_id, msg_body);
      if resp:
        print "Parsed Msg:";
        print resp;
        # Handle chat_listing results....
        if (peer_req_id == chat_listing_id):
          print "Handling ChatLobby Response";
          for lobby in resp.lobbies:
            CHANINFO[lobby.lobby_id+""]=lobby
            MCHANINFO[lobby.lobby_id]=max(MCHANINFO.get(lobby.lobby_id,-1),lobby.no_peers)
            cond=False
            if WHITELIST and not (WHITELIST == []):
                cond= lobby.lobby_name in WHITELIST
            else:
                cond = not bldict.has_key(lobby.lobby_name)
            if lobby.lobby_state == chat_pb2.ChatLobbyInfo.LOBBYSTATE_PUBLIC  and cond :
              # lets try and join it!
              # Request to Join ChatLobby.

                    
              rp = chat_pb2.RequestJoinOrLeaveLobby();
              rp.lobby_id = lobby.lobby_id;
              rp.action = chat_pb2.RequestJoinOrLeaveLobby.JOIN_OR_ACCEPT;
              msg_id = pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.CHAT, chat_pb2.MsgId_RequestJoinOrLeaveLobby, False);
              print "Sending Request to Join Public ChatLobby %s" % (lobby.lobby_name);
              req_id = rs.request(msg_id, rp)
              next_req_cycle.append(req_id);
            else:
              print "Ignoring Other Type of ChatLobby %s" % (lobby.lobby_name);
      else:
        print "Unable to Parse Response";
  
    else:
      print "No Response!";
      continue;

  # Add 
  requests = next_req_cycle;
 
  # wait for a bit, and retry.
  print "Waiting For Chat Events:";
  for i in range(5):
    #print "Sleeping Briefly";
    time.sleep(1);

    more_resp = True;
    while(more_resp):
      # wait for responses.
      ans = rs.response(chat_register_id, timeout);
      if ans:
        (msg_id, msg_body) = ans;
        print "Received Response: msg_id: %d" % (msg_id);
        resp = parser.construct(msg_id, msg_body);
        if resp:
          try:
            messo=html2text.html2text(resp.msg.msg)
            messo=messo.strip(' \t\n\r')
          except:
            pass
          if (msg_id == chatevent_msg_id):
              print resp.msg.id.chat_id
              lobba= CHANINFO.get(resp.msg.id.chat_id+"",False)
              print CHANINFO
              print lobba
              try:
                outa=process_message(messo,lobba)
              except:
                outa=False
              if outa is not False:
                  print outa
                  rp = chat_pb2.RequestSendMessage();

                  rp.msg.id.chat_type = resp.msg.id.chat_type;
                  rp.msg.id.chat_id = resp.msg.id.chat_id;

                  rp.msg.msg = outa;
                  msg_id = pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.CHAT, chat_pb2.MsgId_RequestSendMessage, False);
                  req_id = rs.request(msg_id, rp)
                  requests.append(req_id);

        else:
          pass
          #print "Unable to Parse Response";
      else:
        #print "No Response!";
        more_resp = False;
  

comms.close();






