import { Routes } from '@angular/router';

import { GeraeteListeComponent } from './features/geraete-liste/geraete-liste.component';
import { HistorieComponent } from './features/historie/historie.component';
import { ImportReportComponent } from './features/import-report/import-report.component';
import { UeberfaelligComponent } from './features/ueberfaellig/ueberfaellig.component';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'geraete' },
  { path: 'geraete', component: GeraeteListeComponent },
  { path: 'historie', component: HistorieComponent },
  { path: 'ueberfaellig', component: UeberfaelligComponent },
  { path: 'import-report', component: ImportReportComponent },
  { path: '**', redirectTo: 'geraete' },
];
