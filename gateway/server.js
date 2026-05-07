const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors()); // Allows the Vite React app to communicate with this server
app.use(express.json());

// ==========================================
// ROUTE: TASK A (User Modeling Agent)
// ==========================================
app.post('/api/simulate', async (req, res) => {
    const { userContext, businessContext } = req.body;
    console.log(`[Gateway] Routing Task A simulation request to AI service...`);

    try {
        const aiResponse = await axios.post('http://127.0.0.1:8000/api/task-a/generate', {
            user_id: "demo_user",
            business_id: "demo_business",
            user_context: userContext,
            business_context: businessContext
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
        const aiResponse = await axios.post('http://127.0.0.1:8000/api/task-b/recommend', {
            user_id: "demo_user",
            user_context: userContext
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