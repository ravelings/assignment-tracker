/**
 * Score Management API Client
 * JavaScript functions to interact with the score management backend
 * Include this file in your HTML templates to use the score API
 */

class ScoreAPI {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
    }

    /**
     * Get all scores for the current user
     * @returns {Promise<Array>} Array of score objects
     */
    async getAllScores() {
        try {
            const response = await fetch(`${this.baseUrl}/api/scores/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.scores || [];
        } catch (error) {
            console.error('Error fetching all scores:', error);
            throw error;
        }
    }

    /**
     * Get score for a specific assignment
     * @param {number} assignmentId - The assignment ID
     * @returns {Promise<number|null>} The score or null
     */
    async getScore(assignmentId) {
        try {
            const response = await fetch(`${this.baseUrl}/api/scores/${assignmentId}/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                if (response.status === 404) {
                    return null;
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.score;
        } catch (error) {
            console.error(`Error fetching score for assignment ${assignmentId}:`, error);
            throw error;
        }
    }

    /**
     * Update score for a specific assignment
     * @param {number} assignmentId - The assignment ID
     * @param {number} score - The score to set
     * @returns {Promise<Object>} Response object
     */
    async updateScore(assignmentId, score) {
        try {
            const response = await fetch(`${this.baseUrl}/api/scores/${assignmentId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ score: score }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error(`Error updating score for assignment ${assignmentId}:`, error);
            throw error;
        }
    }

    /**
     * Calculate percentage for an assignment
     * @param {number|null} score - The achieved score
     * @param {number|null} pointsPossible - The maximum points
     * @returns {number|null} Percentage or null if calculation not possible
     */
    calculatePercentage(score, pointsPossible) {
        if (score === null || pointsPossible === null || pointsPossible === 0) {
            return null;
        }
        return (score / pointsPossible) * 100;
    }

    /**
     * Get letter grade from percentage
     * @param {number} percentage - The percentage score
     * @returns {string} Letter grade
     */
    getLetterGrade(percentage) {
        if (percentage >= 90) return 'A';
        if (percentage >= 80) return 'B';
        if (percentage >= 70) return 'C';
        if (percentage >= 60) return 'D';
        return 'F';
    }
}

// Example usage in your HTML:
/*
<script src="{{ url_for('static', filename='scoreAPI.js') }}"></script>
<script>
    const scoreAPI = new ScoreAPI();
    
    // Get all scores
    async function loadScores() {
        const scores = await scoreAPI.getAllScores();
        console.log('All scores:', scores);
        
        scores.forEach(assignment => {
            const percentage = scoreAPI.calculatePercentage(
                assignment.score, 
                assignment.points_possible
            );
            
            if (percentage !== null) {
                const grade = scoreAPI.getLetterGrade(percentage);
                console.log(`${assignment.title}: ${percentage.toFixed(1)}% (${grade})`);
            }
        });
    }
    
    // Update a score
    async function saveScore(assignmentId, score) {
        try {
            const result = await scoreAPI.updateScore(assignmentId, score);
            console.log('Score updated:', result);
            alert('Score saved successfully!');
        } catch (error) {
            console.error('Failed to save score:', error);
            alert('Failed to save score. Please try again.');
        }
    }
    
    // Add inline score editing to your table
    function addScoreInput(assignmentId, currentScore) {
        return `
            <input 
                type="number" 
                value="${currentScore || ''}" 
                placeholder="Enter score"
                step="0.01"
                min="0"
                class="score-input"
                data-assignment-id="${assignmentId}"
                onchange="saveScore(${assignmentId}, this.value)"
            />
        `;
    }
</script>
*/

// Make it available globally
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ScoreAPI;
}
