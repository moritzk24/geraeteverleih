import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE } from './api-base';
import { Ausleihe } from './ausleihe.model';
import { Geraet, GeraetCreate, GeraetUpdate } from './geraet.model';

export interface GeraeteFilter {
  search?: string;
  kategorie?: string;
  nurVerfuegbare?: boolean;
  inklAusgemustert?: boolean;
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
    if (filter.inklAusgemustert) {
      params = params.set('inkl_ausgemustert', 'true');
    }
    return this.http.get<Geraet[]>(`${API_BASE}/geraete`, { params });
  }

  kategorien(): Observable<string[]> {
    return this.http.get<string[]>(`${API_BASE}/geraete/kategorien`);
  }

  historie(geraetId: number): Observable<Ausleihe[]> {
    return this.http.get<Ausleihe[]>(`${API_BASE}/geraete/${geraetId}/ausleihen`);
  }

  erstellen(payload: GeraetCreate): Observable<Geraet> {
    return this.http.post<Geraet>(`${API_BASE}/geraete`, payload);
  }

  aktualisieren(geraetId: number, payload: GeraetUpdate): Observable<Geraet> {
    return this.http.put<Geraet>(`${API_BASE}/geraete/${geraetId}`, payload);
  }

  ausmustern(geraetId: number): Observable<Geraet> {
    return this.http.post<Geraet>(`${API_BASE}/geraete/${geraetId}/ausmustern`, {});
  }
}
