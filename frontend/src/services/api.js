// Axios instance with base URL and API key header injection
// Build target: Month 3
const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
	const response = await fetch(`${API_BASE_URL}${path}`, {
		headers: { "Content-Type": "application/json", ...options.headers },
		...options,
	});
	if (!response.ok) {
		throw new Error(`Request failed (${response.status})`);
	}
	return response.json();
}

export const getHealth = () => request("/health");
export const getLogs = () => request("/logs");
export const getAnomalies = () => request("/anomalies");
