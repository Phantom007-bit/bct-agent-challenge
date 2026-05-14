const express = require('express');
const cors = require('cors');
const axios = require('axios');
const path = require('path'); // <-- ADDED 1: Needed to find your HTML files

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors()); // Allows the Vite React app to communicate with this server
app.use(express.json());

// ==========================================
// --- ADDED 2: SERVE YOUR HTML UI PAGES ---
// ==========================================
// This tells Node to look in the parent folder for your HTML files
app.use(express.static(path.join(__dirname, '../')));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../index.html'));
});

app.get('/login', (req, res) => {
    res.sendFile(path.join(__dirname, '../login.html'));
});

// ==========================================
// ROUTE: TASK A (User Modeling Agent)
// ==========================================
app.post('/api/simulate', async (req, res) => {
    const { userContext, businessContext } = req.body;
    console.log(`[Gateway] Routing Task A simulation request to AI service...`);

    try {
        // <-- ADDED 3: Updated URL to match your actual Python FastAPI route
       const aiResponse = await axios.post('http://127.0.0.1:8000/simulate-review', {
    user_persona: {
        description: userContext
    },
    item: {
        name: businessContext,
        categories: "Restaurant",
        city: "Lagos"
    }
});

        res.json(aiResponse.data);
    } catch (error) {
        console.error(`[Gateway Error - Task A] AI Service unreachable:`, error.message);
        // Fallback data
        res.status(200).json({
            rating: 3.5,
            review_text: "[FALLBACK - AI SERVER OFFLINE] The atmosphere was decent, but the waiting time was something else! I'd probably go back on a less busy day."
        });
    }
});

// ==========================================
// ROUTE: TASK B (Recommendation Agent)
// ==========================================
app.post('/api/recommend', async (req, res) => {
    const { userContext } = req.body;
    console.log(`[Gateway] Routing Task B recommendation request to AI service...`);

    try {
        // <-- ADDED 3: Updated URL to match your actual Python FastAPI route
        const aiResponse = await axios.post('http://127.0.0.1:8000/recommend', {
    user_persona: {
        description: userContext
    },
    context: {
        intent: userContext
    },
    k: 5
});
        res.json(aiResponse.data);
    } catch (error) {
        console.error(`[Gateway Error - Task B] AI Service unreachable:`, error.message);
        // Fallback data demonstrating agentic Chain-of-Thought
        res.status(200).json([
            {
              rank: 1,
              item: "Ocean Basket, Victoria Island",
              category: "Seafood Dining",
              reasoning: "[FALLBACK - AI OFFLINE] User requested a premium first-date spot with seafood. This location minimizes cold-start risk based on premium coastal metrics."
            },
            {
              rank: 2,
              item: "RSVP Lagos, Victoria Island",
              category: "Upscale Continental",
              reasoning: "[FALLBACK - AI OFFLINE] Alternative cross-domain recommendation. Poolside aesthetic matches the 'first-date' ambiance requested."
            },
            {
              rank: 3,
              item: "Nok by Alara, Victoria Island",
              category: "Contemporary African",
              reasoning: "[FALLBACK - AI OFFLINE] Included as a localized wildcard to test conversational retrieval."
            }
        ]);
    }
});

app.listen(PORT, () => {
    console.log(`🚀 Gateway routing server running on http://localhost:${PORT}`);
});