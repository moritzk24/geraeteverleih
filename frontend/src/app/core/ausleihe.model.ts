export interface Ausleihe {
  id: number;
  geraet_id: number;
  inventarnummer: string;
  bezeichnung: string;
  ausgeliehen_von: string;
  ausgeliehen_am: string;
  faellig_am: string;
  zurueckgegeben_am: string | null;
  ueberfaellig: boolean;
}

export interface AusleiheCreate {
  geraet_id: number;
  ausgeliehen_von: string;
}
