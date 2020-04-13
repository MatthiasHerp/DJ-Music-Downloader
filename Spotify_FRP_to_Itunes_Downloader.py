#Das Projekt: Spotify_FRP_to_Itunes_Downloader

#Ziel: erstellen eines automatischen Downloaders für DJS die in Spotify Songs für den Download speichern.

#Vorgehensweise:
#Das Programm erkennt in Spotify gespeicherte Songs in eigens angelegten Playlist.
#Diese Songs werden aus dem DJ Pool Franchise Record Pool (FRP) heruntergeladen sofern ein Abo besteht.
#Dabei wird ein selbst gewählter Entscheidungsbaum genutzt um die gewünschte Version zu erhalten.
#Diese Titel werden dann automatisch der Itunes Bibliothek hinzugefügt.
#Mithilfe von Tags werden die Titel automatisch den jeweils richtigen (intelligenten) Itunes Playlists hinzugefügt.
#Diese Tags werden anhand der Spotify Playlists gesetzt.
#Daher empfiehlt es sich in Spotify die individuelle Ordnerstruktur aus Itunes nach Bedarf nachzubauen.
#Danach müssen einfach Songs diesen Playlisten hinzugefügt werden und das Programm gestartet werden.
#Gefundene Titel erscheinen in Itunes und verschwinden aus der Spotify Playliste.

#Notwendige Daten sind:
#Eine Spotipy App von Spotify (kostenlos und in 2min erstellt) mit Client ID und Secret ID.
#Ein Spotify Nutername (kein Abo notwendig).
#Alle Spotifyplaylist-URIs und die Tags der dazugehörigen Itunes Playlists
#Die Pfade zu einem selbsterstellten Zwishenordner und dem Apple Musik "Hinzufügen" Ordner.
#Gültige Logindaten eines FRP Benutzers (mit kostenpflichtigem Abo).
#Die Informationen des Eigenen Browsers für den Crawler (in der Netzwerkspalte des Browser erhältlich). (optional)


#Alle notwendigen Packete werden importiert.

#Allg. notwendige Packete
import sys
import os

#Spotify Packete
import spotipy
import spotipy.util as util

#Crawler Packete
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.request import urlopen
from urllib.parse import quote
from urllib.request import urlretrieve
import ujson

#ID3 MP3 Tags Packete 
import eyed3
from eyed3.id3 import apple
GRP1 = apple.GRP1

#Datei Verschiebung Packet
import shutil

#Spotify Zugang über das Spotipy App Entwickler Packet von Spotify wird initialisiert.
#Der aktuelle Scope funktioniert mit öffentlichen Playlists
Client_ID = ''
Client_Secret = ''
Redirect_URI = 'https://www.google.de/'
Username =''
Scope ='playlist-modify-public'

try:
    token = util.prompt_for_user_token(Username,
                           Scope,
                           client_id=Client_ID,
                           client_secret=Client_Secret,
                           redirect_uri=Redirect_URI)
    print("SUCCESS")
except:
    print("FAILED TO LOAD")
    
    
#Spotifyobject wird erstellt das mit einem Token, gemäß dem gewählten Scope, authorisiert ist.
sp = spotipy.Spotify(auth=token)

#Liste an Spotifyplaylists in Tupeln mit dazugehörigen Spotify URIs und Itunes tags werden definiert.
#Hier werden einige Beispielplaylists gezeigt.
Twothousanders=('3kI7ipBpmOAcO61TDC2NJl', '2000er')
Dancehall=('3ES1D4H4BedWpGA5jYDxew', 'Dancehall')
Hip_Hop_New=('5mUyKeFpBaZqtBxq2rQ6eY','Hip_Hop_New')
Hip_Hop_New_School=('0k8usgEQQFw4zcmqatFvYU','Hip_Hop_New_School')
Hip_Hop_Old_School=('52qPzgUtgz2FmGXKg21IQa','Hip_Hop_Old_School')
Hip_Hop_Old_Old_School=('0RdLG3py7kk7f17i4JCte1','Hip_Hop_Old_Old_School')

Playlists=[Twothousanders,Dancehall,Hip_Hop_New,Hip_Hop_New_School,Hip_Hop_Old_School,Hip_Hop_Old_Old_School]

#Pfade für die Ordner für die Zwischenablage der Titel sowie für das hinzufügen der Titel zu der Apple Music Bibliothek.
Downloaded_Tracks = 'Pfad einsetzen'
Music_adding_folder = 'Pfad einsetzen'

#Informationen für den Crawler in form der Browserbezeichnung un der Logindaten für Franchise-Record-Pool (FRP)
# werden definiert.
headers_browser = {'Browser Informationen einsetze'
                  }
login_data = {
    'login': 'Benutzername einsetzen',
    'password': 'Passwort einsetzen',
}

#Optional:
#CSV Datei ansteuern um die Inforamtionen der Heruntergeladenen Titel abzuspeichern.
#Dies dient nur dazu spätere Analysen in Python zu vereinfachen.
#Bevor man das Programm startet sollte man die Csv Datei erstellen und kurz die Spalten definieren.
#spalten definieren mit: writer.writerow(["Artist", "Titel", "Playlist"])
writer = csv.writer(open("Spotify_FRP_to_Itunes_Downloader.csv", "w"))


#Sitzung in der der Benutzer in FRP eingeloggt ist wird erstellt.
with requests.Session() as s:
    url_login = 'https://www.franchiserecordpool.com/signin'
    r = s.post(url_login, data=login_data, headers=headers_browser)
    
#Für jede Playlist wird eine Songliste erstellt.
    for h in Playlists:
        to_delete=[]
        Songliste=[]
        results = sp.user_playlist(Username, h[0], fields='tracks', market='de')
        tracks = results['tracks']
        
#Jede Songliste enhält die Position in der Playlist, den Künstlernamen, den Titelnamen und die Spotify URI 
#des Songs sowie das Itunestag der Playlist aus der der Song gewonnen wurde.
        for j, item in enumerate(tracks['items']):
            track = item['track']
            Songliste.append([j, 
                              str(track['artists'][0]['name']), 
                              str(track['name'].split("(")[0].split("-")[0]), 
                              str(track['uri'].split("track:")[1]), 
                              h[1]])
            
#Jeder Song aus der Playlist wird in FRP anhand des Künstlernamens sowie des Titelnamens des Songs gesucht.
#Dabei wird als Rückgabe eine Jsondatei mit allen erhältlichen Versionen des Songs gespeichert.
        for i in Songliste:
            time.sleep(1)
            search = str(i[1]+" "+i[2])
            url_search = 'https://www.franchiserecordpool.com/search/data?search_artist_track=' + quote(search)
            pseudoJson = urlopen(url_search).read()
            pseudoJson=ujson.loads(pseudoJson)

#Aus der Json Datei werden die Ids, Titelnamen sowie Künstlernamen aller Verfügbaren Versionen abgespeichert.
#Dabei werden Video, Instrumental und Acapella Versionen außenvorgelassen da diese nicht berücksichtigt werden sollen.
            Versions=[]
            for j in pseudoJson['rows']:
                if 'data-type="video"' or 'instrumental' or 'acapella' not in str(j):
                    soup = BeautifulSoup(j["cell"][1], "html.parser")
                    Versions.append([j["id"],
                                     soup.find_all('a')[0]['title'],
                                     soup.find_all('a')[1]['title']])
                    
#Die herunterzuladende Version wird anhand eines Entscheidungsbaumes gewonnen.
#Dabei soll die "(Intro Outro) (Dirty)" wenn vorhanden gewählt werden.
#Alternativ soll die "(Dirty)" Version oder die letzte verfügbare Version gewählt werden.
#Bei der Wahl wird die ID der Version gespeichert.
            TrackID=[]
            TrackID_2=[]
            for k in Versions:  
                    if "(Intro Outro) (Dirty)" in str(k[1]):
                        TrackID=k[0]
                        break
                    elif str(str(i[2])+"(Dirty)") == str(k[1]):
                            TrackID=k[0]
                    else:
                        TrackID_2=k[0]
                        continue          
            if TrackID:
                continue
            elif TrackID_2: 
                TrackID=TrackID_2
            else:
                continue
                
#Mit der ID der ausgewählten Version wird diese heruntergeladen.
#Die Datei wird als MP3 in einem Zwischenordner gespeichert.
            if TrackID:
                url_download = 'https://www.franchiserecordpool.com/download/track/' + TrackID
                Pathsetter = os.path.join(Downloaded_Tracks, i[2])
                urlretrieve(url_download, Pathsetter+'.mp3') 
                
#Der heruntergeladene Song wird mit einem Gruppentag versehen dass der jeweiligen Ursprungsplaylist entspricht.
#Die Tags ermöglichen später eine automatische Zuordnung in Itunes.
                audiofile = eyed3.load(str(Pathsetter)+".mp3")
                grp1 = GRP1()
                grp1.text = str(i[4])+" auto_download"
                audiofile.tag.frame_set[b"GRP1"] = grp1
                audiofile.tag.save()
                
#Alle heruntergeladenen Songs werden abgespeichert und anschließend gleichzeitig aus der jeweiligen Spotify
#Playlist gelöscht. Es verbleiben dort nur nicht verfügbare Titel.
                to_delete.append({'uri': i[3],'positions':[i[0]]})

#Alle Heruntergeladenen Titel werden mit Ihren Künstlernamen, Titeln und ihrem zugehörigen Playlist tag
#in der csv Datei abgelegt um später Auswertungen vorzunehmen.
                writer.writerow([i[1], i[2], i[4]])
                
        if to_delete:
            sp.user_playlist_remove_specific_occurrences_of_tracks(Username, 
                                                                   h[0], 
                                                                   to_delete, 
                                                                   snapshot_id=None)

#Anschließend werden alle Titel in die Apple Music Bibliothek eingepflegt.
#Dabei fügen die Tags die Titel einer "automatisch Downloaded" und ihrer jeweiligen Genre Playlist zu.
#Info: In DS-Store-Dateien werden vom Finder (Mac) Daten über Fensterposition, Größe, usw. gespeichert.
#Diese Datei muss entfernt werden
files = os.listdir(Downloaded_Tracks)
files.remove('.DS_Store')
for f in files:
    shutil.move(Downloaded_Tracks+f, Music_adding_folder)
