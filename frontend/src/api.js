import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export async function uploadCsv(file) {
  const form = new FormData()
  form.append('file', file)
  const r = await axios.post(`${API_BASE}/upload-csv`, form, { headers: { 'Content-Type': 'multipart/form-data' }})
  return r.data
}

export async function buildNetwork(method) {
  const r = await axios.post(`${API_BASE}/build-network?method=${encodeURIComponent(method)}`)
  return r.data
}

export async function getGraph() {
  const r = await axios.get(`${API_BASE}/graph`)
  return r.data
}

export async function generateNetwork(params) {
  const r = await axios.post(`${API_BASE}/generate-network`, null, { params })
  return r.data
}

export async function simulate(params) {
  const queryParams = new URLSearchParams()
  if (params.initial_infected) queryParams.append('initial_infected', params.initial_infected)
  if (params.infection_prob !== undefined) queryParams.append('infection_prob', params.infection_prob)
  if (params.death_prob !== undefined) queryParams.append('death_prob', params.death_prob)
  const r = await axios.post(`${API_BASE}/simulate?${queryParams.toString()}`)
  return r.data
}

export async function downloadGraph() {
  const r = await axios.get(`${API_BASE}/download/graph`, { responseType: 'blob' })
  return r.data
}
