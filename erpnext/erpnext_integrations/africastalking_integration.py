import frappe
import requests
from frappe import _
import json

import africastalking
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement
from lxml import etree
import os 
import sys


@frappe.whitelist(allow_guest=True)
def handle_incoming_call(**kwargs):
	try:
		# at_settings = get_at_settings()
		# if not at_settings.enabled: return

		call_payload = kwargs
		status = call_payload.get('isActive')
		direction = call_payload.get('direction')
		if status == "0":
			return
			
		if direction == "Inbound":
			from werkzeug.wrappers import Response
			response = Response()
			response.mimetype = 'text/xml'
			response.charset = 'utf-8'
			response.data = '<?xml version="1.0" encoding="UTF-8"?><Response><Say voice="en-US-Standard-C" playBeep="false" >Welcome to UDA</Say></Response>'
			
			return response

		call_log = get_call_log(call_payload)
		if not call_log:
			create_call_log(call_payload)
		else:
			update_call_log(call_payload, call_log=call_log)

	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(title=_('Error in AT incoming call'))
		frappe.db.commit()


@frappe.whitelist(allow_guest=True)
def make_xm():
	from werkzeug.wrappers import Response
	response = Response()
	response.mimetype = 'text/xml'
	response.charset = 'utf-8'
	response.data = '<?xml version="1.0" encoding="UTF-8"?><Response><Say voice="en-US-Standard-C" playBeep="false" >Welcome to UDA</Say></Response>'
	
	return response

@frappe.whitelist(allow_guest=True)
def get_xml():
	from werkzeug.wrappers import Response
	response = Response()
	response.mimetype = 'text/xml'
	response.charset = 'utf-8'
	response.data = '<xml></xml>'

	return response

@frappe.whitelist(allow_guest=True)
def handle_end_call(**kwargs):
	update_call_log(kwargs, 'Completed')

@frappe.whitelist(allow_guest=True)
def handle_missed_call(**kwargs):
	update_call_log(kwargs, 'Missed')

def update_call_log(call_payload, status='Ringing', call_log=None):
	call_log = call_log or get_call_log(call_payload)
	if call_log:
		call_log.status = call_payload.get('callSessionState')
		call_log.to = call_payload.get('clientDialedNumber')
		call_log.duration = call_payload.get('durationInSeconds') or 0
		call_log.recording_url = call_payload.get('recordingUrl')
		call_log.save(ignore_permissions=True)
		frappe.db.commit()
		return call_log

def get_call_log(call_payload):
	call_log = frappe.get_all('Call Log', {
		'id': call_payload.get('sessionId'),
	}, limit=1)

	if call_log:
		return frappe.get_doc('Call Log', call_log[0].name)

def create_call_log(call_payload):
	call_log = frappe.new_doc('Call Log')
	call_log.id = call_payload.get('sessionId')
	call_log.to = call_payload.get('clientDialedNumber')
	call_log.type = call_payload.get('direction')
	call_log.medium = 'UDA Call Centre'
	call_log.status = call_payload.get('callSessionState')
	setattr(call_log, 'from', call_payload.get('callerNumber'))
	call_log.save(ignore_permissions=True)
	frappe.db.commit()
	return call_log

@frappe.whitelist()
def get_call_status(call_payload):
	status = call_payload.get('callSessionState')
	return status

@frappe.whitelist(allow_guest=True)
def make_a_call():
	endpoint = get_at_endpoint()
	callFrom = "+254711082496"
	callTo   = ["+254710974531"]
	try:
		response = endpoint.call(callFrom,callTo)
		return response
	except Exception as e:
		frappe.throw("Encountered an error while making the call:%s" %str(e))
    

@frappe.whitelist()
def fetch_queued_calls(to_number):
	endpoint = get_at_endpoint()
	response = endpoint.fetch_queued_calls(to_number)

	return response

def get_at_settings():
	return frappe.get_single('AfricasTalking Settings')

def whitelist_numbers(numbers, caller_id):
	endpoint = get_at_endpoint()
	response = requests.post(endpoint, data={
		'VirtualNumber': caller_id,
		'Number': numbers,
	})

	return response

@frappe.whitelist(allow_guest=True)
def get_capability_token():
	settings = get_at_settings()
	url = 'https://webrtc.africastalking.com/capability-token/request'
	payload = {
		'phoneNumber':'+254711082496',
		'clientName': 'bosire',
		'username': 'udaspcc'
	}

	headers = {
		'Content-Type': 'application/json',
		'apikey': '825e1826c5f52c83fa4039c3e8d865e061a2002d7613d93060c268b9a0754761'
	}
	r = requests.post(url, data=json.dumps(payload), headers=headers)
	return r.json()

def safe_identity(cls, identity: str):
	return identity.replace('@', '(at)')

def get_at_endpoint():
    settings = get_at_settings()
    africastalking.initialize(username=settings.username,api_key=settings.api_key)
    at_voice = africastalking.Voice
    return at_voice
