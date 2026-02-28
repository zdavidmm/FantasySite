const React = require('react');
const { render, screen, waitFor, fireEvent } = require('@testing-library/react');
require('@testing-library/jest-dom');
const { App } = require('../app');

describe('App component', () => {
  const mockData = {
    assignments: {
      'Zoe': 'SEA',
      'Adam': 'ATL',
      'Mia': 'CIN',
    },
    scoreboard: {
      'SEA': {
        '0': { date: '2025-04-02', game_pk: 10 },
      },
      'ATL': {
        '0': { date: '2025-04-02', game_pk: 11 },
        '1': { date: '2025-04-04', game_pk: 12 },
      },
      'CIN': {},
    },
  };

  beforeEach(() => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve(mockData),
      })
    );
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  test('renders and sorts by default progress desc then participant asc', async () => {
    render(React.createElement(App));

    await waitFor(() => {
      expect(screen.getByText('Fantasy Runs Challenge')).toBeInTheDocument();
      expect(screen.getByText('Adam')).toBeInTheDocument();
    });

    const nameCells = screen.getAllByRole('cell').filter((cell) =>
      ['Adam', 'Mia', 'Zoe'].includes(cell.textContent.trim())
    );

    expect(nameCells.map((cell) => cell.textContent.trim())).toEqual(['Adam', 'Zoe', 'Mia']);
  });

  test('filters by participant search and can show only missing totals', async () => {
    const fullTotals = {};
    for (let i = 0; i <= 13; i += 1) {
      fullTotals[String(i)] = { date: '2025-04-10', game_pk: 900 + i };
    }
    global.fetch.mockImplementationOnce(() =>
      Promise.resolve({
        json: () =>
          Promise.resolve({
            assignments: mockData.assignments,
            scoreboard: {
              ...mockData.scoreboard,
              ATL: fullTotals,
            },
          }),
      })
    );

    render(React.createElement(App));

    await waitFor(() => {
      expect(screen.getByText('Fantasy Runs Challenge')).toBeInTheDocument();
      expect(screen.getByText('Adam')).toBeInTheDocument();
    });

    fireEvent.change(screen.getByLabelText('Search Participant'), {
      target: { value: 'zo' },
    });

    expect(screen.getByText('Zoe')).toBeInTheDocument();
    expect(screen.queryByText('Adam')).not.toBeInTheDocument();
    expect(screen.queryByText('Mia')).not.toBeInTheDocument();

    fireEvent.change(screen.getByLabelText('Search Participant'), {
      target: { value: '' },
    });
    fireEvent.click(screen.getByLabelText('Only Missing Totals'));

    expect(screen.getByText('Zoe')).toBeInTheDocument();
    expect(screen.getByText('Mia')).toBeInTheDocument();
    expect(screen.queryByText('Adam')).not.toBeInTheDocument();
  });

  test('changes ordering when sort control is set to name descending', async () => {
    render(React.createElement(App));

    await waitFor(() => {
      expect(screen.getByText('Fantasy Runs Challenge')).toBeInTheDocument();
    });

    fireEvent.change(screen.getByLabelText('Sort By'), {
      target: { value: 'name-desc' },
    });

    const nameCells = screen.getAllByRole('cell').filter((cell) =>
      ['Adam', 'Mia', 'Zoe'].includes(cell.textContent.trim())
    );

    expect(nameCells.map((cell) => cell.textContent.trim())).toEqual(['Zoe', 'Mia', 'Adam']);
  });

  test('renders achieved run-total metadata and game links', async () => {
    render(React.createElement(App));

    await waitFor(() => {
      expect(screen.getByText('Fantasy Runs Challenge')).toBeInTheDocument();
    });

    expect(
      screen.getByLabelText('Run total 1 achieved on 2025-04-04 (game id: 12)')
    ).toBeInTheDocument();
    expect(
      screen.getByRole('link', { name: '1' })
    ).toHaveAttribute('href', 'https://www.mlb.com/gameday/12');
    expect(
      screen.getAllByLabelText('Run total 13 not achieved yet').length
    ).toBeGreaterThan(0);
  });
});
