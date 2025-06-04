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

  return (
    <div className="container">
      <h1>Fantasy Runs Challenge</h1>
      <table>
        <thead>
          <tr>
            <th>Participant</th>
            <th>Team</th>
            <th>Runs 0-13</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(assignments).map(([participant, team]) => (
            <tr key={participant}>
              <td>{participant}</td>
              <td>{team}</td>
              <td>{(scoreboard[team] || []).join(', ')}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

ReactDOM.render(<App />, document.getElementById('root'));
