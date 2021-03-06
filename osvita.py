#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-

import requests
import json
import pprint
import sys
#import codecs
#import locale
import multiprocessing
import threading
import logging
import argparse
import datetime

_ = lambda x: x

#sys.stdout = codecs.getwriter("cp1251")(sys.stdout, errors='replace')

# class MyPrettyPrinter(pprint.PrettyPrinter):
#     def format(self, object, context, maxlevels, level):
#         if isinstance(object, unicode):
#             return (object.encode('utf8'), True, False)
#         return pprint.PrettyPrinter.format(self, object, context, maxlevels, level)

# pp = MyPrettyPrinter()
#58b318baabd93dbbf97d3094 - 143
#58b55b17abd93dbbf97f6717 - 457
# hline = 80*"-"
# delim ='\t'
loggers_map = {}
logging_DUMP = 1
def log(name, level, msg, *args, **kwargs):
	global loggers_map
	if not name in loggers_map:
		loggers_map[name] = logging.getLogger(name)
	logger = loggers_map[name]
	logger.log(level, msg, *args, **kwargs)

def log_error(name, msg, *args, **kwargs):
	log(name, logging.ERROR, msg, *args, **kwargs)

def log_warn(name, msg, *args, **kwargs):
	log(name, logging.WARNING, msg, *args, **kwargs)

def log_info(name, msg, *args, **kwargs):
	log(name, logging.INFO, msg, *args, **kwargs)

def log_debug(name, msg, *args, **kwargs):
	log(name, logging.DEBUG, msg, *args, **kwargs)

def log_dump(name, msg, *args, **kwargs):
	log(name, logging_DUMP , msg, *args, **kwargs)

def log_dump_json(label, js):
	log("dump-json", logging_DUMP , "DUMP [{0}] BEGIN\n{1}\nDUMP [{0}] END ".format(label, json.dumps(js, indent=2)))

def validate_json(j):
	if u'data' in j and len(j[u'data']) > 0:
		return j[u'data']
	else:
		raise RuntimeError('Returned invalid json ')

def get_my_orders(email):
	log_debug('get_my_order', 'get_my_order(%s)', email)
	r = requests.get('https://osvita.kievcity.gov.ua/v1/requests?email='+email)
	r.raise_for_status()

	my_infos = validate_json(r.json())
	log_info('get_my_order', "got my_info[%d] for email %s", len(my_infos), email)

	infos = {}
	for my_info in my_infos:
		kg_list = []
		for crit_rec in my_info[u'criterias']:
			if crit_rec[u'key'] == u'kindergartenId':
				for val in crit_rec['values']:
					kg_list += [val]
		log_info('get_my_order', "Order %s number of gindergardens %d", my_info[u'registrationNumber'], len(kg_list))
		log_dump_json("my_info", my_info)

		infos[my_info[u'registrationNumber']] = (my_info, kg_list)
	return infos

def slice_by(lst, key = lambda x: x):
	last_key = False
	last_pos = 0
	for curr_pos, it in enumerate(lst):
		curr_key = key(it)
		if last_key and last_key != curr_key:
			yield last_key, lst[last_pos:curr_pos], curr_key
			last_pos = curr_pos
		last_key = curr_key
	yield last_key, lst[last_pos:], None     

def cmp_by_queueNumber(a, b):
	cmp_res =  int(str(a[u'queueNumber'])[0:-4]) - int(str(b[u'queueNumber'])[0:-4])
	if cmp_res>0:
		return 1
	elif cmp_res<0:
		return -1
	return 0


def get_kg_info(kd_id):
	log_debug('get_kg_info', 'get_kg_info(%s)', str(kd_id))

	r = requests.get('https://osvita.kievcity.gov.ua/v1/kindergartens/'+kd_id)
	r.raise_for_status()

	kg_info = validate_json(r.json())[0]

	kg_edrpou = kg_info[u'edrpou']

	r = requests.get('https://osvita.kievcity.gov.ua/v1/kindergartens_state?edrpou='+kg_edrpou)
	r.raise_for_status()

	kg_state = validate_json(r.json())[0]
	
	isActive = kg_state[u'isActive']
	return kg_info, isActive

def get_kg_orders(kd_id):
	log_debug('get_kg_orders', u'get_kg_orders(%s)', str(kd_id))
	r = requests.get('https://osvita.kievcity.gov.ua/v1/requests/main_info?with_selected_kindergarten='+kd_id)
	r.raise_for_status()
	all_orders = []
	all_orders = validate_json(r.json())

	last_order_id = all_orders[-1][u'_id']
	r = requests.get('https://osvita.kievcity.gov.ua/v1/requests/main_info?with_selected_kindergarten='+kd_id+'&request_to='+last_order_id)
	r.raise_for_status()

	all_orders += validate_json(r.json())

	valid_orders = [req for req in all_orders if req[u'statuses'][-1][u'name'].lower() in [u'approved',u'need-additional-check',u'invite-sent',u'invite-accepted',u'invite-declined']]
	
	log_info('get_kg_orders', u'got %d orders where %d valid ', len(all_orders), len(valid_orders))
	log_debug('get_kg_orders', u'group orders by year and age')

	orders_grouped_by_year = {}
	for year, orders_sub_range, _ in slice_by(valid_orders, lambda order: order[u'periodFrom']):
		if year not in orders_grouped_by_year: orders_grouped_by_year[year] = []
		orders_grouped_by_year[year] += orders_sub_range

	queues = {}

	for year, orders_for_year in orders_grouped_by_year.iteritems():

		if not year in queues: queues[year] = {}

		sorted_orders = sorted(orders_for_year, key=lambda order: order[u'ageLimitFrom'])
		sliced_orders = {}
		places_in_sub_group = []
		for age, orders_for_age, _ in slice_by(sorted_orders, lambda order: order[u'ageLimitFrom']):
			orders_sorted_queueNumber = sorted(orders_for_age, cmp=cmp_by_queueNumber)
			queues[year][age] = orders_sorted_queueNumber
	return queues 	

def find_order_in_kg_orders(my_order, orders_for_year_and_age, current_kg_id):
	log_debug('find_order_in_kg_orders', u'find_order_in_kg_orders(%s, orders_for_year_and_age[%d])', my_order[u'child'][u'birthCertificate'][u'number'], len(orders_for_year_and_age))
	for year, orders_for_age in orders_for_year_and_age.iteritems():
		for age, orders_by_queue_number in orders_for_age.iteritems():
			accepted  = 0
			pending = 0
			for index, order in enumerate(orders_by_queue_number, 1):
				if my_order[u'statuses'][-1][u'name'] != u'removed':
					if u"invite" in order:
						if order[u"invite"][u'isInviteAccepted'] == True:
							accepted += 1;		
						if order[u"invite"][u'isInviteDeclined'] != True:
							#datetime.datetime.strptime( order[u"invite"][u"expiryDate"], "%Y-%m-%dT%H:%M:%S" )
							pending += 1;
					if my_order[u'child'][u'birthCertificate'][u'number'] == order[u'child'][u'birthCertificate'][u'number'] and\
						my_order[u'registrationNumber'] == order[u'registrationNumber']:
					
						return [True, current_kg_id, year, age, index, order, accepted, pending]

	return [False, current_kg_id]

def setup_logging_in_chald_process(logs_params):
	logging.basicConfig(**logs_params)

def find_child_place_in_kg(req):
	kg_id = req[0]
	my_order = req[1]
	logs_params = req[2]
	#setup_logging_in_chald_process(logs_params)

	log_info("find_child_place_in_kg" , u"try to find child(%s) in kg(%s) orders", my_order[u'child'][u'birthCertificate'][u'number'], str(kg_id))
	orders_for_year_and_age = get_kg_orders(kg_id);
	orders_log =''
	for year, orders_for_age in orders_for_year_and_age.iteritems():
		orders_log += u"\t{year}:\n".format(year=str(year))
		for age, orders_by_queue_number in orders_for_age.iteritems():
			orders_log += u"\t\t{age} років, кількість заявок {orders_num}\n".format(age=str(age), orders_num=len(orders_by_queue_number))
	log_debug("find_child_place_in_kg" ,u"fetched orders:\n%s", orders_log)
	return find_order_in_kg_orders(my_order, orders_for_year_and_age, kg_id)

def kg_info_as_tuple(kg_id):
	return (kg_id, get_kg_info(kg_id))

def try_format(fmt_str, *args, **kwargs):
    result = ''
    try:
        result = fmt_str.format(*args, **kwargs)
    except (IndexError, KeyError, ValueError ) as e:
        pass
    finally:
        return result 

def try_format_list(list_fmt_str, *args, **kwargs):
    results = []
    for tmpl in list_fmt_str:
        results += [try_format(tmpl, *args, **kwargs)]
    return results 

def try_format_list_with_format_spec(list_fmt_str, list_fmt_spec, *args, **kwargs):
    results = []
    list_fmt_spec += [{}] *(len(list_fmt_str) - len(list_fmt_spec))
    for tmpl, fmt_spec in zip(list_fmt_str, list_fmt_spec):
        kwargs.update(fmt_spec)
        results += [try_format(tmpl, *args, **kwargs)]
    return results


def guess_format_spec_from_header(cols_format, **header_dict):
    cols_format_spec = []
    for col_fmt in cols_format:
        if 'align' in col_fmt:
            rendered_col = try_format(col_fmt, width=0, align='<', **header_dict)
            cols_format_spec += [{'width':len(rendered_col), 'align':'<' }]
        else:
            rendered_col = try_format(col_fmt, width=0, **header_dict)
            cols_format_spec += [{'width':len(rendered_col) }]
    return cols_format_spec

def main(opts, logs_params):
	my_infos = get_my_orders(opts.email)
	#kg_list=kg_list[1:2]
	delim = u'|'
	header_dict = { 
		  'order_number':u'Заявка №'
		, 'order_status':u'Статус заявки'
		, 'kg_infos':{'number':u'Номер садочка', 'name':u'Назва садочка'}
		, 'yearFromTo':u'Навчальний рік'
		, 'ageFromTo':u'Группа'
		, 'place':u'Місце в черзі' 
		, 'accepted':u'Прийняті' 
		, 'pending':u'Запрошенні' 
	}
	cols_format = [
	      u'{order_number:17}'
	    , u'{order_status:{align}{width}}'
	    , u'{kg_infos[number]:{align}{width}}'
	    , u'{kg_infos[name]:<40}'
	    , u'{yearFromTo:{align}{width}}'
	    , u'{ageFromTo:{align}{width}}'
	    , u'{place:{align}{width}}'
	    , u'{accepted:{align}{width}}'
	    , u'{pending:{align}{width}}'
	]


		#       u'{order_number:17}'
		# , u'{order_status:21}'
		# , u'{kg_infos[number]:14}'
		# , u'{kg_infos[name]:40}'
		# , u'{yearFromTo:14}'
		# , u'{ageFromTo:8}'
		# , u'{place:13}'
		# , u'{inactive:37}'
    
	cols_format_spec = guess_format_spec_from_header(cols_format, **header_dict )

	if opts.tabulated:
		headers = try_format_list_with_format_spec(cols_format, cols_format_spec, **header_dict ) 
		header = delim.join(headers)
		print(header)
		print(u'-'*len(header))
	for reg, info in my_infos.iteritems():
		status_map = {
			u"removed":u"видалена",
			u"approved":u"підтверджена",
			u"invite-sent":u"запрошення надіслане",
			u"need-check":u"перевіряеться"
		}
		my_order = info[0]
		kg_list = info[1]
		log_dump_json("info[u'statuses']", my_order[u"statuses"])
		order_status = my_order[u"statuses"][-1][u"name"]
		order_status_s = order_status
		if order_status in status_map: order_status_s = status_map[order_status]

		number_of_kg = len(kg_list)
		if opts.my_orders_only: continue
		search_results = []
		if order_status in  [u'approved', u"invite-sent"]:
			requests_pool = multiprocessing.Pool(number_of_kg)

			mapped_kg_find_requests = zip(kg_list, [my_order]*number_of_kg, [logs_params]*number_of_kg)
			log_info('main', u"obtaining kg orders in parallel [\n%s]", ',\n'.join([u"\tfind \'%s\' in kg:%s"%(req[1][u'child'][u'birthCertificate'][u'number'], str(req[0])) for req in mapped_kg_find_requests]))
			
			search_results = requests_pool.map(find_child_place_in_kg, mapped_kg_find_requests )
			#requests_poll.join()
			kg_infos = dict(requests_pool.map(kg_info_as_tuple, [res[1] for res in search_results if res[0] ] ))
		if not opts.tabulated:
			print(u'Заявка №{0} [{1}]'.format(reg, order_status_s))
		for res, kg_id, year, age, idx, order, accepted, pending in search_results:
			if res:
				#kg_info, active = get_kg_info(kg_id);
				if not opts.tabulated:
					print(u'\tСадочок №{0[number]}: {0[name]} - Навчальний рiк {1}/{2} группа від {3} до {4} років, позиція у черзі {5}'.format(
						kg_infos[kg_id][0]
					 	, year
					 	, order[u'periodTo']
					 	, age
					 	, order[u'ageLimitTo']
					 	, idx)) 
				else:

					row_dict = {
						'order_number':reg
						, 'order_status':order_status_s
						, 'kg_infos':kg_infos[kg_id][0]
						, 'yearFromTo':"%d-%d"%(year, order[u'periodTo'])
						, 'ageFromTo':"%d-%d"%(age, order[u'ageLimitTo'])
						, 'place':idx 
						, 'accepted':accepted
						, 'pending':pending
						}

					row = try_format_list_with_format_spec(cols_format, cols_format_spec, **row_dict ) 
					print delim.join(row)
		if not opts.tabulated:
			print('')

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description=_("utility to fetch the place in the line of kindergardens of registered child"))
	parser.add_argument('email', help=_("registered emails"))
	parser.add_argument('-v',  dest='verbosity', default=0, action='count', help=_('verbosity level'))
	parser.add_argument('-n',  dest='my_orders_only', default=False, action='store_true', help=_("load only orders, without places in line"))
	parser.add_argument('-t',  dest='tabulated', default=False, action='store_true', help=_("tabled output"))
	logging_presets = {
		0:{'format':'%(message)s', 'level':logging.WARNING},
		1:{'format':'[%(name)s] %(message)s', 'level':logging.INFO},
		2:{'format':'%(asctime)-15s %(levelname)-8s %(name)-60s %(message)s', 'level':logging.DEBUG},
		3:{'format':'%(asctime)-15s %(levelname)-8s [%(process)s:%(processName)s] %(name)-60s %(message)s', 'level':logging.DEBUG},
		4:{'format':'%(asctime)-15s %(levelname)-8s [%(process)s:%(processName)s] %(name)-60s %(message)s', 'level':logging_DUMP}
	}
	min_verbosity_preset, max_verbosity_preset = min(logging_presets.keys()), max(logging_presets.keys())
	opts = parser.parse_args()
	logs_params = logging_presets[max(min_verbosity_preset, min(opts.verbosity, max_verbosity_preset))]
	logging.basicConfig(**logs_params)

	main(opts, logs_params)