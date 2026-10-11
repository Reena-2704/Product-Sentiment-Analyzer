import { useMemo, useState } from "react";
import axios from "axios";
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid
} from "recharts";

const API = "http://127.0.0.1:5000";
const SENTIMENT_COLORS = { Positive: "#22c55e", Neutral: "#3b82f6", Negative: "#ef4444" };

function App() {
  const [url, setUrl] = useState("");
  const [product, setProduct] = useState("");
  const [reviews, setReviews] = useState([]);
  const [history, setHistory] = useState([]);
  const [words, setWords] = useState([]);
  const [status, setStatus] = useState("Paste a product/review page link to begin.");
  const [loading, setLoading] = useState(false);

  const refreshAnalytics = async () => {
    try {
      const [h, w] = await Promise.all([axios.get(`${API}/api/history`), axios.get(`${API}/api/word-frequency`)]);
      setHistory(h.data || []);
      setWords(w.data || []);
    } catch { /* analytics remain empty if the API is unavailable */ }
  };

  const analyzeFromLink = async () => {
    if (!url.trim()) { setStatus("Please paste a product link."); return; }
    setLoading(true); setStatus("Opening the product page and collecting reviews...");
    try {
      const { data } = await axios.post(`${API}/api/scrape`, { url: url.trim() });
      setProduct(data.product || "Unknown Product");
      setReviews(data.reviews || []);
      setStatus(`${data.total || 0} reviews collected and analyzed.`);
      await refreshAnalytics();
    } catch (error) {
      setStatus(error?.response?.data?.details || error?.response?.data?.error || "Could not connect to the backend.");
      setReviews([]);
    } finally { setLoading(false); }
  };

  const loadDemo = async () => {
    setLoading(true); setStatus("Loading demo data...");
    try {
      const { data } = await axios.get(`${API}/api/demo`);
      setProduct(data[0]?.product || "Demo Product"); setReviews(data);
      setStatus("Demo reviews loaded. Use a real URL to build stored history.");
      await refreshAnalytics();
    } catch { setStatus("Start the Flask backend on port 5000."); }
    finally { setLoading(false); }
  };

  const counts = useMemo(() => ({
    Positive: reviews.filter(r => r.sentiment === "Positive").length,
    Neutral: reviews.filter(r => r.sentiment === "Neutral").length,
    Negative: reviews.filter(r => r.sentiment === "Negative").length
  }), [reviews]);
  const total = reviews.length;
  const percentage = value => total ? `${Math.round((value / total) * 100)}%` : "0%";
  const pieData = ["Positive", "Neutral", "Negative"].map(name => ({ name, value: counts[name] }));
  const barData = ["Positive", "Neutral", "Negative"].map(name => ({ name, count: counts[name] }));

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <img src="/sentiment-logo.png" alt="Product Sentiment Analyzer logo" className="brand-logo" />
          <div>
            <h1>Product Sentiment Analyzer</h1>
            <p>Paste a product link and automatically analyze its available customer reviews.</p>
          </div>
        </div>
        <a className="export" href={`${API}/api/export`} target="_blank" rel="noreferrer">Export CSV</a>
      </header>
      <main>
        <section className="search-card">
          <label>Product / Review Page Link</label>
          <div className="search-row"><input value={url} onChange={e => setUrl(e.target.value)} onKeyDown={e => e.key === "Enter" && analyzeFromLink()} placeholder="https://example.com/product/..." /><button className="primary" onClick={analyzeFromLink} disabled={loading}>{loading ? "Fetching..." : "Fetch & Analyze"}</button></div>
          <div className="helper">Product name and reviews are detected automatically from the page.</div>
          <div className="demo-row"><button onClick={loadDemo} disabled={loading}>Try Demo Data</button><span className="status">{status}</span></div>
        </section>

        {product && <section className="product-banner"><span>Detected Product</span><strong>{product}</strong></section>}

        <section className="cards">
          <Stat title="Total Reviews" value={total} />
          <Stat title="Positive" value={counts.Positive} sub={percentage(counts.Positive)} tone="positive" />
          <Stat title="Neutral" value={counts.Neutral} sub={percentage(counts.Neutral)} tone="neutral" />
          <Stat title="Negative" value={counts.Negative} sub={percentage(counts.Negative)} tone="negative" />
        </section>

        <section className="grid">
          <div className="panel"><h2>Sentiment Distribution</h2><div className="chart"><ResponsiveContainer width="100%" height={300}><PieChart><Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>{pieData.map((entry,index)=><Cell key={index} fill={SENTIMENT_COLORS[entry.name]} />)}</Pie><Tooltip /><Legend /></PieChart></ResponsiveContainer></div></div>
          <div className="panel"><h2>Sentiment Overview</h2><div className="chart"><ResponsiveContainer width="100%" height={300}><BarChart data={barData}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis allowDecimals={false} /><Tooltip /><Bar dataKey="count" name="Reviews">{barData.map((entry,index)=><Cell key={index} fill={SENTIMENT_COLORS[entry.name]} />)}</Bar></BarChart></ResponsiveContainer></div></div>
        </section>

        <section className="grid">
          <div className="panel"><h2>Sentiment Trends Over Time</h2><p className="panel-subtitle">Historical review counts grouped by collection date.</p><div className="chart"><ResponsiveContainer width="100%" height={300}><LineChart data={history}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="date" /><YAxis allowDecimals={false} /><Tooltip /><Legend /><Line type="monotone" dataKey="Positive" stroke={SENTIMENT_COLORS.Positive} strokeWidth={3} /><Line type="monotone" dataKey="Neutral" stroke={SENTIMENT_COLORS.Neutral} strokeWidth={3} /><Line type="monotone" dataKey="Negative" stroke={SENTIMENT_COLORS.Negative} strokeWidth={3} /></LineChart></ResponsiveContainer></div></div>
          <div className="panel"><h2>Word Frequency</h2><p className="panel-subtitle">Most frequent meaningful words found in stored reviews.</p><div className="chart"><ResponsiveContainer width="100%" height={300}><BarChart data={words} layout="vertical" margin={{left:20,right:20}}><CartesianGrid strokeDasharray="3 3" /><XAxis type="number" allowDecimals={false} /><YAxis type="category" dataKey="word" width={90} /><Tooltip /><Bar dataKey="count" name="Occurrences" fill="#64748b" /></BarChart></ResponsiveContainer></div></div>
        </section>

        <section className="panel"><div className="panel-heading"><div><h2>Review Analysis</h2><p>Every collected review is classified using TextBlob sentiment polarity.</p></div></div>{reviews.length === 0 ? <div className="empty">Paste a product link above to collect and analyze reviews.</div> : <div className="table-wrap"><table><thead><tr><th>Review</th><th>Rating</th><th>Sentiment</th><th>Polarity</th><th>Collected</th></tr></thead><tbody>{reviews.map((r,i)=><tr key={i}><td>{r.review}</td><td>{r.rating || "—"}</td><td><span className={`badge ${r.sentiment.toLowerCase()}`}>{r.sentiment}</span></td><td>{r.polarity}</td><td>{r.created_at ? new Date(r.created_at).toLocaleString() : "—"}</td></tr>)}</tbody></table></div>}</section>

        <section className="info"><strong>Project pipeline:</strong><span>Product Link</span><b>→</b><span>Selenium + BeautifulSoup</span><b>→</b><span>Reviews</span><b>→</b><span>TextBlob NLP</span><b>→</b><span>MongoDB / Local Storage</span><b>→</b><span>React Analytics</span></section>
        <section className="notice"><strong>Important:</strong> Review scraping depends on the website. Some websites require login, use dynamic content, or block automated access. The project handles common review HTML patterns, but a site-specific selector may be needed for some pages.</section>
      </main>
      <footer>Product Sentiment Analyzer and Review Dashboard</footer>
    </div>
  );
}

function Stat({title,value,sub,tone}) { return <div className={`stat ${tone || ""}`}><span>{title}</span><strong>{value}</strong>{sub && <small>{sub}</small>}</div>; }
export default App;
