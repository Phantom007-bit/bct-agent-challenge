import { useState } from 'react';

function App() {
  const [activeTab, setActiveTab] = useState('taskA'); // 'taskA' or 'taskB'
  
  // --- TASK A STATE ---
  const [userContextA, setUserContextA] = useState('');
  const [businessContextA, setBusinessContextA] = useState('');
  const [loadingA, setLoadingA] = useState(false);
  const [resultA, setResultA] = useState(null);

  // --- TASK B STATE ---
  const [userContextB, setUserContextB] = useState('');
  const [loadingB, setLoadingB] = useState(false);
  const [resultB, setResultB] = useState(null);

  // --- HANDLERS ---
  const handleSimulateTaskA = async (e) => {
    e.preventDefault();
    setLoadingA(true);
    setResultA(null);
    try {
      const response = await fetch('http://localhost:3000/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userContext: userContextA, businessContext: businessContextA }),
      });
      const data = await response.json();
      setResultA(data); 
    } catch (error) {
      console.error("Gateway error:", error);
      alert("Error: Gateway server is offline. Ensure 'node server.js' is running.");
    } finally {
      setLoadingA(false);
    }
  };

  const handleSimulateTaskB = async (e) => {
    e.preventDefault();
    setLoadingB(true);
    setResultB(null);
    try {
      const response = await fetch('http://localhost:3000/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userContext: userContextB }),
      });
      const data = await response.json();
      setResultB(data); 
    } catch (error) {
      console.error("Gateway error:", error);
      alert("Error: Gateway server is offline. Ensure 'node server.js' is running.");
    } finally {
      setLoadingB(false);
    }
  };

  // Helper to normalize Task B payloads safely (Handles native objects vs fallback arrays)
  const getNormalizedRecommendations = (res) => {
    if (!res) return [];
    
    // Case 1: Native backend object schema ({ recommendations: [...] })
    if (res.recommendations && Array.isArray(res.recommendations)) {
      return res.recommendations.map((x, idx) => ({
        rank: idx + 1,
        name: x.name || 'Unknown Candidate',
        category: x.categories || 'Dining',
        reason: x.reason || 'No cultural reasoning provided.',
        stars: x.stars || null,
        score: x.score || null
      }));
    }
    
    // Case 2: Direct array payload (Legacy gateway fallback format)
    if (Array.isArray(res)) {
      return res.map((x, idx) => ({
        rank: x.rank || idx + 1,
        name: x.item || x.name || 'Unknown Candidate',
        category: x.category || x.categories || 'Dining',
        reason: x.reasoning || x.reason || 'No cultural reasoning provided.',
        stars: x.stars || null,
        score: x.score || null
      }));
    }
    return [];
  };

  const normalizedRecommendations = getNormalizedRecommendations(resultB);

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      
      {/* Top Navigation Bar */}
      <nav className="bg-blue-900 text-white shadow-md">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex space-x-8">
            <div className="py-4 font-bold text-xl tracking-wide border-r border-blue-800 pr-8">
              BCT x DSN Agent
            </div>
            <button 
              onClick={() => setActiveTab('taskA')}
              className={`py-4 px-2 font-semibold transition-colors border-b-4 ${activeTab === 'taskA' ? 'border-blue-400 text-blue-100' : 'border-transparent text-blue-300 hover:text-white'}`}
            >
              Task A: User Modeling
            </button>
            <button 
              onClick={() => setActiveTab('taskB')}
              className={`py-4 px-2 font-semibold transition-colors border-b-4 ${activeTab === 'taskB' ? 'border-blue-400 text-blue-100' : 'border-transparent text-blue-300 hover:text-white'}`}
            >
              Task B: Recommendation
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto p-8">
        
        {/* ========================================== */}
        {/* TASK A VIEW                                */}
        {/* ========================================== */}
        {activeTab === 'taskA' && (
          <div className="animate-fade-in">
            <header className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900">Task A: User Modeling Agent</h1>
              <p className="text-gray-600 mt-2">Simulating localized Nigerian user reviews and behavioral star ratings.</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* INPUT FORM */}
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h2 className="text-xl font-semibold mb-4 text-gray-800">Agent Inputs</h2>
                <form onSubmit={handleSimulateTaskA} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">User Persona</label>
                    <textarea 
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm"
                      rows="4" 
                      placeholder="e.g., An upscale generous rater who loves detailed write-ups..."
                      value={userContextA} 
                      onChange={(e) => setUserContextA(e.target.value)} 
                      required
                    ></textarea>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Business Context</label>
                    <textarea 
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm"
                      rows="4" 
                      placeholder="e.g., Premium coastal dining environment on Victoria Island..."
                      value={businessContextA} 
                      onChange={(e) => setBusinessContextA(e.target.value)} 
                      required
                    ></textarea>
                  </div>
                  <button 
                    type="submit" 
                    disabled={loadingA} 
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors disabled:bg-blue-400"
                  >
                    {loadingA ? 'Executing Graph Nodes...' : 'Run Agent Simulation'}
                  </button>
                </form>
              </div>

              {/* OUTPUT DISPLAY */}
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 flex flex-col justify-between">
                <div>
                  <h2 className="text-xl font-semibold mb-4 text-gray-800">Agent Output</h2>
                  {resultA ? (
                    <div className="space-y-5">
                      <div className="bg-blue-50 p-5 rounded-lg border border-blue-100 text-center">
                        <p className="text-xs text-blue-600 uppercase tracking-wide font-bold mb-1">Simulated Rating Output</p>
                        <p className="text-4xl font-extrabold text-blue-900">{resultA.rating} / 5.0</p>
                        <div className="text-amber-500 text-xl mt-1">
                          {'★'.repeat(resultA.rating)}
                          <span className="text-gray-300">{'★'.repeat(5 - resultA.rating)}</span>
                        </div>
                      </div>

                      <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                        <p className="text-xs text-gray-500 uppercase tracking-wide font-bold mb-1">Simulated Cultural Review</p>
                        <p className="text-gray-800 text-sm italic bg-white p-3 border rounded shadow-2xs">
                          "{resultA.review_text || resultA.review}"
                        </p>
                      </div>

                      {resultA.reasoning_trace && (
                        <div className="bg-amber-50/50 p-3 rounded-lg border border-amber-100/50">
                          <p className="text-xs text-amber-800 uppercase tracking-wide font-bold mb-1">Chain-of-Thought Trace</p>
                          <p className="text-xs text-gray-600 font-mono leading-relaxed">
                            {resultA.reasoning_trace}
                          </p>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="h-64 flex items-center justify-center text-gray-400 border-2 border-dashed border-gray-200 rounded-lg p-6 text-center text-sm">
                      {loadingA ? 'Evaluating state graph logic...' : 'Enter scenario parameters to evaluate behavioral output.'}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ========================================== */}
        {/* TASK B VIEW                                */}
        {/* ========================================== */}
        {activeTab === 'taskB' && (
          <div className="animate-fade-in">
            <header className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900">Task B: Contextual Recommendation</h1>
              <p className="text-gray-600 mt-2">Agentic workflow reasoning targeting cold-start states and localized ranking criteria.</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              {/* INPUT FORM */}
              <div className="lg:col-span-4 bg-white p-6 rounded-xl shadow-sm border border-gray-200 h-fit">
                <h2 className="text-xl font-semibold mb-4 text-gray-800">Contextual Intent</h2>
                <form onSubmit={handleSimulateTaskB} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">User Intent & Environment</label>
                    <textarea 
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm"
                      rows="6" 
                      placeholder="e.g., Looking for a premium outdoor seafood spot in VI suitable for an anniversary date..."
                      value={userContextB} 
                      onChange={(e) => setUserContextB(e.target.value)} 
                      required
                    ></textarea>
                  </div>
                  <button 
                    type="submit" 
                    disabled={loadingB} 
                    className="w-full bg-blue-900 hover:bg-blue-800 text-white font-semibold py-3 px-4 rounded-lg transition-colors disabled:bg-blue-400"
                  >
                    {loadingB ? 'Retrieving Vector Indices...' : 'Generate Recommendations'}
                  </button>
                </form>

                {/* Cold start state label if detected natively */}
                {resultB && resultB.is_cold_start !== undefined && (
                  <div className="mt-4 pt-4 border-t flex items-center justify-between text-xs">
                    <span className="text-gray-500 font-medium">Pipeline Router State:</span>
                    <span className={`px-2 py-0.5 rounded font-bold uppercase ${resultB.is_cold_start ? 'bg-cyan-100 text-cyan-800' : 'bg-emerald-100 text-emerald-800'}`}>
                      {resultB.is_cold_start ? 'Cold-Start Route' : 'Established Route'}
                    </span>
                  </div>
                )}
              </div>

              {/* RANKED LIST OUTPUT */}
              <div className="lg:col-span-8 bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h2 className="text-xl font-semibold mb-4 text-gray-800">Ranked Results (NDCG Optimized)</h2>
                {normalizedRecommendations.length > 0 ? (
                  <div className="space-y-4">
                    {normalizedRecommendations.map((item) => (
                      <div key={item.rank} className="p-5 border border-gray-100 rounded-lg bg-gray-50 flex gap-4 transition-all hover:bg-white hover:shadow-xs">
                        <div className="shrink-0 w-11 h-11 bg-blue-100 text-blue-800 font-bold text-lg rounded-full flex items-center justify-center border border-blue-200">
                          #{item.rank}
                        </div>
                        <div className="flex-1">
                          <div className="flex flex-wrap items-baseline justify-between gap-2">
                            <h3 className="text-base font-bold text-gray-900">{item.name}</h3>
                            <div className="flex items-center gap-3 text-xs font-semibold">
                              {item.stars && (
                                <span className="text-amber-600 bg-amber-50 px-2 py-0.5 rounded border border-amber-200/50">
                                  ★ {item.stars.toFixed(1)} Base
                                </span>
                              )}
                              {item.score && (
                                <span className="text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200/50">
                                  Fit: {(item.score * 100).toFixed(0)}%
                                </span>
                              )}
                            </div>
                          </div>
                          
                          <span className="inline-block px-2 py-0.5 bg-gray-200 text-gray-700 text-2xs font-bold uppercase tracking-wider rounded mt-1 mb-2">
                            {item.category}
                          </span>
                          
                          <p className="text-xs text-gray-700 leading-relaxed bg-white p-2.5 border rounded">
                            <strong className="text-gray-900 block text-2xs uppercase text-gray-500 mb-0.5">Cultural Agent Reasoning:</strong> 
                            {item.reason}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="h-64 flex items-center justify-center text-gray-400 border-2 border-dashed border-gray-200 rounded-lg p-6 text-center text-sm">
                    {loadingB ? 'Filtering candidates via semantic LLM routing...' : 'Input user environment vectors to display contextual candidate alignment.'}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

export default App;