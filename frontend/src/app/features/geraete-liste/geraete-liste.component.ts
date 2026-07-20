import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { AusleihenService } from '../../core/ausleihen.service';
import { Geraet } from '../../core/geraet.model';
import { GeraeteService } from '../../core/geraete.service';
import { Reservierung } from '../../core/reservierung.model';
import { ReservierungenService } from '../../core/reservierungen.service';

function heuteIso(): string {
  return new Date().toISOString().slice(0, 10);
}

@Component({
  selector: 'app-geraete-liste',
  imports: [FormsModule],
  templateUrl: './geraete-liste.component.html',
  styleUrl: './geraete-liste.component.css',
})
export class GeraeteListeComponent {
  private readonly geraeteService = inject(GeraeteService);
  private readonly ausleihenService = inject(AusleihenService);
  private readonly reservierungenService = inject(ReservierungenService);

  readonly geraete = signal<Geraet[]>([]);
  readonly kategorien = signal<string[]>([]);

  search = '';
  kategorie = '';
  nurVerfuegbare = false;

  readonly ausleiheGeraet = signal<Geraet | null>(null);
  ausgeliehenVon = '';
  readonly fehler = signal<string | null>(null);
  readonly erfolgFaelligAm = signal<string | null>(null);

  readonly reservierungGeraet = signal<Geraet | null>(null);
  reservierenVon = '';
  reservierenStart = heuteIso();
  reservierenEnde = heuteIso();
  readonly reservierungFehler = signal<string | null>(null);
  readonly reservierungErfolg = signal<Reservierung | null>(null);

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
    this.erfolgFaelligAm.set(null);
  }

  ausleiheAbbrechen(): void {
    this.ausleiheGeraet.set(null);
    this.fehler.set(null);
    this.erfolgFaelligAm.set(null);
    this.ladeGeraete();
  }

  ausleiheBestaetigen(): void {
    const geraet = this.ausleiheGeraet();
    if (!geraet || !this.ausgeliehenVon.trim()) {
      return;
    }
    this.ausleihenService.ausleihen({ geraet_id: geraet.id, ausgeliehen_von: this.ausgeliehenVon }).subscribe({
      next: (ausleihe) => {
        this.fehler.set(null);
        this.erfolgFaelligAm.set(ausleihe.faellig_am);
      },
      error: (err) => {
        this.fehler.set(err?.error?.detail ?? 'Ausleihe fehlgeschlagen');
      },
    });
  }

  reservierenStarten(geraet: Geraet): void {
    this.reservierungGeraet.set(geraet);
    this.reservierenVon = '';
    this.reservierenStart = heuteIso();
    this.reservierenEnde = heuteIso();
    this.reservierungFehler.set(null);
    this.reservierungErfolg.set(null);
  }

  reservierenAbbrechen(): void {
    this.reservierungGeraet.set(null);
    this.reservierungFehler.set(null);
    this.reservierungErfolg.set(null);
    this.ladeGeraete();
  }

  reservierenBestaetigen(): void {
    const geraet = this.reservierungGeraet();
    if (!geraet || !this.reservierenVon.trim()) {
      return;
    }
    this.reservierungenService
      .reservieren({
        geraet_id: geraet.id,
        reserviert_von: this.reservierenVon,
        start_datum: this.reservierenStart,
        end_datum: this.reservierenEnde,
      })
      .subscribe({
        next: (reservierung) => {
          this.reservierungFehler.set(null);
          this.reservierungErfolg.set(reservierung);
        },
        error: (err) => {
          this.reservierungFehler.set(err?.error?.detail ?? 'Reservierung fehlgeschlagen');
        },
      });
  }
}
