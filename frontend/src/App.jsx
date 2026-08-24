import { useEffect, useState } from "react";
import { getAnomalies, getHealth, getLogs } from "./services/api";

function App() {
	const [health, setHealth] = useState(null);
	const [logs, setLogs] = useState([]);
	const [anomalies, setAnomalies] = useState([]);
	const [error, setError] = useState("");

	useEffect(() => {
		Promise.all([getHealth(), getLogs(), getAnomalies()])
			.then(([healthResponse, logsResponse, anomalyResponse]) => {
				setHealth(healthResponse);
				setLogs(logsResponse);
				setAnomalies(anomalyResponse);
			})
			.catch((requestError) => setError(requestError.message));
	}, []);

	return (
		<main style={{ fontFamily: "sans-serif", margin: "0 auto", maxWidth: 1000, padding: 32 }}>
			<header style={{ borderBottom: "1px solid #ddd", marginBottom: 28, paddingBottom: 18 }}>
				<p style={{ color: "#64748b", letterSpacing: 2, margin: 0 }}>SECUREFLOW</p>
				<h1 style={{ margin: "8px 0" }}>Threat intelligence dashboard</h1>
				<p style={{ color: "#475569", margin: 0 }}>
					Monitor ingested events and review suspicious activity.
				</p>
			</header>
			{error && <p role="alert" style={{ color: "#b91c1c" }}>{error}</p>}
			<section style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
				<Metric label="API status" value={health?.status || "Loading"} />
				<Metric label="Events" value={logs.length} />
				<Metric label="Anomalies" value={anomalies.length} />
			</section>
			<section style={{ marginTop: 32 }}>
				<h2>Recent anomalies</h2>
				{anomalies.length === 0 ? <p>No anomalies detected.</p> : (
					<ul>
						{anomalies.map((anomaly) => (
							<li key={anomaly.id} style={{ marginBottom: 12 }}>
								<strong>{anomaly.threat_type}</strong> from {anomaly.src_ip}: {anomaly.reason}
							</li>
						))}
					</ul>
				)}
			</section>
		</main>
	);
}

function Metric({ label, value }) {
	return <article style={{ background: "#f1f5f9", minWidth: 160, padding: 18 }}><small>{label}</small><h2 style={{ margin: "8px 0 0" }}>{value}</h2></article>;
}

export default App;
