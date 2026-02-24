import discord
from discord.ext import commands, tasks
import feedparser
import asyncio
import datetime
import re
import functools
import os

# --- CONFIGURATION ---
TOKEN = ""
CHANNEL_ID = 1474715102329700515  
DB_FILE = "archives_cyber.txt"

SOURCES = {
    "CERT-FR": ("https://www.cert.ssi.gouv.fr/alerte/feed/", "🇫🇷"),
    "CISA": ("https://www.cisa.gov/cybersecurity-advisories/all.xml", "🇺🇸"),
    "The Hacker News": ("https://feeds.feedburner.com/TheHackersNews", "🇺🇸"),
    "BleepingComputer": ("https://www.bleepingcomputer.com/feed/", "🇺🇸"),
    "Microsoft Security": ("https://api.msrc.microsoft.com/report/v1.0/rss/", "🇺🇸"),
    "JPCERT English": ("https://www.jpcert.or.jp/english/at/rss.xml", "🇯🇵"),
    "NIST-NVD": ("https://nvd.nist.gov/feeds/xml/cve/misc/nvd-rss.xml", "🇺🇸"),
    "FBI-IC3": ("https://www.ic3.gov/rss/default.aspx", "🇺🇸"),
    "Cisco Talos": ("https://talosintelligence.com/rss_feed", "🇺🇸"),
    "Google Security": ("https://feeds.feedburner.com/GoogleOnlineSecurityBlog", "🇺🇸"),
    "Mandiant": ("https://www.mandiant.com/resources/blog/rss.xml", "🇺🇸"),
    "FortiGuard": ("https://www.fortiguard.com/rss/ir.xml", "🇺🇸"),
    "NISC JP": ("https://www.nisc.go.jp/rss/nisc.rdf", "🇯🇵"),
    "TrendMicro JP": ("https://blog.trendmicro.co.jp/feed/", "🇯🇵"),
    "Kaspersky JP": ("https://blog.kaspersky.co.jp/feed/", "🇯🇵"),
    "IPA Japan": ("https://www.ipa.go.jp/security/rss/index.rdf", "🇯🇵")
}

# Variable globale pour éviter le double scan simultané
is_scanning = False

def load_archives():
    if not os.path.exists(DB_FILE): return set()
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return set(f.read().splitlines())

def archive_link(link):
    with open(DB_FILE, "a", encoding="utf-8") as f:
        f.write(link + "\n")

def clean_desc(text):
    if not text: return "Détails disponibles sur le lien."
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&[a-z0-9#]+;', ' ', text)
    return (text[:350] + "...") if len(text) > 350 else text

async def fetch_rss(url):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, functools.partial(feedparser.parse, url))

class SmartView(discord.ui.View):
    def __init__(self, articles):
        super().__init__(timeout=None)
        self.articles = articles
        self.index = 0
    def create_embed(self):
        art = self.articles[self.index]
        embed = discord.Embed(
            title="🔔 Nouvelle Alerte Cyber", 
            description=f"**[{art['flag']} {art['source']}] {art['title']}**\n\n{art['desc']}", 
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Lien", value=f"[Lire l'article]({art['link']})")
        embed.set_footer(text=f"Article {self.index + 1}/{len(self.articles)}")
        return embed
    @discord.ui.button(label="◀", style=discord.ButtonStyle.gray)
    async def prev(self, i, b):
        self.index = (self.index - 1) % len(self.articles)
        await i.response.edit_message(embed=self.create_embed())
    @discord.ui.button(label="▶", style=discord.ButtonStyle.gray)
    async def next(self, i, b):
        self.index = (self.index + 1) % len(self.articles)
        await i.response.edit_message(embed=self.create_embed())

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@tasks.loop(hours=2.0)
async def cycle_veille():
    await run_scanner()

async def run_scanner():
    global is_scanning
    if is_scanning: return # Si déjà en train de scanner, on annule le 2ème
    
    is_scanning = True
    print(f"🔍 Scan des flux ({datetime.datetime.now().strftime('%H:%M')})...")
    new_stuff = []
    archives = load_archives()
    
    for name, (url, flag) in SOURCES.items():
        if len(new_stuff) >= 10: break
        try:
            feed = await fetch_rss(url)
            for entry in feed.entries[:5]:
                if entry.link not in archives:
                    new_stuff.append({
                        'source': name, 'flag': flag, 'title': entry.title,
                        'desc': clean_desc(entry.get('summary', entry.get('description', ''))),
                        'link': entry.link
                    })
                    archive_link(entry.link)
                    if len(new_stuff) >= 10: break
        except: continue
    
    if new_stuff:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            view = SmartView(new_stuff)
            await channel.send(embed=view.create_embed(), view=view)
            print(f"✅ {len(new_stuff)} nouveaux articles postés.")
    
    is_scanning = False # Scan terminé, on libère le verrou

@bot.event
async def on_ready():
    print(f"🚀 Bot Veille Connecté : {bot.user}")
    # On vérifie si la tâche tourne déjà pour ne pas la lancer 2 fois
    if not cycle_veille.is_running():
        cycle_veille.start()

# --- LANCEMENT ---
if __name__ == "__main__":
    token_env = os.getenv('DISCORD_TOKEN')
    
    if token_env:
        bot.run(token_env)
    else:
        print("ERREUR : La variable d'environnement 'DISCORD_TOKEN' est manquante.")