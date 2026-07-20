# Annahmen & Geschäftsregeln

Dieses Dokument sammelt alle Annahmen und Entscheidungen, die im Rahmen der Aufgabe getroffen wurden, weil die Spezifikation (`AUFGABE.md`) an dieser Stelle bewusst offen lässt. Es wird pro Teil ergänzt.

## Teil 1 – Daten übernehmen

### Zielschema

- `geraete`: bereinigter Gerätebestand. `inventarnummer` ist eindeutig (UNIQUE), da sie als fachlicher Schlüssel für Ausleihen dient.
- `ausleihen`: bereinigte Ausleihhistorie, referenziert `geraete` über eine surrogate FK (`geraet_id`), nicht über die Inventarnummer direkt.
- `import_report`: eine Zeile pro Rohdatensatz (aus `alt_inventar` bzw. `alt_ausleihen`) mit Entscheidung (`accepted` / `accepted_with_caveat` / `rejected`), Begründung und dem Original-Rohdatensatz (JSON) zur Nachvollziehbarkeit.

### Re-Run-Verhalten (Idempotenz)

Der Import ist als **Wipe-and-Reload** umgesetzt: jeder Lauf leert `ausleihen`, `geraete` und `import_report` und befüllt sie neu aus den Rohdaten. Das ist deutlich einfacher als ein Upsert gegen eine nicht-eindeutige `inventarnummer` in den Rohdaten.

**Einschränkung:** Der Import ist für die Ersteinrichtung gedacht. Wird er erneut ausgeführt, nachdem über die Anwendung bereits manuell Ausleihen angelegt, Geräte bearbeitet o. ä. wurden, gehen diese Änderungen verloren. Für den Rahmen dieser Aufgabe ist das akzeptabel; in einem Produktivsystem würde man stattdessen einen einmaligen Migrationslauf mit anschließender Sperre vorsehen.

### Validierungsregeln `alt_inventar`

| Fall | Entscheidung | Begründung im Report |
|---|---|---|
| `inventarnummer` leer | rejected | Inventarnummer fehlt |
| doppelte `inventarnummer` (z. B. `IT-005`: iPhone *und* iPad) | **erste Zeile wird übernommen, jede weitere abgelehnt** | Doppelte Inventarnummer, erste Zeile übernommen |
| `bezeichnung` leer (z. B. `IT-007`) | accepted_with_caveat, Platzhalter `"Unbekannt (<inventarnummer>)"` | Bezeichnung fehlte |
| `bezeichnung` mit Whitespace (z. B. `IT-004`) | accepted_with_caveat, getrimmt | Bezeichnung getrimmt |
| `kategorie` leer | accepted_with_caveat, Fallback `"Sonstige"` | Kategorie fehlte |
| `menge` fehlt / nicht numerisch / negativ | rejected | Menge fehlt oder ungültig |
| `menge` = 0 (z. B. `IT-023`) | accepted_with_caveat | Menge ist 0 |
| `angeschafft_am` nicht parsebar | accepted_with_caveat, NULL gespeichert | Anschaffungsdatum nicht parsebar |
| `angeschafft_am` im Format `DD.MM.YYYY` | accepted_with_caveat, auf ISO normalisiert | Datumsformat normalisiert |
| `angeschafft_am` in der Zukunft (z. B. `IT-032`) | accepted_with_caveat, Wert bleibt erhalten | Anschaffungsdatum liegt in der Zukunft |

**Begründung Duplikat-Entscheidung (`IT-005`):** Da beide Zeilen dieselbe Inventarnummer, aber unterschiedliche Geräte (iPhone vs. iPad) beschreiben, lässt sich aus den Daten nicht rekonstruieren, welches physische Gerät bei welcher Ausleihe tatsächlich gemeint war. Statt eine künstliche neue Inventarnummer zu vergeben (Gefahr, Fakten zu erfinden, die im Altsystem nicht existieren), wird die erste Zeile als kanonisch behandelt und die zweite abgelehnt und im Report sichtbar gemacht. Ausleihen, die sich auf `IT-005` beziehen, werden dem kanonischen (ersten) Gerät zugeordnet — dokumentierte Unsicherheit, keine stille Annahme.

### Validierungsregeln `alt_ausleihen`

| Fall | Entscheidung | Begründung im Report |
|---|---|---|
| `inventarnummer` verweist auf kein akzeptiertes Gerät (z. B. `IT-042`, oder Gerät wurde selbst abgelehnt) | rejected | Gerät nicht im Bestand gefunden |
| `ausgeliehen_von` leer | rejected | Ausleiher fehlt |
| `ausgeliehen_am` fehlt / nicht parsebar | rejected | Ausleihdatum fehlt oder ungültig |
| `ausgeliehen_am` im Format `DD.MM.YYYY` (z. B. `IT-018`, `IT-010`) | accepted_with_caveat, normalisiert | Datumsformat normalisiert |
| `zurueckgegeben_am` leer | accepted, NULL (= offene Ausleihe) | — kein Caveat, dokumentierte Konvention |
| `zurueckgegeben_am` im Format `DD.MM.YYYY` (z. B. Rückgabe zu `IT-029`) | accepted_with_caveat, normalisiert | Datumsformat normalisiert |
| `zurueckgegeben_am` liegt vor `ausgeliehen_am` (z. B. `IT-006`) | **rejected** | Rückgabedatum liegt vor Ausleihdatum |

**Begründung Rückgabedatum-vor-Ausleihdatum:** Es ist nicht entscheidbar, ob Ausleih- und Rückgabedatum vertauscht wurden, ob eines der beiden Daten schlicht falsch eingetragen wurde, oder ob es sich um zwei unabhängige Fehler handelt. Statt zu raten (z. B. Daten tauschen oder Rückgabedatum verwerfen und als offen behandeln), wird die Zeile komplett abgelehnt und im Report sichtbar gemacht — nachvollziehbar und ohne stille Korrektur einer nicht verifizierbaren Annahme.

## Teil 2 – Verleih (Kern)

### Definition „verfügbar"

`geraete.menge` ist die Stückzahl eines Inventarnummer-Eintrags (z. B. 5× dasselbe Werkzeug unter einer Inventarnummer). Verfügbarkeit wird daher als Stückzahl-Rechnung definiert, nicht als einfaches Ja/Nein pro Gerät:

```
verfuegbare_menge = geraete.menge − Anzahl offener Ausleihen (zurueckgegeben_am IS NULL) für dieses Gerät
verfuegbar = verfuegbare_menge > 0
```

Eine Ausleihe wird nur angelegt, wenn `verfuegbare_menge > 0` zum Zeitpunkt der Anfrage gilt; sonst Ablehnung mit `409` und lesbarem Grund (z. B. „Kein Exemplar verfügbar (0 von 3 verfügbar)"). Überfällige offene Ausleihen zählen hier genauso wie pünktliche als „offen" — die Unterscheidung überfällig/pünktlich ändert nichts an der Verfügbarkeitsdefinition (kommt in Teil 3 als eigene Ansicht hinzu, nicht als Verschärfung dieser Regel).

> ⚠️ **Bekanntes Problem — negative Verfügbarkeit (TODO, noch nicht behoben):** Die importierte Ausleihhistorie enthält Fälle, in denen mehr offene Ausleihen für ein Gerät existieren als `menge` zulässt (z. B. **Canon EOS R6, `IT-009`**: `menge = 1`, aber 2 offene Ausleihen → `verfuegbare_menge = -1`). Das Altsystem hat Verfügbarkeit offenbar nie durchgesetzt. Die aktuelle Formel lässt das zu (negativer Wert, `verfuegbar = false`, neue Ausleihen bleiben blockiert) — sie **korrigiert die Altdaten aber nicht** und die UI erklärt das negative Verhältnis nicht. Muss vor Produktivsetzung entschieden werden: Datenkorrektur beim Import (z. B. überzählige offene Ausleihen im Report markieren/zusammenführen), Anzeige-Klarstellung in der UI, oder explizit als akzeptierter Altlast-Zustand dokumentieren. Nicht vergessen, bevor Teil 3/4 (Fristen, Reservierungen) darauf aufbauen.

### Datumsfelder bei Ausleihe/Rückgabe

`ausgeliehen_am` und `zurueckgegeben_am` werden serverseitig auf das aktuelle Datum gesetzt, nicht vom Client übergeben. Das verhindert unplausible/manipulierte Datumsangaben und ist für den Praxisumfang ausreichend; eine nachträgliche Korrektur (z. B. rückwirkende Erfassung durch eine Admin-Rolle) ist nicht vorgesehen.

### Personen als Freitext

Es gibt (bewusst) keine eigene Personen-Tabelle — `ausgeliehen_von` bleibt ein Freitextfeld wie in den Altdaten. Die Historie-Filterung nach Person ist daher eine case-insensitive Teilstring-Suche, keine exakte Identität; unterschiedliche Schreibweisen derselben Person werden nicht zusammengeführt. Für Teil 5 (Auswertung „wer hat die meisten Geräte") gilt dieselbe Einschränkung.

### Kein Ausmusterungs-Status

Ein „ausgemustert"-Flag existiert noch nicht (kommt erst in Teil 5). Alle Geräte aus dem sauberen Bestand sind aktuell grundsätzlich ausleihbar, solange `verfuegbare_menge > 0`.

## Teil 3 – Leihfristen und Überfälligkeit

### Konfigurationstabelle `leihfristen`

Eine Zeile pro Kategorie (`kategorie`, `frist_tage`); eine Zeile mit `kategorie = NULL` ist die Fallback-/Standardfrist. Seed: `NULL → 14`, `Kamera → 7`, `Präsentation → 7`, `Mobilgerät → 30`. Kategorien ohne eigenen Eintrag (z. B. `Sonstige` oder künftige, in Teil 5 neu angelegte Kategorien) fallen auf die `NULL`-Zeile zurück. Es gibt bewusst keinen Lösch-Endpoint, nur Upsert (`PUT /api/leihfristen/{kategorie}`, Pfadsegment `default` für die Fallback-Zeile) — so kann die Fallback-Zeile nicht versehentlich verschwinden.

### `faellig_am` wird bei Anlage fixiert, nicht live berechnet

`ausleihen.faellig_am` wird beim Anlegen der Ausleihe einmalig aus `ausgeliehen_am + Frist(Gerätekategorie)` berechnet und persistiert (nicht bei jeder Anfrage neu aus der aktuellen Konfiguration abgeleitet).

**Begründung:** Ändert ein Admin später die Frist für eine Kategorie, soll sich das Fälligkeitsdatum bereits laufender, ausgehändigter Ausleihen nicht rückwirkend ändern — die dem Ausleiher kommunizierte Frist gilt so, wie sie bei Übergabe berechnet wurde. Neue Ausleihen verwenden automatisch die dann aktuelle Konfiguration.

Für die einmalige Ersteinrichtung (Migration `0002`) wurde `faellig_am` für alle bereits importierten Alt-Ausleihen anhand der zu diesem Zeitpunkt gültigen Konfiguration nachträglich berechnet (Backfill); ein erneuter ETL-Lauf berechnet `faellig_am` beim Laden ebenfalls neu und bleibt damit konsistent mit der aktuellen Konfiguration zum Import-Zeitpunkt.

### Definition „überfällig"

```
ueberfaellig = zurueckgegeben_am IS NULL AND faellig_am < heute
```

Nur offene Ausleihen können überfällig sein. Eine verspätet zurückgegebene Ausleihe gilt nach Rückgabe nicht mehr als überfällig — das ist reine Historie (aus `ausgeliehen_am`/`zurueckgegeben_am` weiterhin ablesbar), aber keine aktuelle Überfälligkeit mehr.

### Keine Admin-UI für Leihfristen

Die Fristen sind über die API konfigurierbar (`GET`/`PUT /api/leihfristen`), aber es gibt in Teil 3 noch keine eigene Oberfläche zum Bearbeiten — Zeitbudget. Nur Backend-Tabelle + API; eine UI dafür wäre ein sinnvoller Ausbau in Teil 5 (Geräteverwaltung), falls Zeit bleibt.

## Teil 4 – Reservierungen

### Status statt Enum

`reservierungen` folgt derselben Konvention wie `ausleihen` (nullable Spalten statt Status-Enum): `storniert_am IS NULL AND ausleihe_id IS NULL` = aktiv. `storniert_am` gesetzt = storniert. `ausleihe_id` gesetzt = abgeholt (Verweis auf die daraus entstandene Ausleihe).

### Verfügbarkeitsprüfung im Zeitraum

```
verfuegbare_menge_im_zeitraum(geraet, start, end) =
    geraet.menge
    − Anzahl offener Ausleihen (zurueckgegeben_am IS NULL)
    − Anzahl aktiver Reservierungen, die mit [start, end] überlappen
```

Zwei bewusste, konservative Entscheidungen, dokumentiert nach Rückfrage im Gespräch:

1. **Offene Ausleihen blockieren jede künftige Reservierung, unabhängig von `faellig_am` und unabhängig davon, wie weit die Reservierung in der Zukunft liegt.** Pünktliche und überfällige offene Ausleihen werden gleich behandelt. Begründung: Das Rückgabedatum ist unbekannt, solange nicht tatsächlich zurückgegeben wurde; „bis `faellig_am` frei rechnen" wäre bei einem Einzelstück-Gerät ein Versprechen, das das System nicht einhalten kann, insbesondere da die Altdaten bereits zeigen, dass Verfügbarkeit im Altsystem nicht durchgesetzt wurde (s. Teil 2, `IT-009`). Konsequenz, die bewusst in Kauf genommen wird: Ist ein Einzelstück-Gerät gerade verliehen (erst recht überfällig), kann es **für keinen** künftigen Zeitraum reserviert werden, bis es tatsächlich als zurückgegeben erfasst ist — auch nicht für einen Termin Monate später. Eine feinere Regel (z. B. Puffer nach `faellig_am` für noch-nicht-überfällige Ausleihen) wäre möglich, aber ohne echte Nutzungsdaten reine Spekulation über die richtige Puffergröße; daher nicht gebaut.
2. **Sich berührende Intervalle gelten als Überlappung** (`end_datum` einer Reservierung == `start_datum` einer anderen ⇒ blockiert). Ohne Uhrzeiterfassung wird der gemeinsame Tag konservativ als beiden zugehörig behandelt, um keine Doppelbuchung am Übergabetag zu riskieren.

### Reservierungszeitraum ist von der Leihfrist entkoppelt

Das Zeitfenster `[start_datum, end_datum]` einer Reservierung sagt nur, wie lange das Gerät für die Abholung zurückgehalten wird — es ist **keine** Vorwegnahme der Leihdauer. Bei Abholung wird `faellig_am` genauso berechnet wie bei einer regulären Ausleihe: `ausgeliehen_am = heute` (Abholdatum), `faellig_am = heute + aktuelle Leihfrist der Kategorie`. Eine 15-tägige Reservierung bei 14-tägiger Leihfrist ist damit kein Widerspruch — sie sagt nichts über die spätere Leihdauer aus. Eine Kopplung (z. B. `end_datum` auf `start_datum + Leihfrist` deckeln) wäre möglich, wurde aber bewusst nicht gebaut, um „wie lange im Voraus reservierbar" nicht mit „wie lange darf ausgeliehen werden" zu vermengen.

### Abholung: kein Zeitfenster-Zwang, keine erneute Verfügbarkeitsprüfung

Abholung ist für jede aktive Reservierung jederzeit möglich, auch außerhalb von `[start_datum, end_datum]` (z. B. verspätete Abholung nach Ablauf) — es gibt keine Sperre dafür, das wäre reine Zusatzkomplexität ohne klaren Nutzen im gegebenen Zeitbudget. Bei Abholung wird die Kapazität nicht erneut geprüft: Sie war der Reservierung bereits zugeteilt; die Reservierung wird inaktiv (durch Setzen von `ausleihe_id`) und die neu entstehende offene Ausleihe belegt stattdessen Kapazität — macht keinen Unterschied für die Gesamtbilanz.

### Person bei Abholung

`ausgeliehen_von` der entstehenden Ausleihe wird aus `reservierung.reserviert_von` übernommen, ohne Möglichkeit, bei der Abholung eine abweichende Person einzutragen. Für den Praxisumfang ausreichend; wie bei Ausleihen ist „Person" ohnehin nur Freitext ohne Identitätsprüfung (s. Teil 2).

### Reservierung muss in der Zukunft liegen

`start_datum >= heute` (heute selbst ist zulässig) und `end_datum >= start_datum`, sonst 422. Es gibt keine Admin-Möglichkeit, rückwirkend zu reservieren.

### Mehrere überlappende Reservierungen desselben Geräts sind normal, keine Sonderregel pro Person

Bei Geräten mit `menge > 1` können mehrere *verschiedene* Reservierungen für denselben Zeitraum aktiv sein, solange die Kapazitätsformel weiterhin `> 0` ergibt — das ist die beabsichtigte Funktionsweise der Verfügbarkeitsprüfung, kein Fehler. Es gibt außerdem **keine Sperre, die dieselbe Person daran hindert, für dasselbe Gerät im selben Zeitraum mehrere Einheiten zu reservieren** (z. B. zwei überlappende Reservierungen unter demselben Namen).

**Begründung:** `reserviert_von` ist Freitext ohne Identitätsprüfung (s. Teil 2, „Personen als Freitext"). Eine „eine aktive Reservierung pro Person und Gerät"-Regel wäre nur so gut wie der Namensabgleich — schon geringfügig unterschiedliche Schreibweisen (Groß-/Kleinschreibung, Leerzeichen, Kurzform) würden als unterschiedliche Personen behandelt und die Regel unbemerkt umgehen, während ein Nutzer, der seinen Namen konsequent gleich schreibt, unnötig eingeschränkt würde. Zudem ist Mehrfachbedarf ein legitimer Anwendungsfall (z. B. eine Person bucht mehrere Geräte desselben Typs für ein Team-Event). Die einzige Garantie, die das System sinnvoll durchsetzen kann und durchsetzt, ist die Gesamtkapazität (`menge`) über alle Reservierungen und offenen Ausleihen hinweg — wer im Rahmen dieser Kapazität wie viele Einheiten auf sich vereint, ist eine organisatorische Frage der Büroleitung, keine Dateningtegritätsfrage. Es gibt bewusst auch keinen Warnhinweis dazu in der Oberfläche.

### Keine Änderung bestehender Reservierungen

Es gibt keinen Endpunkt, um Datum oder Person einer bestehenden Reservierung zu ändern — nur Anlegen, Stornieren und Abholen. Eine Terminverschiebung erfordert Stornieren + Neuanlegen. Für den Praxisumfang ausreichend; „Bearbeiten" wäre ein sinnvoller Ausbau, falls Zeit bleibt.

### Keine Sperre gegen gleichzeitige Anfragen (Race Condition)

Die Verfügbarkeitsprüfung liest die aktuelle Kapazität (offene Ausleihen + überlappende Reservierungen) und legt danach in einem separaten Schritt die neue Reservierung an, ohne Datenbank-seitige Sperre dazwischen. Zwei nahezu zeitgleiche Anfragen für die letzte freie Einheit eines Geräts könnten daher beide die Prüfung bestehen und das Gerät kurzzeitig überbuchen. Bei den zu erwartenden Nutzungszahlen (kleines Team, keine hochfrequenten parallelen Buchungen) ist das Risiko gering; für den Praxisumfang nicht behoben (würde `SELECT ... FOR UPDATE` oder eine DB-Constraint auf Belegungs-Ebene erfordern), aber bewusst dokumentiert statt stillschweigend in Kauf genommen.

## Teil 5 – Verwaltung und Auswertungen

### Ausmusterung: nullable Spalte statt eigener Tabelle

`geraete.ausgemustert_am` (Date, nullable) statt einer separaten Tabelle — konsistent mit der bereits etablierten Konvention „Status statt Enum/Extra-Tabelle" (s. `ausleihen.zurueckgegeben_am`, `reservierungen.storniert_am`). Kein Reaktivierungs-Endpoint, da von der Aufgabenstellung nicht gefordert; Ausmustern ist damit endgültig (nur per direktem DB-Eingriff rückgängig zu machen).

Ausgemusterte Geräte werden per Default aus `GET /api/geraete` ausgeblendet (Query-Param `inkl_ausgemustert=true` zeigt sie zusätzlich, genutzt von der Verwaltungsansicht); ihre Historie (`GET /api/geraete/{id}/ausleihen`) bleibt unverändert abrufbar. Neue Ausleihen und Reservierungen für ausgemusterte Geräte werden mit `409` abgelehnt — unabhängig von rechnerischer Verfügbarkeit. Bestehende offene Ausleihen/Reservierungen eines ausgemusterten Geräts bleiben unangetastet; Ausmustern erzwingt keine vorherige Rückgabe.

### Geräteverwaltung: `menge`-Reduktion gegen gebundene Kapazität geprüft

Beim Bearbeiten eines Geräts (`PUT /api/geraete/{id}`) wird eine Verringerung von `menge` gegen die aktuell gebundene Menge geprüft (offene Ausleihen + alle aktiven Reservierungen, unabhängig vom Zeitraum — dieselbe konservative Behandlung offener Ausleihen wie in Teil 4). Eine Reduktion unter diesen Wert wird mit `409` abgelehnt, um nicht denselben "negative Verfügbarkeit"-Zustand wie bei `IT-009` (s. Teil 2) neu zu erzeugen. `inventarnummer` ist nach Anlage nicht mehr änderbar (fachlicher Schlüssel, von Ausleihen/Reservierungen referenziert).

### Definition „Auslastung je Kategorie"

```
kapazitaet(kategorie) = SUM(menge) über nicht-ausgemusterte Geräte der Kategorie
gebunden(kategorie)   = offene Ausleihen (beliebiger Zeitpunkt, wie in Teil 2/4)
                       + aktive Reservierungen, deren [start_datum, end_datum] den heutigen Tag überlappen
                       — jeweils nur für nicht-ausgemusterte Geräte
quote = gebunden / kapazitaet
label: quote < 40%           -> "niedrig"
       40% <= quote <= 80%   -> "mittel"
       quote > 80%           -> "hoch"
       kapazitaet == 0       -> "n/a" (Division durch 0 vermieden; z. B. Kategorie, deren einzige Geräte ausgemustert sind)
```

Zwei bewusste Entscheidungen, dokumentiert nach Rückfrage im Gespräch:

1. **Reservierungen zählen nur, wenn ihr Zeitraum den heutigen Tag überlappt**, nicht alle aktiven Reservierungen unabhängig vom Datum. Eine Reservierung für einen Termin in mehreren Monaten soll die *aktuelle* Auslastung nicht künstlich hochtreiben — „Auslastung" ist als Momentaufnahme des gerade gebundenen Bestands definiert, nicht als Vorschau auf künftige Bindung.
2. **Grenzwerte 40 %/80 % sind auf der „mittel"-Seite geschlossen** (`>= 40 %` und `<= 80 %` zählen als „mittel"), da die Vorgabe an den exakten Grenzwerten selbst offen war.

Ausgemusterte Geräte fließen weder in `kapazitaet` noch in `gebunden` ein (gleiche Grundgesamtheit in Zähler und Nenner) — eine offene Ausleihe eines zwischenzeitlich ausgemusterten Geräts würde sonst eine Kategorie künstlich über 100 % Auslastung heben, ohne dass die verbleibenden (nicht ausgemusterten) Geräte tatsächlich stärker gebunden sind.

### Auswertungen: nur die drei in der Aufgabenstellung genannten Beispiele

`GET /api/stats/top-personen` (meiste aktuell offene Ausleihen), `GET /api/stats/top-geraete` (häufigste Ausleihen, alle Zeit) und `GET /api/stats/auslastung`. Keine zusätzlichen Kennzahlen gebaut — Zeitbudget, „kleine Ansicht" laut Aufgabenstellung. Die „wer hat die meisten Geräte"-Auswertung erbt die bekannte Einschränkung aus Teil 2 (`ausgeliehen_von` ist Freitext, keine Identitätsauflösung).

## Teil 6 – Zusammenfassung: Datenauffälligkeiten & Entscheidungen

Kurzfassung der oben ausführlich dokumentierten Punkte, als Grundlage für `TEIL6.md`.

### Datenqualität (Rohdaten)

1. **Doppelte Inventarnummer** (`IT-005`: iPhone *und* iPad) → erste Zeile kanonisch übernommen, zweite abgelehnt. Begründung: nicht rekonstruierbar, welches Gerät gemeint war — keine Fakten erfinden (z. B. neue Inventarnummer vergeben).
2. **Fehlende Pflichtfelder** (leere `bezeichnung`, `kategorie`) → mit Platzhalter/Fallback akzeptiert, nicht abgelehnt, aber als Caveat markiert. Begründung: Datensatz bleibt nutzbar, Unsicherheit bleibt sichtbar.
3. **Inkonsistente Datumsformate** (`DD.MM.YYYY` vs. ISO) → normalisiert, mit Caveat.
4. **Rückgabedatum vor Ausleihdatum** (`IT-006`) → komplett abgelehnt. Begründung: nicht entscheidbar, ob vertauscht oder falsch — lieber sichtbar ablehnen als stillschweigend raten.
5. **Zukünftiges Anschaffungsdatum** (`IT-032`), **Menge = 0** (`IT-023`) → akzeptiert mit Caveat, Wert unverändert übernommen.
6. **Negative Verfügbarkeit im Altsystem** (`IT-009`, Canon EOS R6: `menge=1`, aber 2 offene Ausleihen) → zeigt, dass das Altsystem Verfügbarkeit nie durchgesetzt hat. Aktuell dokumentiertes offenes TODO, nicht korrigiert.

### Geschäftsregel-Entscheidungen (Spezifikationslücken, nicht aus Daten)

- Verfügbarkeit = Stückzahl-Rechnung (`menge − offene Ausleihen`), nicht Ja/Nein.
- Reservierungen: offene Ausleihen blockieren jede künftige Reservierung, unabhängig von `faellig_am` — konservativ, weil Rückgabedatum vorab unbekannt ist.
- Berührende Reservierungsintervalle gelten als Überlappung (kein Uhrzeit-Tracking).
- `faellig_am` wird bei Anlage fixiert (nicht live neu berechnet) — Frist-Änderungen wirken nicht rückwirkend.
- Personen sind Freitext ohne Identitätsauflösung — Auswertungen (Teil 5) erben diese Einschränkung.
- Auslastung zählt nur Reservierungen, die den heutigen Tag überlappen; Grenzwerte 40 %/80 % auf „mittel"-Seite geschlossen.
- Keine DB-seitige Sperre gegen gleichzeitige Reservierungsanfragen (Race Condition) — bewusst dokumentiertes Restrisiko statt stillschweigend in Kauf genommen.

## Drei Fragen an die Büroleitung vor Go-Live

1. **Personenidentität:** Reicht ein Freitextfeld für „wer leiht aus", oder gibt es eine feste Mitarbeiterliste, gegen die validiert werden sollte? Ohne das werden Tippfehler und Namensvarianten nie zusammengeführt — das verzerrt auch Auswertungen wie „meistausleihende Person".
2. **Rollen/Rechte:** Sollen alle Mitarbeiter dieselben Rechte haben, oder braucht es eine Admin-Rolle für kritische Aktionen (Geräte ausmustern, Leihfristen ändern, Mengen reduzieren)? Aktuell gibt es keine Authentifizierung oder Rechtetrennung.
3. **Nutzerzahl/Gleichzeitigkeit:** Wie viele Personen nutzen das System etwa gleichzeitig, und wie oft kommt es vor, dass zwei Leute fast zeitgleich dasselbe knappe Gerät buchen wollen? Die aktuelle Verfügbarkeitsprüfung hat keine Datenbank-Sperre gegen echte Race Conditions — bei kleinem Team und seltenen parallelen Buchungen ist das Risiko gering, bei mehr Gleichzeitigkeit wäre das nachzurüsten.