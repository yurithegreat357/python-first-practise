import logging
import xmlrpclib

log = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s: %(asctime)s: %(message)s', level=logging.INFO)

# specify the server IP address and port number
host = "10.74.157.35"
port = 9997

# make a request to XML-RPC server and control the switch to make a connection.
proxy = xmlrpclib.ServerProxy("http://%s:%s/" % (host, port))
log.info("Make a IQMax connection")
log.info("Start to recall example_TQMAX_test from server--CPP machine")
ret=proxy.step1()
ret=proxy.step2()
ret=proxy.step3()
log.info("Complete example_TQMAX_test from server--CPP machine")
log.info("Please Check the log from server--CPP machine(IP:10.74.157.35)")
