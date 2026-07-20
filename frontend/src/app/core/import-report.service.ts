import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE } from './api-base';
import { ImportReportEntry, ImportReportSummaryRow } from './import-report.model';

export interface ImportReportFilter {
  sourceTable?: string;
  decision?: string;
  inventarnummer?: string;
}

@Injectable({
  providedIn: 'root',
})
export class ImportReportService {
  private readonly http = inject(HttpClient);

  list(filter: ImportReportFilter): Observable<ImportReportEntry[]> {
    let params = new HttpParams();
    if (filter.sourceTable) {
      params = params.set('source_table', filter.sourceTable);
    }
    if (filter.decision) {
      params = params.set('decision', filter.decision);
    }
    if (filter.inventarnummer) {
      params = params.set('inventarnummer', filter.inventarnummer);
    }
    return this.http.get<ImportReportEntry[]>(`${API_BASE}/import-report`, { params });
  }

  summary(): Observable<ImportReportSummaryRow[]> {
    return this.http.get<ImportReportSummaryRow[]>(`${API_BASE}/import-report/summary`);
  }
}
