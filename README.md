# TuvaluBot

to run the interwiki bot the following should be done:
* create a config folder for your wiki, copy inciclopedia or uncyclopedia ones. It will need to be passed as first argument to the program 
* edit your configuration files: config.json should include your wiki name, language, etc. Display_language for now must be either ``es`` or ``en``, it is the language of the program, the rest, change to your wiki language
* interwiki.json should be the beforementioned interwikis JSON file, so you should go to Special:Interwiki and double check all the listed (and working!) interwikis are in the JSON file (otherwise it might remove interwikis you have in your wiki but not in the file)
* create a bot user and give it a password in Special:BotPasswords

Install Python 3 (https://www.python.org/), clone the project, then from a terminal run in the project folder:

```bash
python -m pip install requirements.txt
```

And finally to run the bot:

```bash
python scripts/interwiki/interwiki_remapper.py wiki_name_as_in_config_folder YourUserName@BotName BotPasswordYouCreated
```

And the query editor will pop up.
