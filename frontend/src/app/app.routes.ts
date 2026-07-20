import { Routes } from '@angular/router';

import { AuswertungenComponent } from './features/auswertungen/auswertungen.component';
import { GeraeteListeComponent } from './features/geraete-liste/geraete-liste.component';
import { GeraeteVerwaltungComponent } from './features/geraete-verwaltung/geraete-verwaltung.component';
import { HistorieComponent } from './features/historie/historie.component';
import { ImportReportComponent } from './features/import-report/import-report.component';
import { ReservierungenComponent } from './features/reservierungen/reservierungen.component';
import { UeberfaelligComponent } from './features/ueberfaellig/ueberfaellig.component';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'geraete' },
  { path: 'geraete', component: GeraeteListeComponent },
  { path: 'historie', component: HistorieComponent },
  { path: 'ueberfaellig', component: UeberfaelligComponent },
  { path: 'reservierungen', component: ReservierungenComponent },
  { path: 'import-report', component: ImportReportComponent },
  { path: 'verwaltung', component: GeraeteVerwaltungComponent },
  { path: 'auswertungen', component: AuswertungenComponent },
  { path: '**', redirectTo: 'geraete' },
];
