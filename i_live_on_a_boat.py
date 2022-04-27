import requests
city = 'alameda'
url = 'http://api.waqi.info/feed/' + city + '/?token='
api_key = '6b47ef379c416b27e36c33d9e9d4095789221068'

main_url = url + api_key
r = requests.get(main_url)
data = r.json()['data']
aqi = data['aqi']
iaqi = data['iaqi']
dew = iaqi.get('dew','Nil')
no2 = iaqi.get('no2','Nil')
o3 = iaqi.get('o3','Nil')
so2 = iaqi.get('so2','Nil')
pm10 = iaqi.get('pm10','Nil')
pm25 = iaqi.get('pm25','Nil')
pollen = iaqi.get('pol','Nil')

print(f'{city} AQI :',aqi,'\n')
print('Individual Air quality')
print('pm25 :',pm25['v'])
print('Dew :',dew['v'])
print('no2 :',no2['v'])
print('Ozone :',o3['v'])
print('sulphur :',so2['v'])
print('pm10 :',so2['v'])
