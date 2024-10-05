
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from icalendar import Calendar, Event
from dateutil.rrule import WEEKLY
import requests
from bs4 import BeautifulSoup


##シラバスのURL
url = "https://www.ocw.titech.ac.jp/index.php?module=General&action=T0300&JWC=202402445&lang=JA&vid=03"

startHour = {
'1': "8",
'3': "10",
'5': "13",
'7': "15",
'9': "17"
}
startMinute = {
'1': "50",
'3': "45",
'5': "30",
'7': "25",
'9': "15"
}

endHour = {
'2' : '10',
'4' : '12',
'6' : '15',
'8' : '17',
'10': '18'
}
endMinute = {
'2' : '30',
'4' : '25',
'6' : '10',
'8' : '05',
'10': '55'
}

startMonth = {
'3Q': '10',
'4Q': '12'
}

startDay = {
'3Q': '3',
'4Q': '6'
}
endMonth = {
'3Q': '11',
'4Q': '2'    
}
endDay = {
'3Q': '21',
'4Q': '3'
}

day_abbreviations = {
    '月': 'Mo',  # Monday
    '火': 'Tu',  # Tuesday
    '水': 'We',  # Wednesday
    '木': 'Th',  # Thursday
    '金': 'Fr',  # Friday
    '土': 'Sa',  # Saturday
    '日': 'Su'   # Sunday
}


day_to_number = {
    'Mo': 0,  # Monday
    'Tu': 1,  # Tuesday
    'We': 2,  # Wednesday
    'Th': 3,  # Thursday
    'Fr': 4,  # Friday
    'Sa': 5,  # Saturday
    'Su': 6   # Sunday
}

res = requests.get(url)
res.encoding = res.apparent_encoding
soup = BeautifulSoup(res.text, 'html.parser')


#class name (2024年度　動的システム   Dynamical Systems)
h3_text = soup.find('h3').text
h3_text_splitted = re.split(r'[\u3000\xa0]+', h3_text)
className = h3_text_splitted[2] + "(" + h3_text_splitted[1]+ ")"
year = int(h3_text_splitted[0][:4])

#time and place(火1-2(W2-402(W242))  金1-2(W2-402(W242))  )
dd_text = soup.find('dd', class_='place').decode_contents()
dd_text = dd_text.replace(' ', '')
dd_text = dd_text.replace('\n', '')
dd_text = dd_text.replace('\xa0', '')
before_parentheses = dd_text.split('(') 

# 2. 各部分を処理し、)で分割
timeAndPlace = []
for part in before_parentheses:
    # )で分割し、必要な部分を取得
    split_part = part.split(')')
    
    for part2 in split_part:
        if part2.strip():  # 空でない場合のみ追加
            timeAndPlace.append(part2.strip())



#quarter
quarter_dd = soup.find('dt', string='開講クォーター').find_next_sibling('dd')
# <dd>タグの内容を取得し、前後の空白を削除
quarter = quarter_dd.text.strip()





weekdays = ['月', '火', '水', '木', '金', '土', '日']
timeWeekly = []
timePeriodStart = []
timePeriodEnd = []
location = []
for elem in timeAndPlace:
    if elem[0] in weekdays:
        timeWeekly.append(day_abbreviations[elem[0]])
        timePeriodStart.append(elem[1])
        timePeriodEnd.append(elem[3])
    else:
        if (len(location) == (len(timeWeekly)-1)):
            location.append(elem)
        else:
            location[-1] = location[-1] + "(" + elem + ")"



print(className) #Dynamical Systems(動的システム)
print(year) #2024
print(timeWeekly) #['Tu', 'Fr']
print(timePeriodStart) #['1', '1']
print(timePeriodEnd) #['2', '2']
print(location) #['W2-402(W242)', 'W2-402(W242)']
print(quarter) #3Q

# カレンダーの生成
cal = Calendar()
cal.add('prodid', '-//Test//test-product//ja//')
cal.add('version', '2.0')
cal.add('calscale', 'GREGORIAN')

for i in range(len(timeWeekly)):

    # 開始日時の設定
    quarterStartDate = datetime(year, int(startMonth[quarter]), int(startDay[quarter]))
    weekdayNum = int(day_to_number[timeWeekly[i]])

    if quarterStartDate.weekday() != weekdayNum:  
        days_until_thursday = (weekdayNum - quarterStartDate.weekday()+7) % 7
        
        classStartDate=quarterStartDate + timedelta(days=days_until_thursday)
    else:
        classStartDate= quarterStartDate

 




    # イベントの作成
    event = Event()
    event.add('summary', className)  # イベントのタイトル
    event.add('dtstart', classStartDate.replace(hour = int(startHour[timePeriodStart[i]]),minute = int(startMinute[timePeriodStart[i]])) )  # 開始日時
    event.add('dtend', classStartDate.replace(hour = int(endHour[timePeriodEnd[i]]),minute = int(endMinute[timePeriodEnd[i]]))) # 終了日時
    event.add('dtstamp', datetime.now())  # タイムスタンプ
    event.add('location', location[i])  # 場所
    event.add('description', url)

    # 毎週の繰り返し設定（2024年12月10日まで毎週木曜日）
    event.add('rrule', {
        'freq': 'weekly',  # 毎週
        'until': datetime(year,  int(endMonth[quarter]), int(endDay[quarter]), 23, 59, 0),  # 終了日
        'byday': timeWeekly[i],  # 木曜日に繰り返し
    })

    # イベントをカレンダーに追加
    cal.add_component(event)

# カレンダーをファイルに保存
filename = h3_text_splitted[2].replace(" ", "")+".ics"
with open(filename, 'wb') as f:
    f.write(cal.to_ical())