import React, { useState, useEffect } from "react";
import apiClient from "../lib/apiClient.js";

export default function ExpensesPage() {
  const [expenses, setExpenses] = useState([]);
  const [groups, setGroups] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [formData, setFormData] = useState({
    description: "",
    amount: "",
    type: "debit",
    date: new Date().toISOString().split('T')[0],
    group_id: "",
  });
  const [groupForm, setGroupForm] = useState({
    name: "",
    description: "",
  });
  const [viewMode, setViewMode] = useState("day");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showGroupForm, setShowGroupForm] = useState(false);
  const [editingExpense, setEditingExpense] = useState(null);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem("authToken");
    const user = localStorage.getItem("currentUser");
    if (token && user) {
      setCurrentUser(JSON.parse(user));
      fetchExpenses(token);
      fetchGroups(token);
    } else {
      // Redirect to login if not authenticated
      window.location.href = "/admin/login";
    }
  }, []);

  const fetchExpenses = async (token) => {
    try {
      const data = await apiClient.getExpenses();
      setExpenses(data.expenses || []);
    } catch (error) {
      console.error("Failed to fetch expenses:", error);
      setError(error.message || "Failed to fetch expenses");
    }
  };

  const fetchGroups = async (token) => {
    try {
      const data = await apiClient.getExpenseGroups();
      setGroups(data.groups || []);
    } catch (error) {
      console.error("Failed to fetch groups:", error);
      setError(error.message || "Failed to fetch expense groups");
    }
  };

  const handleExpenseSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      let result;
      if (editingExpense) {
        // For now, we'll skip editing functionality
        alert("Edit functionality not yet implemented");
        return;
      } else {
        result = await apiClient.createExpense(formData);
      }

      // Reset form
      setFormData({
        description: "",
        amount: "",
        type: "debit",
        date: new Date().toISOString().split('T')[0],
        group_id: "",
      });
      setEditingExpense(null);
      
      // Refresh expenses
      const token = localStorage.getItem("authToken");
      fetchExpenses(token);
    } catch (error) {
      console.error("Failed to save expense:", error);
      setError(error.message || "Failed to save expense");
    } finally {
      setLoading(false);
    }
  };

  const handleGroupSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await apiClient.createExpenseGroup(groupForm);

      // Reset form and refresh groups
      setGroupForm({ name: "", description: "" });
      setShowGroupForm(false);
      
      const token = localStorage.getItem("authToken");
      fetchGroups(token);
    } catch (error) {
      console.error("Failed to create group:", error);
      setError(error.message || "Failed to create group");
    } finally {
      setLoading(false);
    }
  };

  const handleEditExpense = (expense) => {
    setEditingExpense(expense);
    setFormData({
      description: expense.description,
      amount: expense.amount.toString(),
      type: expense.type,
      date: expense.date,
      group_id: expense.group_id || "",
    });
  };

  const handleDeleteExpense = async (expenseId) => {
    if (!window.confirm("Are you sure you want to delete this expense?")) return;

    setLoading(true);
    const token = localStorage.getItem("authToken");

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/expenses/${expenseId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to delete expense");
      }

      fetchExpenses(token);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleGroupChange = (e) => {
    const { name, value } = e.target;
    setGroupForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const calculateTotals = () => {
    const debit = expenses
      .filter(exp => exp.type === 'debit')
      .reduce((sum, exp) => sum + parseFloat(exp.amount), 0);
    const credit = expenses
      .filter(exp => exp.type === 'credit')
      .reduce((sum, exp) => sum + parseFloat(exp.amount), 0);
    const total = credit - debit;
    
    return { debit, credit, total };
  };

  const { debit, credit, total } = calculateTotals();
  const isAdmin = currentUser?.is_admin || false;

  return (
    <div className="page">
      <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '2rem' }}>
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
                    name="name"
                    value={groupForm.name}
                    onChange={handleGroupChange}
                    required
                    style={{ 
                      padding: '0.75rem', 
                      border: '1px solid rgba(255, 255, 255, 0.1)', 
                      borderRadius: '6px', 
                      background: 'var(--bg)', 
                      color: 'var(--text)', 
                      fontSize: '1rem' 
                    }}
                  />
                </div>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  <label htmlFor="groupDescription" style={{ fontWeight: '600', color: 'var(--text)' }}>Description</label>
                  <textarea
                    id="groupDescription"
                    name="description"
                    value={groupForm.description}
                    onChange={handleGroupChange}
                    rows={3}
                    style={{ 
                      padding: '0.75rem', 
                      border: '1px solid rgba(255, 255, 255, 0.1)', 
                      borderRadius: '6px', 
                      background: 'var(--bg)', 
                      color: 'var(--text)', 
                      fontSize: '1rem',
                      resize: 'vertical'
                    }}
                  />
                </div>
              </div>

              <button 
                type="submit" 
                disabled={loading} 
                style={{ 
                  padding: '0.75rem 1.5rem', 
                  border: 'none', 
                  borderRadius: '6px', 
                  background: loading ? 'rgba(94, 234, 212, 0.6)' : 'var(--accent)', 
                  color: 'var(--bg)', 
                  fontWeight: '600', 
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: loading ? 0.6 : 1
                }}
              >
                {loading ? "Creating..." : "Create Group"}
              </button>
            </form>
          </div>
        )}

        {/* Add/Edit Expense Form */}
        <div style={{ 
          background: 'var(--card)', 
          padding: '1.5rem', 
          borderRadius: '8px', 
          marginBottom: '2rem' 
        }}>
          <h2 style={{ color: 'var(--text)', marginBottom: '1rem' }}>
            {editingExpense ? 'Edit Expense' : 'Add Expense'}
          </h2>
          <form onSubmit={handleExpenseSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <label htmlFor="description" style={{ fontWeight: '600', color: 'var(--text)' }}>Description</label>
                <input
                  type="text"
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  required
                  style={{ 
                    padding: '0.75rem', 
                    border: '1px solid rgba(255, 255, 255, 0.1)', 
                    borderRadius: '6px', 
                    background: 'var(--bg)', 
                    color: 'var(--text)', 
                    fontSize: '1rem' 
                  }}
                />
              </div>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <label htmlFor="amount" style={{ fontWeight: '600', color: 'var(--text)' }}>Amount</label>
                <input
                  type="number"
                  id="amount"
                  name="amount"
                  value={formData.amount}
                  onChange={handleChange}
                  required
                  min="0"
                  step="0.01"
                  style={{ 
                    padding: '0.75rem', 
                    border: '1px solid rgba(255, 255, 255, 0.1)', 
                    borderRadius: '6px', 
                    background: 'var(--bg)', 
                    color: 'var(--text)', 
                    fontSize: '1rem' 
                  }}
                />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <label htmlFor="type" style={{ fontWeight: '600', color: 'var(--text)' }}>Type</label>
                <select
                  id="type"
                  name="type"
                  value={formData.type}
                  onChange={handleChange}
                  style={{ 
                    padding: '0.75rem', 
                    border: '1px solid rgba(255, 255, 255, 0.1)', 
                    borderRadius: '6px', 
                    background: 'var(--bg)', 
                    color: 'var(--text)', 
                    fontSize: '1rem' 
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
                  name="date"
                  value={formData.date}
                  onChange={handleChange}
                  required
                  style={{ 
                    padding: '0.75rem', 
                    border: '1px solid rgba(255, 255, 255, 0.1)', 
                    borderRadius: '6px', 
                    background: 'var(--bg)', 
                    color: 'var(--text)', 
                    fontSize: '1rem' 
                  }}
                />
              </div>

              {groups.length > 0 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  <label htmlFor="group_id" style={{ fontWeight: '600', color: 'var(--text)' }}>Group</label>
                  <select
                    id="group_id"
                    name="group_id"
                    value={formData.group_id}
                    onChange={handleChange}
                    style={{ 
                      padding: '0.75rem', 
                      border: '1px solid rgba(255, 255, 255, 0.1)', 
                      borderRadius: '6px', 
                      background: 'var(--bg)', 
                      color: 'var(--text)', 
                      fontSize: '1rem' 
                    }}
                  >
                    <option value="">Personal Expense</option>
                    {groups.map(group => (
                      <option key={group.id} value={group.id}>
                        {group.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div style={{ display: 'flex', alignItems: 'flex-end', gap: '0.5rem' }}>
                <button 
                  type="submit" 
                  disabled={loading} 
                  style={{ 
                    padding: '0.75rem 1.5rem', 
                    border: 'none', 
                    borderRadius: '6px', 
                    background: loading ? 'rgba(94, 234, 212, 0.6)' : 'var(--accent)', 
                    color: 'var(--bg)', 
                    fontWeight: '600', 
                    cursor: loading ? 'not-allowed' : 'pointer',
                    opacity: loading ? 0.6 : 1
                  }}
                >
                  {loading ? "Saving..." : (editingExpense ? "Update Expense" : "Add Expense")}
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
                        group_id: "",
                      });
                    }}
                    style={{
                      padding: '0.75rem 1.5rem',
                      border: '1px solid var(--danger)',
                      borderRadius: '6px',
                      background: 'var(--bg)',
                      color: 'var(--danger)',
                      fontWeight: '600',
                      cursor: 'pointer'
                    }}
                  >
                    Cancel
                  </button>
                )}
              </div>
            </div>
          </form>
        </div>

        {/* View Mode Selector */}
        <div style={{ 
          background: 'var(--card)', 
          padding: '1rem', 
          borderRadius: '8px', 
          marginBottom: '2rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <h3 style={{ color: 'var(--text)', margin: 0 }}>View Mode</h3>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            {['day', 'month', 'year'].map(mode => (
              <button
                key={mode}
                onClick={() => setViewMode(mode)}
                style={{
                  padding: '0.5rem 1rem',
                  border: 'none',
                  borderRadius: '4px',
                  background: viewMode === mode ? 'var(--accent)' : 'var(--bg)',
                  color: viewMode === mode ? 'var(--bg)' : 'var(--text)',
                  cursor: 'pointer',
                  textTransform: 'capitalize'
                }}
              >
                {mode}
              </button>
            ))}
          </div>
        </div>

        {/* Summary */}
        <div style={{ 
          background: 'var(--card)', 
          padding: '1.5rem', 
          borderRadius: '8px', 
          marginBottom: '2rem' 
        }}>
          <h3 style={{ color: 'var(--text)', marginBottom: '1rem' }}>Summary</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ color: 'var(--danger)', fontSize: '1.5rem', fontWeight: 'bold' }}>
                ${debit.toFixed(2)}
              </div>
              <div style={{ color: 'var(--muted)' }}>Total Debit</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ color: 'var(--accent)', fontSize: '1.5rem', fontWeight: 'bold' }}>
                ${credit.toFixed(2)}
              </div>
              <div style={{ color: 'var(--muted)' }}>Total Credit</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ 
                color: total >= 0 ? 'var(--accent)' : 'var(--danger)', 
                fontSize: '1.5rem', 
                fontWeight: 'bold' 
              }}>
                ${total.toFixed(2)}
              </div>
              <div style={{ color: 'var(--muted)' }}>Net Total</div>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div style={{ 
            padding: '0.75rem', 
            borderRadius: '6px', 
            background: 'rgba(255, 107, 107, 0.1)', 
            border: '1px solid var(--danger)', 
            color: 'var(--danger)', 
            textAlign: 'center',
            marginBottom: '1rem'
          }}>
            {error}
          </div>
        )}

        {/* Expenses List */}
        <div style={{ background: 'var(--card)', padding: '1.5rem', borderRadius: '8px' }}>
          <h3 style={{ color: 'var(--text)', marginBottom: '1rem' }}>
            Expenses ({viewMode === 'day' ? 'Today' : viewMode === 'month' ? 'This Month' : 'This Year'})
          </h3>
          {expenses.length === 0 ? (
            <p style={{ color: 'var(--muted)', textAlign: 'center' }}>No expenses found</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {expenses.map((expense) => (
                <div 
                  key={expense.id} 
                  style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    padding: '0.75rem',
                    background: 'var(--bg)',
                    borderRadius: '4px',
                    border: editingExpense?.id === expense.id ? '2px solid var(--accent)' : 'none'
                  }}
                >
                  <div style={{ flex: 1 }}>
                    <div style={{ color: 'var(--text)', fontWeight: '500' }}>{expense.description}</div>
                    <div style={{ color: 'var(--muted)', fontSize: '0.875rem' }}>
                      {new Date(expense.date).toLocaleDateString()} 
                      {expense.group_id && (
                        <span style={{ marginLeft: '0.5rem', color: 'var(--accent)' }}>
                          • {groups.find(g => g.id === expense.group_id)?.name || 'Group'}
                        </span>
                      )}
                    </div>
                  </div>
                  <div style={{ 
                    color: expense.type === 'debit' ? 'var(--danger)' : 'var(--accent)',
                    fontWeight: 'bold',
                    fontSize: '1.1rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}>
                    {expense.type === 'debit' ? '-' : '+'}${parseFloat(expense.amount).toFixed(2)}
                    {isAdmin && (
                      <div style={{ display: 'flex', gap: '0.25rem' }}>
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
      </div>
    </div>
  );
}
