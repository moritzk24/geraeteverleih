import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE } from './api-base';
import { Auslastung, TopGeraet, TopPerson } from './stats.model';

@Injectable({
  providedIn: 'root',
})
export class StatsService {
  private readonly http = inject(HttpClient);

  topPersonen(): Observable<TopPerson[]> {
    return this.http.get<TopPerson[]>(`${API_BASE}/stats/top-personen`);
  }

  topGeraete(): Observable<TopGeraet[]> {
    return this.http.get<TopGeraet[]>(`${API_BASE}/stats/top-geraete`);
  }

  auslastung(): Observable<Auslastung[]> {
    return this.http.get<Auslastung[]>(`${API_BASE}/stats/auslastung`);
  }
}
