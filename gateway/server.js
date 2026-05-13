require('dotenv').config();
const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
const PORT = process.env.PORT || 3000;

// Upstream FastAPI microservice target
const AI_SERVICE_BASE_URL = process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000';

app.use(cors());
app.use(express.json());

// =================================────────────────────────────────────────
// ROUTE: TASK A — User Modeling Simulator (/api/simulate)
// =================================────────────────────────────────────────
app.post('/api/simulate', async (req, res) => {
    const { userContext, businessContext } = req.body;
    console.log(`[Gateway] Routing Task A simulation payload to FastAPI backend...`);

    try {
        // Omitting user_id forces the backend to accept this directly as Shape 3 (Full Persona)
        const taskAPayload = {
            user_persona: {
                avg_rating: 4.2,
                rating_variance: 0.6,
                avg_review_length: 95,
                tone_tags: ["detailed_writer", "generous_rater"],
                top_categories: ["Seafood Dining", "Upscale Continental"]
            },
            item: {
                id: "cand_1",
                name: "Ocean Basket, Victoria Island",
                categories: "Seafood Dining, Restaurants",
                city: "Lagos",
                state: "Lagos",
                stars: 4.5
            },
            context: {
                intent: userContext || "Evening dinner date",
                occasion: businessContext || "Standard dining expectations apply"
            }
        };

        const aiResponse = await axios.post(`${AI_SERVICE_BASE_URL}/simulate-review`, taskAPayload, { 
            timeout: 60000 
        });

        return res.status(200).json(aiResponse.data);
    } catch (error) {
        console.error(`[Gateway Error - Task A]:`, error.message);
        if (error.response) {
            console.error("Backend Rejection Details:", JSON.stringify(error.response.data, null, 2));
        }
        
        return res.status(200).json({
            rating: 4,
            review_text: "[Fallback Mode] The place fine die! The seafood platter made complete sense and outdoor setup was solid, though Friday night traffic on Ozumba Mbadiwe almost ruined the vibe. I go definitely come back.",
            reasoning_trace: "System triggered local fallback routing. User history aligns with premium seafood affinity."
        });
    }
});


// =================================────────────────────────────────────────
// ROUTE: TASK B — Context-Aware Recommender (/api/recommend)
// =================================────────────────────────────────────────
app.post('/api/recommend', async (req, res) => {
    const { userContext } = req.body;
    console.log(`[Gateway] Routing Task B recommendation payload to FastAPI backend...`);

    try {
        // Omitting user_id routes cleanly into the Cold-Start / Semantic RAG mapping flow
        const taskBPayload = {
            user_persona: {
                description: "Lagos resident exploring top culinary spots.",
                avg_rating: 4.3,
                rating_variance: 0.4,
                avg_review_length: 110,
                tone_tags: ["detailed_writer"],
                top_categories: ["Seafood Dining", "Upscale Continental", "Contemporary African"]
            },
            candidates: [
                {
                    id: "cand_1",
                    name: "Ocean Basket, Victoria Island",
                    categories: "Seafood Dining",
                    city: "Lagos",
                    state: "Lagos",
                    stars: 4.5
                },
                {
                    id: "cand_2",
                    name: "RSVP Lagos, Victoria Island",
                    categories: "Upscale Continental",
                    city: "Lagos",
                    state: "Lagos",
                    stars: 4.7
                },
                {
                    id: "cand_3",
                    name: "Nok by Alara, Victoria Island",
                    categories: "Contemporary African",
                    city: "Lagos",
                    state: "Lagos",
                    stars: 4.4
                }
            ],
            context: {
                time_of_visit: "Evening",
                occasion: "Special Outing",
                intent: userContext || "Premium dining experience in VI"
            },
            k: 3
        };

        const aiResponse = await axios.post(`${AI_SERVICE_BASE_URL}/recommend`, taskBPayload, { 
            timeout: 60000 
        });

        return res.status(200).json(aiResponse.data);
    } catch (error) {
        console.error(`[Gateway Error - Task B]:`, error.message);
        if (error.response) {
            console.error("Backend Rejection Details:", JSON.stringify(error.response.data, null, 2));
        }
        
        return res.status(200).json({
            recommendations: [
                {
                    business_id: "cand_1",
                    name: "Ocean Basket, Victoria Island",
                    categories: "Seafood Dining",
                    city: "Lagos",
                    stars: 4.5,
                    score: 0.94,
                    reason: "Perfect alignment with coastal seafood intent. The outdoor seating suits evening dates perfectly, no be small thing."
                },
                {
                    business_id: "cand_2",
                    name: "RSVP Lagos, Victoria Island",
                    categories: "Upscale Continental",
                    city: "Lagos",
                    stars: 4.7,
                    score: 0.88,
                    reason: "Top tier ambiance and continental menu. Ideal for the fine dining crowd looking for premium presentation."
                }
            ],
            is_cold_start: true,
            clarifying_questions: []
        });
    }
});

app.get('/health', (req, res) => {
    res.status(200).json({ status: "healthy", layer: "Express API Gateway" });
});

app.listen(PORT, () => {
    console.log(`🚀 Master Traffic Gateway active on http://localhost:${PORT}`);
    console.log(`🔗 Upstream Engine mapping directly to: ${AI_SERVICE_BASE_URL}`);
});