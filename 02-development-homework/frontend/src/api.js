const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const TRIP_STORAGE_KEY = "sharetrip-trip-id";
const memberColors = ["coral", "blue", "yellow", "green"];

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });

  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    throw new Error(detail?.detail || `Request failed: ${response.status}`);
  }

  return response.status === 204 ? null : response.json();
}

function normalizeTrip(data, balances = [], settlements = []) {
  return {
    ...data,
    currency: "EUR",
    members: data.members.map((member, index) => ({ ...member, color: memberColors[index % memberColors.length] })),
    expenses: data.expenses.map((expense) => ({
      ...expense,
      paidBy: expense.paid_by,
      createdAt: expense.created_at
    })),
    balances: Object.fromEntries(balances.map((entry) => [entry.member_id, entry.balance])),
    settlements: settlements.map((settlement) => ({
      from: settlement.from_member_id,
      to: settlement.to_member_id,
      amount: settlement.amount
    }))
  };
}

async function createDefaultTrip() {
  const data = await request("/trips", { method: "POST", body: JSON.stringify({ name: "Weekend à Rome" }) });
  const names = ["Yann", "Marc", "Sarah", "Inès"];
  for (const name of names) {
    await request(`/trips/${data.id}/members`, { method: "POST", body: JSON.stringify({ name }) });
  }
  localStorage.setItem(TRIP_STORAGE_KEY, data.id);
  return data.id;
}

async function getTripId() {
  const storedId = localStorage.getItem(TRIP_STORAGE_KEY);
  if (storedId) return storedId;
  return createDefaultTrip();
}

export async function getTrip() {
  let tripId = await getTripId();
  let data;
  try {
    data = await request(`/trips/${tripId}`);
  } catch (error) {
    if (!error.message.includes("Trip not found")) throw error;
    tripId = await createDefaultTrip();
    data = await request(`/trips/${tripId}`);
  }
  const [balances, settlements] = await Promise.all([
    request(`/trips/${tripId}/balances`),
    request(`/trips/${tripId}/settlements`)
  ]);
  return normalizeTrip(data, balances, settlements);
}

export async function addExpense({ description, amount, paidBy }) {
  const tripId = await getTripId();
  return request(`/trips/${tripId}/expenses`, {
    method: "POST",
    body: JSON.stringify({ description, amount: Number(amount), paid_by: paidBy })
  });
}

export async function addMember(name) {
  const tripId = await getTripId();
  return request(`/trips/${tripId}/members`, {
    method: "POST",
    body: JSON.stringify({ name: name.trim() })
  });
}

export async function createTrip(name) {
  const data = await request("/trips", { method: "POST", body: JSON.stringify({ name: name.trim() }) });
  localStorage.setItem(TRIP_STORAGE_KEY, data.id);
  return data;
}

export async function deleteExpense(expenseId) {
  const tripId = await getTripId();
  return request(`/trips/${tripId}/expenses/${expenseId}`, { method: "DELETE" });
}
