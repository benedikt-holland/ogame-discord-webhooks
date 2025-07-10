import pandas as pd
import requests
import argparse
from discord import SyncWebhook
from os.path import exists

if __name__ == '__main__':
    parser = argparse.ArgumentParser()        
    parser.add_argument("-d", "--domain", type=str, default="de")
    parser.add_argument("-u", "--universe", type=int, default=199)
    parser.add_argument("-n", "--alliance-name", type=str)
    parser.add_argument("-t", "--alliance-tag", type=str)
    parser.add_argument("-w", "--webhook", type=str)
    parser.add_argument("-c", "--score-category", default=0, type=int, choices=range(8), help="Total, Economy, Research, Military, Military Built, Military Destroyed, Military Lost, Honor")
    args = parser.parse_args()
    for table in ["players", "alliances", "highscore"]:
        url = f"https://s{args.universe}-{args.domain}.ogame.gameforge.com/api/{table}.xml"
        if table == "highscore":
            url += f"?category=1&type={args.score_category}"
        response = requests.get(url)
        filename = f'{table}.xml'
        with open(filename, 'wb') as file:
            file.write(response.content)
    highscore = pd.read_xml("highscore.xml")
    players = pd.read_xml("players.xml")
    alliances = pd.read_xml("alliances.xml")
    if args.alliance_name is not None:
        alliance_id = alliances[alliances.name == args.alliance_name].id.iloc[0]
    elif args.alliance_tag is not None:
        alliance_id = alliances[alliances.tag == args.alliance_tag].id.iloc[0]
    else:
        parser.error("At least one of alliance-name or alliance-tag is required")
    players = players[players.alliance == alliance_id].join(highscore.set_index("id"), on="id")
    players["date"] = pd.Timestamp.today().date()
    players = players.drop(["id", "alliance"], axis=1)
    players["category"] = args.score_category
    players[["name","status","position","score","date","category"]].to_csv("highscore.csv", mode="a", header=None if exists("highscore.csv") else ["name","status","position","score","date","category"], index=None)
    history = pd.read_csv("highscore.csv")
    history = history[history["category"] == args.score_category]
    history = history.sort_values(["name", "date"])
    history = history.join(history[["position", "score"]].shift(), rsuffix="_prev")
    for col in ["score", "position"]:
        history[f"{col}_diff"] = history[col]-history[f"{col}_prev"]
    history["score_rel"] = (history["score"]-history["score_prev"]) / history["score_prev"] * 100
    history.dropna(inplace=True, axis=0)
    history = history.groupby("name").last().reset_index()
    history = history.sort_values("score_rel", ascending=False)
    history["position_diff"] = (history["position_diff"] * -1).astype(int)
    history["position_diff"] = history["position_diff"].apply(lambda x: f"{x:.0f}")
    history["score"] = history["score"].apply(lambda x: f"{x/1000000:,.0f}kk")
    history["score_diff"] = history["score_diff"].apply(lambda x: f"{x/1000000:,.0f}kk")
    history["score_rel"] = history["score_rel"].apply(lambda x: f"{x:.2f}%")
    history.rename({"name": "Spieler", "position": "Platz", "position_diff": "Δ#", "score": "Punkte", "score_diff": "Δ", "score_rel": "%"}, axis=1, inplace=True)
    table_text = history[["Spieler", "Platz", "Δ#", "Punkte", "Δ", "%"]].to_string(index=False)
    message = f"```{table_text}```"
    if args.webhook:
        webhook = SyncWebhook.from_url(args.webhook)
        webhook.send(message)
    else:
        print(message)