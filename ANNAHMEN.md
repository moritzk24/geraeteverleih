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
