### Funding Alert

Search for Funding Fees using the coinglass API

**How to use the script
- Create an account on coinglass [Here](https://www.coinglass.com/pricing/ "Here") and "Get Free API Key".
- Install the necessary libraries with the following command:
````python
pip install -r requirements.txt
````
- rename or copy the config.example.json file and change it to config.json
- edit the config.json file
  - coinglass_apikey: enter the api here
  - funding: minimum value to search for coins e.g. 0.5 search for coins with funding greater than 0.5 or less than -0.5
  - minutes_revision: time in minutes to query, default is 5 minutes.

- To run it open a terminal and type the following command:
`python main.py`
- To edit it I recommend PyCharm
