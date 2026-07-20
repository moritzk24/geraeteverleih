import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE } from './api-base';
import { Ausleihe, AusleiheCreate } from './ausleihe.model';

export interface AusleihenFilter {
  person?: string;
  geraetId?: number;
  offen?: boolean;
}

@Injectable({
  providedIn: 'root',
})
export class AusleihenService {
  private readonly http = inject(HttpClient);

  list(filter: AusleihenFilter): Observable<Ausleihe[]> {
    let params = new HttpParams();
    if (filter.person) {
      params = params.set('person', filter.person);
    }
    if (filter.geraetId != null) {
      params = params.set('geraet_id', filter.geraetId);
    }
    if (filter.offen != null) {
      params = params.set('offen', String(filter.offen));
    }
    return this.http.get<Ausleihe[]>(`${API_BASE}/ausleihen`, { params });
  }

  ausleihen(payload: AusleiheCreate): Observable<Ausleihe> {
    return this.http.post<Ausleihe>(`${API_BASE}/ausleihen`, payload);
  }

  rueckgabe(ausleiheId: number): Observable<Ausleihe> {
    return this.http.post<Ausleihe>(`${API_BASE}/ausleihen/${ausleiheId}/rueckgabe`, {});
  }
}
