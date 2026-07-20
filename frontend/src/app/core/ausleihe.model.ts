export interface Ausleihe {
  id: number;
  geraet_id: number;
  inventarnummer: string;
  bezeichnung: string;
  ausgeliehen_von: string;
  ausgeliehen_am: string;
  zurueckgegeben_am: string | null;
}

export interface AusleiheCreate {
  geraet_id: number;
  ausgeliehen_von: string;
}
