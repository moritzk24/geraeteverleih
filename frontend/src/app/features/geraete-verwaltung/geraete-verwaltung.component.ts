import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { Geraet, GeraetCreate, GeraetUpdate } from '../../core/geraet.model';
import { GeraeteService } from '../../core/geraete.service';
import { extractErrorMessage } from '../../core/http-error';

interface GeraetFormState {
  inventarnummer: string;
  bezeichnung: string;
  kategorie: string;
  menge: number;
  angeschafft_am: string;
}

function leeresFormular(): GeraetFormState {
  return { inventarnummer: '', bezeichnung: '', kategorie: '', menge: 1, angeschafft_am: '' };
}

@Component({
  selector: 'app-geraete-verwaltung',
  imports: [FormsModule],
  templateUrl: './geraete-verwaltung.component.html',
  styleUrl: './geraete-verwaltung.component.css',
})
export class GeraeteVerwaltungComponent {
  private readonly geraeteService = inject(GeraeteService);

  readonly geraete = signal<Geraet[]>([]);

  readonly anlegenOffen = signal(false);
  form = leeresFormular();
  readonly anlegenFehler = signal<string | null>(null);

  readonly bearbeitenGeraet = signal<Geraet | null>(null);
  bearbeitenForm = leeresFormular();
  readonly bearbeitenFehler = signal<string | null>(null);

  readonly ausmusternFehler = signal<string | null>(null);

  constructor() {
    this.laden();
  }

  laden(): void {
    this.geraeteService.list({ inklAusgemustert: true }).subscribe((geraete) => this.geraete.set(geraete));
  }

  anlegenStarten(): void {
    this.form = leeresFormular();
    this.anlegenFehler.set(null);
    this.anlegenOffen.set(true);
  }

  anlegenAbbrechen(): void {
    this.anlegenOffen.set(false);
  }

  anlegenBestaetigen(): void {
    const payload: GeraetCreate = {
      inventarnummer: this.form.inventarnummer,
      bezeichnung: this.form.bezeichnung,
      kategorie: this.form.kategorie,
      menge: this.form.menge,
      angeschafft_am: this.form.angeschafft_am || null,
    };
    this.geraeteService.erstellen(payload).subscribe({
      next: () => {
        this.anlegenOffen.set(false);
        this.laden();
      },
      error: (err) => this.anlegenFehler.set(extractErrorMessage(err, 'Anlegen fehlgeschlagen')),
    });
  }

  bearbeitenStarten(geraet: Geraet): void {
    this.bearbeitenGeraet.set(geraet);
    this.bearbeitenForm = {
      inventarnummer: geraet.inventarnummer,
      bezeichnung: geraet.bezeichnung,
      kategorie: geraet.kategorie,
      menge: geraet.menge,
      angeschafft_am: geraet.angeschafft_am ?? '',
    };
    this.bearbeitenFehler.set(null);
  }

  bearbeitenAbbrechen(): void {
    this.bearbeitenGeraet.set(null);
  }

  bearbeitenBestaetigen(): void {
    const geraet = this.bearbeitenGeraet();
    if (!geraet) {
      return;
    }
    const payload: GeraetUpdate = {
      bezeichnung: this.bearbeitenForm.bezeichnung,
      kategorie: this.bearbeitenForm.kategorie,
      menge: this.bearbeitenForm.menge,
      angeschafft_am: this.bearbeitenForm.angeschafft_am || null,
    };
    this.geraeteService.aktualisieren(geraet.id, payload).subscribe({
      next: () => {
        this.bearbeitenGeraet.set(null);
        this.laden();
      },
      error: (err) => this.bearbeitenFehler.set(extractErrorMessage(err, 'Aktualisieren fehlgeschlagen')),
    });
  }

  ausmustern(geraet: Geraet): void {
    this.ausmusternFehler.set(null);
    this.geraeteService.ausmustern(geraet.id).subscribe({
      next: () => this.laden(),
      error: (err) => this.ausmusternFehler.set(extractErrorMessage(err, 'Ausmustern fehlgeschlagen')),
    });
  }
}
