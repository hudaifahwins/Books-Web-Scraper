import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Hide Streamlit UI completely
st.markdown("""
    <style>
        #MainMenu, header, footer {visibility: hidden;}
        .block-container {padding: 0 !important; margin: 0 !important; max-width: 100% !important;}
        iframe {height: 100vh !important; width: 100vw !important; border: none;}
    </style>
""", unsafe_allow_html=True)

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #27272a; border-radius: 4px; }
    </style>
</head>
<body class="bg-[#09090b] text-zinc-100 flex h-screen overflow-hidden selection:bg-indigo-500/30">

    <!-- Sidebar -->
    <div class="w-[260px] bg-[#0c0c0e] border-r border-white/5 p-6 flex flex-col gap-8 z-20">
        <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white shadow-[0_0_15px_rgba(79,70,229,0.4)]">B</div>
            <span class="text-base font-semibold tracking-tight text-white">BookScraper Pro</span>
        </div>
        
        <div class="relative w-full">
            <svg class="absolute left-3 top-2.5 h-4 w-4 text-zinc-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
            <input type="text" id="searchInput" placeholder="Search books..." class="w-full bg-[#18181b] border border-white/10 rounded-lg pl-10 pr-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all placeholder-zinc-500">
        </div>

        <nav class="flex flex-col gap-1 mt-2">
            <a href="#" class="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-indigo-500/10 text-indigo-400 text-sm font-medium border-l-2 border-indigo-500">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path></svg>
                Overview
            </a>
            <a href="#" class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-zinc-400 hover:text-white hover:bg-white/5 text-sm font-medium transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
                Analytics
            </a>
        </nav>
    </div>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col h-screen overflow-hidden relative">
        <!-- Top Nav -->
        <div class="h-16 border-b border-white/5 flex items-center justify-between px-8 bg-[#09090b]/80 backdrop-blur-md z-20">
            <div class="flex items-center gap-2 text-sm text-zinc-500">
                <span class="hover:text-white cursor-pointer transition-colors">Dashboard</span>
                <span>/</span>
                <span class="text-zinc-200 font-medium">Overview</span>
            </div>
            <div class="flex items-center gap-4">
                <div class="relative">
                    <svg class="w-5 h-5 text-zinc-400 hover:text-white cursor-pointer transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path></svg>
                    <div class="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full border border-[#09090b]"></div>
                </div>
                <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 border border-white/20 shadow-lg cursor-pointer"></div>
            </div>
        </div>

        <!-- Scrollable Content -->
        <div class="flex-1 overflow-y-auto p-8 relative">
            <!-- Ambient Glow -->
            <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-indigo-500/10 blur-[120px] rounded-full pointer-events-none z-0"></div>

            <div class="relative z-10 max-w-6xl mx-auto flex flex-col gap-8">
                <!-- Header -->
                <div>
                    <h1 class="text-2xl font-semibold tracking-tight text-white">Enterprise Analytics</h1>
                    <p class="text-sm text-zinc-400 mt-1">Real-time insights from your book collection.</p>
                </div>

                <!-- KPI Cards -->
                <div class="grid grid-cols-3 gap-6">
                    <!-- Card 1 -->
                    <div class="bg-gradient-to-b from-[#18181b] to-[#09090b] border border-white/5 rounded-2xl p-6 shadow-2xl relative overflow-hidden group hover:border-indigo-500/30 transition-all duration-300">
                        <div class="text-xs font-semibold text-zinc-500 uppercase tracking-widest">Total Books</div>
                        <div class="text-4xl font-bold text-white mt-3 tracking-tight" id="total-books">0</div>
                    </div>
                    <!-- Card 2 -->
                    <div class="bg-gradient-to-b from-[#18181b] to-[#09090b] border border-white/5 rounded-2xl p-6 shadow-2xl relative overflow-hidden group hover:border-indigo-500/30 transition-all duration-300">
                        <div class="text-xs font-semibold text-zinc-500 uppercase tracking-widest">Average Price</div>
                        <div class="text-4xl font-bold text-white mt-3 tracking-tight" id="avg-price">£0.00</div>
                    </div>
                    <!-- Card 3 -->
                    <div class="bg-gradient-to-b from-[#18181b] to-[#09090b] border border-white/5 rounded-2xl p-6 shadow-2xl relative overflow-hidden group hover:border-indigo-500/30 transition-all duration-300">
                        <div class="text-xs font-semibold text-zinc-500 uppercase tracking-widest">Most Expensive</div>
                        <div class="text-4xl font-bold text-white mt-3 tracking-tight" id="max-price">£0.00</div>
                    </div>
                </div>

                <!-- Chart Container -->
                <div class="bg-[#121214] border border-white/5 rounded-2xl p-6 shadow-2xl h-[420px] flex flex-col">
                    <h3 class="text-base font-semibold text-white mb-6">Top 10 Most Expensive Books</h3>
                    <div class="flex-1 relative w-full">
                        <canvas id="booksChart"></canvas>
                    </div>
                </div>

                <!-- Table Container -->
                <div class="bg-[#121214] border border-white/5 rounded-2xl shadow-2xl overflow-hidden mb-8">
                    <table class="w-full text-left text-sm text-zinc-400">
                        <thead class="bg-[#18181b] text-xs uppercase tracking-wider text-zinc-500 border-b border-white/5">
                            <tr>
                                <th class="px-6 py-4 font-medium">Title</th>
                                <th class="px-6 py-4 font-medium text-right">Price</th>
                            </tr>
                        </thead>
                        <tbody id="table-body" class="divide-y divide-white/5">
                            <!-- JS populates here -->
                        </tbody>
                    </table>
                </div>

            </div>
        </div>
    </div>

    <script>
        async function initDashboard() {
            try {
                const res = await fetch('http://localhost:8000/books?limit=100');
                const data = await res.json();
                
                // Update KPIs
                document.getElementById('total-books').innerText = data.length.toLocaleString();
                const total = data.reduce((sum, book) => sum + book.price, 0);
                document.getElementById('avg-price').innerText = '£' + (total / data.length).toFixed(2);
                const sorted = [...data].sort((a, b) => b.price - a.price);
                document.getElementById('max-price').innerText = '£' + sorted[0].price.toFixed(2);

                // Populate Table (Top 15)
                const tbody = document.getElementById('table-body');
                sorted.slice(0, 15).forEach(book => {
                    tbody.innerHTML += `
                        <tr class="hover:bg-white/[0.02] transition-colors">
                            <td class="px-6 py-4 text-white font-medium">${book.title}</td>
                            <td class="px-6 py-4 text-right text-indigo-400 font-medium">£${book.price.toFixed(2)}</td>
                        </tr>
                    `;
                });

                // Chart Setup
                const ctx = document.getElementById('booksChart').getContext('2d');
                
                // Create Gradient
                const gradient = ctx.createLinearGradient(0, 0, 800, 0);
                gradient.addColorStop(0, '#4f46e5'); // Indigo
                gradient.addColorStop(1, '#c084fc'); // Purple

                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: sorted.slice(0, 10).map(b => b.title),
                        datasets: [{
                            data: sorted.slice(0, 10).map(b => b.price),
                            backgroundColor: gradient,
                            borderRadius: 4,
                            borderSkipped: false,
                            barThickness: 10 // ULTRA THIN ELEGANT BARS
                        }]
                    },
                    options: {
                        indexAxis: 'y',
                        responsive: true,
                        maintainAspectRatio: false,
                        layout: { padding: { right: 30 } },
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                backgroundColor: '#18181b',
                                titleColor: '#fff',
                                bodyColor: '#a1a1aa',
                                borderColor: 'rgba(255,255,255,0.1)',
                                borderWidth: 1,
                                padding: 12,
                                cornerRadius: 8,
                                displayColors: false,
                                callbacks: {
                                    label: function(context) { return '£' + context.raw.toFixed(2); }
                                }
                            }
                        },
                        scales: {
                            x: {
                                grid: { display: false, drawBorder: false },
                                ticks: { color: '#52525b', font: { family: 'Inter', size: 12 } }
                            },
                            y: {
                                grid: { display: false, drawBorder: false },
                                ticks: { color: '#a1a1aa', font: { family: 'Inter', size: 12, weight: 500 } }
                            }
                        }
                    }
                });
            } catch (e) {
                console.error("Error fetching data:", e);
            }
        }
        initDashboard();
    </script>
</body>
</html>
"""

components.html(html_content, height=1000, scrolling=False)
