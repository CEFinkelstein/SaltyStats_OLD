# SaltyStats 1.0

SaltyStats is a stat tracker for Salty Bet. It records a variety of
information, such as win/loss records, fight outcomes, and upsets. At the
beginning of a fight, it displays relavant information about the fight's two
combatants.

SaltyStats works by reading messages sent in Salty Bet's twitch chat by the 
bot "Waifu4u". In order to use SaltyStats, you will need to provide your
Twitch login information (in the form of a username and OAuth token) so the
program can connect to Salty Bet's Twitch IRC chat. SaltyStats should have a
config.conf file that you can input this information into, but if the file
does not exist for some reason, you can run SaltyStats to create one.

SaltyStats does not come with and stats and it will not bet for you. It is a
tool that makes stat tracking easier, not a betting bot. It only displays
information that you have recorded, meaning that its records become more
reliable the longer you use it. Please do not share your records with other
users, as Salty Bet discourages stat sharing.


## Setup

You need Python in order to run SaltyStats. You can download it from
python.org.

Additionally, you need to configure the config file, config.cfg. If you do
not have a config file, simply run SaltyStats and it will create one for you.

Below is some information about each setting in config.cfg:

- username: Your Twitch username. SaltyStats needs this to connect to Salty
Bet's IRC channel.

- oauth: For security reasons, Twitch does not allow you to connect to an IRC
channel using your Twitch password. Twitch IRC uses OAuth tokens instead. An
OAuth token looks like "oauth:asdasd234asd234ad234asds23". You can generate
an OAuth token by going to http://twitchapps.com/tmi/.

- statfile: The location/name of the file SaltyStats saves records to. By
default, this is stats.p in the same directory as the SaltyStats program.


## Use

"saltystats.py" is the main SaltyStats program. Running it will record and
display fight information for matchmaking fights on Salty Bet. SaltyStats
does not record or display information for tournaments and exhibitions.
However, you can still access your records during those fights using
SaltyStats Console. Running "console.py" will launch SaltyStats Console,
which will allow you to manually search and view your recorded information.