function App() {
  const [data, setData] = React.useState(null);

  React.useEffect(() => {
    fetch('/api/data')
      .then(res => res.json())
      .then(setData);
  }, []);

  if (!data) {
    return React.createElement('div', { className: 'loading' }, 'Loading...');
  }

  const { assignments, scoreboard } = data;

  const RUN_TOTALS = Array.from({ length: 14 }, (_, i) => i);

  const rows = Object.entries(assignments)
    .map(([participant, team]) => ({
      participant,
      team,
      achieved: scoreboard[team] || [],
    }))
    .sort((a, b) => b.achieved.length - a.achieved.length);

  return (
    <div className="container">
      <h1>Fantasy Runs Challenge</h1>
      <table>
        <thead>
          <tr>
            <th>Participant</th>
            <th>Team</th>
            {RUN_TOTALS.map((n) => (
              <th key={n} className="center">{n}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.participant}>
              <td>{row.participant}</td>
              <td>{row.team}</td>
              {RUN_TOTALS.map((n) => (
                <td key={n} className="center">
                  {row.achieved.includes(n) ? '✓' : ''}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

ReactDOM.render(<App />, document.getElementById('root'));
