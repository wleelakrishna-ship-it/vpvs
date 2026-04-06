import React, { useState, useEffect } from "react";
import apiClient from "../lib/universalApiClient.js";

export default function ExpensesPage() {
  const [expenses, setExpenses] = useState([]);
  const [groups, setGroups] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [formData, setFormData] = useState({
    description: "",
    amount: "",
    type: "debit",
    date: new Date().toISOString().split('T')[0],
    group_id: ""
  });
  const [groupForm, setGroupForm] = useState({
    name: "",
    description: ""
  });
  const [showGroupForm, setShowGroupForm] = useState(false);
  const [editingExpense, setEditingExpense] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check authentication
    const user = localStorage.getItem("currentUser");
    if (!user) {
      window.location.href = "/login";
      return;
    }
    setCurrentUser(JSON.parse(user));

    // Fetch data
    fetchExpenses();
    fetchGroups();
  }, []);

  const fetchExpenses = async () => {
    setLoading(true);
    try {
      const data = await apiClient.getExpenses();
      setExpenses(data.expenses || []);
    } catch (err) {
      setError(err.message || "Failed to fetch expenses");
    } finally {
      setLoading(false);
    }
  };

  const fetchGroups = async () => {
    try {
      const data = await apiClient.getExpenseGroups();
      setGroups(data.groups || []);
    } catch (err) {
      console.error("Failed to fetch groups:", err);
    }
  };

  const handleExpenseSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (editingExpense) {
        await apiClient.updateExpense(editingExpense.id, formData);
      } else {
        await apiClient.createExpense(formData);
      }
      
      setFormData({
        description: "",
        amount: "",
        type: "debit",
        date: new Date().toISOString().split('T')[0],
        group_id: ""
      });
      setEditingExpense(null);
      await fetchExpenses();
    } catch (err) {
      setError(err.message || "Failed to save expense");
    } finally {
      setLoading(false);
    }
  };

  const handleGroupSubmit = async (e) => {
    e.preventDefault();
    try {
      await apiClient.createExpenseGroup(groupForm);
      setGroupForm({ name: "", description: "" });
      setShowGroupForm(false);
      await fetchGroups();
    } catch (err) {
      setError(err.message || "Failed to create group");
    }
  };

  const handleEditExpense = (expense) => {
    setFormData({
      description: expense.description,
      amount: expense.amount,
      type: expense.type,
      date: expense.date,
      group_id: expense.group_id || ""
    });
    setEditingExpense(expense);
  };

  const handleDeleteExpense = async (id) => {
    if (!window.confirm("Are you sure you want to delete this expense?")) {
      return;
    }
    
    try {
      await apiClient.deleteExpense(id);
      await fetchExpenses();
    } catch (err) {
      setError(err.message || "Failed to delete expense");
    }
  };

  const isAdmin = currentUser?.is_admin || false;

  return (
    <div className="page" style={{ maxWidth: '1000px', margin: '0 auto', padding: '2rem' }}>
      {/* Loading State */}
      {loading && !expenses.length && (
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          minHeight: '60vh',
          flexDirection: 'column',
          gap: '1rem'
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            border: '3px solid var(--border)',
            borderTop: '3px solid var(--accent)',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }}></div>
          <p style={{ color: 'var(--muted)' }}>Loading expenses...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '8px',
          padding: '1rem',
          marginBottom: '2rem',
          color: '#ef4444'
        }}>
          <strong>Error:</strong> {error}
          <button
            onClick={() => setError(null)}
            style={{
              marginLeft: '1rem',
              padding: '0.25rem 0.5rem',
              border: '1px solid #ef4444',
              borderRadius: '3px',
              background: 'white',
              color: '#ef4444',
              cursor: 'pointer'
            }}
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Main Content */}
      {!loading && (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
            <h1 style={{ color: 'var(--text)', margin: 0 }}>Expenses Tracker</h1>
            <div style={{ color: 'var(--muted)' }}>
              Logged in as: <strong>{currentUser?.username}</strong> ({isAdmin ? 'Admin' : 'User'})
            </div>
          </div>

          {/* Admin: Create Group Button */}
          {isAdmin && (
            <div style={{ marginBottom: '2rem' }}>
              <button
                onClick={() => setShowGroupForm(!showGroupForm)}
                style={{
                  padding: '0.75rem 1.5rem',
                  border: 'none',
                  borderRadius: '6px',
                  background: 'var(--accent)',
                  color: 'var(--bg)',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}
              >
                {showGroupForm ? 'Cancel' : 'Create Group'}
              </button>
            </div>
          )}

          {/* Group Creation Form */}
          {showGroupForm && isAdmin && (
            <div style={{ 
              background: 'var(--card)', 
              padding: '1.5rem', 
              borderRadius: '8px', 
              marginBottom: '2rem' 
            }}>
              <h3 style={{ color: 'var(--text)', marginBottom: '1rem' }}>Create Expense Group</h3>
              <form onSubmit={handleGroupSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    <label htmlFor="groupName" style={{ fontWeight: '600', color: 'var(--text)' }}>Group Name</label>
                    <input
                      type="text"
                      id="groupName"
                      value={groupForm.name}
                      onChange={(e) => setGroupForm({ ...groupForm, name: e.target.value })}
                      required
                      style={{
                        padding: '0.5rem',
                        border: '1px solid var(--border)',
                        borderRadius: '4px',
                        background: 'var(--bg)',
                        color: 'var(--text)'
                      }}
                    />
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    <label htmlFor="groupDescription" style={{ fontWeight: '600', color: 'var(--text)' }}>Description</label>
                    <textarea
                      id="groupDescription"
                      value={groupForm.description}
                      onChange={(e) => setGroupForm({ ...groupForm, description: e.target.value })}
                      rows="3"
                      style={{
                        padding: '0.5rem',
                        border: '1px solid var(--border)',
                        borderRadius: '4px',
                        background: 'var(--bg)',
                        color: 'var(--text)',
                        resize: 'vertical'
                      }}
                    />
                  </div>
                </div>
                <button
                  type="submit"
                  style={{
                    padding: '0.75rem 1.5rem',
                    border: 'none',
                    borderRadius: '6px',
                    background: 'var(--accent)',
                    color: 'var(--bg)',
                    fontWeight: '600',
                    cursor: 'pointer'
                  }}
                >
                  Create Group
                </button>
              </form>
            </div>
          )}

          {/* Expense Form */}
          <div style={{ 
            background: 'var(--card)', 
            padding: '1.5rem', 
            borderRadius: '8px', 
            marginBottom: '2rem' 
          }}>
            <h3 style={{ color: 'var(--text)', marginBottom: '1rem' }}>
              {editingExpense ? 'Edit Expense' : 'Add Expense'}
            </h3>
            <form onSubmit={handleExpenseSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  <label htmlFor="description" style={{ fontWeight: '600', color: 'var(--text)' }}>Description</label>
                  <input
                    type="text"
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    required
                    style={{
                      padding: '0.5rem',
                      border: '1px solid var(--border)',
                      borderRadius: '4px',
                      background: 'var(--bg)',
                      color: 'var(--text)'
                    }}
                  />
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  <label htmlFor="amount" style={{ fontWeight: '600', color: 'var(--text)' }}>Amount</label>
                  <input
                    type="number"
                    id="amount"
                    value={formData.amount}
                    onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                    required
                    step="0.01"
                    style={{
                      padding: '0.5rem',
                      border: '1px solid var(--border)',
                      borderRadius: '4px',
                      background: 'var(--bg)',
                      color: 'var(--text)'
                    }}
                  />
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  <label htmlFor="type" style={{ fontWeight: '600', color: 'var(--text)' }}>Type</label>
                  <select
                    id="type"
                    value={formData.type}
                    onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                    style={{
                      padding: '0.5rem',
                      border: '1px solid var(--border)',
                      borderRadius: '4px',
                      background: 'var(--bg)',
                      color: 'var(--text)'
                    }}
                  >
                    <option value="debit">Debit</option>
                    <option value="credit">Credit</option>
                  </select>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  <label htmlFor="date" style={{ fontWeight: '600', color: 'var(--text)' }}>Date</label>
                  <input
                    type="date"
                    id="date"
                    value={formData.date}
                    onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                    required
                    style={{
                      padding: '0.5rem',
                      border: '1px solid var(--border)',
                      borderRadius: '4px',
                      background: 'var(--bg)',
                      color: 'var(--text)'
                    }}
                  />
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  <label htmlFor="group" style={{ fontWeight: '600', color: 'var(--text)' }}>Group</label>
                  <select
                    id="group"
                    value={formData.group_id}
                    onChange={(e) => setFormData({ ...formData, group_id: e.target.value })}
                    style={{
                      padding: '0.5rem',
                      border: '1px solid var(--border)',
                      borderRadius: '4px',
                      background: 'var(--bg)',
                      color: 'var(--text)'
                    }}
                  >
                    <option value="">No Group</option>
                    {groups.map((group) => (
                      <option key={group.id} value={group.id}>
                        {group.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <button
                  type="submit"
                  style={{
                    padding: '0.75rem 1.5rem',
                    border: 'none',
                    borderRadius: '6px',
                    background: 'var(--accent)',
                    color: 'var(--bg)',
                    fontWeight: '600',
                    cursor: 'pointer'
                  }}
                >
                  {editingExpense ? 'Update Expense' : 'Add Expense'}
                </button>
                {editingExpense && (
                  <button
                    type="button"
                    onClick={() => {
                      setEditingExpense(null);
                      setFormData({
                        description: "",
                        amount: "",
                        type: "debit",
                        date: new Date().toISOString().split('T')[0],
                        group_id: ""
                      });
                    }}
                    style={{
                      padding: '0.75rem 1.5rem',
                      border: '1px solid var(--border)',
                      borderRadius: '6px',
                      background: 'var(--bg)',
                      color: 'var(--text)',
                      fontWeight: '600',
                      cursor: 'pointer'
                    }}
                  >
                    Cancel
                  </button>
                )}
              </div>
            </form>
          </div>

          {/* Expenses List */}
          <div style={{ background: 'var(--card)', padding: '1.5rem', borderRadius: '8px' }}>
            <h3 style={{ color: 'var(--text)', marginBottom: '1rem' }}>
              Expenses ({new Date().toLocaleDateString() === formData.date ? 'Today' : 'All'})
            </h3>
            {expenses.length === 0 ? (
              <p style={{ color: 'var(--muted)', textAlign: 'center' }}>No expenses found</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {expenses.map((expense) => (
                  <div
                    key={expense.id}
                    style={{
                      padding: '1rem',
                      border: '1px solid var(--border)',
                      borderRadius: '6px',
                      background: 'var(--bg)',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}
                  >
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: '600', color: 'var(--text)' }}>
                        {expense.description}
                      </div>
                      <div style={{ fontSize: '0.9rem', color: 'var(--muted)' }}>
                        {expense.date} • {expense.group_name || 'No Group'}
                      </div>
                    </div>
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '1rem' 
                    }}>
                      <span style={{
                        fontWeight: '700',
                        fontSize: '1.1rem',
                        color: expense.type === 'debit' ? '#ef4444' : '#10b981'
                      }}>
                        {expense.type === 'debit' ? '-' : '+'} ${expense.amount}
                      </span>
                      {isAdmin && (
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                          <button
                            onClick={() => handleEditExpense(expense)}
                            style={{
                              padding: '0.25rem 0.5rem',
                              border: '1px solid var(--accent)',
                              borderRadius: '3px',
                              background: 'var(--bg)',
                              color: 'var(--accent)',
                              cursor: 'pointer',
                              fontSize: '0.75rem'
                            }}
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteExpense(expense.id)}
                            style={{
                              padding: '0.25rem 0.5rem',
                              border: '1px solid var(--danger)',
                              borderRadius: '3px',
                              background: 'var(--bg)',
                              color: 'var(--danger)',
                              cursor: 'pointer',
                              fontSize: '0.75rem'
                            }}
                          >
                            Delete
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
