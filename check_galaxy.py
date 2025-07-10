import requests
import xml.etree.ElementTree as ET 
from datetime import datetime
import argparse
from discord import SyncWebhook
from dateutil.tz import tzlocal


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--domain", default="de", type=str)
    parser.add_argument("-u", "--universe", default=199, type=int)
    parser.add_argument("-g", "--galaxy", default=None, type=int)
    parser.add_argument("-s", "--system", default=None, type=int)
    parser.add_argument("-p", "--position", default=None, type=int)
    parser.add_argument("-w", "--webhook", default=None, type=str)
    parser.add_argument("-t", "--tag", type=str)
    args = parser.parse_args()
    url = f"https://s{args.universe}-{args.domain}.ogame.gameforge.com/api/universe.xml"
    response = requests.get(url)
    filename = 'universe.xml'
    with open(filename, 'wb') as file:
        file.write(response.content)
    tree = ET.parse(filename)
    root = tree.getroot()
    timestamp = datetime.fromtimestamp(int(root.get('timestamp'))).astimezone(tzlocal()).strftime('%d.%m.%Y %H:%M:%S Uhr')
    timestamp_filename = f'timestamp{args.universe}.txt'
    with open(timestamp_filename, 'w+') as file:
        old_timestamp = file.read()
        if not args.webhook or timestamp != old_timestamp:
            file.write(timestamp)
            open_coords = []
            galaxies = []
            for planet in root.findall('planet'):
                coords = planet.get("coords")
                coord_list = coords.split(":")
                galaxy = coord_list[0]
                if galaxy not in galaxies:
                    galaxies.append(galaxy)
                    for system in range(1, 500):
                        for position in range(1, 16):
                            if (args.galaxy is None or args.galaxy == galaxy) and (args.system is None or args.system == system) and (args.position is None or args.position == position):
                                open_coords.append(f"{galaxy}:{system}:{position}")
                if (args.galaxy is None or int(coord_list[-3]) == args.galaxy) and (args.system is None or int(coord_list[-2]) == args.system) and (args.position is None or int(coord_list[-1]) == args.position):
                    open_coords.remove(coords)
            if len(open_coords) > 0 and args.tag is not None:
                message = args.tag + "\n"
            else:
                message = "Keine "
            message += f"Freie 8er {timestamp}"
            for coord in open_coords:
                message += f"\n- {coord}"
            if args.webhook:
                webhook = SyncWebhook.from_url(args.webhook)
                webhook.send(message)
            else:
                print(message)