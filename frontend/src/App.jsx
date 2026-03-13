import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Cell
} from 'recharts';
import { Search, Activity, Users, ShoppingBag, Globe } from 'lucide-react';
import './index.css';

const API_BASE = "http://localhost:8000/api";

const Dashboard = () => {
  const [revenue, setRevenue] = useState([]);
  const [topCustomers, setTopCustomers] = useState([]);
  const [categories, setCategories] = useState([]);
  const [regions, setRegions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [revRes, custRes, catRes, regRes] = await Promise.all([
          fetch(`${API_BASE}/revenue`),
          fetch(`${API_BASE}/top-customers`),
          fetch(`${API_BASE}/categories`),
          fetch(`${API_BASE}/regions`)
        ]);

        if (!revRes.ok || !custRes.ok || !catRes.ok || !regRes.ok) {
          throw new Error("One or more API requests failed.");
        }

        setRevenue(await revRes.json());
        setTopCustomers(await custRes.json());
        setCategories(await catRes.json());
        setRegions(await regRes.json());
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const filteredRevenue = revenue.filter(item => {
    const date = item.order_year_month;
    if (startDate && date < startDate) return false;
    if (endDate && date > endDate) return false;
    return true;
  });

  const filteredCustomers = topCustomers.filter(c => 
    c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.region.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) return <div className="loading">Loading dashboard data...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="dashboard">
      <header className="header">
        <h1>Business Insights Dashboard</h1>
        <p style={{color: 'var(--text-muted)'}}>Data-driven performance overview</p>
      </header>

      <div className="grid">
        {/* Revenue Trend */}
        <div className="card" style={{gridColumn: '1 / -1'}}>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem'}}>
            <h2 style={{margin: 0}}>Revenue Trend</h2>
            <div style={{display: 'flex', gap: '0.5rem', alignItems: 'center'}}>
              <span style={{fontSize: '0.875rem', color: '#94a3b8'}}>Range:</span>
              <input 
                type="month" 
                className="search-box" 
                style={{width: 'auto', padding: '0.25rem 0.5rem'}}
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
              <span style={{color: '#94a3b8'}}>-</span>
              <input 
                type="month" 
                className="search-box" 
                style={{width: 'auto', padding: '0.25rem 0.5rem'}}
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
              {(startDate || endDate) && (
                <button 
                  onClick={() => {setStartDate(''); setEndDate('');}}
                  style={{background: 'transparent', border: 'none', color: '#6366f1', cursor: 'pointer', fontSize: '0.875rem'}}
                >
                  Clear
                </button>
              )}
            </div>
          </div>
          <div style={{height: 300}}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={filteredRevenue}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="order_year_month" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip 
                  contentStyle={{backgroundColor: '#1e293b', border: '1px solid #334155'}}
                  itemStyle={{color: '#6366f1'}}
                />
                <Line type="monotone" dataKey="total_revenue" stroke="#6366f1" strokeWidth={3} dot={{r: 6}} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Performance */}
        <div className="card">
          <h2>Category Performance</h2>
          <div style={{height: 300}}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categories}>
                <XAxis dataKey="category" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip 
                   contentStyle={{backgroundColor: '#1e293b', border: '1px solid #334155'}}
                />
                <Bar dataKey="total_revenue" fill="#9333ea" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Regional KPIs */}
        <div className="card">
          <h2>Region Summary</h2>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Region</th>
                  <th>Revenue</th>
                  <th>Customers</th>
                </tr>
              </thead>
              <tbody>
                {regions.map(r => (
                  <tr key={r.region}>
                    <td>{r.region}</td>
                    <td>${r.total_revenue.toLocaleString()}</td>
                    <td>{r.number_of_customers}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Top Customers */}
        <div className="card" style={{gridColumn: '1 / -1'}}>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem'}}>
            <h2 style={{margin: 0}}>Top 10 Customers</h2>
            <div style={{position: 'relative', width: '300px'}}>
              <Search style={{position: 'absolute', left: 10, top: 10, color: '#94a3b8'}} size={18} />
              <input 
                type="text" 
                placeholder="Search name or region..." 
                className="search-box"
                style={{paddingLeft: '2.5rem'}}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Region</th>
                  <th>Total Spend</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredCustomers.map(c => (
                  <tr key={c.customer_id}>
                    <td>{c.name}</td>
                    <td>{c.region}</td>
                    <td>${c.total_spend.toLocaleString()}</td>
                    <td>
                      {c.churned ? <span className="churned-tag">Churned</span> : <span style={{color: '#10b981'}}>Active</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
