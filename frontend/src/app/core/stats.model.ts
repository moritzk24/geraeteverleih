export interface TopPerson {
  person: string;
  anzahl_offene_ausleihen: number;
}

export interface TopGeraet {
  geraet_id: number;
  inventarnummer: string;
  bezeichnung: string;
  anzahl_ausleihen: number;
}

export type AuslastungLabel = 'niedrig' | 'mittel' | 'hoch' | 'n/a';

export interface Auslastung {
  kategorie: string;
  kapazitaet: number;
  gebunden: number;
  quote: number | null;
  label: AuslastungLabel;
}
