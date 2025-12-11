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

/* Create an input section */
function createRow(id, name) { /*2 Entries a row above 1400px*/
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

/* Create an input section for each feature column*/
function buildUI() {
    const container = document.getElementById("parameter-container");
    for(let i = 0; i < FEATURE_COLS.length; i++) {

        const col = FEATURE_COLS[i];
        const name = NAMES[i]

        container.insertAdjacentHTML("beforeend", createRow(col, name));

        const slider = document.getElementById(`weight-${col}`);
        const box = document.getElementById(`weight-${col}-num`);

        /*Sync box and slider values*/
        slider.addEventListener("input", () => box.value = slider.value);
        box.addEventListener("input", () => slider.value = box.value);

    }
}

document.addEventListener("DOMContentLoaded", buildUI);