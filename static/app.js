const FEATURE_COLS = [
    "bpm", "difficultyrating", "diff_aim", "diff_speed", "diff_size",
    "diff_overall", "diff_approach", "diff_drain", "hit_length",
    "total_length", "rating", "playcount", "passcount",
    "count_normal", "count_slider", "count_spinner", "max_combo"
];

const NAMES = [
    "BPM", "Difficulty Rating", "Aim Difficulty", "Speed Difficulty", "Diff size",
    "OD", "AR", "Diff drain", "Hit Length",
    "Total Length", "Rating", "Playcount", "Passcount",
    "Circle Count", "Slider Count", "Spinner Count", "Max Combo"
];

URL = "http://localhost:8000"

/* Create an input section. */
function createRow(id, name) { /* 2 Entries a row above 1400px. */
    return `
        <div class="col-12 col-xxl-6">
            <div class="param-row">
                <div class="param-name">${name}</div>

                <input type="number" id="stat-${id}" class="form-control value-box" step="0.01">

                <input type="range" id="weight-${id}" class="form-range weight-slider"
                    min="0" max="1" step="0.01" value="0">

                <input type="number" id="weight-${id}-num"
                    class="form-control weight-number" min="0" max="1" step="0.01" value="0">
            </div>
        </div>
    `;
}

/* Create an input section for each feature column. */
function buildUI() {
    const container = document.getElementById("parameter-container");
    for(let i = 0; i < FEATURE_COLS.length; i++) {

        const col = FEATURE_COLS[i];
        const name = NAMES[i]

        container.insertAdjacentHTML("beforeend", createRow(col, name));

        const slider = document.getElementById(`weight-${col}`);
        const box = document.getElementById(`weight-${col}-num`);

        /*Sync box and slider values. */
        slider.addEventListener("input", () => box.value = slider.value);
        box.addEventListener("input", () => slider.value = box.value);

    }
}

function loadBeatmapStats() {
    /* When the user presses the load button, run the function below to load values from backend. */
    document.getElementById("load-btn").addEventListener("click", async (e) => {

        /* Get the users value which should equate to a beatmap ID. */
        const beatmapID = document.getElementById("load-map-id").value;

        if (!beatmapID) return;

        try {
            const result = await fetch(`${URL}/map/${beatmapID}`);
            if (!result.ok) {
                throw new Error("Beatmap not found.")
            }
            const data = await result.json();
            console.log(data)

            FEATURE_COLS.forEach(col => {
                const stat = document.getElementById(`stat-${col}`);
                if (stat) stat.value = data[col] ?? 0;
            });
            
        } catch (error) {
            console.error(error);
            alert("Error fetching beatmap data.");
        }
    });
}

function loadOutputMaps() {
    document.getElementById("submit-btn").addEventListener("click", async (e) => {

        /* Close settings panel */
        document.querySelector("details").open = false;

        /* Collect stats */
        const stats = {};
        for (const col of FEATURE_COLS) {
            const element = document.getElementById(`stat-${col}`);
            stats[col] = parseFloat(element.value) || 0;
        }

        /* Collect weights */
        const weights = {};
        for (const col of FEATURE_COLS) {
            const element = document.getElementById(`weight-${col}`);
            weights[col] = parseFloat(element.value) || 0;
        }

        /* Beatmap id depriciated to be removed when I get round to optimising backend function. */
        /* Top n to be changable by the user eventually. */
        const payload = {
            beatmap_id: null,
            stats: stats,
            weights: weights,
            top_n: 10
        };

        /* Send request and receive response. */
        try {
            const response = await fetch(`${URL}/similarity`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            if(!response.ok) {
                throw new Error("Request failed.")
            }

            const data = await response.json();

            renderBeatmapResults(data);

        } catch (error) {
            console.error(error);
            alert("Error fetching beatmap data. Make sure you are searching for a valid beatmap id.");
        }
    });
}

function renderBeatmapResults(results) {
    const container = document.getElementById("results-container")
    container.innerHTML = ""; /* Reset container contents */

    results.forEach(map => {
        const {
            beatmap_id,
            title,
            artist,
            similarity,
            bpm,
            difficultyrating,
            diff_aim,
            diff_speed,
        } = map;

        const statsHTML = Object.entries(map)
            .filter(([key, value]) => FEATURE_COLS.includes(key))
            .map(([key, value]) => `<span><strong>${key.replace(/_/g, " ")}:</strong> ${value}</span>`)
            .join("");

        const cardHTML = `
            <a href="https://osu.ppy.sh/beatmapsets/${beatmap_id}" 
                target="_blank" 
                style="text-decoration: none; color: inherit;">
            
                <div class="result-card">

                    <div class="result-thumb"></div>

                    <div class="result-info">
                        <div class="result-title">${title || "Unknown Title"}</div>
                        
                        <div class="result-stats">
                            ${statsHTML}
                        </div>

                        <div class="text-muted mt-1">
                            Similarity: ${(similarity * 100).toFixed(1)}%
                        </div>
                    </div>

                </div>
            </a>
        `;

        container.insertAdjacentHTML("beforeend", cardHTML)

    });
};

/* Run these functions after DOMContentLoaded event. */
document.addEventListener("DOMContentLoaded", async (e) => {
    buildUI();
    loadBeatmapStats();
    loadOutputMaps();
});
