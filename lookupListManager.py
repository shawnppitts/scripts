import requests
import json
from datetime import datetime
import random
"""
Goal: This script needs to get expired items from the lookup list and remove them

Implementation: Since POST /v1/lookup-lists/{lookupListId}/elements/search only returns active items that are not expired
we cannot pop out the expired values. Instead we will need to 
	
	1. Fetch lookup list id from /v1/lookup-lists/search and store it in var	
	2. Fetch lookup list active elements from /v1/lookup-lists/{lookupListId}/elements/search and store them in list
	3. Delete original lookup list (DELETE /v1/lookup-lists/{id})
	4. Create new lookup list with title of original list and return new lookup list id
	5. Bulk update new lookup list with elements using /v1/lookup-lists/{lookupListId}/elements/bulk-add
"""
# GLOBAL VARIABLES
X_API_TOKEN = "<<API_TOKEN>>"
lookup_list_to_fetch = "<<LOOKUP_LIST_NAME>>"
now = datetime.utcnow()

def get_lookup_list(region, token, lookup_name):
	url = f"https://{region}/v1/lookup-lists/search"
	payload = json.dumps({
		"filter": {
			"searchTerm": lookup_name
		},
		"pagination": {
			"pageNumber": 1,
			"pageSize": 1000
		}
	})
	headers = {
    	"X-API-TOKEN": str(token),
    	"Content-Type": "application/json"
	}
	response = requests.request("POST", url, headers=headers, data=payload)
	response = response.json()
	return response

def get_lookup_list_elements(region, token, lookup_id, page):
	url = f"https://{region}/v1/lookup-lists/{lookup_id}/elements/search"
	payload = json.dumps({
		"pagination": {
			"pageNumber": page,
			"pageSize": 1000
		}
	})
	headers = {
    	"X-API-TOKEN": str(token),
    	"Content-Type": "application/json"
	}

	# print(f"GET {url}\n{payload}")
	response = requests.request("POST", url, headers=headers, data=payload)
	response = response.json()
	return response

def create_lookup_list(region, token, lookup_name):
	url = f"https://{region}/v1/lookup-lists"
	payload = json.dumps({
		"name": lookup_name
	})
	headers = {
    	"X-API-TOKEN": str(token),
    	"Content-Type": "application/json"
	}

	# print(f"POST {url}\n{payload}")
	response = requests.request("POST", url, headers=headers, data=payload)
	response = response.json()
	return response

def delete_lookup_list(region, token, lookup_id):
	url = f"https://{region}/v1/lookup-lists/{lookup_id}"
	payload = {}
	headers = {
    	"X-API-TOKEN": str(token),
    	"Content-Type": "application/json"
	}

	# print(f"POST {url}\n{payload}")
	response = requests.request("DELETE", url, headers=headers, data=payload)
	response = response.json()
	return response

def bulk_update_lookup_list(region, token, lookup_id, elements):
	url = f"https://{region}/v1/lookup-lists/{lookup_id}/elements/bulk-add"
	payload = json.dumps(elements)
	headers = {
    	"X-API-TOKEN": str(token),
    	"Content-Type": "application/json"
	}

	# print(f"POST {url}\n{payload}")
	response = requests.request("POST", url, headers=headers, data=payload)
	response = response.json()
	return response

def get_region_endpoint(region):
	if region == "us":
		return "api.logz.io"
	elif region == "au":
		return "api-au.logz.io"
	elif region == "ca":
		return "api-ca.logz.io"
	elif region == "eu":
		return "api-eu.logz.io"
	elif region == "nl":
		return "api-nl.logz.io"
	elif region == "uk":
		return "api-uk.logz.io"
	elif region == "wa":
		return "api-wa.logz.io"

api_region = get_region_endpoint("us")
print(f"\n{now} - Fetching original lookup list of {lookup_list_to_fetch}")
lookup = get_lookup_list(api_region, X_API_TOKEN, lookup_list_to_fetch)
lookup_id = lookup["results"][0]["id"]
lookup_name = lookup["results"][0]["name"]

page = 1
bulk_element_list = []
next_page = True
while next_page:
	print(f"\n{now} - Fetching elements in {lookup_id} on {page}")	
	lookup_elements = get_lookup_list_elements(api_region, X_API_TOKEN, lookup_id, page)	
	results = lookup_elements["results"]
	if results:
		bulk_element_list = lookup_elements["results"]
		page = page + 1
		next_page = True
	else:
		next_page = False

print(f"\n{now} - Deleting original lookup {lookup_id}")
deleted = delete_lookup_list(api_region, X_API_TOKEN, lookup_id)

print(f"\n{now} - Creating new lookup with title {lookup_name}")
created = create_lookup_list(api_region, X_API_TOKEN, lookup_name)
new_lookup_id = ""
try:
	new_lookup_id = created["id"]
	print(f"\n{now} Created new {lookup_name} lookup with id of {new_lookup_id}")	
except Exception as e:
	print(e)

num_elements = len(bulk_element_list)
print(f"\n{now} - Bulk updating {new_lookup_id} with {num_elements}")
bulk_updated = bulk_update_lookup_list(api_region, X_API_TOKEN, new_lookup_id, bulk_element_list)
print(bulk_updated)