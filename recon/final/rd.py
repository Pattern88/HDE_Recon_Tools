from Robots import Robots
from bruteForceAdminPanel import AdminPanel
from googleDorking import GoogleDorking
from Netcraft import Netcraft
from bruteForceFindSubDomain import SubDomain
from IpAndGeoL import GeoLocation
from Facebook import Facebook
from linkedin import Linkedin
from emailFinder import WebCr
from Metadata import Metadata
import time

val = raw_input("Enter Domain for start: ")

try:
	clear = Controller(val)
	clear.dropAllTables()
	print "Clear ;)"
except:
	"Error: Can't drop al tables"


rb = Robots(val)
print "#########Sleep 10 seconds"
time.sleep(10)
gd = GoogleDorking(val)
print "######Sleep 10 seconds"
time.sleep(10)
ap = AdminPanel(val)
print "######Sleep 10 seconds"
time.sleep(10)
n  = Netcraft(val)
print "######Sleep 10 seconds"
time.sleep(10)
sd = SubDomain(val)
print "######Sleep 10 seconds"
time.sleep(10)

gl = GeoLocation(val)
print "######Sleep 10 seconds"
time.sleep(10)

l = Linkedin(val)
print "######Sleep 10 seconds"
time.sleep(10)

f = Facebook(val)
print "######Sleep 10 seconds"
time.sleep(10)

wc = WebCr(val)
print "######Sleep 10 seconds"
time.sleep(10)

m = Metadata(val)
print "######Sleep 10 seconds"
time.sleep(10)


