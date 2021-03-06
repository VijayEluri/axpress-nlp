# Google Talk constants
FROM_GMAIL_ID = "zdwiel@gmail.com"
try :
  GMAIL_PASS = open('/home/dwiel/.gmpw').read().strip()
except IOError :
  GMAIL_PASS = None
GTALK_SERVER = "talk.google.com"
TO_GMAIL_ID = "zdwiel@gmail.com"

def send_im(vars) :
  import xmpp

  message = vars['msg']
  addr = vars['addr']
  
  jid=xmpp.protocol.JID(FROM_GMAIL_ID)
  cl=xmpp.Client(jid.getDomain(),debug=[])
  if not cl.connect((GTALK_SERVER,5222)):
    vars['response'] = 'Can not connect to server.'
    return
  if not cl.auth(jid.getNode(),GMAIL_PASS):
    vars['response'] = 'Can not auth with server.'
    return

  cl.send(xmpp.Message(addr, message))
  cl.disconnect()
  
  vars['response'] = "sent %s to %s" % (message, addr)

def loadTranslations(axpress) :
  axpress.n.bind('im', '<http://dwiel.net/axpress/im/0.1/>')
  axpress.n.bind('person', '<http://dwiel.net/axpress/person/0.1/>')
  rule = axpress.rule

  # this seems to be something different ... or maybe not :)
  # TODO: allow optionally accepting a person's name here for the response
  rule("send im", """
    person[person.email_address] = _addr
    message[string.text] = _msg
    ret = im.send(person, message)
  """, """
    ret[string.text] = _response
  """, send_im)
  
  rule("say hi", """
    foo[axpress.is] = "(say|send) hi to %person_str%"
  """, """
    person[axpress.is] = "%person_str%"
    message[string.text] = 'hi'
    foo = im.send(person, message)
  """)
