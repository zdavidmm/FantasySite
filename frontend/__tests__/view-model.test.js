const {
  RUN_TOTALS,
  buildRows,
  sortRows,
  filterRows,
  deriveVisibleRows,
  getLatestAchievedDate,
  formatDateDisplay,
} = require('../view-model');

describe('view-model', () => {
  const assignments = {
    'Casey': 'NYM',
    'Alex': 'LAD',
    'Blake': 'BOS',
  };

  const scoreboard = {
    'NYM': {
      '0': { date: '2025-04-01', game_pk: 123 },
      '1': { date: '2025-04-03', game_pk: 124 },
    },
    'LAD': {
      '0': { date: '2025-04-02', game_pk: 222 },
      '1': { date: '2025-04-06', game_pk: 223 },
      '2': { date: '2025-04-04', game_pk: 224 },
    },
    'BOS': {},
  };

  test('buildRows computes progress metadata', () => {
    const rows = buildRows(assignments, scoreboard);
    const lad = rows.find((row) => row.participant === 'Alex');
    expect(lad.progressCount).toBe(3);
    expect(lad.hasMissingTotals).toBe(true);
    expect(lad.completionRatio).toBeCloseTo(3 / RUN_TOTALS.length);
  });

  test('default sort is progress desc then participant asc', () => {
    const rows = buildRows(assignments, scoreboard);
    const sorted = sortRows(rows, 'progress-desc');
    expect(sorted.map((row) => row.participant)).toEqual(['Alex', 'Casey', 'Blake']);
  });

  test('filterRows applies search and missing-only flag', () => {
    const rows = buildRows(assignments, scoreboard);
    const filtered = filterRows(rows, { searchTerm: 'as', showOnlyMissing: true });
    expect(filtered.map((row) => row.participant)).toEqual(['Casey']);
  });

  test('deriveVisibleRows applies filter then sort', () => {
    const rows = deriveVisibleRows(assignments, scoreboard, {
      searchTerm: 'a',
      sortKey: 'name-asc',
      showOnlyMissing: false,
    });
    expect(rows.map((row) => row.participant)).toEqual(['Alex', 'Blake', 'Casey']);
  });

  test('latest achieved date is extracted correctly', () => {
    expect(getLatestAchievedDate(scoreboard)).toBe('2025-04-06');
  });

  test('formatDateDisplay handles known ISO dates', () => {
    const label = formatDateDisplay('2025-04-01');
    expect(label).toMatch(/2025/);
    expect(label).toMatch(/Apr|April/);
  });
});
