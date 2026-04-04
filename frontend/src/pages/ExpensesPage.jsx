import React, { useState, useEffect } from "react";

export default function ExpensesPage() {
  const [expenses, setExpenses] = useState([]);
  const [formData, setFormData] = useState({
    description: "",
    amount: "",
    type: "debit",
    date: new Date().toISOString().split('T')[0],
  });
  const [viewMode, setViewMode] = useState("day");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchExpenses();
  }, [viewMode]);

  const fetchExpenses = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/expenses?view=${viewMode}`);
      const data = await response.json();
      if (response.ok) {
        setExpenses(data.expenses || []);
      } else {
        throw new Error(data.error || "Failed to fetch expenses");
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/expenses`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to add expense");
      }

      // Reset form and refresh expenses
      setFormData({
        description: "",
        amount: "",
        type: "debit",
        date: new Date().toISOString().split('T')[0],
      });
      fetchExpenses();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
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

  return (
    <div className="page">
      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem' }}>
        <h1 style={{ textAlign: 'center', marginBottom: '2rem', color: 'var(--text)' }}>Expenses Tracker</h1>
        
        {/* Add Expense Form */}
        <div style={{ 
          background: 'var(--card)', 
          padding: '1.5rem', 
          borderRadius: '8px', 
          marginBottom: '2rem' 
        }}>
          <h2 style={{ color: 'var(--text)', marginBottom: '1rem' }}>Add Expense</h2>
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
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

              <div style={{ display: 'flex', alignItems: 'flex-end' }}>
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
                    opacity: loading ? 0.6 : 1,
                    width: '100%'
                  }}
                >
                  {loading ? "Adding..." : "Add Expense"}
                </button>
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
                    borderRadius: '4px'
                  }}
                >
                  <div>
                    <div style={{ color: 'var(--text)', fontWeight: '500' }}>{expense.description}</div>
                    <div style={{ color: 'var(--muted)', fontSize: '0.875rem' }}>
                      {new Date(expense.date).toLocaleDateString()}
                    </div>
                  </div>
                  <div style={{ 
                    color: expense.type === 'debit' ? 'var(--danger)' : 'var(--accent)',
                    fontWeight: 'bold',
                    fontSize: '1.1rem'
                  }}>
                    {expense.type === 'debit' ? '-' : '+'}${parseFloat(expense.amount).toFixed(2)}
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
