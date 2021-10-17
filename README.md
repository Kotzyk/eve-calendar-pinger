# eve-calendar-pinger
### A script meant to run on a remote server for EVE Online groups to get their ingame calendar events pinged in Discord

Because this script is meant to run on a remote server with high chance of no GUI access, to keep things simple, EVE SSO auth for downloading calendar events from the ESI has been handled using an [external service called eventical](https://github.com/lunohodov/eventical)

### Usage:
1. Authorize desired character in [eve-calendars.com](https://www.eve-calendars.com/) to be the source of the calendar feed
2. Find out your feed name: go to [My feed](www.eve-calendars.com/calendar) and copy the link to "Apple Calendar" - paste the `private-(...).ics` part into .env `CALENDAR_FEED`
3. [Create a webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) in the Discord channel you want your pings posted in and paste the URL after `https://discord.com/api/webhooks/` into `WEBHOOK`
4. Decide on a logo for your webhook messages and paste the image's URL into `LOGO`
5. Customize your ping format (for example change @here to @everyone or a specific role etc.) or the time of day at which the event checks are performed
6. Run the script 

To keep the script running perpetually you may want your OS to restart it always, for example with a system Service.
