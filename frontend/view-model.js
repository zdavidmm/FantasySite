(function(root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
    return;
  }
  root.FantasyViewModel = factory();
})(typeof self !== 'undefined' ? self : this, function() {
  var RUN_TOTALS = Array.from({ length: 14 }, function(_, i) { return i; });

  function achievedCount(row) {
    return Object.keys(row.achieved || {}).length;
  }

  function buildRows(assignments, scoreboard) {
    var safeAssignments = assignments || {};
    var safeScoreboard = scoreboard || {};

    return Object.entries(safeAssignments).map(function(entry) {
      var participant = entry[0];
      var team = entry[1];
      var achieved = safeScoreboard[team] || {};
      var progressCount = achievedCount({ achieved: achieved });
      var completionRatio = progressCount / RUN_TOTALS.length;

      return {
        participant: participant,
        team: team,
        achieved: achieved,
        progressCount: progressCount,
        completionRatio: completionRatio,
        hasMissingTotals: progressCount < RUN_TOTALS.length
      };
    });
  }

  function compareRows(sortKey, a, b) {
    if (sortKey === 'progress-asc') {
      if (a.progressCount !== b.progressCount) {
        return a.progressCount - b.progressCount;
      }
      return a.participant.localeCompare(b.participant);
    }

    if (sortKey === 'name-desc') {
      return b.participant.localeCompare(a.participant);
    }

    if (sortKey === 'team-asc') {
      var teamComparison = a.team.localeCompare(b.team);
      if (teamComparison !== 0) {
        return teamComparison;
      }
      return a.participant.localeCompare(b.participant);
    }

    if (sortKey === 'name-asc') {
      return a.participant.localeCompare(b.participant);
    }

    if (a.progressCount !== b.progressCount) {
      return b.progressCount - a.progressCount;
    }

    return a.participant.localeCompare(b.participant);
  }

  function sortRows(rows, sortKey) {
    return rows.slice().sort(function(a, b) {
      return compareRows(sortKey || 'progress-desc', a, b);
    });
  }

  function filterRows(rows, options) {
    var safeOptions = options || {};
    var query = (safeOptions.searchTerm || '').trim().toLowerCase();
    var showOnlyMissing = !!safeOptions.showOnlyMissing;

    return rows.filter(function(row) {
      var nameMatches = !query || row.participant.toLowerCase().indexOf(query) !== -1;
      var missingMatches = !showOnlyMissing || row.hasMissingTotals;
      return nameMatches && missingMatches;
    });
  }

  function deriveVisibleRows(assignments, scoreboard, options) {
    var safeOptions = options || {};
    var baseRows = buildRows(assignments, scoreboard);
    var filtered = filterRows(baseRows, safeOptions);
    return sortRows(filtered, safeOptions.sortKey || 'progress-desc');
  }

  function getLatestAchievedDate(scoreboard) {
    var safeScoreboard = scoreboard || {};
    var latest = null;

    Object.values(safeScoreboard).forEach(function(teamRuns) {
      Object.values(teamRuns || {}).forEach(function(info) {
        if (!info || !info.date) {
          return;
        }
        if (!latest || info.date > latest) {
          latest = info.date;
        }
      });
    });

    return latest;
  }

  function formatDateDisplay(isoDate) {
    if (!isoDate) {
      return 'N/A';
    }

    var date = new Date(isoDate + 'T00:00:00');
    if (isNaN(date.getTime())) {
      return isoDate;
    }

    return date.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  }

  return {
    RUN_TOTALS: RUN_TOTALS,
    buildRows: buildRows,
    sortRows: sortRows,
    filterRows: filterRows,
    deriveVisibleRows: deriveVisibleRows,
    getLatestAchievedDate: getLatestAchievedDate,
    formatDateDisplay: formatDateDisplay
  };
});
