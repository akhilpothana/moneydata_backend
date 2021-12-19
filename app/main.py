from flask import Flask
from flask import jsonify
from flask import request

import requests
import json
import plaid

from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_account_filters import LinkTokenAccountFilters
from plaid.model.depository_filter import DepositoryFilter
from plaid.model.account_subtypes import AccountSubtypes
from plaid.model.account_subtype import AccountSubtype
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest

app = Flask(__name__)

configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': '61be77cfa1254d0013deef3a',
        'secret': '6f4e87a41a0e33f6a9eeb25a0de055',
        'plaidVersion': '2020-09-14'
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)
 
@app.route('/')
def index():
  return '<h1>I want to Deploy Flask to Heroku</h1>'

@app.route('/getLinkToken')
def getLinkToken():
    request = LinkTokenCreateRequest(
    products=[Products('auth'), Products('transactions')],
    client_name="Money Data",
    country_codes=[CountryCode('US')],
    language='en',
    webhook='https://sample-webhook-uri.com',
    link_customization_name='default',
    account_filters=LinkTokenAccountFilters(
        depository=DepositoryFilter(
            account_subtypes=AccountSubtypes(
                [AccountSubtype('checking'), AccountSubtype('savings')]
            )
        )
    ),
      user=LinkTokenCreateRequestUser(
          client_user_id='123-test-user-id'
      )
    )   
    response = client.link_token_create(request)
    link_token = response['link_token']
    return f'<p>{link_token}</p>'

@app.route('/api/set_access_token', methods=['POST'])
def get_access_token():
    global access_token
    global item_id
    global transfer_id
    public_token = request.form['public_token']
    try:
        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token)
        exchange_response = client.item_public_token_exchange(exchange_request)
        access_token = exchange_response['access_token']
        item_id = exchange_response['item_id']
        return jsonify(exchange_response.to_dict())
    except plaid.ApiException as e:
        return json.loads(e.body)