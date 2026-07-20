import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { Ausleihe } from '../../core/ausleihe.model';
import { AusleihenService } from '../../core/ausleihen.service';
import { Geraet } from '../../core/geraet.model';
import { GeraeteService } from '../../core/geraete.service';

@Component({
  selector: 'app-historie',
  imports: [FormsModule],
  templateUrl: './historie.component.html',
  styleUrl: './historie.component.css',
})
export class HistorieComponent {
  private readonly geraeteService = inject(GeraeteService);
  private readonly ausleihenService = inject(AusleihenService);

  readonly geraete = signal<Geraet[]>([]);
  readonly ausleihen = signal<Ausleihe[]>([]);

  geraetId: number | null = null;
  person = '';
  nurOffene = false;

  constructor() {
    this.geraeteService.list({}).subscribe((geraete) => this.geraete.set(geraete));
    this.suchen();
  }

  suchen(): void {
    this.ausleihenService
      .list({
        geraetId: this.geraetId ?? undefined,
        person: this.person || undefined,
        offen: this.nurOffene ? true : undefined,
      })
      .subscribe((ausleihen) => this.ausleihen.set(ausleihen));
  }

  zurueckgeben(ausleihe: Ausleihe): void {
    this.ausleihenService.rueckgabe(ausleihe.id).subscribe(() => this.suchen());
  }
}
