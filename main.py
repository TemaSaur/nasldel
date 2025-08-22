import requests
import sys
import os
import pandas as pd
import traceback
from datetime import datetime


URL = 'https://notariat.ru/api/probate-cases'

data = []


def find(name, birth_date):
	try:
		response = requests.post(URL, json={'name': name, 'birth_date': birth_date, 'death_date': 'NULL'})
		return response.json()
	except Exception:
		print('запрос не работает капец')
		traceback.print_exc()
	return None



## example
# find('Иванов Сергей Александрович', '19381201', '20070610')


def get_output_path():
	with open('./config.txt') as f:
		path = f.readline().strip()
		try:
			os.makedirs(path)
		except FileExistsError:
			pass
		return path


def fdate(date):
	s = str(date)
	return s[:4] + s[5:7] + s[8:10]


def fixrecord(record) -> dict:
	"""flatten record into a single dict"""
	# todo: check
	return record


def do(df):
	for line in df.index:
		row = df.iloc[line]
		name = " ".join(row[k] for k in ('Фамилия', 'Имя', 'Отчество'))
		birth_date = fdate(row['Рождение'])

		datum = find(name, birth_date)

		if datum is None:
			continue

		assert 'count' in datum, 'формат ответа сломался'

		for record in datum['records']:
			frecord = fixrecord(record)
			assert isinstance(frecord, dict), 'с сайта вернулось непонятно что'
			data.append({'ФИО': name} | frecord)

if __name__ == '__main__':
	if len(sys.argv) >= 2:
		file_path = sys.argv[1]
	else:
		file_path = input('input file: ')
	print('читаю', file_path)
	try:
		df = pd.read_excel(file_path)
	except Exception as e:
		print('не читается файл')
		traceback.print_exc()
		sys.exit()

	do(df)

	res = pd.DataFrame(data)
	res.to_excel(os.path.join(get_output_path(), f'{datetime.today().strftime("%y%m%d%H%M%S")}.xlsx'), index=False)
