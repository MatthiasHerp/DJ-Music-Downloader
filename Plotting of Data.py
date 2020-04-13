import os
from os import walk
import eyed3
from eyed3.id3 import apple
GRP1 = apple.GRP1
import csv
import numpy as np
import pandas as pd
%matplotlib inline 
import matplotlib.pyplot as plt

#Alle automatisch heruntergeladenen Songdateien werden aufgerufen die 
#vor der Automatischen Abspeicherung in der CSV heruntergeladen wurden.
f = []
for (dirpath, dirnames, filenames) in walk('Pfad zum Ordner'):
    f.extend(filenames, )
    break

#Für Jede Datei wird der Titel, Künstlername und das Gruppierungstag welches die Playlistverknüpfung enthält gespeichert.
t=[]
a=[]
p=[]
i=0
while i < len(f):
    Pfad = os.path.join('Pfad zum Ordner', f[i])
    audiofile = eyed3.load(Pfad)
    if '.DS_Store' not in f[i] :
        t.append(audiofile.tag.title)
        a.append(audiofile.tag.artist)
        p.append(audiofile.tag.frame_set[b"GRP1"][0].text.split(" ")[0])
    i += 1

#Diese Inforamtionen werden in die CSV Datei geschrieben.
writer = csv.writer(open("Spotify_FRP_to_Itunes_Downloader.csv", "w"))
writer.writerow(["Titel", "Artist", "Playlist"])

i=0
while i < len(t):
    writer.writerow([t[i], a[i], p[i]])
    i+=1

#Die CSV Datei wird mit Pandas als Dataframe aufgerufen.
df = pd.read_csv("Spotify_FRP_to_Itunes_Downloader.csv"
                , delimiter=",")
df.head()

#Für die anzahl der Titel je Playlist wird ein Balkendiagramm erstellt.
List1=[]
List2=[]
for i in df.Playlist.unique():
    List1.append(i)
    List2.append(len(df[df["Playlist"]==i]))
plt.bar(List1, List2, width=0.5)
plt.xticks(rotation=45)
plt.title('Titel je Playlist', {'fontsize': 15, 'fontweight' : 'bold'})
plt.savefig('bar_chart.pdf')

#Für die anzahl der Titel je Playlist wird ein Kuchendiagramm erstellt.
plt.pie(List2)
plt.legend(df.Playlist.unique())
plt.title('Titel je Playlist', {'fontsize': 15, 'fontweight' : 'bold'})
plt.savefig('pie_chart.pdf')
