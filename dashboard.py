import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Hide Streamlit chrome and remove padding for full-screen iframe
st.markdown("""
<style>
    #MainMenu, header, footer {visibility: hidden;}
    .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    iframe {
        height: 100vh !important;
        width: 100vw !important;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BookScraper Pro</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .custom-scrollbar::-webkit-scrollbar { width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
    </style>
</head>
<body class="bg-[#000000] text-white font-['Inter'] antialiased flex h-screen overflow-hidden selection:bg-blue-500/30">

    <!-- Sidebar -->
    <aside class="w-[280px] border-r border-white/[0.05] bg-[#050505] p-6 flex flex-col gap-8 z-20 relative">
        <!-- Logo -->
        <div class="flex items-center gap-3">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                <defs>
                    <filter id="glow">
                        <feGaussianBlur stdDeviation="2" result="blur"/>
                        <feMerge>
                            <feMergeNode in="blur"/>
                            <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                    </filter>
                </defs>
                <polygon points="16,2 28,9 28,23 16,30 4,23 4,9" stroke="#60a5fa" stroke-width="2" filter="url(#glow)"/>
                <circle cx="16" cy="16" r="4" fill="#3b82f6"/>
            </svg>
            <span class="text-lg font-semibold tracking-tight">BookScraper Pro</span>
        </div>

        <!-- Search Box -->
        <div class="relative">
            <div class="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                </svg>
            </div>
            <input type="text" id="searchInput" placeholder="Search books..." class="w-full bg-white/[0.03] border border-white/[0.1] rounded-xl pl-11 pr-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all placeholder-gray-500 text-white">
        </div>
    </aside>

    <!-- Main Area -->
    <main class="flex-1 p-10 overflow-y-auto relative z-10 custom-scrollbar">
        <!-- Background Glow -->
        <div class="absolute top-[-20%] left-[20%] w-[800px] h-[600px] bg-blue-600/15 blur-[120px] rounded-full pointer-events-none z-[-1]"></div>

        <!-- Header -->
        <h1 class="text-3xl font-semibold tracking-tight text-white mb-1">Enterprise Analytics</h1>
        <p class="text-sm text-gray-400 mb-8">Real-time data pipeline insights.</p>

        <!-- KPI Cards -->
        <div class="grid grid-cols-3 gap-6 mb-8">
            <div class="bg-[#09090b]/80 backdrop-blur-xl border border-white/[0.05] rounded-2xl p-6 shadow-2xl transition-all duration-300 hover:-translate-y-1 hover:border-white/[0.1] group">
                <div class="absolute top-4 right-4 w-2 h-2 bg-blue-500 rounded-full shadow-[0_0_12px_rgba(59,130,246,0.8)]"></div>
                <div class="text-xs uppercase tracking-wider text-gray-500 mb-2">Total Books</div>
                <div id="kpi-total" class="text-4xl font-semibold">0</div>
            </div>
            <div class="bg-[#09090b]/80 backdrop-blur-xl border border-white/[0.05] rounded-2xl p-6 shadow-2xl transition-all duration-300 hover:-translate-y-1 hover:border-white/[0.1] group">
                <div class="absolute top-4 right-4 w-2 h-2 bg-blue-500 rounded-full shadow-[0_0_12px_rgba(59,130,246,0.8)]"></div>
                <div class="text-xs uppercase tracking-wider text-gray-500 mb-2">Average Price</div>
                <div id="kpi-avg" class="text-4xl font-semibold">£0.00</div>
            </div>
            <div class="bg-[#09090b]/80 backdrop-blur-xl border border-white/[0.05] rounded-2xl p-6 shadow-2xl transition-all duration-300 hover:-translate-y-1 hover:border-white/[0.1] group">
                <div class="absolute top-4 right-4 w-2 h-2 bg-blue-500 rounded-full shadow-[0_0_12px_rgba(59,130,246,0.8)]"></div>
                <div class="text-xs uppercase tracking-wider text-gray-500 mb-2">Most Expensive</div>
                <div id="kpi-max" class="text-4xl font-semibold">£0.00</div>
            </div>
        </div>

        <!-- Chart Container -->
        <div class="bg-[#09090b]/80 backdrop-blur-xl border border-white/[0.05] rounded-2xl p-6 shadow-2xl mb-8 h-[450px]">
            <div class="relative w-full h-full">
                <canvas id="chartCanvas"></canvas>
            </div>
        </div>

        <!-- Custom Table Container -->
        <div class="bg-[#09090b]/80 backdrop-blur-xl border border-white/[0.05] rounded-2xl p-6 shadow-2xl overflow-hidden">
            <table class="w-full text-left text-sm text-gray-300">
                <thead class="text-xs uppercase bg-white/[0.02] text-gray-400 border-b border-white/[0.05]">
                    <tr>
                        <th class="px-6 py-4 font-medium">ID</th>
                        <th class="px-6 py-4 font-medium">Title</th>
                        <th class="px-6 py-4 font-medium text-right">Price</th>
                    </tr>
                </thead>
                <tbody id="tableBody" class="divide-y divide-white/[0.02]"></tbody>
            </table>
        </div>
    </main>

    <script>
        let allData = [];
        let chart = null;

        async function init() {
            try {
                const res = await fetch('http://localhost:8000/books?limit=1000');
                allData = await res.json();
                renderDashboard(allData);
            } catch (err) {
                console.error('Failed to load data', err);
            }
        }

        function renderDashboard(data) {
            // Update KPIs
            document.getElementById('kpi-total').textContent = data.length.toLocaleString();
            const avg = data.reduce((sum, b) => sum + b.price, 0) / data.length;
            document.getElementById('kpi-avg').textContent = '£' + avg.toFixed(2);
            const maxBook = data.reduce((max, b) => b.price > max.price ? b : max, data[0]);
            document.getElementById('kpi-max').textContent = '£' + maxBook.price.toFixed(2);

            // Top 10 most expensive for chart
            const top10 = [...data].sort((a, b) => b.price - a.price).slice(0, 10);

            // Render chart
            const ctx = document.getElementById('chartCanvas').getContext('2d');
            const gradient = ctx.createLinearGradient(0, 0, 0, 450);
            gradient.addColorStop(0, '#1d4ed8');
            gradient.addColorStop(1, '#06b6d4');

            if (chart) {
                chart.destroy();
            }

            chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: top10.map(b => b.title),
                    datasets: [{
                        label: 'Price (£)',
                        data: top10.map(b => b.price),
                        backgroundColor: gradient,
                        borderRadius: 20,
                        borderSkipped: false
                    }]
                },
                options: {
                    indexAxis: 'y',
                    maintainAspectRatio: false,
                    layout: {
                        padding: {
                            left: 20,
                            right: 20
                        }
                    },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: '#111',
                            titleColor: '#ffffff',
                            bodyColor: '#a1a1aa',
                            borderColor: 'rgba(255,255,255,0.1)',
                            borderWidth: 1,
                            padding: 12,
                            cornerRadius: 8
                        }
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: {
                                color: '#a1a1aa',
                                font: { size: 12, weight: '500' }
                            }
                        },
                        y: {
                            grid: { display: false },
                            ticks: {
                                color: '#ffffff',
                                font: { size: 12, weight: '600' }
                            }
                        }
                    }
                }
            });

            // Populate table with top 50
            const top50 = [...data].sort((a, b) => b.price - a.price).slice(0, 50);
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = top50.map(book => `
                <tr class="hover:bg-white/[0.02] transition-colors">
                    <td class="px-6 py-4 text-gray-500">${book.id}</td>
                    <td class="px-6 py-4">${book.title}</td>
                    <td class="px-6 py-4 text-right font-medium text-white">£${book.price.toFixed(2)}</td>
                </tr>
            `).join('');
        }

        // Search listener
        document.getElementById('searchInput').addEventListener('input', function(e) {
            const query = e.target.value.trim().toLowerCase();
            if (!query) {
                renderDashboard(allData);
                return;
            }
            const filtered = allData.filter(book => book.title.toLowerCase().includes(query));
            renderDashboard(filtered);
        });

        init();
    </script>
</body>
</html>
"""

components.html(html_content, height=1000, scrolling=False)
