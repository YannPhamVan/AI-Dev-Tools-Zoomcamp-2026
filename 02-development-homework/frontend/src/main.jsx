import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { ArrowDownLeft, ArrowUpRight, Check, ChevronDown, CirclePlus, Copy, MoreHorizontal, Plus, Receipt, Send, Sparkles, Trash2, UserPlus, Users, X } from "lucide-react";
import { addExpense, addMember, createTrip, deleteExpense, getTrip } from "./api";
import "./styles.css";

const money = new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" });
const dateFormatter = new Intl.DateTimeFormat("fr-FR", { day: "numeric", month: "short" });

function App() {
  const [trip, setTrip] = useState(null);
  const [activeTab, setActiveTab] = useState("expenses");
  const [modal, setModal] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getTrip().then(setTrip).catch((requestError) => setError(requestError.message)).finally(() => setLoading(false));
  }, []);

  const refresh = async () => setTrip(await getTrip());
  const closeModal = () => setModal(null);

  if (loading) return <div className="loading-screen"><Sparkles size={20} /> Chargement du voyage...</div>;
  if (error || !trip) return <div className="loading-screen"><strong>Impossible de charger le voyage</strong><span>{error}</span><small>Vérifie que le backend tourne sur le port 8000.</small></div>;

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="ShareTrip accueil"><span className="brand-mark">S</span><span>sharetrip</span></a>
        <div className="topbar-actions"><button className="icon-button" aria-label="Options" title="Options"><MoreHorizontal size={20} /></button><div className="profile">YP</div></div>
      </header>
      <main id="top" className="page">
        <section className="trip-header">
          <div>
            <p className="eyebrow">TON VOYAGE <span className="live-dot" /> EN COURS</p>
            <h1>{trip.name}</h1>
            <p className="trip-meta">7 — 9 septembre 2026 <span>·</span> Rome, Italie</p>
          </div>
          <button className="outline-button" onClick={() => setModal("member")}><UserPlus size={16} /> <span>Inviter</span></button>
        </section>
        <section className="member-strip" aria-label="Participants">
          <div className="avatar-stack">{trip.members.map((member) => <Avatar key={member.id} member={member} />)}</div>
          <div className="member-copy"><strong>{trip.members.length} participants</strong><span>{trip.members.map((member) => member.name).join(", ")}</span></div>
          <button className="round-add" onClick={() => setModal("member")} aria-label="Ajouter un participant" title="Ajouter un participant"><Plus size={18} /></button>
        </section>
        <section className="summary-grid">
          <SummaryCard label="Dépensé au total" value={money.format(totalSpent(trip.expenses))} caption={`soit ${money.format(totalSpent(trip.expenses) / Math.max(trip.members.length, 1))} / personne`} />
          <SummaryCard label="Ta balance" value={formatBalance(balanceFor(currentUserId(trip), trip))} caption={balanceFor(currentUserId(trip), trip) >= 0 ? "on te doit de l'argent" : "tu dois encore régler"} accent={balanceFor(currentUserId(trip), trip) >= 0 ? "positive" : "negative"} />
        </section>
        <nav className="tabs" aria-label="Vue du voyage"><button className={activeTab === "expenses" ? "active" : ""} onClick={() => setActiveTab("expenses")}><Receipt size={17} /> Dépenses <span>{trip.expenses.length}</span></button><button className={activeTab === "settlement" ? "active" : ""} onClick={() => setActiveTab("settlement")}><Sparkles size={17} /> Équilibrage <span className="tab-ping">!</span></button></nav>
        {activeTab === "expenses" ? <ExpensesView trip={trip} onAdd={() => setModal("expense")} onDelete={async (id) => { await deleteExpense(id); await refresh(); }} /> : <SettlementView trip={trip} />}
      </main>
      {modal === "expense" && <ExpenseModal trip={trip} onClose={closeModal} onSaved={async () => { await refresh(); closeModal(); }} />}
      {modal === "member" && <MemberModal onClose={closeModal} onSaved={async () => { await refresh(); closeModal(); }} />}
    </div>
  );
}

function SummaryCard({ label, value, caption, accent = "" }) { return <article className={`summary-card ${accent}`}><p>{label}</p><strong>{value}</strong><span>{caption}</span></article>; }
function Avatar({ member, small = false }) { return <span className={`avatar ${member.color} ${small ? "small" : ""}`} title={member.name}>{member.name.slice(0, 1)}</span>; }
function totalSpent(expenses) { return expenses.reduce((sum, expense) => sum + expense.amount, 0); }
function balanceFor(memberId, trip) { return getBalances(trip)[memberId] || 0; }
function getBalances(trip) { return trip.balances || {}; }
function formatBalance(value) { return `${value >= 0 ? "+" : "−"}${money.format(Math.abs(value))}`; }
function currentUserId(trip) { return trip.members.find((member) => member.name.toLowerCase() === "yann")?.id || trip.members[0]?.id; }
function memberName(trip, id) { return trip.members.find((member) => member.id === id)?.name || "Inconnu"; }

function ExpensesView({ trip, onAdd, onDelete }) {
  const expenses = [...trip.expenses].sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  return <>
    <section className="section-heading"><div><p className="eyebrow">JOURNAL DU GROUPE</p><h2>Les dernières dépenses</h2></div><button className="primary-button" onClick={onAdd}><CirclePlus size={18} /> Ajouter</button></section>
    <div className="expense-list">{expenses.length ? expenses.map((expense) => <ExpenseRow key={expense.id} expense={expense} trip={trip} onDelete={onDelete} />) : <EmptyState onAdd={onAdd} />}</div>
    <p className="privacy-note"><Check size={15} /> Toutes les dépenses sont partagées équitablement entre les participants</p>
  </>;
}
function ExpenseRow({ expense, trip, onDelete }) { const payer = trip.members.find((member) => member.id === expense.paidBy); return <article className="expense-row"><div className="expense-icon"><Receipt size={18} /></div><div className="expense-details"><strong>{expense.description}</strong><span><Avatar member={payer} small /> {payer?.name} a payé <i>·</i> {dateFormatter.format(new Date(expense.createdAt))}</span></div><div className="expense-amount"><strong>{money.format(expense.amount)}</strong><button className="delete-button" onClick={() => onDelete(expense.id)} aria-label={`Supprimer ${expense.description}`} title="Supprimer"><Trash2 size={14} /></button></div></article>; }
function EmptyState({ onAdd }) { return <div className="empty-state"><Receipt size={28} /><strong>Aucune dépense pour le moment</strong><span>Ajoute la première et tout le monde verra la balance.</span><button className="text-button" onClick={onAdd}>Ajouter une dépense <ArrowUpRight size={15} /></button></div>; }

function SettlementView({ trip }) { const transfers = trip.settlements || []; const balances = getBalances(trip); const userId = currentUserId(trip); return <section className="settlement"><div className="settlement-intro"><div className="sparkle-badge"><Sparkles size={19} /></div><div><p className="eyebrow">ALGORITHME OPTIMISÉ</p><h2>On remet les comptes à zéro.</h2><p>Un minimum de virements pour que chacun reparte léger.</p></div></div><div className="balance-list"><h3>Balances actuelles</h3>{trip.members.map((member) => <div className="balance-row" key={member.id}><div className="person"><Avatar member={member} small /><span>{member.name}{member.id === userId && <em>toi</em>}</span></div><strong className={balances[member.id] >= 0 ? "positive" : "negative"}>{formatBalance(balances[member.id])}</strong></div>)}</div><div className="transfer-block"><div className="transfer-heading"><h3>À régler</h3><span>{transfers.length} virement{transfers.length > 1 ? "s" : ""}</span></div>{transfers.length ? transfers.map((transfer, index) => <TransferRow key={`${transfer.from}-${transfer.to}`} transfer={transfer} trip={trip} index={index} />) : <div className="settled"><Check size={20} /> Tout est déjà équilibré.</div>}</div></section>; }
function TransferRow({ transfer, trip, index }) { const from = trip.members.find((member) => member.id === transfer.from); const to = trip.members.find((member) => member.id === transfer.to); return <article className="transfer-row"><div className="transfer-number">0{index + 1}</div><Avatar member={from} small /><div className="transfer-person"><strong>{from.name}</strong><span>doit à {to.name}</span></div><ArrowUpRight className="transfer-arrow" size={17} /><Avatar member={to} small /><strong className="transfer-amount">{money.format(transfer.amount)}</strong><button className="copy-button" aria-label="Copier le virement" title="Copier" onClick={() => navigator.clipboard?.writeText(`${from.name} doit ${money.format(transfer.amount)} à ${to.name}`)}><Copy size={15} /></button></article>; }

function Modal({ title, children, onClose }) { return <div className="modal-backdrop" onMouseDown={(event) => event.target === event.currentTarget && onClose()}><div className="modal" role="dialog" aria-modal="true"><div className="modal-header"><h2>{title}</h2><button className="icon-button" onClick={onClose} aria-label="Fermer"><X size={19} /></button></div>{children}</div></div>; }
function ExpenseModal({ trip, onClose, onSaved }) { const [form, setForm] = useState({ description: "", amount: "", paidBy: trip.members[0]?.id || "" }); const [saving, setSaving] = useState(false); const submit = async (event) => { event.preventDefault(); if (!form.description || !Number(form.amount) || !form.paidBy) return; setSaving(true); await addExpense(form); await onSaved(); }; return <Modal title="Nouvelle dépense" onClose={onClose}><form className="form" onSubmit={submit}><label>Description<input autoFocus value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} placeholder="Ex. Gelato sur la piazza" required /></label><label>Montant<div className="amount-input"><input type="number" min="0.01" step="0.01" value={form.amount} onChange={(event) => setForm({ ...form, amount: event.target.value })} placeholder="0,00" required /><span>€</span></div></label><label>Qui a payé ?<div className="select-wrap"><select value={form.paidBy} onChange={(event) => setForm({ ...form, paidBy: event.target.value })}>{trip.members.map((member) => <option value={member.id} key={member.id}>{member.name}</option>)}</select><ChevronDown size={16} /></div></label><p className="form-hint"><Users size={15} /> Partagé équitablement entre {trip.members.length} personnes</p><button className="primary-button full" disabled={saving}>{saving ? "Ajout en cours..." : "Ajouter la dépense"}<ArrowUpRight size={17} /></button></form></Modal>; }
function MemberModal({ onClose, onSaved }) { const [name, setName] = useState(""); const [saving, setSaving] = useState(false); const submit = async (event) => { event.preventDefault(); if (!name.trim()) return; setSaving(true); await addMember(name); await onSaved(); }; return <Modal title="Ajouter un participant" onClose={onClose}><form className="form" onSubmit={submit}><label>Prénom<input autoFocus value={name} onChange={(event) => setName(event.target.value)} placeholder="Ex. Thomas" required /></label><p className="form-hint"><UserPlus size={15} /> Il pourra être ajouté aux prochaines dépenses</p><button className="primary-button full" disabled={saving}>{saving ? "Ajout en cours..." : "Ajouter au groupe"}<Plus size={17} /></button></form></Modal>; }

createRoot(document.getElementById("root")).render(<App />);
