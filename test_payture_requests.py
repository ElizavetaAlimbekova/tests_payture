import requests  # запрос на импорт
import time      # время импорта

stage_url = 'https://sandbox3.payture.com'  # url к которой обращаемся


def create_payment_session(order_id, amount):   # функция, условие, переменные
	params = {                                  # заданные параметры
		'Key': 'Merchant',
		'Data':
			f'SessionType=Pay;OrderId={order_id};Amount={amount};'
			f'Product=Ticket;Total={amount / 100};Phone=79156783333;Description=MyTestTransaction;'
			'Url=https://payture.com/result?orderid={orderid}&result={success};'
			'AdditionalField1=Value1;AdditionalField2=Value2'
	}
	requests.post(f'{stage_url}/apim/Init', params=params)   # запрос


def block_payment_session(order_id, key, amount):  # функция, условие, переменные
	params = {                                     # заданные параметры
		'Key': key,
		'Amount': amount,
		'OrderId': order_id,
		'PayInfo': f"PAN=654111111111100000; \
					EMonth=12; \
					EYear=22; \
					CardHolder=Ivan Ivanov; \
					SecureCode=123; \
					OrderId=115e6dea-b076-2617-45b2-072cb8c9121f; \
					Amount={amount}"
	}
	return requests.post(f'{stage_url}/api/Block', params=params)  # запрос с возвратом значений


def unblock_payment_session(order_id, key):   # функция, условие, переменные
	params = {
		'Key': key,
		'OrderId': order_id
	}
	return requests.post(f'{stage_url}/api/Unblock', params=params)  # запрос с возвратом значений


def charge_payment_session(order_id, key):   # функция, условие, переменные
	params = {                               # заданные параметры
		'Key': key,
		'OrderId': order_id
	}
	return requests.post(f'{stage_url}/api/Charge', params=params)   # запрос с возвратом значений


def get_payment_state(order_id, key):  # функция, условие, переменные
	params = {                     # заданные параметры
		'Key': key,
		'OrderId': order_id
	}
	return requests.post(f'{stage_url}/api/GetState', params=params)   # запрос с возвратом значений


class TestPayture:  # создается класс
	amount = 12735   # неизменные значения
	key = "Merchant"

	def test_new_payment_block(self):   # функция, оператор self указает на принадлежность к данному классу
		"""
		Проверка блокировки новой payment session
			1. Создать payment session
			2. Заблокировать payment session
			Результат:
			1. Статус код блокировки = 200
			2. Success="True" в response блокировки
			3. State="Authorized" в response get state запросе
		"""
		order_id = int(time.time())
		create_payment_session(order_id, self.amount)

		response = block_payment_session(order_id, self.key, self.amount)
		state_response = get_payment_state(order_id, self.key)
		assert response.status_code == 200
		assert 'Success="True"' in response.text
		assert 'State="Authorized"' in state_response.text

	def test_charge_payment_block(self):
		"""
		Проверка оплаты заблокированного платежа
            1. Создать payment session
			2. Перевести payment session в статус Charged
			3. Заблокировать платеж в статусе Charged
            Результат:
            1. Статус код блокировки = 200
            2. Success="False" в response блокировки
            3. ErrCode="DUPLICATE_ORDER_ID"
	    """

		order_id = int(time.time()) + 1
		create_payment_session(order_id, self.amount)
		block_response = block_payment_session(order_id, self.key, self.amount)
		assert block_response.status_code == 200
		assert 'Success="True"' in block_response.text
		charge_response = charge_payment_session(order_id, self.key)
		assert charge_response.status_code == 200
		assert 'Success="True"' in charge_response.text
		assert 'State="Charged"' in get_payment_state(order_id, self.key).text
		dublicate_block_response = block_payment_session(order_id, self.key, self.amount)
		assert dublicate_block_response.status_code == 200
		assert 'Success="False" ErrCode="DUPLICATE_ORDER_ID"' in dublicate_block_response.text

	def test_unblock_payment_block(self):
		"""
			Проверка блокировки разблокированного  платежа
				1. Создать payment session
			    2. Заблокировать payment session
				3.Перевести payment session в Unblock
				4.Заблокировать payment session в состояние Unblock
				Результат:
				1. Статус код блокировки = 200
				2. Success="False" в response блокировки
				3. ErrCode="DUPLICATE_ORDER_ID"
		"""

		order_id = int(time.time()) + 2
		create_payment_session(order_id, self.amount)
		block_response = block_payment_session(order_id, self.key, self.amount)
		assert block_response.status_code == 200
		assert 'Success="True"' in block_response.text
		unblock_response = unblock_payment_session(order_id, self.key)
		assert unblock_response.status_code == 200
		assert 'Success="True"' in unblock_response.text
		assert 'State="Voided"' in get_payment_state(order_id, self.key).text
		dublicate_block_response = block_payment_session(order_id, self.key, self.amount)
		assert dublicate_block_response.status_code == 200
		assert 'Success="False" ErrCode="DUPLICATE_ORDER_ID"' in dublicate_block_response.text
