import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { Geraet } from '../../core/geraet.model';
import { GeraeteService } from '../../core/geraete.service';
import { Reservierung, ReservierungStatus } from '../../core/reservierung.model';
import { ReservierungenService } from '../../core/reservierungen.service';

@Component({
  selector: 'app-reservierungen',
  imports: [FormsModule],
  templateUrl: './reservierungen.component.html',
  styleUrl: './reservierungen.component.css',
})
export class ReservierungenComponent {
  private readonly geraeteService = inject(GeraeteService);
  private readonly reservierungenService = inject(ReservierungenService);

  readonly geraete = signal<Geraet[]>([]);
  readonly reservierungen = signal<Reservierung[]>([]);
  readonly fehler = signal<string | null>(null);

  geraetId: number | null = null;
  person = '';
  status: ReservierungStatus | '' = 'aktiv';

  constructor() {
    this.geraeteService.list({}).subscribe((geraete) => this.geraete.set(geraete));
    this.suchen();
  }

  suchen(): void {
    this.reservierungenService
      .list({
        geraetId: this.geraetId ?? undefined,
        person: this.person || undefined,
        status: this.status || undefined,
      })
      .subscribe((reservierungen) => this.reservierungen.set(reservierungen));
  }

  stornieren(reservierung: Reservierung): void {
    this.fehler.set(null);
    this.reservierungenService.stornieren(reservierung.id).subscribe({
      next: () => this.suchen(),
      error: (err) => this.fehler.set(err?.error?.detail ?? 'Stornieren fehlgeschlagen'),
    });
  }

  abholen(reservierung: Reservierung): void {
    this.fehler.set(null);
    this.reservierungenService.abholen(reservierung.id).subscribe({
      next: () => this.suchen(),
      error: (err) => this.fehler.set(err?.error?.detail ?? 'Abholen fehlgeschlagen'),
    });
  }
}
