import { Component, inject, signal } from '@angular/core';

import { Auslastung, TopGeraet, TopPerson } from '../../core/stats.model';
import { StatsService } from '../../core/stats.service';

@Component({
  selector: 'app-auswertungen',
  imports: [],
  templateUrl: './auswertungen.component.html',
  styleUrl: './auswertungen.component.css',
})
export class AuswertungenComponent {
  private readonly statsService = inject(StatsService);

  readonly topPersonen = signal<TopPerson[]>([]);
  readonly topGeraete = signal<TopGeraet[]>([]);
  readonly auslastung = signal<Auslastung[]>([]);

  constructor() {
    this.statsService.topPersonen().subscribe((werte) => this.topPersonen.set(werte));
    this.statsService.topGeraete().subscribe((werte) => this.topGeraete.set(werte));
    this.statsService.auslastung().subscribe((werte) => this.auslastung.set(werte));
  }
}
