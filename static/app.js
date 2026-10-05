// DOM Elements
const driverSelect = document.getElementById('driverSelect');
const circuitSelect = document.getElementById('circuitSelect');
const seasonSelect = document.getElementById('seasonSelect');

let circuitsData = [];

// Format time from ms to M:SS.ms
function formatTime(ms) {
    if (!ms || ms === 0) return "--:--.---";
    const date = new Date(ms);
    const minutes = date.getUTCMinutes();
    const seconds = date.getUTCSeconds().toString().padStart(2, '0');
    const milliseconds = date.getUTCMilliseconds().toString().padStart(3, '0');
    return `${minutes}:${seconds}.${milliseconds}`;
}

// View switching
function switchView(viewName) {
    const teleView = document.getElementById('telemetryView');
    const champView = document.getElementById('championshipView');
    const hofView = document.getElementById('hallOfFameView');
    const teleControls = document.getElementById('telemetryControls');
    const champControls = document.getElementById('champControls');
    const hofControls = document.getElementById('hofControls');
    
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    
    teleView.style.display = 'none';
    champView.style.display = 'none';
    hofView.style.display = 'none';
    teleControls.style.display = 'none';
    champControls.style.display = 'none';
    hofControls.style.display = 'none';
    
    if (viewName === 'telemetry') {
        teleView.style.display = 'grid';
        teleControls.style.display = 'flex';
        document.querySelector('.nav-btn:nth-child(1)').classList.add('active');
        if(circuitsData.length === 0) fetchCircuits();
    } else if (viewName === 'championship') {
        champView.style.display = 'grid';
        champControls.style.display = 'flex';
        document.querySelector('.nav-btn:nth-child(2)').classList.add('active');
        fetchStandings();
        fetchRaces();
    } else if (viewName === 'halloffame') {
        hofView.style.display = 'grid';
        hofControls.style.display = 'flex';
        document.querySelector('.nav-btn:nth-child(3)').classList.add('active');
        fetchHallOfFame();
    }
}

// Modal handling
function openModal() { document.getElementById('resultModal').style.display = 'block'; }
function closeModal() { document.getElementById('resultModal').style.display = 'none'; }

// Chart.js instances
let lapChart = null;
let champChart = null;
function initChart() {
    const ctx = document.getElementById('lapChart').getContext('2d');
    Chart.defaults.color = '#9BA1B0';
    Chart.defaults.font.family = 'Inter';
    lapChart = new Chart(ctx, {
        type: 'line',
        data: { labels: [], datasets: [{ label: 'Lap Time (s)', data: [], borderColor: '#E10600', backgroundColor: 'rgba(225, 6, 0, 0.1)', borderWidth: 2, pointBackgroundColor: '#FCD116', pointRadius: 4, tension: 0.3, fill: true }] },
        options: { responsive: true, maintainAspectRatio: false, scales: { y: { title: { display: true, text: 'Time (Seconds)' }, grid: { color: '#262B38' } }, x: { title: { display: true, text: 'Lap Number' }, grid: { color: '#262B38' } } }, plugins: { legend: { display: false } } }
    });

    const ctxChamp = document.getElementById('champChart').getContext('2d');
    champChart = new Chart(ctxChamp, {
        type: 'line',
        data: { labels: [], datasets: [] },
        options: { responsive: true, maintainAspectRatio: false, scales: { y: { title: { display: true, text: 'Points' }, grid: { color: '#262B38' } }, x: { grid: { color: '#262B38' } } }, plugins: { legend: { position: 'right', labels: { color: '#9BA1B0', font: { family: 'Inter' } } } } }
    });
}

// Global Context
let currentSeasonId = null;

// Seasons
async function initSeasons() {
    try {
        const res = await fetch('/api/seasons');
        const seasons = await res.json();
        seasonSelect.innerHTML = '';
        seasons.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s.id;
            opt.textContent = s.year_label;
            if(s.is_current) opt.selected = true;
            seasonSelect.appendChild(opt);
        });
        currentSeasonId = seasonSelect.value;
        fetchDrivers();
    } catch(e) { console.error(e); }
}

function onSeasonChange() {
    currentSeasonId = seasonSelect.value;
    fetchDrivers();
    fetchStandings();
    fetchRaces();
    fetchProgression();
}

let driversData = [];

async function fetchDrivers() {
    if(!currentSeasonId) return;
    try {
        const res = await fetch(`/drivers/?season_id=${currentSeasonId}`);
        driversData = await res.json();
        
        driverSelect.innerHTML = '<option value="">Select Driver</option>';
        const resDriverId = document.getElementById('resDriverId');
        resDriverId.innerHTML = '';
        
        driversData.forEach(d => {
            const opt1 = document.createElement('option');
            opt1.value = d.id;
            opt1.textContent = `${d.name} (${d.car_number})`;
            driverSelect.appendChild(opt1);
            
            const opt2 = document.createElement('option');
            opt2.value = d.id;
            opt2.textContent = `${d.name} (${d.car_number})`;
            resDriverId.appendChild(opt2);
        });
    } catch (e) { console.error("Failed to fetch drivers", e); }
}

async function fetchRaces() {
    if(!currentSeasonId) return;
    try {
        const res = await fetch(`/api/seasons/${currentSeasonId}/races`);
        const races = await res.json();
        const resRaceId = document.getElementById('resRaceId');
        resRaceId.innerHTML = '';
        
        const tbody = document.querySelector('#raceResultsSummaryTable tbody');
        tbody.innerHTML = '';

        races.forEach(r => {
            const opt = document.createElement('option');
            opt.value = r.id;
            opt.textContent = `R${r.round_number} - ${r.gp_name}`;
            resRaceId.appendChild(opt);

            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${r.round_number}</td><td><strong>${r.gp_name}</strong></td><td>--</td>`;
            tbody.appendChild(tr);
        });
    } catch(e) { console.error(e); }
}

// Circuit & Leaderboard Logic
async function fetchCircuits() {
    try {
        const res = await fetch('/api/circuits');
        circuitsData = await res.json();
        circuitSelect.innerHTML = '<option value="">Select Circuit</option>';
        circuitsData.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c.id;
            opt.textContent = c.name;
            circuitSelect.appendChild(opt);
        });
    } catch (e) { console.error(e); }
}

function onCircuitChange() {
    const cId = parseInt(circuitSelect.value);
    const imgEl = document.getElementById('circuitMapImg');
    const fallbackEl = document.getElementById('circuitMapFallback');
    const statsEl = document.getElementById('circuitStats');
    
    if(!cId) {
        imgEl.style.display = 'none';
        statsEl.style.display = 'none';
        fallbackEl.style.display = 'block';
        document.getElementById('kingContent').style.display = 'none';
        document.getElementById('kingFallback').style.display = 'block';
        fetchLaps();
        return;
    }
    
    const circ = circuitsData.find(c => c.id === cId);
    if(circ) {
        imgEl.src = circ.image_url;
        imgEl.style.display = 'block';
        fallbackEl.style.display = 'none';
        statsEl.style.display = 'flex';
        statsEl.style.gap = '1rem';
        document.getElementById('circLength').textContent = circ.length_m;
        document.getElementById('circCorners').textContent = circ.corners;
        document.getElementById('circDRS').textContent = circ.drs_zones;
        
        fetchCircuitLeaderboard(cId);
        fetchLaps();
    }
}

async function fetchCircuitLeaderboard(cId) {
    try {
        const res = await fetch(`/api/circuits/${cId}/leaderboard`);
        const data = await res.json();
        
        document.getElementById('kingFallback').style.display = 'none';
        document.getElementById('kingContent').style.display = 'flex';
        
        if (data.best_lap) {
            document.getElementById('kingDriver').textContent = `${data.best_lap.name} (#${data.best_lap.car_number})`;
            document.getElementById('kingDriver').style.color = data.best_lap.hex_color || 'var(--text-primary)';
            document.getElementById('kingTime').textContent = formatTime(data.best_lap.ms);
        } else {
            document.getElementById('kingDriver').textContent = "No data";
            document.getElementById('kingTime').textContent = "--:--.---";
        }
        
        document.getElementById('kingS1').textContent = data.s1 ? `${formatTime(data.s1.ms)} (${data.s1.name})` : '--';
        document.getElementById('kingS2').textContent = data.s2 ? `${formatTime(data.s2.ms)} (${data.s2.name})` : '--';
        document.getElementById('kingS3').textContent = data.s3 ? `${formatTime(data.s3.ms)} (${data.s3.name})` : '--';
        
        let absIdeal = 0;
        if(data.s1) absIdeal += data.s1.ms;
        if(data.s2) absIdeal += data.s2.ms;
        if(data.s3) absIdeal += data.s3.ms;
        document.getElementById('kingAbsolute').textContent = absIdeal > 0 ? formatTime(absIdeal) : '--:--.---';
        
    } catch(e) { console.error(e); }
}

function getTyreClass(c) { if(!c) return 'soft'; const t=c.toLowerCase(); if(t.includes('soft'))return'soft';if(t.includes('medium'))return'medium';if(t.includes('hard'))return'hard';if(t.includes('inter'))return'inter';if(t.includes('wet'))return'wet'; return 'soft';}
function getTyreLetter(c) { if(!c) return 'S'; return c.charAt(0).toUpperCase(); }

// Telemetry Logic
function updateDashboard(data) {
    const laps = data.laps || [];
    const ideal_lap_ms = data.ideal_lap_ms || 0;
    
    // reset UI if no laps
    if (!laps || laps.length === 0) {
        document.querySelector('#lapsTable tbody').innerHTML = '';
        lapChart.data.labels = [];
        lapChart.data.datasets[0].data = [];
        lapChart.update();
        return;
    }
    
    const validLaps = laps.filter(l => l.is_valid && l.lap_time_ms > 0);
    if (validLaps.length === 0) return;
    
    // Update Driver Info Panel
    const dId = parseInt(document.getElementById('driverSelect').value);
    const driver = driversData.find(d => d.id === dId);
    if(driver) {
        document.getElementById('dispDriverName').textContent = driver.name;
        document.getElementById('dispDriverNum').textContent = `#${driver.car_number}`;
        // Since we don't have team name in driver endpoint easily without join, we leave it or fetch it. For now just set color if team_id exists.
        // Actually, let's just color the border red as a default if we don't have hex.
        document.getElementById('driverInfoPanel').style.borderTop = `4px solid var(--accent-red)`;
    }

    const lastLap = validLaps[validLaps.length - 1];
    document.getElementById('weatherIcon').textContent = lastLap.weather === 'Rain' ? '🌧️' : '☀️';
    document.getElementById('trackTemp').textContent = lastLap.track_temperature_c ? `${lastLap.track_temperature_c}°C` : '28°C';
    document.getElementById('sessionTypeBadge').textContent = lastLap.session_type_str ? lastLap.session_type_str.toUpperCase() : 'SESSION';
    
    const tyreEl = document.getElementById('currentTyre');
    tyreEl.className = 'tyre-badge ' + getTyreClass(lastLap.tyre_compound);
    tyreEl.innerHTML = `${getTyreLetter(lastLap.tyre_compound)} <span>${(lastLap.tyre_wear_pct || 0).toFixed(0)}%</span>`;
    
    document.getElementById('dmgFL').className = 'damage-pip ' + ((lastLap.front_left_damage || 0) > 10 ? 'red' : 'green');
    document.getElementById('dmgFR').className = 'damage-pip ' + ((lastLap.front_right_damage || 0) > 10 ? 'red' : 'green');
    document.getElementById('dmgRW').className = 'damage-pip ' + ((lastLap.rear_wing_damage || 0) > 10 ? 'red' : 'green');

    const pbLap = validLaps.reduce((min, lap) => lap.lap_time_ms < min.lap_time_ms ? lap : min, validLaps[0]);
    document.getElementById('pbTime').textContent = formatTime(pbLap.lap_time_ms);
    document.getElementById('idealTime').textContent = formatTime(ideal_lap_ms);

    const last10 = validLaps.slice(-10);
    const avgMs = last10.reduce((sum, lap) => sum + lap.lap_time_ms, 0) / last10.length;
    const variance = last10.reduce((sum, lap) => sum + Math.pow(lap.lap_time_ms - avgMs, 2), 0) / last10.length;
    const stdDevMs = Math.sqrt(variance);
    document.getElementById('consistencyVal').textContent = (stdDevMs / 1000).toFixed(3) + ' s';

    lapChart.data.labels = validLaps.map(l => `Lap ${l.lap_number}`);
    lapChart.data.datasets[0].data = validLaps.map(l => l.lap_time_ms / 1000);
    lapChart.update();

    const tbody = document.querySelector('#lapsTable tbody');
    tbody.innerHTML = '';
    [...validLaps].reverse().slice(0,20).forEach(l => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${l.lap_number}</td><td style="font-weight:bold">${formatTime(l.lap_time_ms)}</td><td>${formatTime(l.sector1_ms)}</td><td>${formatTime(l.sector2_ms)}</td><td>${formatTime(l.sector3_ms)}</td><td><span class="tyre-badge ${getTyreClass(l.tyre_compound)}" style="padding: 2px 6px; font-size: 0.8rem;">${getTyreLetter(l.tyre_compound)}</span></td><td>${(l.tyre_wear_pct || 0).toFixed(0)}%</td>`;
        tbody.appendChild(tr);
    });
}

async function fetchLaps() {
    const dId = driverSelect.value;
    const cId = circuitSelect.value;
    let url = '/laps/?';
    if (dId) url += `driver_id=${dId}&`;
    if (cId) url += `circuit_id=${cId}`;
    try {
        const res = await fetch(url);
        updateDashboard(await res.json());
    } catch (e) {}
}

// Championship Logic
async function fetchStandings() {
    if(!currentSeasonId) return;
    try {
        const [dRes, cRes] = await Promise.all([
            fetch(`/standings/drivers?season_id=${currentSeasonId}`),
            fetch(`/standings/constructors?season_id=${currentSeasonId}`)
        ]);
        const dStandings = await dRes.json();
        const cStandings = await cRes.json();
        
        const dBody = document.querySelector('#driverStandingsTable tbody');
        dBody.innerHTML = '';
        dStandings.forEach((s, idx) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td style="padding-left:1.5rem;"><div class="team-color-strip" style="background-color: ${s.hex_color || '#fff'}"></div>${idx + 1}</td><td><strong>#${s.car_number}</strong> ${s.name}</td><td>${s.team_name || 'N/A'}</td><td class="value-large" style="font-size:1.2rem;">${s.total_points || 0}</td><td><span class="badge-wins">${s.wins || 0}</span></td>`;
            dBody.appendChild(tr);
        });

        const cBody = document.querySelector('#constructorStandingsTable tbody');
        cBody.innerHTML = '';
        cStandings.forEach((s, idx) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td style="padding-left:1.5rem;"><div class="team-color-strip" style="background-color: ${s.hex_color || '#fff'}"></div>${idx + 1}</td><td>${s.name}</td><td class="value-large" style="font-size:1.2rem;">${s.total_points || 0}</td><td><span class="badge-wins">${s.wins || 0}</span></td>`;
            cBody.appendChild(tr);
        });
    } catch (e) {}
}

async function fetchProgression() {
    if(!currentSeasonId) return;
    try {
        const res = await fetch(`/api/seasons/${currentSeasonId}/progression`);
        const data = await res.json();
        champChart.data.labels = data.labels;
        champChart.data.datasets = data.datasets;
        champChart.update();
    } catch(e) {}
}

// Hall of Fame Logic
async function fetchHallOfFame() {
    try {
        const [dRes, cRes] = await Promise.all([fetch('/hall_of_fame/drivers'), fetch('/hall_of_fame/constructors')]);
        const dHof = await dRes.json();
        const cHof = await cRes.json();
        
        const dGrid = document.getElementById('driverHofGrid'); dGrid.innerHTML = '';
        dHof.forEach(s => {
            if (s.titles > 0) dGrid.innerHTML += `<div class="hof-card" style="border-left: 4px solid var(--accent-red)"><div class="hof-titles">${s.titles}x</div><div class="hof-name">${s.name}</div><div class="hof-years">${s.years.sort().join(', ')}</div></div>`;
        });

        const cGrid = document.getElementById('constructorHofGrid'); cGrid.innerHTML = '';
        cHof.forEach(s => {
            if (s.titles > 0) cGrid.innerHTML += `<div class="hof-card" style="border-left: 4px solid var(--accent-red)"><div class="hof-titles">${s.titles}x</div><div class="hof-name">${s.name}</div><div class="hof-years">${s.years.sort().join(', ')}</div></div>`;
        });
    } catch (e) {}
}

async function exportBackup() {
    try {
        const res = await fetch('/export');
        const blob = new Blob([JSON.stringify(await res.json(), null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a'); a.href = url; a.download = `f124_backup.json`;
        document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url);
    } catch (e) { alert("Export failed."); }
}

document.getElementById('resultForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        season_race_id: parseInt(document.getElementById('resRaceId').value),
        results: [{
            driver_id: parseInt(document.getElementById('resDriverId').value),
            grid_position: parseInt(document.getElementById('resGridPos').value),
            finish_position: parseInt(document.getElementById('resFinishPos').value),
            has_fastest_lap: document.getElementById('resFastestLap').checked,
            is_dnf: document.getElementById('resDnf').checked
        }]
    };
    try {
        const res = await fetch('/race_results/batch', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        if (res.ok) { alert('Result saved!'); closeModal(); fetchStandings(); }
    } catch(e) { console.error(e); }
});

// Init
setInterval(() => { if (document.getElementById('telemetryView').style.display !== 'none') fetchLaps(); }, 2000);
window.onload = () => { initChart(); initSeasons(); fetchCircuits(); fetchProgression(); };
