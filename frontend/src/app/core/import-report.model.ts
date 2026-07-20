export interface ImportReportEntry {
  id: number;
  run_at: string;
  source_table: string;
  row_identifier: string;
  raw_data: Record<string, unknown>;
  decision: string;
  reason: string;
}

export interface ImportReportSummaryRow {
  source_table: string;
  decision: string;
  count: number;
}
