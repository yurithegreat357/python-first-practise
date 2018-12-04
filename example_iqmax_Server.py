from SimpleXMLRPCServer import SimpleXMLRPCServer
from example_iqmax import *

log = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s: %(asctime)s: %(message)s', level=logging.INFO)

# specify the server IP address and port number
host = "10.74.157.35"
port = 9997

# register a function to respond to XML-RPC requests and start XML-RPC server
server = SimpleXMLRPCServer((host, port))
log.info("Server %s Listening on port %d..." % (host, port))
server.register_function(step1, "step1")
server.register_function(step2, "step2")
server.register_function(step3, "step3")

server.register_instance(example_IQMAX_test("192.168.106.19"))
server.serve_forever()