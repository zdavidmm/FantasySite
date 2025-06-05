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
      achieved: scoreboard[team] || {},
    }))
    .sort((a, b) =>
      Object.keys(b.achieved).length - Object.keys(a.achieved).length
    );

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
              {RUN_TOTALS.map((n) => {
                const info = row.achieved[n];
                if (!info) {
                  return <td key={n} className="center"></td>;
                }
                const link = `https://www.mlb.com/gameday/${info.game_pk}`;
                return (
                  <td key={n} className="center">
                    <div className="mark">
                      <span className="check">✓</span>
                      <a href={link} target="_blank" rel="noopener noreferrer">
                        {info.date}
                      </a>
                    </div>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

ReactDOM.render(<App />, document.getElementById('root'));
