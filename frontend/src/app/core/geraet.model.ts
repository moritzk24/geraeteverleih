export interface Geraet {
  id: number;
  inventarnummer: string;
  bezeichnung: string;
  kategorie: string;
  menge: number;
  angeschafft_am: string | null;
  verfuegbare_menge: number;
  verfuegbar: boolean;
}
