import requests

openPrice = []
params = {
  'access_key': 'd0f9f1d896641cb03a9849109b690917'
}

api_result = requests.get('http://api.marketstack.com/v1/tickers/BAJAJ_AUTO.XNSE/eod', params)

api_response = api_result.json()
print(api_response['data']['eod'][0]['date'])

for stock_data in api_response['data']['eod']:
  openPrice.append(stock_data['close'])
  
print(openPrice)
