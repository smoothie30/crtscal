import sys, feedparser, re, smtplib
from bs4 import BeautifulSoup
# time import mktime
from datetime import datetime
from datetime import timedelta
from optparse import OptionParser
# time_pattern = re.compile('\d\d?:\d\d [AP]M')

# things to search for
last_name = "Lee"
first_name = "Shannon"
teachers = []
teachers.append("Kavafian")
teachers.append("Steinhardt")
chamber_groups = []
chamber_groups.append("Chooi-Lee-Hlusko-Lee")
chamber_groups.append("Super Quartet")
chamber_groups.append("Lee-Crawford-Lin")
chamber_groups.append("Archduke")
chamber_groups.append("Stucky")
orchestras = []
extras = []
# don't wanna know their orchestra sectional times
not_sections = ["Wind","Brass","Percussion"]
# search results
events = []

parser = OptionParser()
# 1 for show, 0 for hide
parser.set_defaults(op_studio=1,op_chamber=1,op_orch=0)
parser.add_option("-s", type="int", dest="op_studio")
parser.add_option("-c", type="int", dest="op_chamber")
parser.add_option("-o", type="int", dest="op_orch")
parser.add_option("-e", dest="op_extra")
(options, args) = parser.parse_args()
# show orch related
if options.op_orch == 1:
	orchestras.append("Symphony 2")
	orchestras.append("Reading 2")
# hide studio related
if options.op_studio == 0:
	teachers = []
# hide chamber related
if options.op_chamber == 0:
	chamber_groups = []

# show extras only
if options.op_extra:
	teachers = []
	chamber_groups = []
	orchestras = []
	for ex in options.op_extra:
		extras.append(options.op_extra)

# search for events between today and 2 weeks from now
DAYS_FROM_NOW = 14
# rss feed info
feed_start = datetime.strftime(datetime.today(), "%m/%d/%Y")
feed_end = datetime.strftime(timedelta(days=DAYS_FROM_NOW) + datetime.today(), "%m/%d/%Y")
feed_url = 'http://commonroom.curtis.edu/Calendar/RSSSyndicator.aspx?category=&location=&type=Y&starting=' + feed_start + '&ending=' + feed_end + '&binary=Y&keywords=&ics=Y'
parsed_feed = feedparser.parse(feed_url)

def convert_date_format(orig_date):
	return datetime.strftime(datetime.strptime(orig_date, "%m/%d/%Y"), "%a, %b %d, %Y")

def get_details(i):
	info_dict = dict()

	soup = BeautifulSoup(i.description)
	all_br = soup.find_all("br")
	if len(all_br) != 0:
		bldg = all_br[0].next_element
		# we know what campus 1726 and Lenfest belong to
		bldg = bldg.replace("Curtis Institute of Music - ","")
		room = all_br[1].next_element
		# some events don't have rooms
		# add room if it exists
		if isinstance(room, basestring):
			info_dict["room"] = room
		info_dict["bldg"] = bldg
		descr = all_br[3].find_all_next(text=True)

	all_td = soup.td.find_all("td")
	# true if an all day event
	all_day = "All Day" in all_td[2].get_text()
	start_date = convert_date_format( all_td[1].get_text() )
	start_time = all_td[3].get_text()
	end_date = convert_date_format( all_td[5].get_text() )
	end_time = all_td[7].get_text()
	info_dict["all_day"] = all_day
	info_dict["start_date"] = start_date
	info_dict["start_time"] = start_time
	info_dict["end_date"] = end_date
	info_dict["end_time"] = end_time
	info_dict["descr"] = descr

	return info_dict

def print_info(i):
	d = get_details(i)
	# title
	s = i.title + '\n'
	# date
	s += '\t' + d["start_date"]
	if d["start_date"] != d["end_date"]:
		s += d["end_date"]
	# time OR all day
	if d["all_day"] == True:
		s += " - All Day" + '\n'
	else:
		s += " from " + d["start_time"] + " - " + d["end_time"] + "\n"
	# location
	if "bldg" in d:
		s += '\t' + d["bldg"]
	if "room" in d:
		s += ' - ' + d["room"]
	return s

output = ""
for i in parsed_feed.entries:
	# find personal events (lessons) by name AND teachers
	if last_name in i.title and first_name in i.title:
		if len(teachers) > 0 and any(teacher in i.title for teacher in teachers):
			temp = print_info(i) + '\n\n'
			output += "<font color=red>" + temp + "</font>"
			print "\033[.31m", temp, "\033[.0m", 
			events.append(i)
	# find studio events by teachers and "Studio"
	if len(teachers) > 0 and any(teacher in i.title for teacher in teachers):
		if "Studio" in i.title:
			temp = print_info(i) + '\n\n'
			output += "<font color=pink>" + temp + "</font>"
			print "\033[.35m", temp, "\033[.0m", 
			events.append(i)
	# find chamber events by group name
	if len(chamber_groups) > 0 and any(chamber in i.title for chamber in chamber_groups):
		temp = print_info(i) + '\n\n'
		output += "<font color=blue>" + temp + "</font>"
		print "\033[.36m", temp, "\033[.0m", 
		events.append(i)
	# find orchestra events by orchestra name
	if len(orchestras) > 0 and any(orch in i.title for orch in orchestras):
		if not any(not_section in i.title for not_section in not_sections):
			temp = print_info(i) + '\n\n'
			output += "<font color=gray>" + temp + "</font>"
			print "\033[.34m", temp, "\033[.0m", 
			events.append(i)
	# extras
	if len(extras) > 0 and any(extra in i.title for extra in extras):
		temp = print_info(i) + '\n\n'
		output += temp
		print "\033[.37m", temp, "\033[.0m", 
		events.append(i)

#print output

#import pdb #@@@
#pdb.set_trace() #@@@
#print 'stop here' #@@@

