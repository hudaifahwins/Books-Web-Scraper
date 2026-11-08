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
</head>
<body class="bg-[#050505] text-white font-sans antialiased flex h-screen overflow-hidden selection:bg-blue-500/30">

    <!-- Sidebar -->
    <aside class="w-64 h-screen bg-[#0a0a0a] border-r border-white/5 p-6 flex flex-col gap-8 shrink-0">
        <!-- Minimalist logo -->
        <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                <div class="w-3 h-3 bg-blue-500 rounded-full"></div>
            </div>
            <span class="text-lg font-semibold tracking-tight">BookScraper</span>
        </div>

        <!-- Pill-shaped search input -->
        <div class="relative w-full">
            <input type="text" placeholder="Search books..." class="w-full bg-[#111] border border-white/10 rounded-full px-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 transition-all" oninput="filterBooks(this.value)">
        </div>
    </aside>

    <!-- Main content -->
    <main class="flex-1 p-10 overflow-y-auto relative">
        <!-- Glowing background orb -->
        <div class="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-600/20 blur-[120px] rounded-full pointer-events-none"></div>

        <!-- Header -->
        <h1 class="text-4xl font-semibold tracking-tight mb-2">Enterprise Analytics</h1>
        <p class="text-gray-500 text-sm mb-8">Real-time insights from your book collection</p>

        <!-- KPI Cards -->
        <div class="grid grid-cols-3 gap-6 mt-8 relative">
            <div class="bg-[#0a0a0a] border border-white/10 rounded-3xl p-6 shadow-2xl relative overflow-hidden group hover:border-blue-500/50 transition-all">
                <div class="absolute top-0 right-0 w-24 h-24 bg-blue-500/10 rounded-full blur-2xl group-hover:bg-blue-500/20 transition-all"></div>
                <div class="text-sm text-[#a1a1aa] uppercase tracking-wider mb-2">Total Books</div>
                <div class="text-4xl font-semibold tracking-tight"><h2 id="total-books" class="inline">0</h2></div>
            </div>
            <div class="bg-[#0a0a0a] border border-white/10 rounded-3xl p-6 shadow-2xl relative overflow-hidden group hover:border-blue-500/50 transition-all">
                <div class="absolute top-0 right-0 w-24 h-24 bg-blue-500/10 rounded-full blur-2xl group-hover:bg-blue-500/20 transition-all"></div>
                <div class="text-sm text-[#a1a1aa] uppercase tracking-wider mb-2">Average Price</div>
                <div class="text-4xl font-semibold tracking-tight"><h2 id="avg-price" class="inline">£0.00</h2></div>
            </div>
            <div class="bg-[#0a0a0a] border border-white/10 rounded-3xl p-6 shadow-2xl relative overflow-hidden group hover:border-blue-500/50 transition-all">
                <div class="absolute top-0 right-0 w-24 h-24 bg-blue-500/10 rounded-full blur-2xl group-hover:bg-blue-500/20 transition-all"></div>
                <div class="text-sm text-[#a1a1aa] uppercase tracking-wider mb-2">Most Expensive</div>
                <div class="text-4xl font-semibold tracking-tight"><h2 id="max-price" class="inline">£0.00</h2></div>
            </div>
        </div>

        <!-- Chart -->
        <div class="bg-[#0a0a0a] border border-white/10 rounded-3xl p-6 mt-8 shadow-2xl relative">
            <div class="relative w-full h-[400px]">
                <canvas id="booksChart"></canvas>
            </div>
        </div>
    </main>

    <script>
        let allBooks = [];
        let chart = null;

        async function initDashboard() {
            try {
                const res = await fetch('http://localhost:8000/books');
                allBooks = await res.json();

                // Update KPI numbers
                document.getElementById('total-books').textContent = allBooks.length;
                const avg = allBooks.reduce((sum, b) => sum + b.price, 0) / allBooks.length;
                document.getElementById('avg-price').textContent = '£' + avg.toFixed(2);
                const maxBook = allBooks.reduce((max, b) => b.price > max.price ? b : max, allBooks[0]);
                document.getElementById('max-price').textContent = '£' + maxBook.price.toFixed(2);

                renderChart(allBooks);
            } catch (err) {
                console.error('Failed to load data', err);
            }
        }

        function renderChart(books) {
            // Sort top 10 by price descending
            const top10 = [...books].sort((a, b) => b.price - a.price).slice(0, 10);

            if (chart) {
                chart.destroy();
            }

            // Create gradient for bars
            const ctx = document.getElementById('booksChart').getContext('2d');
            const gradient = ctx.createLinearGradient(0, 0, 0, 400);
            gradient.addColorStop(0, '#60a5fa');
            gradient.addColorStop(1, '#3b82f6');

            chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: top10.map(b => b.title),
                    datasets: [{
                        label: 'Price (£)',
                        data: top10.map(b => b.price),
                        backgroundColor: gradient,
                        borderRadius: 8,
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
                        legend: { display: false }
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
        }

        function filterBooks(query) {
            if (!query) {
                renderChart(allBooks);
                return;
            }
            const filtered = allBooks.filter(b => b.title.toLowerCase().includes(query.toLowerCase()));
            renderChart(filtered);
        }

        initDashboard();
    </script>
</body>
</html>
"""

components.html(html_content, height=1000, scrolling=False)
