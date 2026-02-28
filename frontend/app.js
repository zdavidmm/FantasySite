(function(root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory(require('./view-model'));
    return;
  }
  root.FantasyApp = factory(root.FantasyViewModel);
})(typeof self !== 'undefined' ? self : this, function(viewModel) {
  var ReactRef = (typeof window !== 'undefined' && window.React) ? window.React : require('react');
  var e = ReactRef.createElement;

  var RUN_TOTALS = viewModel.RUN_TOTALS;

  function CheckIcon() {
    return e(
      'svg',
      {
        className: 'h-3.5 w-3.5 text-accent-300',
        viewBox: '0 0 24 24',
        fill: 'none',
        stroke: 'currentColor',
        strokeWidth: '2',
        strokeLinecap: 'round',
        strokeLinejoin: 'round',
        'aria-hidden': 'true'
      },
      e('path', { d: 'M20 6 9 17l-5-5' })
    );
  }

  function metricLabel(count) {
    return count + '/' + RUN_TOTALS.length;
  }

  function cellTooltip(runTotal, info) {
    if (!info) {
      return 'Run total ' + runTotal + ' not achieved yet';
    }

    var base = 'Run total ' + runTotal + ' achieved on ' + (info.date || 'unknown date');
    if (info.game_pk) {
      return base + ' (game id: ' + info.game_pk + ')';
    }
    return base;
  }

  function gameLink(info) {
    if (!info || !info.game_pk) {
      return null;
    }
    return 'https://www.mlb.com/gameday/' + info.game_pk;
  }

  function TotalCell(props) {
    var runTotal = props.runTotal;
    var info = props.info;
    var achieved = !!info;
    var link = gameLink(info);

    return e(
      'td',
      {
        className: 'px-2 py-2 text-center border-b border-white/5',
        title: cellTooltip(runTotal, info),
        'aria-label': cellTooltip(runTotal, info)
      },
      achieved
        ? e(
            'div',
            { className: 'inline-flex items-center justify-center rounded-full border border-accent-400/40 bg-accent-500/10 px-1.5 py-1' },
            link
              ? e(
                  'a',
                  {
                    href: link,
                    target: '_blank',
                    rel: 'noopener noreferrer',
                    className: 'inline-flex items-center gap-1 text-xs font-semibold text-accent-300 hover:text-accent-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-300/70 rounded-sm'
                  },
                  e(CheckIcon),
                  e('span', null, runTotal)
                )
              : e(
                  'span',
                  { className: 'inline-flex items-center gap-1 text-xs font-semibold text-accent-300' },
                  e(CheckIcon),
                  e('span', null, runTotal)
                )
          )
        : e('span', { className: 'inline-flex h-6 w-6 items-center justify-center rounded-full border border-slate-600/50 text-[11px] text-slate-500' }, runTotal)
    );
  }

  function ProgressCell(props) {
    var row = props.row;
    var barWidth = Math.round(row.completionRatio * 100) + '%';

    return e(
      'td',
      { className: 'px-3 py-2 border-b border-white/5 min-w-32' },
      e('div', { className: 'text-sm font-bold text-slate-100' }, metricLabel(row.progressCount)),
      e(
        'div',
        { className: 'mt-1 h-1.5 w-full rounded-full bg-slate-700/80 overflow-hidden', role: 'img', 'aria-label': 'Progress bar ' + metricLabel(row.progressCount) },
        e('div', { className: 'h-full bg-gradient-to-r from-accent-500 to-accent-300 transition-all duration-300', style: { width: barWidth } })
      )
    );
  }

  function Row(props) {
    var row = props.row;

    return e(
      'tr',
      { className: 'even:bg-surface-900/60 hover:bg-surface-700/55 transition-colors duration-150' },
      e(
        'td',
        { className: 'px-3 py-2 border-b border-white/5 min-w-44' },
        e('div', { className: 'text-sm font-semibold text-slate-100' }, row.participant)
      ),
      e(
        'td',
        { className: 'px-3 py-2 border-b border-white/5 min-w-24' },
        e('span', { className: 'inline-flex items-center rounded-full border border-slate-500/60 bg-slate-700/55 px-2 py-1 text-xs font-bold uppercase tracking-wide text-slate-200' }, row.team)
      ),
      e(ProgressCell, { row: row }),
      RUN_TOTALS.map(function(total) {
        return e(TotalCell, { key: total, runTotal: total, info: row.achieved[total] });
      })
    );
  }

  function EmptyState() {
    return e(
      'div',
      { className: 'rounded-2xl border border-dashed border-slate-700 bg-surface-900/40 px-4 py-8 text-center text-sm text-slate-400' },
      'No participants match the current filters.'
    );
  }

  function Controls(props) {
    return e(
      'section',
      { className: 'mb-4 grid grid-cols-1 gap-3 md:grid-cols-[1fr_auto_auto]' },
      e(
        'div',
        null,
        e('label', { className: 'mb-1 block text-xs font-bold uppercase tracking-[0.08em] text-slate-400', htmlFor: 'participant-search' }, 'Search Participant'),
        e('input', {
          id: 'participant-search',
          type: 'search',
          value: props.searchTerm,
          onChange: props.onSearchChange,
          placeholder: 'Type a participant name...',
          className: 'w-full rounded-xl border border-slate-700 bg-surface-900 px-3 py-2 text-sm text-slate-100 outline-none ring-accent-300/70 transition focus:ring-2'
        })
      ),
      e(
        'div',
        null,
        e('label', { className: 'mb-1 block text-xs font-bold uppercase tracking-[0.08em] text-slate-400', htmlFor: 'sort-select' }, 'Sort By'),
        e(
          'select',
          {
            id: 'sort-select',
            value: props.sortKey,
            onChange: props.onSortChange,
            className: 'w-full rounded-xl border border-slate-700 bg-surface-900 px-3 py-2 text-sm text-slate-100 outline-none ring-accent-300/70 transition focus:ring-2'
          },
          e('option', { value: 'progress-desc' }, 'Progress (High to Low)'),
          e('option', { value: 'progress-asc' }, 'Progress (Low to High)'),
          e('option', { value: 'name-asc' }, 'Name (A-Z)'),
          e('option', { value: 'name-desc' }, 'Name (Z-A)'),
          e('option', { value: 'team-asc' }, 'Team (A-Z)')
        )
      ),
      e(
        'label',
        { className: 'inline-flex items-center gap-2 self-end rounded-xl border border-slate-700 bg-surface-900 px-3 py-2 text-sm text-slate-200 cursor-pointer' },
        e('input', {
          type: 'checkbox',
          checked: props.showOnlyMissing,
          onChange: props.onMissingToggle,
          className: 'h-4 w-4 rounded border-slate-500 bg-surface-900 text-accent-400 focus:ring-accent-300/70'
        }),
        e('span', null, 'Only Missing Totals')
      )
    );
  }

  function LastUpdated(props) {
    return e(
      'p',
      { className: 'text-xs text-slate-400' },
      'Last updated: ',
      e('span', { className: 'font-semibold text-slate-200' }, props.lastUpdatedLabel),
      '. Data includes games through this date. Auto-refresh runs daily at 6:00 AM UTC.'
    );
  }

  function FantasyRunsTable(props) {
    var rows = props.rows;

    if (!rows.length) {
      return e(EmptyState);
    }

    return e(
      'div',
      { className: 'data-table-scroll overflow-x-auto rounded-2xl border border-white/10 bg-surface-900/70 shadow-glow' },
      e(
        'table',
        { className: 'w-full min-w-[980px] border-collapse text-left' },
        e(
          'thead',
          null,
          e(
            'tr',
            { className: 'sticky top-0 z-10 bg-surface-800/95 backdrop-blur' },
            e('th', { className: 'px-3 py-3 text-xs font-bold uppercase tracking-[0.12em] text-slate-300' }, 'Participant'),
            e('th', { className: 'px-3 py-3 text-xs font-bold uppercase tracking-[0.12em] text-slate-300' }, 'Team'),
            e('th', { className: 'px-3 py-3 text-xs font-bold uppercase tracking-[0.12em] text-slate-300' }, 'Progress'),
            RUN_TOTALS.map(function(total) {
              return e('th', { key: total, className: 'px-2 py-3 text-center text-xs font-bold uppercase tracking-[0.12em] text-slate-400' }, total);
            })
          )
        ),
        e(
          'tbody',
          null,
          rows.map(function(row) {
            return e(Row, { key: row.participant, row: row });
          })
        )
      )
    );
  }

  function App() {
    var useState = ReactRef.useState;
    var useMemo = ReactRef.useMemo;
    var useEffect = ReactRef.useEffect;

    var _useState = useState(null);
    var data = _useState[0];
    var setData = _useState[1];

    var _useState2 = useState('');
    var searchTerm = _useState2[0];
    var setSearchTerm = _useState2[1];

    var _useState3 = useState('progress-desc');
    var sortKey = _useState3[0];
    var setSortKey = _useState3[1];

    var _useState4 = useState(false);
    var showOnlyMissing = _useState4[0];
    var setShowOnlyMissing = _useState4[1];

    function parseJsonResponse(response) {
      if (response.ok === false) {
        throw new Error('Request failed with status ' + response.status);
      }
      return response.json();
    }

    function fetchData() {
      return fetch('/api/data')
        .then(parseJsonResponse)
        .catch(function() {
          return Promise.all([
            fetch('participants.json').then(parseJsonResponse),
            fetch('scoreboard.json').then(parseJsonResponse)
          ]).then(function(results) {
            return {
              assignments: results[0],
              scoreboard: results[1]
            };
          });
        });
    }

    useEffect(function() {
      fetchData()
        .then(setData);
    }, []);

    var rows = useMemo(function() {
      if (!data) {
        return [];
      }
      return viewModel.deriveVisibleRows(data.assignments, data.scoreboard, {
        searchTerm: searchTerm,
        sortKey: sortKey,
        showOnlyMissing: showOnlyMissing
      });
    }, [data, searchTerm, sortKey, showOnlyMissing]);

    if (!data) {
      return e(
        'div',
        { className: 'mx-auto flex min-h-screen w-full max-w-5xl items-center justify-center px-4 py-10' },
        e('div', { className: 'rounded-2xl border border-slate-700 bg-surface-900/70 px-5 py-4 text-sm text-slate-300' }, 'Loading challenge board...')
      );
    }

    var latestDate = viewModel.getLatestAchievedDate(data.scoreboard);
    var lastUpdatedLabel = viewModel.formatDateDisplay(latestDate);

    return e(
      'main',
      { className: 'mx-auto w-full max-w-6xl px-3 py-6 sm:px-6 sm:py-8' },
      e(
        'header',
        { className: 'mb-6 rounded-2xl border border-white/10 bg-gradient-to-r from-surface-800 to-surface-900 p-4 sm:p-6 shadow-glow' },
        e('p', { className: 'mb-2 text-[11px] font-bold uppercase tracking-[0.18em] text-accent-300' }, '2026 Fantasy Baseball Tracker'),
        e('h1', { className: 'font-display text-2xl font-bold tracking-tight text-white sm:text-3xl' }, 'Fantasy Runs Challenge'),
        e('p', { className: 'mt-2 max-w-3xl text-sm text-slate-300' }, 'Track race-to-completion standings for each participant. Progress updates when teams record new run totals from 0 through 13.'),
        e('div', { className: 'mt-3' }, e(LastUpdated, { lastUpdatedLabel: lastUpdatedLabel }))
      ),
      e(Controls, {
        searchTerm: searchTerm,
        sortKey: sortKey,
        showOnlyMissing: showOnlyMissing,
        onSearchChange: function(event) { return setSearchTerm(event.target.value); },
        onSortChange: function(event) { return setSortKey(event.target.value); },
        onMissingToggle: function(event) { return setShowOnlyMissing(event.target.checked); }
      }),
      e(FantasyRunsTable, { rows: rows })
    );
  }

  var api = {
    App: App,
    FantasyRunsTable: FantasyRunsTable,
    Controls: Controls
  };

  if (typeof window !== 'undefined' && window.document && window.ReactDOM) {
    window.ReactDOM.render(e(App), window.document.getElementById('root'));
  }

  return api;
});
