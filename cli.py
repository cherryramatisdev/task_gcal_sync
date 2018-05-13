from clize import run
import os
from datetime import datetime
from tzlocal import get_localzone
from taskw import TaskWarrior

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

folder = os.path.expanduser('~/.task_sync_gcal')
try:
    os.mkdir(folder)
except OSError:
    pass
client_id = os.path.join(folder, 'client_id.json')
credentials = os.path.join(folder, 'credentials.json')
calendar_id = open(os.path.join(folder, 'calendar_id')).read().strip()


def clear():
    tw = TaskWarrior(marshal=True)
    tasks = tw.load_tasks()
    pending_tasks = tasks['pending']
    for t in pending_tasks:
        if 'gcal_id' in t:
            _delete_event(t['gcal_id'])
            t['gcal_id'] = ''
            tw.task_update(t)


def sync_to():
    tw = TaskWarrior(marshal=True)
    tasks = tw.load_tasks()
    pending_tasks = tasks['pending']
    for t in pending_tasks:
        if 'gcal_id' in t:
            print('Updating task {} remotely...'.format(t['id']))
            try:
                _add_or_update_event_from_task(t, gcal_event_id=t['gcal_id'])
            except ValueError as ex:
                print(ex)
        else:
            print('Adding task remotely {}...'.format(t['id']))
            try:
                event = _add_or_update_event_from_task(t)
            except ValueError as ex:
                print(ex)
            else:
                t['gcal_id'] = event['id']
                tw.task_update(t)


def sync_from():
    tw = TaskWarrior(marshal=True)
    tasks = tw.load_tasks()
    pending_tasks = tasks['pending']

    task_from_gcal_id = {}
    for t in pending_tasks:
        if 'gcal_id' in t:
            task_from_gcal_id[t['gcal_id']] = t
    events = _get_events()
    for ev in events:
        if ev['id'] in task_from_gcal_id:
            t = task_from_gcal_id[ev['id']]
            start = ev['start']['dateTime']
            end = ev['end']['dateTime']
            t['scheduled'] = _parse_datetime(start)
            t['due'] = _parse_datetime(end)
            print('Updating task {} locally'.format(t['id']))
            tw.task_update(t)


def _get_events():
    service = _get_service()
    events = service.events().list(calendarId=calendar_id).execute()
    return events['items']


def _delete_event(event_id):
    service = _get_service()
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()


def _add_or_update_event_from_task(task, gcal_event_id=None):
    if 'scheduled' not in task:
        raise ValueError('Task {} has no scheduled specified. '
                         'Please do that in task warrior'.format(task['id']))
    service = _get_service()
    desc = task['description']
    timezone = str(get_localzone())
    start = task['scheduled']
    start = _format_datetime(start)
    if 'due' in task:
        end = task['due']
        end = _format_datetime(end)
    else:
        end = start
    body = {
        'summary': desc,
        'description': desc,
        'start': {'dateTime': start, 'timeZone': timezone},
        'end': {'dateTime': end, 'timeZone': timezone},
    }
    if gcal_event_id:
        event = service.events().update(
            calendarId=calendar_id,
            eventId=gcal_event_id,
            body=body,
        ).execute()
    else:
        event = service.events().insert(
            calendarId=calendar_id,
            body=body).execute()
    return event


def _parse_datetime(s):
    if '+' in s:
        s = s[0:s.index('+')]
    dt = datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")
    return dt


def _format_datetime(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def _get_service():
    SCOPES = 'https://www.googleapis.com/auth/calendar'
    store = file.Storage(credentials)
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(client_id, SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))
    return service


if __name__ == '__main__':
    run([sync_from, sync_to, clear])
