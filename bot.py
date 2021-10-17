import os
from icalendar import Calendar, Event
from discord import Webhook, Client, RequestsWebhookAdapter
from dotenv import load_dotenv
import requests
import logging
from datetime import datetime, timedelta
import asyncio

load_dotenv()
# setup
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
url = 'https://discord.com/api/webhooks/{}'.format(os.getenv('WEBHOOK'))
calendar_url = 'https://www.eve-calendars.com/calendars/{}'.format(os.getenv('CALENDAR_FEED'))
client = Client()
webhook = Webhook.from_url(url, adapter=RequestsWebhookAdapter())
logging.basicConfig(filename='cal.log',
                    filemode='a',
                    format='%(asctime)s, %(name)s %(levelname)s %(message)s',
                    datefmt='%d/%m %H:%M:%S',
                    level=logging.INFO)
mylogger = logging.getLogger('Calendar_Client')


@client.event
async def on_ready():
    mylogger.info('Calendar pings are now running')
    webhook.send('Calendar pings are now running', username='Calendar pinger', avatar_url=os.getenv('LOGO'))


@client.event
async def on_error(event):
    mylogger.error(event)


def parse_ics():
    events = list()
    # download ICS file
    try:
        if os.path.exists("calendar.ics"):
            os.remove("calendar.ics")

        r = requests.get(calendar_url, allow_redirects=True)
        open('calendar.ics', 'wb').write(r.content)
    except Exception as e:
        mylogger.error(e)
    # open and parse ICS file, add events to list
    with open('calendar.ics', 'rb') as g:
        gcal = Calendar.from_ical(g.read())
        for component in gcal.walk():
            if component.name == "VEVENT":
                events.append(component)
    return events


async def sleepUntil(hour, minute):
    t = datetime.today()
    future = datetime(t.year, t.month, t.day, hour, minute)
    if t.timestamp() > future.timestamp():
        future += timedelta(days=1)
    await asyncio.sleep((future - t).total_seconds())


def check_today():
    events = parse_ics()
    pinged_today = list()
    for event in events:
        timestamp = event.get('dtstart').dt.replace(tzinfo=None)
        today = datetime.utcnow()
        delta = timestamp - today
        if delta.days == 0:
            pinged_today.append(event)
    return pinged_today


async def ping_today(pinged_today):
    for todays_event in pinged_today:
        now = datetime.utcnow()
        target = todays_event.get('dtstart').dt.replace(tzinfo=None)
        mylogger.info("Sleeping till event.")
        await asyncio.sleep((target - now).total_seconds())
        content = '@here \n **An event is starting: ** \n {0} {1}\n'.format((todays_event.get('dtstart').dt).strftime("%d/%m/%Y, %H:%M"), todays_event.get('summary'))
        webhook.send(content, username='Calendar pinger', avatar_url=os.getenv('LOGO'))

async def check_events():
    while True:
        mylogger.info("Beginning event check")
        pinged_today = check_today()
        if len(pinged_today) > 0:
            mylogger.info("Found events for today")
            await ping_today(pinged_today)
        else:
            mylogger.info("Waiting till tomorrow 3AM UTC")
            await sleepUntil(3, 00)


if __name__ == '__main__':
    client.loop.create_task(check_events())
    client.loop.run_forever()
    client.run(TOKEN)
