from checkio_client.api import get_user_missions


def main(args):
    print('Requesting...')
    data = get_user_missions()
    station_groups = {}
    for item in data['objects']:
        station_groups.setdefault(item['stationName'], []).append(item)

    for station, data in sorted(station_groups.items(), key=lambda a: a[0]):
        print(station)
        for mission in data:
            line = '  '
            if mission['isSolved']:
                line += '+ '
            elif mission['isStarted']:
                line += '- '
            else:
                line += '  '
            line  += mission['slug']
            print(line)