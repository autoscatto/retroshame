#!/usr/bin/python

# Clone of Basic Example to connect to rs-nogui.
# thanks to Retroshare authors! <3

import sys
import pyrs.comms
import pyrs.rpc
import pyrs.msgs
import time

# Message Definitions.
from pyrs.proto import core_pb2
from pyrs.proto import peers_pb2
from pyrs.proto import system_pb2
from pyrs.proto import chat_pb2

import pyrs.test.auth
# This will load auth parameters from file 'auth.txt'
# ONLY use for tests - make the user login properly.
auth = pyrs.test.auth.Auth()

#----------------------------------------------------------------------------
#### nickname del joinino
NICKNAME="botulino"

### tempo d'attesa (sec) tra un check di chat event e l'altro 
TIMEOUT=10

#### le lobbies blacklistate non verranno joinate
BLACKLIST=["casapau","emmamarronefans","retroshare devel","IRC Bridge"]

### le lobbies redlistate non saranno sensibili a !kill
REDLIST=["eigenLab"]

### True se il bot deve far uscire il client dalla lobbies alla chiusura del bot stesso
LEAVEONEXIT=True

#----------------------------------------------------------------------------
LOBBIES={}
REDL={}

# Construct a Msg Parser.
parser = pyrs.msgs.RpcMsgs()

# create comms object.
comms = pyrs.comms.SSHcomms(auth.user, auth.pwd, auth.host, auth.port)
comms.connect()

rs = pyrs.rpc.RsRpc(comms) 

timeout = 0.5
requests = []
# Firstly we subscribe to Chat Events.

# Request for Chat Lobbies.
rp = chat_pb2.RequestChatLobbies()
rp.lobby_set = chat_pb2.RequestChatLobbies.LOBBYSET_ALL
msg_id = pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.CHAT, chat_pb2.MsgId_RequestRegisterEvents, False)
chat_register_id = rs.request(msg_id, rp)
requests.append(chat_register_id)

# change the default nickname to PyChatBot.
rp = chat_pb2.RequestSetLobbyNickname()
rp.nickname = NICKNAME
msg_id = pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.CHAT, chat_pb2.MsgId_RequestSetLobbyNickname, False)
req_id = rs.request(msg_id, rp)
requests.append(req_id)

# wait for responses for initial commands.
for peer_req_id in requests:
  ans = rs.response(peer_req_id, timeout)
  if ans:
      (msg_id, msg_body) = ans
      resp = parser.construct(msg_id, msg_body)
      if not resp:
        print "Unable to Parse Response"
  else:
      print "No Response!"
  
requests = []

# Reference Msg IDs.
chatevent_msg_id = pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.CHAT, chat_pb2.MsgId_EventChatMessage, True)


time.sleep(10)


def join_leave(lid,join):
     rp = chat_pb2.RequestJoinOrLeaveLobby()
     rp.lobby_id = lid
     if join:
        rp.action = chat_pb2.RequestJoinOrLeaveLobby.JOIN_OR_ACCEPT
     else:
        rp.action = chat_pb2.RequestJoinOrLeaveLobby.LEAVE_OR_DENY 

     msg_id = pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.CHAT, chat_pb2.MsgId_RequestJoinOrLeaveLobby, False)
     req_id = rs.request(msg_id, rp)
     return req_id

# This script only logs in once!
# while(True): # for more cycles.
while(True):
      bldict={}
      for blr in BLACKLIST:
            bldict[blr]=True
      print "Starting new fetch cycle"

      # Request for Chat Lobbies.
      rp = chat_pb2.RequestChatLobbies()
      rp.lobby_set = chat_pb2.RequestChatLobbies.LOBBYSET_ALL

      msg_id = pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.CHAT, chat_pb2.MsgId_RequestChatLobbies, False)
      print "Sending Request for ChatLobbies"
      chat_listing_id = rs.request(msg_id, rp)

      requests.append(chat_listing_id)

      # Now iterate through all the responses.
      next_req_cycle = []
      for peer_req_id in requests:

        # wait for responses.

        ans = rs.response(peer_req_id, timeout)
        if ans:
          (msg_id, msg_body) = ans
          resp = parser.construct(msg_id, msg_body)
          if resp:
            # Handle chat_listing results....
            if (peer_req_id == chat_listing_id):
              sys.stdout.write("Handling ChatLobby Response\t")
              for lobby in resp.lobbies:
                if lobby.lobby_state == chat_pb2.ChatLobbyInfo.LOBBYSTATE_PUBLIC:
                  LOBBIES[lobby.lobby_name]=lobby.lobby_id
                  if not bldict.has_key(lobby.lobby_name): ## faccio la req solo se non sono blacklistato
                      print ""
                      print "-"*20
                      print u"Sending Request to Join Public ChatLobby %s" % ((lobby.lobby_name).encode('utf-8'))
                      print "-"*20
                      req_id = join_leave(lobby.lobby_id,True)
                      next_req_cycle.append(req_id)
                      if lobby.lobby_name in REDLIST:
                            REDL[str(lobby.lobby_id)]=False
                else:
                  #print "Ignoring Other Type of ChatLobby %s" % (lobby.lobby_name)
                  sys.stdout.write("[.]")
          else:
            sys.stdout.write("[Unable to Parse Response]")
      
        else:
          sys.stdout.write("No Response!")
          continue

      # Add 
      requests = next_req_cycle
     
      # wait for a bit, and retry.
      print "\nWaiting For Chat Events"
      try:
        time.sleep(TIMEOUT)    ## ctrl-c entra in "prompt" mode (TODO: e' la scelta giusta? magari threaddare?)
      except KeyboardInterrupt: ## TODO una interazione seria (part, addblacklist, reload etc)
        inp = raw_input( 'chattino$ ' )
        if(inp in ["Exit","exit","Quit","quit"] ):
            break
        if(inp in ["leave"]):
            inp=raw_input( 'channel to leave: ' )
            l_id=LOBBIES.get(inp,False)
            if(l_id):
                  req_id = join_leave(l_id,False)
                  BLACKLIST.append(inp)
                  next_req_cycle.append(req_id)
        if(inp in ["listlobbies"]):
            print LOBBIES.keys()
        if(inp in ["join"]):
            inp=raw_input( 'channel to join: ' )
            l_id=LOBBIES.get(inp,False)
            if(l_id):
                  req_id = join_leave(l_id,True)
                  BLACKLIST = [value for value in BLACKLIST if value!=inp]
                  next_req_cycle.append(req_id)

      more_resp = True
      while(more_resp):
       ans = rs.response(chat_register_id, timeout)
       if ans:
        (msg_id, msg_body) = ans
        resp = parser.construct(msg_id, msg_body)
        if "!kill" in msg_body:
                if REDL.get(str(resp.msg.id.chat_id),True):
                  print "KILLED!!!!!!!!!!!!"
                  inv_map = dict((LOBBIES[k], k) for k in LOBBIES)
                  bb=inv_map.get(resp.msg.id.chat_id,False)
                  if bb:
                    BLACKLIST.append(bb)
                    req_id = join_leave(resp.msg.id.chat_id,False)
                    next_req_cycle.append(req_id)

       else:
        more_resp = False

## fuori dal ciclo
# esco dalle lobbi in cui sono
if LEAVEONEXIT:
    for l_id in LOBBIES.values():
                  req_id = join_leave(l_id,False)
                  rs.response(req_id, timeout)
comms.close()

