import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE } from './api-base';
import { Ausleihe } from './ausleihe.model';
import { Geraet } from './geraet.model';

export interface GeraeteFilter {
  search?: string;
  kategorie?: string;
  nurVerfuegbare?: boolean;
}

@Injectable({
  providedIn: 'root',
})
export class GeraeteService {
  private readonly http = inject(HttpClient);

  list(filter: GeraeteFilter): Observable<Geraet[]> {
    let params = new HttpParams();
    if (filter.search) {
      params = params.set('search', filter.search);
    }
    if (filter.kategorie) {
      params = params.set('kategorie', filter.kategorie);
    }
    if (filter.nurVerfuegbare) {
      params = params.set('nur_verfuegbare', 'true');
    }
    return this.http.get<Geraet[]>(`${API_BASE}/geraete`, { params });
  }

  kategorien(): Observable<string[]> {
    return this.http.get<string[]>(`${API_BASE}/geraete/kategorien`);
  }

  historie(geraetId: number): Observable<Ausleihe[]> {
    return this.http.get<Ausleihe[]>(`${API_BASE}/geraete/${geraetId}/ausleihen`);
  }
}
