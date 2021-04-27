from pushbullet import Pushbullet
from datetime import datetime
from lxml import html
import requests as r
import schedule, time

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import smtplib
import os

pb = Pushbullet(os.getenv('PushBullet'))
Sender = os.getenv('EmailSender')
password = os.getenv('Password')
Receiver = os.getenv('MainEmail')

def SendEmailAndNotification(msg, weather, time):
    # Send notification
    push = pb.push_note('IMPWeatherNotification', f'Будет {weather} в {time}')
    
    # Email text
    sep = "="
    msg = MIMEText('time  |  weather  |  temp  | feelslike |  prec  |  hum  |  wind\n' + msg, 'plain', 'utf-8')
    msg['Subject'] = Header('WeatherNotification', 'utf-8')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(Sender, password)
        smtp.sendmail(Sender, Receiver, msg.as_string())



def collectInfo(link='https://weather.com/ru-RU/weather/hourbyhour/l/0bcfa52f378b07303d9323a15f35704271c930f777e8e8b93261be77cacc3b88#detailIndex4'):
    page = r.get(link)
    tree = html.fromstring(page.content)
    text = ''
    
    print('time  |  weather  |  temp  | feelslike |  prec  |  hum  |  wind')
    for x in range(1,4):
        el = tree.xpath(f'//*[@id="WxuHourlyCard-main-74f43669-10ed-4577-a8c4-85ad9d041036"]/section/div[2]/details[{x}]')[0]
        time = el.cssselect('.DetailsSummary--daypartName--1Mebr')[0].text_content()
        weather = el.find_class('DetailsSummary--extendedData--aaFeV')[0].text_content()
        temp = el.find_class('DetailsSummary--tempValue--RcZzi')[0].text_content()
        feelslike = el.find_class('DetailsTable--value--1F3Ze')[0].text_content()
        prec = el.find_class('DetailsSummary--precip--2ARnx')[0][1].text_content()
        hum = el.find_class('DetailsTable--DetailsTable--2qH8C')[0][2][1][1].text_content()
        wind = el.find_class('DetailsSummary--wind--Cv4BH DetailsSummary--extendedData--aaFeV')[0][1].text_content().split()[1]
        
        info = f'{time}  |  {weather}  |   {temp}   |    {feelslike}    |    {prec}   |  {hum}   |  {wind} км/ч'
        
        print(info)
        text += info + '\n'
        if ('дожд' in weather.lower()):
            SendEmailAndNotification(text, weather, time)
            return


schedule.every(0.1).minutes.do(collectInfo)
while True:
    schedule.run_pending()
    time.sleep(1)
