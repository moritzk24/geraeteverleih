import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { AusleihenService } from '../../core/ausleihen.service';
import { Geraet } from '../../core/geraet.model';
import { GeraeteService } from '../../core/geraete.service';

@Component({
  selector: 'app-geraete-liste',
  imports: [FormsModule],
  templateUrl: './geraete-liste.component.html',
  styleUrl: './geraete-liste.component.css',
})
export class GeraeteListeComponent {
  private readonly geraeteService = inject(GeraeteService);
  private readonly ausleihenService = inject(AusleihenService);

  readonly geraete = signal<Geraet[]>([]);
  readonly kategorien = signal<string[]>([]);

  search = '';
  kategorie = '';
  nurVerfuegbare = false;

  readonly ausleiheGeraet = signal<Geraet | null>(null);
  ausgeliehenVon = '';
  readonly fehler = signal<string | null>(null);

  constructor() {
    this.geraeteService.kategorien().subscribe((kategorien) => this.kategorien.set(kategorien));
    this.ladeGeraete();
  }

  ladeGeraete(): void {
    this.geraeteService
      .list({ search: this.search, kategorie: this.kategorie, nurVerfuegbare: this.nurVerfuegbare })
      .subscribe((geraete) => this.geraete.set(geraete));
  }

  ausleiheStarten(geraet: Geraet): void {
    this.ausleiheGeraet.set(geraet);
    this.ausgeliehenVon = '';
    this.fehler.set(null);
  }

  ausleiheAbbrechen(): void {
    this.ausleiheGeraet.set(null);
    this.fehler.set(null);
  }

  ausleiheBestaetigen(): void {
    const geraet = this.ausleiheGeraet();
    if (!geraet || !this.ausgeliehenVon.trim()) {
      return;
    }
    this.ausleihenService.ausleihen({ geraet_id: geraet.id, ausgeliehen_von: this.ausgeliehenVon }).subscribe({
      next: () => {
        this.ausleiheGeraet.set(null);
        this.ladeGeraete();
      },
      error: (err) => {
        this.fehler.set(err?.error?.detail ?? 'Ausleihe fehlgeschlagen');
      },
    });
  }
}
