export interface Geraet {
  id: number;
  inventarnummer: string;
  bezeichnung: string;
  kategorie: string;
  menge: number;
  angeschafft_am: string | null;
  verfuegbare_menge: number;
  verfuegbar: boolean;
  ausgemustert: boolean;
  ausgemustert_am: string | null;
}

export interface GeraetCreate {
  inventarnummer: string;
  bezeichnung: string;
  kategorie: string;
  menge: number;
  angeschafft_am?: string | null;
}

export interface GeraetUpdate {
  bezeichnung: string;
  kategorie: string;
  menge: number;
  angeschafft_am?: string | null;
}
