# -*- coding: utf-8 -*- 
import sys
import os
import time, Cookie

#os.chdir('/www/uwsgi')
#os.chdir('/usr/share/uwsgi/www')

def parse_query_string(data):
	request_data = data.split('&')

	def parse_value(pair):
		pair = pair.split('=')
		pair[1] = ' '.join(pair[1].split('+'))
	
		return pair

	return dict(tuple(parse_value(pair) for pair in request_data))



def create_url(url, file_name = 'index.html'):
	if url == '':
		url = 'hello/{0}'.format(file_name)
	else:
		url_parts = [part for part in url.split('/') if part]
		
		if not '.' in url_parts[-1]:
			url_parts.append(file_name)

			url = '/'.join(url_parts)

	return url

def do_GET(environ, environ_values):
	response_body = ''
	url = create_url((environ_values['PATH_INFO'])[1:])

	print('url = ', url)

	if environ_values['QUERY_STRING']:
		data = parse_query_string(environ_values['QUERY_STRING'])
		response_body = '\n'.join(['<tr><td>{0}</td>\n<td>{1}</td></tr>'.format(key, value) for key, value in data.items()])
		
		with open(url, 'r') as file:
			response_body = file.read() % response_body
	elif url[-17:] == 'cookie/index.html':
		if environ.get('HTTP_COOKIE'):
			cookie = Cookie.SimpleCookie(environ['HTTP_COOKIE'])

			if 'page_visits' in cookie:
				cookie['page_visits'] = int(cookie['page_visits'].value) + 1
			else:
				cookie['page_visits'] = 1
		else:
			cookie = Cookie.SimpleCookie()
			cookie['page_visits'] = 1

		with open(url, 'r') as file:
			response_body = file.read() % cookie['page_visits'].value

		response_headers.append(('Set-Cookie',cookie['page_visits'].OutputString()))

	else:
		with open(url, 'r') as file:
			response_body = file.read()

	return response_body

def do_POST(environ, environ_values):
	response_body = ''
	education_dict = {'low': 'Низшее', 'middle': 'Среднее', 'high': 'Высшее'}
	sex_dict = {'male': 'Мужской', 'female': 'Женский'}
	spam_dict = {'on': 'Да', 'off': 'Нет'}
	url = create_url((environ_values['PATH_INFO'])[1:], file_name = 'post.html')
	length= int(environ_values['CONTENT_LENGTH'])
	request_data = environ['wsgi.input'].read(length).encode('utf-8')
	data = parse_query_string(request_data)
	
	print('post = ', request_data)
	
	with open(url, 'r') as file:
		response_body = (file.read()).format(name = data['name'], sex = sex_dict[data['sex']], education = education_dict[data['education']],
						comment = data['comment'].decode('utf-8'), spam = spam_dict[data.get('spam', 'off')])# % response_body

		return response_body

def application(environ, start_response):
	environ_values = dict(environ.items())
	response_body = ''
	response_headers = []

	print('PATH_INFO = ', environ_values['PATH_INFO'])
	print('QUERY_STRING = ', environ_values['QUERY_STRING'])
	
	if environ_values['REQUEST_METHOD'] == 'GET':
		response_body = do_GET(environ, environ_values)
	elif environ_values['REQUEST_METHOD'] == 'POST':
		response_body = do_POST(environ, environ_values)
	#for key, value in environ_values.items():
		#print('{0}: {1}'.format(key, value))
	response_headers.append(('Content-Type', 'text/html'))
	response_headers.append(('Content-Length', str(len(response_body))))
	
	start_response('200 OK', response_headers)

	return response_body
