#Grafische Oberfläche mit Minimax
# Importe
import time
import random
import matplotlib
import matplotlib.backends.backend_agg as agg
import pylab
import pygame
import copy

farb_vokabular = ["Herz", "Schaufel", "Karo", "Kreuz"]  # Farbenbezeichnungen
spieler_vokabular = ["Mensch", "Computer"]  # Spielerbezeichnungen
spiel_modi = ["Obe-Abe", "Une-Ufe", "Herz-Trumpf", "Schaufel-Trumpf", "Karo-Trumpf",
              "Kreuz-Trumpf"]  # Spielmodi-Bezeichungen
sorten = ["6", "7", "8", "9", "10", "J", "Q", "K", "A"]  # Abkürzungen der Kartennamen

farben = [pygame.image.load("Data/" + i + ".png") for i in farb_vokabular]  # Graphische Dateien laden

entwickler_mod = True  # Computer Karten können eingesehen werden
performance = False  # Baumtiefenuntersuchung auf max 1

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


def get_punkte(x):  # gibt Punktewert einer Karte zurück

    if get_col(x) == trumpf:
        return trumpf_tabelle[get_typ(x)]
    else:
        return punkte_tabelle[get_typ(x)]


def get_col(x):  # Funktion die die Kartenfarbe (Herz etc) ausgibt
    return x // 9


def switch(x):  # Wechselt den Wert 0 zu 1 und 1 zu 0
    x = 1 - x
    return x


def get_hand(anzahl, länge):  # Gibt "anzahl" zufällige Hände der länge "länge" aus
    hand = list(range(36))
    random.shuffle(hand)
    result = []
    for i in range(anzahl):
        result.append(hand[länge * i:länge * (i + 1)])
    return result


def evaluate_game(game, ansager):  # Gibt ein Punktevektor aus, für ein eingespeistes Spiel 'game'

    pkt = [0, 0]
    for i in range(int(len(game) / 2)):  # Abrechnung findet jeden zweiten Stich statt
        if get_winner(game[i * 2], game[i * 2 + 1]) == 0:
            ansager = switch(ansager)
        pkt[ansager] += get_punkte(game[i * 2]) + get_punkte(game[i * 2 + 1])
    return pkt


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


def ansage_sim(spieler, grösse, hand):  # Minimax-Ansage bei unvollständiger Information

    verlauf = []
    for i in range(grösse):
        spielfeld = []  # Spielfeld für die Simulation leeren
        try:
            spielfeld.append(ausspielen(copy.deepcopy(hand), spieler, False))  # Minimax Ansage
            spieler = switch(spieler)  # Spieler wechseln
            spielfeld.append(ausspielen(copy.deepcopy(hand), switch(spieler), spielfeld[0]))  # Minimax Reaktion

            if get_winner(spielfeld[0], spielfeld[1]) == 1:  # Gewinner bestimmen
                spieler = switch(spieler)
            for ii in range(2):  # Ausgespielte karten entfernen
                hand[ii] = [iii for iii in hand[ii] if iii not in spielfeld]

            [verlauf.append(ii) for ii in spielfeld]  # Spielverlauf updaten
        except:
            break
    return verlauf


def ausspielen(hand, ansager, karte_1):  # Minimax Ansage/Reaktion

    global trumpf, punkte_tabelle, trumpf_tabelle, punkte_tabelle, memo_verlauf, pred_card

    trumpf = 100  # Trumpf deaktivieren

    if modus == 0:
        punkte_tabelle = [0, 0, 8, 0, 10, 2, 3, 4, 11]  # Punktetabelle: Obe-Abe
    elif modus == 1:
        punkte_tabelle = [11, 0, 8, 0, 10, 2, 3, 4, 0]  # Punktetabelle: Une-Ufe
    else:
        punkte_tabelle = [0, 0, 0, 0, 10, 2, 3, 4, 11]  # Punktetabelle: Nicht - Trumpfkarten
        trumpf = modus - 2  # Trumpf aktivieren

    trumpf_tabelle = [0, 0, 0, 14, 10, 20, 3, 4, 11]  # Trumpfkarten

    # Spielbaum vorbereiten - Wurzel legen

    hand[0].sort()  # Hand sortieren
    hand[1].sort()

    layer = 0  # Baumtiefe zu beginn der Baumbildung

    for i in range(len(hand)):  # Handinhalt in Card-Objekte umwandeln
        for ii in range(len(hand[i])):
            name = copy.deepcopy(hand[i][ii])
            used = copy.deepcopy([hand[i][ii]])
            owner = copy.deepcopy(i)
            hand[i][ii] = Card(name, used, owner, 0)

    if not karte_1:  # karte_1 = Spielfeld[0], Reagieren/Ansagen
        subject_cards = hand[ansager]  # Ansagen -> Karten des Ansagers werden ausgelegt
        tree = [Knoten(hand[ansager][i], str(hand[ansager][i].val)) for i in range(len(hand[ansager]))]
    else:
        # Karte 1 in Objekt umformen, Wurzel des Baumes wird Spielfeld[0]
        name = copy.deepcopy(karte_1)
        used = copy.deepcopy([karte_1])
        owner = copy.deepcopy(ansager)
        karte_1 = Card(name, used, owner, 0)

        subject_cards = [karte_1]  # Reagieren -> Erste Karte des Stichs bereits ausgespielt
        tree = [Knoten(karte_1, str(karte_1.val))]

    layer += 1  # Baumtiefe anpassen
    prnts = list(range(0, len(subject_cards)))  # Position der Väterknöten in tree einspeichern
    component_sum = [len(tree)]  # Längen des Trees zu jedem neuen Layer
    layer_len = []  # Einzelne Längen der Layers

    if performance and not karte_1:  # Baumtiefenuntersuchung: Ansagen
        rechen_schritte = [2, 2, 2, 3, 3, 4, 4, 5, 4, 3, 2, 0]
    elif performance:  # Baumtiefenuntersuchung: Reaktion
        rechen_schritte = [2, 3, 3, 3, 4, 4, 5, 5, 4, 3, 2, 0]
    else:  # Baumtiefenuntersuchung: Modus Ansagen, Böcke finden
        rechen_schritte = [2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 2, 0]

    print(rechen_schritte)

    reps = rechen_schritte[-len(hand[1])]  # Baumtiefenuntersuchung
    # Spielbaum ausbauen - An Wurzel und neue Äste anknüpfen

    for g in range(reps):

        for i in prnts:  # Stich Reaktion

            start_size = len(tree)  # Baumgrösse speichern

            ansager_stich = 0  # Ansager des Stichs bestimmen
            if tree[i].name.val in [ii.val for ii in hand[1]]:
                ansager_stich = 1

            subj = tree[i].name  # Ansagerkarten werden als 'subj' bezeichnet
            moeglich = [copy.deepcopy(hand[switch(ansager_stich)][iii])  # Noch nicht ausgespielte Karten finden
                        for iii in range(len(hand[ansager_stich])) if
                        hand[switch(ansager_stich)][iii].val not in tree[i].name.usd]

            object_cards = []
            [object_cards.append(i) for i in moeglich if
             get_col(i.val) == get_col(subj.val)
             or get_col(i.val) == trumpf]  # Regelzulässige Karten aus 'moeglich' filtern
            [object_cards.pop(i) for i in range(len(object_cards))

             if object_cards[i] in subj.usd]  # Gebrauchte Karten d. Subjekts werden entfernt

            if not object_cards:  # Falls Gegner Farbe nicht hat kann er alles auspielen
                object_cards = moeglich[:]

            subj = tree[i].name  # Ansagerkarte bestimmen

            for ii in range(len(object_cards)):  # Ansager mit Reaktionskarten abgleichen
                wechsel = get_winner(subj.val, object_cards[ii].val)  # Gewinnerkarte bestimmen
                if wechsel == 1:
                    winner = switch(subj.ownr)  # Besitzerwechsel
                else:
                    winner = copy.deepcopy(subj.ownr)  # ursprünglicher Besitzer

                object_cards[ii].ownr = copy.deepcopy(winner)  # Neuer Besitzer der Objektkarte anpassen
                object_cards[ii].lyr = copy.deepcopy(layer)  # 'layer' der Rohkarte updaten
                object_cards[ii].usd = copy.deepcopy(tree[i].name.usd)  # Gebrauchte Karten updaten
                object_cards[ii].usd.append(object_cards[ii].val)

                if len(object_cards[ii].usd) > layer + 1:  # eingespeicherte Werte löschen
                    object_cards[ii].usd.pop(1)

                tree.append(Knoten(copy.deepcopy(object_cards[ii]), tree[i]))  # überarbeitete Rohkarte in Tree einfügen

            tree[i].children = copy.deepcopy(tree[start_size:len(tree)])

        component_sum.append(len(tree))  # Baumlänge updaten

        prnts = [i for i in range(len(tree)) if tree[i].name.lyr == layer]  # Vaterknoten eintragen
        layer += 1  # Baumtiefe updaten

        if g != reps - 1:  # Ansagen

            subject_cards = []

            for i in prnts:  # Vaterknoten
                for ii in hand[tree[i].name.ownr]:  # Hand des Spielers, des Vaterknotens
                    if ii.val not in tree[i].name.usd:  # Bereitsgespielte Karten aussortieren
                        ii.lyr = copy.deepcopy(layer)  # Layer updaten

                        if get_winner(tree[i].name.val, ii.val) == 1:  # Besitzer auf Ansager setzen falls verloren
                            ii.ownr = copy.deepcopy(switch(tree[i].name.ownr))
                        else:
                            ii.ownr = copy.deepcopy(tree[i].name.ownr)

                        ii.usd = copy.deepcopy(tree[i].name.usd)  # Ausgespielte Karten updaten
                        ii.usd.append(ii.val)  # Gespilete Karten updaten

                        subject_cards.append(copy.deepcopy(ii))  # Vorbereitetes Objekt zu den Subjektkarten hinzufügen
                        tree.append(Knoten(copy.deepcopy(ii), tree[i]))  # tree & graphic tree hinzufügen

            layer += 1  # Baumtiefe anpassen
            component_sum.append(len(tree))  # Baumlänge updaten
            layer_len.append(len(tree) - component_sum[-2])  # Länge der einzelnen Layers updaten
            prnts = list(range(component_sum[-1] - layer_len[-1], component_sum[-1]))  # 'prnts' Positionsliste updaten

    # Baum beendet - Minimax Auswertung des Baumes

    all_games = []  # Liste mit näherer Auswahl an Spielverläufen

    for tot in range(int(len(component_sum) - 1)):  # Jede Komponente d. Baumes

        if tot % 2 == 0:  # Jeder 2. Zug ist Stichabrechnung
            layer = tree[component_sum[-tot - 2]:component_sum[-tot - 1]]  # Einzelner Layer aus dem Baum filtern

            if len(layer) != 0:  # leerer Layer

                prnts = []  # Vaternknoten
                chldr = []  # Kinder der Vaterknoten

                for i in layer:

                    if i.parent not in prnts:  # Vaterkarte finden
                        prnts.append(i.parent)
                        chldr.append([i])

                    else:  # neue Vaterkarte bereits in prnts vorhanden
                        chldr[prnts.index(i.parent)].append(i)

                for i in range(len(prnts)):

                    # Heuristischer Teil der Arbeit, Kriterien für Minimax, was ist eine gute Karte?
                    # Kann ein Kind gewinnen? -> es tut es möglichst punkte reich

                    sieg = [ii for ii in chldr[i] if get_winner(prnts[i].name.val, ii.name.val) == 1]

                    if not sieg:
                        sieg = chldr[i]  # Wenn Gewinnen keine Möglichkeit ist, dann alle auswählbar

                    typen = [get_typ(ii.name.val) for ii in sieg]  # Hierarchien der Karteneintragen
                    if modus == 0:  # Obe-Abe
                        opt_card = sieg[typen.index(min(typen))]
                    elif modus == 1:  # Une-ufe
                        opt_card = sieg[typen.index(max(typen))]
                    else:  # Trumpf hat eigene Hierarchien, Typen muss neu berechnet werden
                        typen = []
                        for ii in sieg:
                            if get_col(ii.name.val) == trumpf:
                                if get_typ(ii.name.val) == 5:
                                    typen.append(10)  # Trumpf Junge bekommt höchste Wertung (hierarchisch, Ass: 8)
                                elif get_typ(ii.name.val) == 3:
                                    typen.append(9)  # Näll bekommt 2.höchste Wertung
                                else:
                                    typen.append(get_typ(ii.name.val))
                            else:
                                typen.append(get_typ(ii.name.val))
                        opt_card = sieg[typen.index(min(typen))]

                    # Nachbarkarten suchen, die günstiger (hinsichtlich Punkte) sind.

                    try:
                        referenz = 0
                        if opt_card.name.val + 1 in [ii.name.val for ii in sieg] and get_punkte(
                                opt_card.name.val + 1) > get_punkte(opt_card.name.val):
                            opt_card = sieg[[ii.name.val for ii in sieg].index(opt_card.name.val + 1)]
                            referenz = get_punkte(opt_card.name.val)
                        if opt_card.name.val - 1 in [ii.name.val for ii in sieg] and get_punkte(
                                opt_card.name.val - 1) > get_punkte(opt_card.name.val):
                            if get_punkte(sieg[[ii.name.val for ii in sieg].index(
                                    opt_card.name.val - 1)].name.val) > referenz:
                                opt_card = sieg[[ii.name.val for ii in sieg].index(opt_card.name.val - 1)]
                    except:
                        pass  # Es existieren keine Nachbarkarten

                    chldr[i] = opt_card  # Beste Karte wird eingetragen

                # Verknüpfen - Spielverläufe einspeichern

                if tot == 0:  # Bei erster Komponente wird all_games geupdatet (Wurzel für jeden Spielverlauf gelegt)
                    all_games = [[prnts[i], chldr[i]] for i in range(len(prnts))]
                else:
                    for i in range(len(all_games)):  # An jeweilige Wurzel anknüpfen
                        for ii in chldr:
                            if all_games[i][0].parent == ii:
                                all_games[i].insert(0, ii)
                                all_games[i].insert(0, ii.parent)

        max_len = max([len(i) for i in all_games])  # Spielverläufe die zu kurz sind heraus streichen
        all_games = [i for i in all_games if len(i) == max_len]  # Vollständiger Spielverlauf einspeichern

    all_games = [[ii.name.val for ii in i] for i in all_games]

    auszahlung = max(
        [evaluate_game(i, ansager)[0] - evaluate_game(i, ansager)[1] for i in
         all_games])  # Höchste Auszahlungs Differenz nehmen

    for i in all_games:
        if evaluate_game(i, ansager)[0] - evaluate_game(i, ansager)[1] == auszahlung:
            opt_verlauf = i

    memo_verlauf = opt_verlauf  # Manchmal muss der Zug nicht vorgerechnet werden, wenn vorausgesagte Karte gelegt wird
    pred_card = opt_verlauf[1]

    if not karte_1:  # Stichansage
        return opt_verlauf[0]
    else:  # Stichreaktion
        return opt_verlauf[1]


pygame.init()  # initialisieren von pygame
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
    write("i) Ansager Bestimmen..........:", 25, 58, 7)

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
        write(spiel_modi[modus] + " (Bestimmt durch Computer)", 209, 84, 7)

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
gesammt_ansager = 1
performance = True
stich = [0, 0]  # zählt die stiche um einen Match zu identifizieren

while spielaktiv:

    screen.fill(BLACK)  # Grundierung

    # Überprüfen, ob Nutzer eine Aktion durchgeführt hat

    m_x = pygame.mouse.get_pos()[0]
    m_y = pygame.mouse.get_pos()[1]

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            spielaktiv = False
            print("Spieler hat Quit-Button angeklickt")
            matplotlib.pyplot.close('all')
        elif event.type == pygame.MOUSEBUTTONUP and status == -2:  # Deckblatt
            if m_y > 250 * y_norm:
                if m_x > 290 * x_norm:
                    status = -1.11
                elif m_x < 140 * x_norm:
                    if entwickler_mod:
                        entwickler_mod = False
                    else:
                        entwickler_mod = True

        elif event.type == pygame.MOUSEBUTTONUP and status == -1.1:
            if 250 * screen_size <= m_y <= 268 * screen_size:  # Zurück zum Hauptmenü
                status = -1

        elif event.type == pygame.MOUSEBUTTONUP and status == -1:
            if 58 * screen_size <= m_y <= 78 * screen_size:
                if m_x >= 140 * screen_size:  # Modus wählen
                    if m_x <= 195 * screen_size:
                        spieler = 0
                        modus = 0

                    elif m_x <= 270 * screen_size:
                        modus = sugg
                        spieler = 1

                    elif spieler == 0:
                        status = -1.1

                    gesammt_ansager = spieler
                    matplotlib.pyplot.close()

            elif spieler == 0 and 98 * screen_size + len(spiel_modi) * screen_size * 18 >= m_y >= 98 * screen_size \
                    and m_x >= 205 * screen_size:
                modus = (m_y - 98 * screen_size) // (18 * screen_size)

            elif 260 * screen_size <= m_y <= 278 * screen_size:
                status = spieler  # Spielstart
                print("MODUS:", spiel_modi[modus])
                print("TRUMPF:", trumpf)
                performance = True

        elif event.type == pygame.MOUSEBUTTONUP and status == 0:  # Spieler 1 sagt Stich an
            if 12 * screen_size <= m_y <= 27 * screen_size and 243 * screen_size <= m_x <= 258 * screen_size and entwickler_mod:
                print("Spieler hat PC Karten angesehen")
                status = 4
            else:

                if len(spielfeld) == 1:
                    moegl_karten = [i for i in hand[0] if get_col(i) == get_col(spielfeld[0])]

                    komplett_hand = False
                    if not moegl_karten:
                        komplett_hand = True

                    [moegl_karten.append(ii) for ii in hand[0] if
                        get_col(ii) == trumpf and modus > 1]  # Trumpf Karten dazu

                    if komplett_hand:
                        moegl_karten = hand[0]
                else:
                    moegl_karten = hand[0]

                try:
                    if hand[0][auswählen()] in moegl_karten:
                        spielfeld.append(hand[0][auswählen()])
                        if len(spielfeld) == 1:
                            status = 1
                        else:
                            status = 2

                        spielbericht.append("Karte " + str(len(spielfeld)) + ": " + farb_vokabular[get_col(spielfeld[-1])] + " " +
                        sorten[get_typ(spielfeld[-1])])
                        spieler = switch(spieler)
                except:
                    pass # Input Mensch ungültig

        elif status == 2 and event.type == pygame.MOUSEBUTTONUP:  # Auswerten

            hand[0] = [i for i in hand[0] if i not in spielfeld]  # Karten wegnehmen
            hand[1] = [i for i in hand[1] if i not in spielfeld]

            if get_winner(spielfeld[0], spielfeld[1]) == 0:
                spieler = switch(spieler)

            punkte[spieler] += sum([get_punkte(i) for i in spielfeld])

            punkte_verlauf.append(punkte[0] - punkte[1])

            spielbericht.append(spieler_vokabular[spieler] + " gewinnt " + str(
                sum([get_punkte(i) for i in spielfeld])) + " Punkte.")

            print("Pred:", memo_verlauf)
            print("Actual:", spielfeld)

            spielfeld = []
            status = spieler

            if len(hand[0]) == 0:  # Alle Karten ausgespielt, Beenden schirm
                punkte[spieler] += 5  # Letzter Stich gibt 5 P
                status = 3

        elif status == 3 and 242 * screen_size <= m_y <= 262 * screen_size \
                and 20 * screen_size <= m_x <= 377 * screen_size and event.type == pygame.MOUSEBUTTONUP:  # Beenden knopf

            print("Spiel wurde beendet mit " + str(punkte))
            matplotlib.pyplot.close('all')

            status = -1.11  # Reset

        elif status == 4 and 250 * screen_size <= m_y <= 268 * screen_size and event.type == pygame.MOUSEBUTTONUP:

            status = 0

    # Spielfeld/figuren zeichnen

    if 0 <= status <= 2:

        hintergrund()
        show_hand(hand[0])

        # Spielprotokoll auzeigen:
        for i in range(6):
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

    elif status == -1:  # startfeld
        eingabe_fenster()
        if spieler == 1:
            modus = sugg

    elif status == -1.1:  # Karten anschauen:
        karten_vorschau()

    elif status == -1.11:  # Neustarten, Variablen reseten

        gesammt_ansager = switch(gesammt_ansager)  # Ansager jede Runde Wechseln

        hand = get_hand(2, 12)  # Hand austeilen
        hand[0].sort()  # Hand sortieren
        hand[1].sort()

        print(hand)

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

        mod_pkt = [0 for ii in range(6)]
        for ii in range(6):
            mod_hand = copy.deepcopy(hand)
            modus = ii
            spieler = 1
            for iii in range(11):
                spielfeld = [ausspielen(copy.deepcopy(mod_hand), spieler, False)]  # Ansagen

                spieler = switch(spieler)
                spielfeld.append(ausspielen(copy.deepcopy(mod_hand), spieler, spielfeld[0]))
                if get_winner(spielfeld[0], spielfeld[1]) == 0:
                    spieler = switch(spieler)
                if spieler == 1:
                    mod_pkt[modus] += get_punkte(spielfeld[0]) + get_punkte(spielfeld[1])
                else:
                    mod_pkt[modus] -= get_punkte(spielfeld[0]) + get_punkte(spielfeld[1])
                for iv in range(2):
                    mod_hand[iv] = [v for v in mod_hand[iv] if v not in spielfeld]

        sugg = mod_pkt.index(max(mod_pkt))
        print("Vorhersagen:")
        print("Punkte Differenz (PC sagt an): ", max(mod_pkt))
        print("Punkte Differenz (Mensch sagt an): ", min(mod_pkt))
        spielfeld = []

        performance = True
        modus = 0
        spieler = gesammt_ansager

    elif status == 0:

        auswählen()
        pygame.draw.rect(screen, ORANGE,
                         pygame.Rect(30 * screen_size, 52 * screen_size, 210 * screen_size, 192 * screen_size),
                         2 * screen_size)

    elif status == 1:  # PC ist dran mit reagieren/vorsagen - Warte status

        bitte_warten()

        pygame.display.flip()

        letzter_stich = False

        if spielfeld == []:  # 1. Stich (Ansagen - Computer)

            # Ansagen

            if len(hand[1]) > 1:
                opt_zug = ausspielen(copy.deepcopy(hand), 1, False)
            else:
                letzter_stich = True

            if not letzter_stich:

                spielfeld.append(opt_zug)
            else:
                spielfeld.append(hand[1][len(hand[1]) - 1])

        else:  # 2. Stich (reaktion)

            mögl = [ii for ii in hand[1] if
                    get_col(ii) == get_col(spielfeld[0]) or get_col(ii) == trumpf and modus > 1]

            if not mögl:
                mögl = hand[1]

            if len(hand[1]) > 1:
                opt_zug = ausspielen(copy.deepcopy(hand), 1, spielfeld[0])
                spielfeld.append(opt_zug)
            else:
                spielfeld.append(hand[1][-1])

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

        canvas = agg.FigureCanvasAgg(fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        size = canvas.get_width_height()

        rectangle(20, 20, 357, 19)  # Hintergrund Titel
        write_col("Spiel beendet", 22, 22, 10, ORANGE)
        pygame.draw.line(screen, ORANGE, [22 * screen_size, 34 * screen_size], [372 * screen_size, 34 * screen_size], 4)
        rectangle(20, 48, 140, 15)  # Hintergrund "Auswertung"
        write("Auswertung", 22, 50, 10)
        rectangle(20, 74, 140, 118)  # Inforechteck
        write_col("Mensch: " + str(punkte[0]), 52, 78, 7, ORANGE)
        write("Punkte:                       / Computer: " + str(punkte[1]), 24, 78, 7)
        write("Differenz: " + str(punkte_verlauf[-1]), 24, 88, 7)
        rectangle(20, 202, 357, 30)  # Endauswertung
        rectangle(20, 242, 357, 20)  # Beenden Knopf
        write_col("Beenden", 180, 247, 10, ORANGE)
        rectangle(171, 48, 202, 145)  # Hintergrund Diagramm
        if punkte[0] > punkte[1]:
            spieler = 0
        else:
            spieler = 1
        write_col(spieler_vokabular[spieler] + " gewinnt.", 160, 211, 10, ORANGE)
        surf = pygame.image.fromstring(raw_data, size, "RGB")
        screen.blit(surf, (176 * x_norm, 54 * y_norm))  # Spielverlauf anzeigen

    elif status == 4:
        karten_einsehen()

    # Fenster aktualisieren
    pygame.display.flip()

    # Refresh-Zeiten festlegen
    clock.tick(30)

pygame.quit()
