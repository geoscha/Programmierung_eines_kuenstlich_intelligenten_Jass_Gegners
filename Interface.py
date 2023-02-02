# Graphische Nutzer Oberfläche für das Jass Programm

# Importe
import time
import random
import matplotlib
import matplotlib.backends.backend_agg as agg
import pylab
import pygame
import copy
from pygame import mixer
from tensorflow.keras.models import load_model

trumpf_tabelle = [0, 0, 0, 14, 10, 20, 3, 4, 11]
farb_vokabular = ["Herz", "Schaufel", "Karo", "Kreuz"]  # Farbenbezeichnungen
spieler_vokabular = ["Mensch", "Computer"]  # Spielerbezeichnungen
spiel_modi = ["Obe-Abe", "Une-Ufe", "Herz-Trumpf", "Schaufel-Trumpf", "Karo-Trumpf",
              "Kreuz-Trumpf"]  # Spielmodi-Bezeichungen
sorten = ["6", "7", "8", "9", "10", "J", "Q", "K", "A"]  # Abkürzungen der Kartennamen

farben = [pygame.image.load("Data/" + i + ".png") for i in
          farb_vokabular]  # Graphische Dateien laden

entwickler_mod = True  # Computer Karten können eingesehen werden

spieler = 0  # Spieler auf Mensch setzen
status = -2  # GUI Status bestimmen
spielfeld = []  # Spielfled leeren
punkte = [0, 0]  # Punktestand
punkte_verlauf = [0]  # Punkteverlauf 0 setzten

# RGB Farbwerte

ORANGE = (255, 180, 50)
GREEN = (153, 153, 70)
BLACK = (0, 0, 0)
GREY = (60, 60, 60)
WHITE = (200, 200, 200)

pygame.init()  # initialisieren von pygame
mixer.init()  # Instantiate mixer
#mixer.music.set_volume(1)  # Set preferred volume
screen_size = 3  # Grösse des Bildschirms
width = 400 * screen_size  # Fesntergrösse bestimmen (X-Richtung)
height = 300 * screen_size  # Fesntergrösse bestimmen (Y-Richtung)
x_norm = width / 400  # Grössenkoeffizienten anpassen (X-Richtung)
y_norm: float = height / 300  # Grössenkoeffizienten anpassen (Y-Richtung)

screen = pygame.display.set_mode((width, height))  # Fenster öffnen
pygame.display.set_caption("Jassen zu zweit")  # Titel für Fensterkopf
clock = pygame.time.Clock()  # Bildschirmaktualisierungsrate bestimmen

spielaktiv = True  # solange die Variable True ist, soll das Spiel laufen

font = pygame.font.Font('freesansbold.ttf', 10 * screen_size)  # Schrift importieren

spielbericht = ["Programmstart - " + str(time.strftime("%d.%m.%Y %H:%M:%S"))]  # Spielbericht -Startnachricht

model = []  # Liste mit allen KNN Modellen
silb = [["A", "R"], ["OA", "UU", "HE", "SC", "KA", "KR"]]

print("KNN laden")
v = 1
for i in silb[0]:
    s1 = i
    for ii in silb[1]:
        s2 = ii
        try:
            model.append(load_model('Data/model_108_' + s1 + '-' + s2 + '_data.h5'))  # KNN Modell laden
        except:
            model.append("False")
    print(str(v), "/2")
    v += 1


class Card:  # Kartenobjekt
    def __init__(self, val, usd, ownr, lyr):
        self.val = val  # Kartenwert
        self.usd = usd  # Spielverlauf
        self.ownr = ownr  # Besitzer
        self.lyr = lyr  # Baumtiefe


class Knoten:  # Baumknotenpunkt mit der Fähigkeit einen Baum mit beliebiger Ordung und Tiefe aufzubauen
    def __init__(self, name, parent):
        self.name = name  # Speicherwert(Kartenobjekt)
        self.parent = parent  # Vaterknoten
        self.opt = 0  # Opt = 0: nicht Optimale Karte (gemäss Minimax)

        tiefe = 0
        obj = parent
        while True:  # Parents zählen um Tiefe zu ermitteln
            try:
                obj = obj.parent
                tiefe += 1
            except:
                break
        self.layer = tiefe
        self.children = []

    def select(self):  # Markieren als optimale Karte (Minimax)
        self.opt = 1


def get_typ(x):  # Funktion die den Kartentyp (6, 7, 8, 9, 10, j, Q, etc) ausgibt
    return x - x // 9 * 9


def get_col(x):  # Funktion die die Kartenfarbe (Herz etc) ausgibt
    return x // 9


def switch(x):  # Wechselt den Wert 0 zu 1 und 1 zu 0
    x = 1 - x
    return x


def get_punkte(x):  # gibt Punktewert einer Karte zurück

    if get_col(x) == trumpf:
        return trumpf_tabelle[get_typ(x)]
    elif modus == 0:
        return punkte_tabelle[get_typ(x)]
    else:
        return [11, 0, 8, 0, 10, 2, 3, 4, 0][get_typ(x)]


def evaluate_game(game, ansager):  # Gibt ein Punktevektor aus, für ein eingespeistes Spiel 'game'

    pkt = [0, 0]
    for i in range(int(len(game) / 2)):  # Abrechnung findet jeden zweiten Stich statt
        if get_winner(game[i * 2], game[i * 2 + 1]) == 0:
            ansager = switch(ansager)
        pkt[ansager] += get_punkte(game[i * 2]) + get_punkte(game[i * 2 + 1])
    return pkt


def get_hand(anzahl, länge):  # Gibt "anzahl" zufällige Hände der länge "länge" aus
    hand = list(range(36))
    random.shuffle(hand)
    result = []
    for i in range(anzahl):
        result.append(hand[länge * i:länge * (i + 1)])
    return result


def hand_erg(ursp, used):  # Ergänzt hand mit zufälligen aber gültigen Karten
    hand = [i for i in range(36) if i not in ursp and i not in used]
    random.shuffle(hand)
    return hand[0:len(ursp)]


def situation_to_x(h, used, ansager, s1, s2):  # Fasst Spielsituation für KNN zusammen

    if s2 == False:
        x = [0 for i in range(144)]  # Ansagen
    else:
        x = [0 for i in range(180)]  # Reagieren

    for i in h[ansager]:  # Meine Hand Karten
        x[i] = 1
    for i in h[switch(ansager)]:  # Seine Hand Karten
        x[i + 36] = 1

    for i in used:  # Gespielte Karten
        x[i + 72] = 1

    x[s1 + 108] = 1  # Ausgespielte Karte einfügen

    if s2 != False:
        x[s2 + 144] = 1  # Ausgespielte Karte einfügen

    return [x]


def get_winner(c1, c2):  # Gewinner für einen Stich erruieren, Wechsel = 1 bedeutet Reak gewinnt

    wechsel = 0
    if modus == 0 and get_typ(c1) < get_typ(c2) and get_col(c1) == get_col(c2):  # Obe Abe
        wechsel = 1
    elif modus == 1 and get_typ(c1) > get_typ(c2) and get_col(c1) == get_col(c2):  # Une Ufe
        wechsel = 1
    elif modus > 1 and get_typ(c1) < get_typ(c2) and get_col(c1) == get_col(c2) and get_col(c2) != trumpf or get_col(
            c2) == trumpf \
            and get_col(c1) != trumpf or get_typ(c2) == 5 and get_col(c2) == trumpf or \
            get_typ(c2) == 3 and get_col(c2) == trumpf and get_typ(c1) != 5 and get_col(
        c1) != trumpf:  # Nichttrumpf, Junge vs irgendwas
        wechsel = 1
    elif modus > 1 and get_col(c1) == trumpf and get_col(c2) == trumpf \
            and get_typ(c2) > get_typ(c1) != 5 and get_typ(c1) != 3:  # Sieg v. Trumpf Junge
        wechsel = 1
    if get_col(c2) == trumpf and get_typ(c2) == 3 and not (get_typ(c1) == 5 and get_col(c1) == trumpf):  # Näll auf S2
        wechsel = 1
    if get_col(c1) == trumpf and get_typ(c1) == 3 and not (get_typ(c2) == 5 and get_col(c2) == trumpf):  # Näll auf S1
        wechsel = 0
    return wechsel


def get_AI_pred(hand: object, used: object, spieler: object, ansage_ai) -> object:
    selec = [0 for i in range(36)]

    for g in range(25):

        if ansage_ai:
            mögl = copy.deepcopy(hand[spieler])
        else:
            mögl = [i for i in hand[spieler] if get_col(i) == get_col(spielfeld[0]) or get_col(i) == trumpf]

        if not mögl:
            mögl = copy.deepcopy(hand[spieler])

        model_no = modus
        if ansage_ai:
            x = [situation_to_x([hand_erg(hand[1], used), hand[1]], used, spieler, i, False) for i in mögl]
        else:
            x = [situation_to_x([hand_erg(hand[1], used), hand[1]], used, spieler, spielfeld[0], i) for i in mögl]
            model_no += 6
        pred = [model[model_no].predict(i).astype(float) for i in x]
        selec[mögl[pred.index(max(pred))]] += 1

    return selec.index(max(selec))


def write(txt, x, y, size):
    font = pygame.font.Font('freesansbold.ttf', size * screen_size)
    text = font.render(txt, True, WHITE)
    screen.blit(text, [x * x_norm, y * y_norm])


def write_col(txt, x, y, size, col):
    font = pygame.font.Font('freesansbold.ttf', size * screen_size)
    text = font.render(txt, True, col)
    screen.blit(text, [x * x_norm, y * y_norm])


def rectangle(x, y, x2, y2):  # Macht einrechteck mit umrandung
    pygame.draw.rect(screen, BLACK, pygame.Rect(x * x_norm, y * y_norm, x2 * x_norm,
                                                y2 * y_norm))
    pygame.draw.rect(screen, GREY,
                     pygame.Rect(x * screen_size, y * screen_size, x2 * screen_size, y2 * screen_size),
                     screen_size)


def hintergrund():
    # Hintergrund Meine Karten:

    x = 10 * x_norm
    y = 10 * y_norm

    dichte = 100

    for i in range(dichte):
        pygame.draw.line(screen, GREY, [x, y], [x, 290 * screen_size], 1)
        x += 250 / dichte * x_norm

    x = 10 * x_norm
    y = 10 * y_norm

    for i in range(dichte):
        pygame.draw.line(screen, GREY, [x, y], [260 * screen_size, y], 1)
        y += 280 / dichte * y_norm

    # Hintergrund Spielfeld:

    x = 265 * x_norm
    y = 10 * y_norm

    dichte = 50

    for i in range(dichte):
        pygame.draw.line(screen, GREY, [x, y], [x, 145 * screen_size], 1)
        x += 125 / dichte * x_norm

    x = 265 * x_norm
    y = 10 * y_norm

    for i in range(dichte):
        pygame.draw.line(screen, GREY, [x, y], [390 * screen_size, y], 1)
        y += 135 / dichte * y_norm

    # Umrahmung

    pygame.draw.rect(screen, WHITE, [5 * x_norm, 5 * y_norm, 390 * screen_size, 290 * screen_size],
                     screen_size)  # äussertes Quadrat
    pygame.draw.rect(screen, WHITE, [0 * x_norm, 0 * y_norm, 400 * screen_size, 300 * screen_size],
                     screen_size)  # II. äussertes Quadrat

    pygame.draw.rect(screen, WHITE, [10 * x_norm, 10 * y_norm, 250 * screen_size, 280 * screen_size],
                     screen_size)  # Meine Karten Quadrat
    pygame.draw.rect(screen, WHITE, [265 * x_norm, 10 * y_norm, 125 * screen_size, 135 * screen_size],
                     screen_size)  # Spielfeld Quadrat
    pygame.draw.rect(screen, WHITE, [265 * x_norm, 150 * y_norm, 125 * screen_size, 140 * screen_size],
                     screen_size)  # Spielinfo Quadrat

    pygame.draw.rect(screen, BLACK,
                     pygame.Rect(13 * x_norm, 13 * y_norm, 72 * x_norm, 13 * y_norm))  # Grundierung Meine Karten
    pygame.draw.rect(screen, BLACK,
                     pygame.Rect(268 * x_norm, 13 * y_norm, 52 * x_norm, 13 * y_norm))  # Grundierung Spielfeld

    write("Meine Karten", 15, 15, 10)
    write("Spielfeld", 270, 15, 10)
    write("Spielinformationen", 270, 155, 10)
    write("Spielbericht", 270, 210, 10)

    # 12 Karten Slots zeichnen

    y = 55
    for i in range(3):
        x = 32.5
        for ii in range(4):
            pygame.draw.rect(screen, BLACK,
                             pygame.Rect(x * x_norm, y * y_norm, 40 * x_norm, 56 * y_norm))  # Grundierung
            pygame.draw.rect(screen, WHITE, [x * x_norm, y * y_norm, 40 * x_norm, 56 * y_norm],
                             screen_size)  # Karten Rahmen
            x += 55
        y += 65

    # Spielfeld einzeichnen

    x = 280
    y = 55
    for i in range(2):
        pygame.draw.rect(screen, BLACK,
                         pygame.Rect(x * x_norm, y * y_norm, 40 * x_norm, 56 * y_norm))  # Grundierung
        pygame.draw.rect(screen, WHITE, [x * x_norm, y * y_norm, 40 * x_norm, 56 * y_norm],
                         screen_size)  # Karten Rahmen
        x += 50

    # Daten aufschreiben
    write("Modus: " + str(spiel_modi[modus]), 270, 170, 6)
    write("Punktestand: " + str(punkte[0]) + " (Du)/ " + str(punkte[1]) + " (PC)", 270, 180, 6)
    write("Am Zug: " + spieler_vokabular[spieler], 270, 190, 6)

    rectangle(243, 12, 15, 15)  # Metaknopf
    write_col("PC", 246, 16, 7, ORANGE)

    if not entwickler_mod:
        pygame.draw.line(screen, ORANGE, [243 * x_norm, 12 * y_norm], [258 * x_norm, 27 * y_norm], screen_size)


def auswählen():  # Zeichnet ausgewählte Karte an

    mouse_cor = pygame.mouse.get_pos()
    x = mouse_cor[0] / screen_size - 20
    y = mouse_cor[1] / screen_size - 28

    x = (round((x - 32.5) / 55, 0) * 55 + 32.5)
    y = (round((y - 55) / 65, 0) * 65 + 55)

    all_pos = [[32.5, 55.0], [87.5, 55], [142.5, 55], [197.5, 55], [32.5, 120], [87.5, 120], [142.5, 120], [197.5, 120],
               [32.5, 185], [87.5, 185], [142.5, 185], [197.5, 185]]

    try:
        element = all_pos.index([x, y])
    except:
        element = 100  # Element ist nicht in der Liste enthalten

    if element != 100:
        pygame.draw.rect(screen, ORANGE,
                         pygame.Rect(x * screen_size, y * screen_size, 40 * screen_size, 56 * screen_size),
                         2 * screen_size)  # Auswahl

    return element


def show_spielfeld(spielfeld):  # Zeigt ausgespielte Karten (max. 2)
    for i in range(2):
        try:
            inhalt = sorten[get_typ(spielfeld[i])]
            pygame.draw.rect(screen, WHITE, pygame.Rect((280 + 50 * i) * x_norm, 55 * y_norm, 40 * x_norm,
                                                        56 * y_norm))  # Grundierung Karte
            screen.blit(pygame.transform.scale(farben[get_col(spielfeld[i])], (10 * x_norm, 10 * y_norm)),
                        ((295 + 50 * i) * x_norm, 70 * y_norm))
            write_col(inhalt, 282 + 50 * i, 57, 10, BLACK)
        except:
            pass


def show_hand(hand):  # Zeigt Hand des Spielers an
    x = 32.5
    y = 55

    mögl = []

    if len(spielfeld) == 1:
        mögl = [i for i in hand if get_col(i) == get_col(spielfeld[0])]
        komplett = False
        if mögl == []:
            komplett = True
        [mögl.append(i) for i in hand if get_col(i) == trumpf and modus > 1]
        if komplett:
            mögl = hand

    else:
        mögl = hand

    for i in range(12):
        try:

            if hand[i] not in mögl:
                pygame.draw.rect(screen, GREY, pygame.Rect(x * x_norm, y * y_norm, 40 * x_norm,
                                                           56 * y_norm))
            else:
                pygame.draw.rect(screen, WHITE, pygame.Rect(x * x_norm, y * y_norm, 40 * x_norm,
                                                            56 * y_norm))

            inhalt = sorten[get_typ(hand[i])]

            write_col(inhalt, x + 2, y + 2, 10, BLACK)

            screen.blit(pygame.transform.scale(farben[get_col(hand[i])], (10 * x_norm, 10 * y_norm)),
                        ((x + 15) * x_norm, (y + 15) * y_norm))
            x += 55

            if x > 197.5:
                x = 32.5
                y += 65
        except:
            pass


def bitte_warten():
    x = 37.5
    y = 80

    rectangle(x, y, 195, 45)

    write_col("Bitte warten - Gegner am Zug", 60, 95, 10, ORANGE)
    write("Dies kann einige Zeit in Anspruch nehmen.", 60, 105, 7)


def deckblatt():  # Titelseite

    screen.fill(ORANGE)  # Grundierung
    write_col("Schieber für zwei", 10, 10, 30, BLACK)
    write_col("Kantonsschule Zug, 2022/2023", 10, 37, 17, BLACK)

    write_col("Programmierung eines künstlich intelligenten", 165, 207, 10, BLACK)
    write_col("Jass Gegners, Maturaarbeit im Bereich Informatik", 144, 217, 10, BLACK)
    write_col("Betreuende Lehrperson: Mohammed Kubba", 175, 227, 10, BLACK)

    if entwickler_mod:
        write_col("Entwickler Modus: Ein", 10, 285, 10, BLACK)
    else:
        write_col("Entwickler Modus: Aus", 10, 285, 10, BLACK)
    write_col("Menü öffnen >", 320, 285, 10, BLACK)


def eingabe_fenster():
    global trumpf, punkte_tabelle

    rectangle(10, 10, 380, 280)
    x = 10 * x_norm
    y = 10 * y_norm

    dichte = 100

    for i in range(dichte):
        pygame.draw.line(screen, GREY, [x, y], [x, 290 * screen_size], 1)
        x += 380 / dichte * x_norm

    x = 10 * x_norm
    y = 10 * y_norm

    for i in range(dichte):
        pygame.draw.line(screen, GREY, [x, y], [390 * screen_size, y], 1)
        y += 280 / dichte * y_norm

    rectangle(20, 20, 360, 22)  # Titel
    write_col("Jassen zu zweit", 24, 24, 10, ORANGE)
    pygame.draw.line(screen, ORANGE, [24 * screen_size, 35 * screen_size], [375 * screen_size, 35 * screen_size],
                     2 * screen_size)

    # Zeile 1 -> Ansager

    for i in range(3):
        rectangle(20 + i * 125, 52, 110, 20)  # Zeile 1

    # Spalte 1
    write("i) Ansager bestimmen..........:", 25, 58, 7)

    # -      Spalte 2

    rectangle(145, 52, 55, 20)

    if spieler == 0:
        write_col("Mensch", 160, 58, 7, ORANGE)
        write("Computer", 210, 58, 7)

    else:
        write("Mensch", 160, 58, 7)
        write_col("Computer", 210, 58, 7, ORANGE)

    # -      Spalte 3
    if spieler == 0:
        write_col("Karten ansehen >", 275, 58, 7, ORANGE)
    else:
        write("Computer sagt an", 275, 58, 7)

    # Zeile 2

    for i in range(2):
        rectangle(20 + i * 185, 80, 175, 18)

    write("ii) Spielmodus wählen.........................................:", 24, 84, 7)

    if spieler == 0:
        write_col(spiel_modi[modus] + " > (Wahl anpassen ?)", 209, 84, 7, ORANGE)

        if modus > 1:
            trumpf = modus - 2
        else:
            trumpf = 100

        if modus == 0:
            punkte_tabelle = [0, 0, 8, 0, 10, 2, 3, 4, 11]
        elif modus == 1:
            punkte_tabelle = [11, 0, 8, 0, 10, 2, 3, 4, 0]
        else:
            punkte_tabelle = [0, 0, 0, 0, 10, 2, 3, 4, 11]
            [punkte_tabelle.append(0) for ii in range(100)]
            punkte_tabelle.append(14)
            punkte_tabelle.append(20)

        for i in range(len(spiel_modi)):
            rectangle(205, 98 + 18 * i, 175, 18)
            write("- " + spiel_modi[i], 209, 102 + 18 * i, 7)

    else:
        write(spiel_modi[sugg] + " (Bestimmt durch Computer)", 209, 84, 7)

    # Zeile 3 - Spielstart Knop

    rectangle(20, 260, 360, 18)

    write_col("Spielstart >", 24, 264, 10, ORANGE)


def karten_vorschau():  # Im Menü
    rectangle(10, 10, 380, 280)
    x = 10 * x_norm
    y = 10 * y_norm

    dichte = 100

    for i in range(dichte):
        pygame.draw.line(screen, GREY, [x, y], [x, 290 * screen_size], 1)
        x += 380 / dichte * x_norm

    x = 10 * x_norm
    y = 10 * y_norm

    for i in range(dichte):
        pygame.draw.line(screen, GREY, [x, y], [390 * screen_size, y], 1)
        y += 280 / dichte * y_norm

    rectangle(20, 20, 360, 22)  # Titel
    write_col("Kartenvorschau", 24, 24, 10, ORANGE)
    pygame.draw.line(screen, ORANGE, [24 * screen_size, 35 * screen_size], [375 * screen_size, 35 * screen_size],
                     2 * screen_size)

    for i in range(2):
        for ii in range(6):
            inhalt = sorten[get_typ(hand[0][i * 6 + ii])]
            pygame.draw.rect(screen, WHITE, pygame.Rect((60 * ii + 24) * x_norm, (50 + (i * 100)) * y_norm, 50 * x_norm,
                                                        75 * y_norm))  # Grundierung Karte
            screen.blit(pygame.transform.scale(farben[get_col(hand[0][i * 6 + ii])], (10 * x_norm, 10 * y_norm)),
                        ((60 * ii + 43) * x_norm, (80 + (i * 100)) * y_norm))
            write_col(inhalt, (60 * ii + 27), 55 + (i * 100), 10, BLACK)

    rectangle(20, 250, 360, 18)
    write("< Zurück", 24, 254, 10)


def karten_einsehen():
    rectangle(10, 10, 380, 280)
    write("Computer Karten", 20, 20, 10)

    # 12 Karten aufzeichnen

    for i in range(2):
        for ii in range(6):
            try:
                inhalt = sorten[get_typ(hand[1][i * 6 + ii])]
                pygame.draw.rect(screen, WHITE,
                                 pygame.Rect((60 * ii + 24) * x_norm, (50 + (i * 100)) * y_norm, 50 * x_norm,
                                             75 * y_norm))  # Grundierung Karte
                screen.blit(pygame.transform.scale(farben[get_col(hand[1][i * 6 + ii])], (10 * x_norm, 10 * y_norm)),
                            ((60 * ii + 43) * x_norm, (80 + (i * 100)) * y_norm))
                write_col(inhalt, (60 * ii + 27), 55 + (i * 100), 10, BLACK)
            except:
                pass

    rectangle(20, 250, 360, 18)
    write("< Zurück", 24, 254, 10)


# Schleife Hauptprogramm
matplotlib.use("Agg")  # Matplotlib
gesammt_ansager = 1 # Ansager während des Spieles
performance = True
stich = [0, 0]  # zählt die stiche um einen Match zu identifizieren
spielverlauf = []

while spielaktiv:

    screen.fill(BLACK)  # Grundierung

    m_x = pygame.mouse.get_pos()[0]
    m_y = pygame.mouse.get_pos()[1]

    for event in pygame.event.get():  # Überprüfen, ob Nutzer eine Aktion durchgeführt hat

        if event.type == pygame.QUIT:  # Fenster beenden
            spielaktiv = False  # Schleife beenden
            print("Programmende")
            matplotlib.pyplot.close('all')  # Graph schliessen

        elif event.type == pygame.MOUSEBUTTONUP and status == -2:  # Startbildschirm
            if m_y > 250 * y_norm:
                if m_x > 290 * x_norm:  # Startknopf
                    status = -1.11
                elif m_x < 140 * x_norm:  # Entwicklermodus umschalten
                    if entwickler_mod:
                        entwickler_mod = False
                    else:
                        entwickler_mod = True

        elif event.type == pygame.MOUSEBUTTONUP and status == -1.1:  # Kartenvorschau
            if 250 * screen_size <= m_y <= 268 * screen_size:  # Zurück zum Hauptmenü
                status = -1

        elif event.type == pygame.MOUSEBUTTONUP and status == -1:  # Spielmenü
            if 58 * screen_size <= m_y <= 78 * screen_size:
                if m_x >= 140 * screen_size:  # Mensch bestimmt Modus
                    if m_x <= 195 * screen_size:
                        spieler = 0
                        modus = 0

                    elif m_x <= 270 * screen_size:  # Computer bestimmt Modus
                        modus = sugg
                        if modus > 1:
                            trumpf = modus - 2
                        else:
                            trumpf = 100
                        spieler = 1

                    elif spieler == 0:  # Karten "Mensch" einsehen
                        status = -1.1

                    gesammt_ansager = spieler

            elif spieler == 0 and 98 * screen_size + \
                    len(spiel_modi) * screen_size * 18 >= m_y >= 98 * screen_size \
                    and m_x >= 205 * screen_size:
                modus = (m_y - 98 * screen_size) // (18 * screen_size)  # Modus aus Tabelle bestimmen

            elif 260 * screen_size <= m_y <= 278 * screen_size:  # Spielstart
                status = spieler
                if spieler == 1:
                    modus = sugg
                print("MODUS:", spiel_modi[modus])
                print("TRUMPF:", trumpf)

        elif event.type == pygame.MOUSEBUTTONUP and status == 0:  # Mensch am Zug
            if 12 * screen_size <= m_y <= 27 * screen_size and 243 * screen_size <= m_x <= 258 * screen_size and entwickler_mod:
                print("Spieler hat PC Karten angesehen")
                status = 4  # Entwicklermodus, Computer Karten einsehen
            else:

                if len(spielfeld) == 1:  # Reagieren, Möglche Karten filtern
                    moegl_karten = [i for i in hand[0] if get_col(i) == get_col(spielfeld[0])]

                    komplett_hand = False

                    if not moegl_karten:  # Mensch hat Farbe nicht
                        komplett_hand = True

                    [moegl_karten.append(ii) for ii in hand[0] if
                     get_col(ii) == trumpf and modus > 1]  # Trumpf Karten dazu

                    if komplett_hand:
                        moegl_karten = hand[0]
                else:  # Jede Karte darf angesagt werden
                    moegl_karten = hand[0]

                try:  # gewählte Karte überprüfen und zu Spielfeld hinzufügen
                    if hand[0][auswählen()] in moegl_karten:
                        spielfeld.append(hand[0][auswählen()])
                        spielverlauf.append(int(spielfeld[-1]))
                        if len(spielfeld) == 1:
                            status = 1
                        else:
                            status = 2

                        spielbericht.append(
                            "Karte " + str(len(spielfeld)) + ": " + farb_vokabular[get_col(spielfeld[-1])] + " " +
                            sorten[get_typ(spielfeld[-1])])
                        spieler = switch(spieler)
                except:
                    pass  # Input Mensch ungültig

        elif status == 2 and event.type == pygame.MOUSEBUTTONUP:  # Auswerten des Spielfeldes

            hand[0] = [i for i in hand[0] if i not in spielfeld]  # Karten wegnehmen
            hand[1] = [i for i in hand[1] if i not in spielfeld]

            if get_winner(spielfeld[0], spielfeld[1]) == 0:
                spieler = switch(spieler)

            punkte[spieler] += sum([get_punkte(i) for i in spielfeld])  # Punkte eintragen

            punkte_verlauf.append(punkte[0] - punkte[1])

            spielbericht.append(spieler_vokabular[spieler] + " gewinnt " + str(
                sum([get_punkte(i) for i in spielfeld])) + " Punkte.")

            spielfeld = []
            status = spieler  # Gewinner sagt nächsten Stich an

            if len(hand[0]) == 0:  # Alle Karten ausgespielt, Beenden-Schirm
                punkte[spieler] += 5  # Letzter Stich gibt 5 P
                status = 3

        elif status == 3 and 242 * screen_size <= m_y <= 262 * screen_size \
                and 20 * screen_size <= m_x <= 377 * screen_size and event.type == pygame.MOUSEBUTTONUP:  # Beenden knopf

            print("Spiel wurde beendet mit " + str(punkte))
            matplotlib.pyplot.close('all')

            status = -1.11  # Reset

        elif status == 4 and 250 * screen_size <= m_y <= 268 * screen_size and event.type == pygame.MOUSEBUTTONUP:

            status = 0

    # Aktionen, unabhängig von Mausklick
    if 0 <= status <= 2:  # Hintergrund zeichnen

        hintergrund()
        show_hand(hand[0])

        for i in range(6):  # Spielprotokoll auzeigen:
            try:
                write_col(str(i + 1) + ": " + spielbericht[-i - 1], 270, 225 + i * 10, 5, ORANGE)

            except:
                pass

    show_spielfeld(spielfeld)

    if status == -2:  # Begrüssung, Projektvorstellung
        deckblatt()
        if m_y > 270 * y_norm:
            if m_x < 140 * x_norm:
                pygame.draw.line(screen, BLACK, [10 * screen_size, 295 * screen_size],
                                 [128 * screen_size, 295 * screen_size],
                                 2 * screen_size)
            elif m_x > 300 * x_norm:
                pygame.draw.line(screen, BLACK, [318 * screen_size, 295 * screen_size],
                                 [392 * screen_size, 295 * screen_size],
                                 2 * screen_size)

    elif status == -1.11:  # Neustarten, Variablen reseten

        gesammt_ansager = switch(gesammt_ansager)  # Ansager jede Runde Wechseln

        hand = get_hand(2, 12)  # Hand austeilen
        hand[0].sort()  # Hand sortieren
        hand[1].sort()

        modus = 0
        trumpf = 100
        status = -1

        performance = False
        sugg = 0

        screen.fill(BLACK)  # Grundierung
        write_col("Neues Spiel wird vorbereitet", 10, 10, 10, WHITE)
        write_col("Laden...", 345, 290, 10, WHITE)

        pygame.display.flip()

        # Modus Ansage Computer vorbereiten

        print("Computer-Ansage vorbereiten")

        pred = []
        for i in range(6):
            modus = i
            if modus > 1:
                trumpf = modus - 2
            else:
                trumpf = 100

            p_sieg = []

            for ii in hand[1]:
                if get_col(ii) == trumpf:
                    hierarchie = [0, 1, 2, 4, 6, 7, 8, 3, 5]
                elif modus == 1:
                    hierarchie = [8, 7, 6, 5, 4, 3, 2, 1, 0]
                else:
                    hierarchie = [0, 1, 2, 3, 4, 5, 6, 7, 8]

                gewichtung = [-2, -1, -0.5, -0.125, 0.25, 0.5, 1, 2, 4]     # Gewichtung fürs Ansagen
                p_sieg.append(gewichtung[hierarchie.index(get_typ(ii))])
            pred.append(sum(p_sieg))

        sugg = pred.index(max(pred))

        spielfeld = []

        modus = 0
        spieler = gesammt_ansager

    elif status == -1.1:  # Karten anschauen:
        karten_vorschau()

    elif status == -1:  # startfeld
        eingabe_fenster()

    elif status == 0:
        auswählen()
        pygame.draw.rect(screen, ORANGE,
                         pygame.Rect(30 * screen_size, 52 * screen_size, 210 * screen_size, 192 * screen_size),
                         2 * screen_size)

    elif status == 1:  # PC ist dran mit reagieren/vorsagen - Warte status
        bitte_warten()
        pygame.display.flip()
        if not spielfeld:
            spielfeld.append(get_AI_pred(hand, spielverlauf, spieler, True))  # KNN sagt an

        else:  # 2. Stich (reaktion), in seltenen Fällen ist sie fehlerhaft

            mögliche_karten = [i for i in hand[1] if get_col(i) == get_col(spielfeld[0]) or get_col(i) == trumpf]

            if not mögliche_karten:
                mögliche_karten = copy.deepcopy(hand[1])

            sieg = [get_winner(spielfeld[0], i) for i in mögliche_karten]

            try:
                empfehlung = get_AI_pred(hand, spielverlauf, spieler, False)
            except:
                max_punkte = []
                for i in range(len(sieg)):
                    if sieg[i] == 1:
                        max_punkte.append(get_punkte(sieg[i]))
                    else:
                        max_punkte.append(-get_punkte(sieg[i]))
                if sum(sieg) > 0:  # Es kann gewonnen werden
                    empfehlung = mögliche_karten[max_punkte.index(max(max_punkte))]
                else:
                    empfehlung = mögliche_karten[max_punkte.index(min(max_punkte))]

            spielfeld.append(empfehlung)

        spielverlauf.append(spielfeld[-1])
        spielbericht.append("Karte " + str(len(spielfeld)) + ": " + farb_vokabular[get_col(spielfeld[-1])] + " " +
                            sorten[get_typ(spielfeld[-1])])

        if len(spielfeld) == 1:
            status = 0
        else:
            status = 2

    elif status == 2:  # Stich Auswerten

        pygame.draw.rect(screen, BLACK, pygame.Rect(285 * x_norm, 118 * y_norm, 80 * x_norm,
                                                    15 * y_norm))
        pygame.draw.rect(screen, ORANGE,
                         pygame.Rect(285 * x_norm, 118 * y_norm, 80 * x_norm,
                                     15 * y_norm), screen_size)
        pygame.draw.rect(screen, ORANGE,
                         pygame.Rect(275 * x_norm, 50 * y_norm, 100 * x_norm,
                                     90 * y_norm), 2 * screen_size)

        write_col("Nächster Stich", 288, 120, 10, ORANGE)

    elif status == 3:  # Endsauswertung
        screen.fill(BLACK)
        # Hintergrund Meine Karten:

        x = 10 * x_norm
        y = 10 * y_norm

        dichte = 100

        for i in range(dichte):
            pygame.draw.line(screen, GREY, [x, y], [x, 290 * screen_size], 1)
            x += 380 / dichte * x_norm

        x = 10 * x_norm
        y = 10 * y_norm

        for i in range(dichte):
            pygame.draw.line(screen, GREY, [x, y], [390 * screen_size, y], 1)
            y += 280 / dichte * y_norm

        # Figur
        fig = pylab.figure(figsize=[4.8, 3.3],  # Inches
                           dpi=40 * screen_size)  # 100 dots per inch, so the resulting buffer is 400x400 pixels

        ax = fig.gca()

        ax.plot(punkte_verlauf, color='black')

        canvas = agg.FigureCanvasAgg(fig)   # Graph definieren
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        size = canvas.get_width_height()

        rectangle(20, 20, 357, 19)          # Hintergrund Titel
        write_col("Spiel beendet", 22, 22, 10, ORANGE)
        pygame.draw.line(screen, ORANGE, [22 * screen_size, 34 * screen_size], [372 * screen_size, 34 * screen_size], 4)
        rectangle(20, 48, 140, 15)          # Hintergrund "Auswertung"
        write("Auswertung über alle Runden:", 22, 50, 10)
        rectangle(20, 74, 140, 118)         # Inforechteck
        write_col("Mensch: " + str(punkte[0]), 52, 78, 7, ORANGE)
        write("Punkte:                       / Computer: " + str(punkte[1]), 24, 78, 7)
        write("Differenz: " + str(punkte[1] - punkte[0]), 24, 88, 7)
        rectangle(20, 202, 357, 30)         # Endauswertung
        rectangle(20, 242, 357, 20)         # Beenden Knopf
        write_col("Beenden", 180, 247, 10, ORANGE)
        rectangle(171, 48, 202, 145)        # Hintergrund Diagramm

        if punkte[0] > punkte[1]:
            spieler = 0
        else:
            spieler = 1
        write_col(spieler_vokabular[spieler] + " gewinnt.", 160, 211, 10, ORANGE)
        surf = pygame.image.fromstring(raw_data, size, "RGB")
        screen.blit(surf, (176 * x_norm, 54 * y_norm))  # Spielverlauf anzeigen

    elif status == 4:
        karten_einsehen()

    pygame.display.flip()   # Fenster aktualisieren

    clock.tick(30)  # Refresh-Zeiten festlegen

pygame.quit()
