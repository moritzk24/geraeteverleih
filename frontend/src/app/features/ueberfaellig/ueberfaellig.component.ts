import { Component, inject, signal } from '@angular/core';

import { Ausleihe } from '../../core/ausleihe.model';
import { AusleihenService } from '../../core/ausleihen.service';

@Component({
  selector: 'app-ueberfaellig',
  imports: [],
  templateUrl: './ueberfaellig.component.html',
  styleUrl: './ueberfaellig.component.css',
})
export class UeberfaelligComponent {
  private readonly ausleihenService = inject(AusleihenService);

  readonly ausleihen = signal<Ausleihe[]>([]);

  constructor() {
    this.laden();
  }

  laden(): void {
    this.ausleihenService.list({ ueberfaellig: true }).subscribe((ausleihen) => this.ausleihen.set(ausleihen));
  }

  zurueckgeben(ausleihe: Ausleihe): void {
    this.ausleihenService.rueckgabe(ausleihe.id).subscribe(() => this.laden());
  }
}
