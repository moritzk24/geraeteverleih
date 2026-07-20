import { JsonPipe } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { ImportReportEntry, ImportReportSummaryRow } from '../../core/import-report.model';
import { ImportReportService } from '../../core/import-report.service';

@Component({
  selector: 'app-import-report',
  imports: [FormsModule, JsonPipe],
  templateUrl: './import-report.component.html',
  styleUrl: './import-report.component.css',
})
export class ImportReportComponent {
  private readonly reportService = inject(ImportReportService);

  readonly summary = signal<ImportReportSummaryRow[]>([]);
  readonly entries = signal<ImportReportEntry[]>([]);
  readonly aufgeklappt = signal<number | null>(null);

  sourceTable = '';
  decision = '';
  inventarnummer = '';

  constructor() {
    this.reportService.summary().subscribe((summary) => this.summary.set(summary));
    this.suchen();
  }

  suchen(): void {
    this.reportService
      .list({
        sourceTable: this.sourceTable || undefined,
        decision: this.decision || undefined,
        inventarnummer: this.inventarnummer || undefined,
      })
      .subscribe((entries) => this.entries.set(entries));
  }

  toggleRohdaten(entry: ImportReportEntry): void {
    this.aufgeklappt.set(this.aufgeklappt() === entry.id ? null : entry.id);
  }
}
