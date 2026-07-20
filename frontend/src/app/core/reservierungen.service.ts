import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE } from './api-base';
import { Ausleihe } from './ausleihe.model';
import { Reservierung, ReservierungCreate, ReservierungStatus } from './reservierung.model';

export interface ReservierungenFilter {
  person?: string;
  geraetId?: number;
  status?: ReservierungStatus;
}

@Injectable({
  providedIn: 'root',
})
export class ReservierungenService {
  private readonly http = inject(HttpClient);

  list(filter: ReservierungenFilter): Observable<Reservierung[]> {
    let params = new HttpParams();
    if (filter.person) {
      params = params.set('person', filter.person);
    }
    if (filter.geraetId != null) {
      params = params.set('geraet_id', filter.geraetId);
    }
    if (filter.status) {
      params = params.set('status', filter.status);
    }
    return this.http.get<Reservierung[]>(`${API_BASE}/reservierungen`, { params });
  }

  reservieren(payload: ReservierungCreate): Observable<Reservierung> {
    return this.http.post<Reservierung>(`${API_BASE}/reservierungen`, payload);
  }

  stornieren(reservierungId: number): Observable<Reservierung> {
    return this.http.post<Reservierung>(`${API_BASE}/reservierungen/${reservierungId}/stornieren`, {});
  }

  abholen(reservierungId: number): Observable<Ausleihe> {
    return this.http.post<Ausleihe>(`${API_BASE}/reservierungen/${reservierungId}/abholen`, {});
  }
}
