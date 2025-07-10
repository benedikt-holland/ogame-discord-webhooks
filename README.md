# Ogame Discord Webhooks
Collection of various Discord webhooks for the browser game Ogame
## Setup
```bash
python -m venv .venv/
source .venv/bin/activate
pip install -r requirements.txt
```
## Galaxy webhook
Scans universe data to find empty positions and posts them to Discord. Only posts once new data is available, usually once per week.
```bash
python check_galaxy.py
``` 
### Command line arguments
#### Required
- --domain Country code of your universe e.g. "de"
- --universe Id of your universe e.g. 199 (look at the link when you play: s199-de.ogame.gameforge.com)
- --webhook Webhook URL you get from Discord, if none is provided the program will just print to console instead of posting a Discord message
#### Optional
- --galaxy only look at one specific galaxy
- --system only look at one specific system accross multiple galaxies
- --position recommended, only look at one position in each system e.g. 8
- --tag Tag a specific user group in Discord with @ e.g. <@&1250104300550492210> (copy a message from Discord into a text editor to get the role code like this) 
## Highscore webhook
Posts the current highscore compared to the last execution of all players in an alliance
```bash
python highscore.py
```
### Command line arguments
- --domain Country code of your universe e.g. "de"
- --universe Id of your universe e.g. 199 (look at the link when you play: s199-de.ogame.gameforge.com)
- --webhook Webhook URL you get from Discord, if none is provided the program will just print to console instead of posting a Discord message
- --alliance-tag Tag of your alliance e.g. "ABC"
- --alliance-name Name of your alliance e.g. "ABC Alliance", either alliance-tag or alliance-name is required
- --score-category optional, Category of score to post: Total=0, Economy=1, Research=2, Military=3, Military Built=4, Military Destroyed=5, Military Lost=6, Honor=7