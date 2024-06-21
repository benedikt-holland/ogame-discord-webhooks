import requests
import xml.etree.ElementTree as ET 
from datetime import datetime
import argparse
from discord import SyncWebhook
from dotenv import load_dotenv
import os
from dateutil.tz import tzlocal


if __name__ == '__main__':
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--domain", default="de", type=str)
    parser.add_argument("-u", "--universe", default=199, type=int)
    parser.add_argument("-g", "--galaxy", default=None, type=int)
    parser.add_argument("-s", "--system", default=None, type=int)
    parser.add_argument("-p", "--position", default=None, type=int)
    parser.add_argument("-n", "--galaxy-num", default=8, type=int)
    parser.add_argument("-de", "--debug", action='store_true', default=False)
    args = parser.parse_args()
    url = f"https://s{args.universe}-{args.domain}.ogame.gameforge.com/api/universe.xml"
    response = requests.get(url)
    with open('universe.xml', 'wb') as file:
        file.write(response.content)
    tree = ET.parse('universe.xml')
    root = tree.getroot()
    timestamp = datetime.fromtimestamp(int(root.get('timestamp'))).astimezone(tzlocal()).strftime('%d.%m.%Y %H:%M:%S Uhr')
    with open('timestamp.txt', 'rt') as file:
        old_timestamp = file.read()
    if args.debug or timestamp != old_timestamp:
        with open('timestamp.txt', 'wt') as file:
            file.write(timestamp)
        open_coords = []
        for galaxy in range(1, args.galaxy_num + 1):
            for system in range(1, 500):
                for position in range(1, 16):
                    if (args.galaxy is None or args.galaxy == galaxy) and (args.system is None or args.system == system) and (args.position is None or args.position == position):
                        open_coords.append(f"{galaxy}:{system}:{position}")
        for planet in root.findall('planet'):
            coords = planet.get("coords")
            coord_list = coords.split(":")
            if (args.galaxy is None or int(coord_list[-3]) == args.galaxy) and (args.system is None or int(coord_list[-2]) == args.system) and (args.position is None or int(coord_list[-1]) == args.position):
                open_coords.remove(coords)
        webhook = SyncWebhook.from_url(os.environ.get("DISCORD_WEBHOOK"))
        message = f"<@&1250104300550492210>\nFreie 8er {timestamp}"
        for coord in open_coords:
            message += f"\n- {coord}"
        if args.debug:
            print(message)
        else:
            webhook.send(message)