# Minimax für Une-Ufe, Obe-Abe (Stichansage, -reaktion), Daten Produktion

import copy
import pickle
import random
import time

performance = True

class Card:                                     # Kartenobjekt
    def __init__(self, val, usd, ownr, lyr):
        self.val = val                          # Speicherwert (0-35, für jeweils eine Karte)
        self.usd = usd                          # Gebrauchte Karten
        self.ownr = ownr                        # Inhaber der Karte
        self.lyr = lyr                          # Baumtiefe


class Knoten:                                   # Baumknotenpunkt
    def __init__(self, name, parent):
        self.name = name                        # Speicherwert des Knotens
        self.parent = parent                    # Vaterknoten
        self.opt = 0                            # Variabel zur besseren Identifikation im Minimax-Verfahren

        tiefe = 0                               # Schleife zur Ermittlung der Baumtiefe
        obj = parent
        while True:
            try:
                obj = obj.parent
                tiefe += 1
            except:
                break
        self.layer = tiefe

        self.children = []                      # Kinderknoten

    def select(self):                           # Markieren der Karte wenn sie im optimalen Spielverlauf
        self.opt = 1                            # enthalten ist.


def get_hand(anzahl, länge):                            # Gibt "anzahl" zufällige Hände der länge "länge" aus
    hand = list(range(36))
    random.shuffle(hand)
    result = []
    for i in range(anzahl):
        result.append(hand[länge * i:länge * (i + 1)])
    return result


def get_typ(x):                                         # Funktion die den Kartentyp (6, 7, 8, 9, 10, j, Q, etc) ausgibt
    return x - x // 9 * 9


def get_col(x):                                         # Funktion die die Kartenfarbe (Herz etc) ausgibt
    return x // 9


def switch(x):                                          # Wechselt den Wert 0 zu 1 und 1 zu 0
    x = 1 - x
    return x


def evaluate_game(game, ansager):                       # Gibt die Auszahlung für ein eingespeistes Spiel 'game' aus

    pkt = [0, 0]
    for i in range(int(len(game) / 2)):                 # Abrechnung findet jeden zweiten Stich statt

        crds = [game[i * 2], game[i * 2 + 1]]

        bal = 0
        for ii in crds:
            if get_col(ii) == trumpf and modus > 1:
                if get_typ(ii) == 5:
                    bal += 20
                elif get_typ(ii) == 3:
                    bal += 14
            else:
                bal += punkte_tabelle[get_typ(ii)]

        if get_winner(crds[0], crds[1]) == 1:
            ansager = switch(ansager)

        pkt[ansager] += bal

    return pkt


def get_winner(c1, c2):                                   # Gewinner für einen Stich
    wechsel = 0
    if modus == 0 and get_typ(c1) < get_typ(c2) and get_col(c1) == get_col(c2):
        wechsel = 1
    elif modus == 1 and get_typ(c1) > get_typ(c2) and get_col(c1) == get_col(c2):
        wechsel = 1
    elif modus > 1 and get_typ(c1) < get_typ(c2) and get_col(c1) == get_col(c2) and get_col(c2) != trumpf or get_col(c2) == trumpf \
            and get_col(c1) != trumpf or (get_typ(c2) == 5 and get_col(c2) == trumpf) or \
            get_typ(c2) == 3 and get_col(c2) == trumpf and get_typ(c1) != 5 and get_col(c1) != trumpf:
        wechsel = 1
    elif modus > 1 and get_col(c1) == trumpf and get_col(c2) == trumpf\
            and get_typ(c2) > get_typ(c1) != 5 and get_typ(c1) != 3:
        wechsel = 1
    return wechsel


def get_punkte(x):

    if get_col(x) == trumpf and modus > 1:
        return trumpf_tabelle[get_typ(x)]
    else:
        return punkte_tabelle[get_typ(x)]


def ausspielen(hand, ansager, karte_1):  # Minimax Ansage/Reaktion

    global trumpf, punkte_tabelle, trumpf_tabelle, punkte_tabelle

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
        rechen_schritte = [1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 2, 0]
    elif performance:  # Baumtiefenuntersuchung: Reaktion
        rechen_schritte = [1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 2, 0]
    else:  # Baumtiefenuntersuchung: Modus Ansagen, Böcke finden
        rechen_schritte = [1, 1, 1, 1, 1, 2, 2, 3, 3, 3, 2, 0]

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

    if not karte_1:  # Stichansage
        return opt_verlauf[0]
    else:  # Stichreaktion
        return opt_verlauf[1]


def ansage_sim (spieler, grösse, hand):

    verlauf = []
    for i in range(grösse):

        spielfeld = []

        try:
            if spieler == 0:
                spielfeld.append(ausspielen(copy.deepcopy(hand), 0, False))         # Minimax Ansage
            else:
                spielfeld.append(ausspielen(copy.deepcopy(hand), 1, False))  # Minimax Ansage

            spieler = switch(spieler)                                               # Spieler wechseln

            if spieler == 0:                                                        # Stich-Reaktion
                spielfeld.append(ausspielen(copy.deepcopy(hand), 1, spielfeld[0]))  # Minimax Reaktion

            else:
                spielfeld.append(ausspielen(copy.deepcopy(hand), 0, spielfeld[0]))  # Minimax Reaktion

            if get_winner(spielfeld[0], spielfeld[1]) == 1:                         # Gewinner bestimmen
                spieler = switch(spieler)

            for ii in range(2):
                hand[ii] = [iii for iii in hand[ii] if iii not in spielfeld]       # Ausgespielte karten entfernen

            [verlauf.append(ii) for ii in spielfeld]                               # Verlauf updaten
        except:
            break

    return verlauf


def get_hand(anzahl, länge):  # Gibt "anzahl" zufällige Hände der länge "länge" aus
    hand = list(range(36))
    random.shuffle(hand)
    result = []
    for i in range(anzahl):
        result.append(hand[länge * i:länge * (i + 1)])
    return result


def get_typ(x):  # Funktion die den Kartentyp (6, 7, 8, 9, 10, j, Q, etc) ausgibt
    return x - x // 9 * 9


def get_col(x):  # Funktion die die Kartenfarbe (Herz etc) ausgibt
    return x // 9


def get_x(hand, gebr, ansage, minimax): # Trainingsdaten vorbereiten

    global data_a, data_r
    if ansage:
        x = [0 for i in range(144)]  # Ansagen
    else:
        x = [0 for i in range(180)]  # Reagieren

    for ii in hand[spieler]:  # Meine Hand Karten
        x[ii] = 1

    for ii in hand[switch(spieler)]:  # Seine Hand Karten
        x[ii + 36] = 1

    for ii in gebr:  # Gespielte Karten
        x[ii + 72] = 1

    if ansage:
        x[spielfeld[0] + 108] = 1  # Ausgespielte Karte einfügen
    else:
        x[spielfeld[0] + 108] = 1  # Ausgespielte Karte einfügen
        x[spielfeld[-1] + 144] = 1  # regierende Karte einfügen

    if minimax: # Nicht Minimax Karten negativ belasten, Minimax im erfolgsfall belohnen
        y = [1]
    else:
        y = [0]

    if ansage:
        data_a[0].append(x)
        data_a[1].append(y)
    else:
        data_r[0].append(x)
        data_r[1].append(y)

modus = 0

if modus < 2:
    punkte_tabelle = [0, 0, 8, 0, 10, 2, 3, 4, 11]  # Bepunktung der einzelnen Karten
else:
    punkte_tabelle = [0, 0, 0, 0, 10, 2, 3, 4, 11]  # Bepunktung der einzelnen Karten

mod_name = ["OA", "UU", "HE", "SC", "KA", "KR"]
s_name = ["Data/108_A-"+mod_name[modus]+"_data", "Data/108_R-"+mod_name[modus]+"_data"]

# Speicher definieren / löschen
pickle.dump([[], []], open(s_name[0], "wb"))       # Löscht alle gespeicherten Daten
pickle.dump([[], []], open(s_name[1], "wb"))       # Löscht alle gespeicherten Daten

data_a = [[], []]  # Ansage Data
data_r = [[], []]  # Reaktions Data

print("Start: ",  time.strftime("%d.%m.%Y %H:%M:%S"))
aktiv = True

while aktiv:
    g_hand = get_hand(2, 12)
    # Modus bestimmen
    spieler = 0
    for gg in range(2): # Einmal mit minimax, einmal zufällig und nicht minimax Karte
        hand = copy.deepcopy(g_hand)

        used = []
        for i in range(11):
            spielfeld = []
            # Ansagen
            if gg == 0:
                spielfeld.append(ausspielen(copy.deepcopy(hand), spieler, False))
                used.append(spielfeld[-1])
                get_x(hand, used, True, True)
            else:
                random.shuffle(hand[spieler])
                spielfeld.append(hand[spieler][0])
                hand[spieler].sort()
                used.append(spielfeld[-1])
                get_x(hand, used, True, False)

            spieler = switch(spieler)

            # Reagieren
            if gg == 0:
                spielfeld.append(ausspielen(copy.deepcopy(hand), spieler, spielfeld[0]))
                used.append(spielfeld[-1])
                get_x(hand, used, False, True)
            else:

                mögl_g = [iii for iii in hand[spieler] if get_col(iii) == trumpf or get_col(iii) == get_col(spielfeld[0])]
                if not mögl_g:
                    mögl_g = copy.deepcopy(hand[spieler])
                random.shuffle(mögl_g)
                spielfeld.append(mögl_g[0])
                used.append(spielfeld[-1])
                get_x(hand, used, False, False)

            if get_winner(spielfeld[0], spielfeld[1]) == 0:
                spieler = switch(spieler)
            for ii in range(2):
                hand[ii] = [iii for iii in hand[ii] if iii not in spielfeld]
                
    if int(time.strftime("%d")) == 2 and int(time.strftime("%H")) > 16:    # Datum und Stunde eingeben wann es beenden soll
        print("Ende: ", time.strftime("%d.%m.%Y %H:%M:%S"))
        aktiv = False

print("Nicht beenden...")
t_x = pickle.load(open(s_name[0], "rb"))[0]
t_y = pickle.load(open(s_name[0], "rb"))[1]

[t_x.append(i) for i in data_a[0]]
[t_y.append(i) for i in data_a[1]]

pickle.dump([t_x, t_y], open(s_name[0], "wb"))

t_x = pickle.load(open(s_name[1], "rb"))[0]
t_y = pickle.load(open(s_name[1], "rb"))[1]

[t_x.append(i) for i in data_r[0]]
[t_y.append(i) for i in data_r[1]]

pickle.dump([t_x, t_y], open(s_name[1], "wb"))
print("lenX:", len(t_x), "lenY:", len(t_y))
print("Beenden Freigegeben")
