export type ReservierungStatus = 'aktiv' | 'storniert' | 'abgeholt';

export interface Reservierung {
  id: number;
  geraet_id: number;
  inventarnummer: string;
  bezeichnung: string;
  reserviert_von: string;
  start_datum: string;
  end_datum: string;
  status: ReservierungStatus;
  ausleihe_id: number | null;
}

export interface ReservierungCreate {
  geraet_id: number;
  reserviert_von: string;
  start_datum: string;
  end_datum: string;
}
