import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Hide all Streamlit chrome and remove padding for full-screen iframe
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
<body class="bg-[#09090b] text-white font-['Inter'] m-0 p-0 w-full h-full flex">

    <!-- Sidebar -->
    <aside class="w-64 h-screen bg-[#18181b] border-r border-[#27272a] p-6 flex flex-col shrink-0">
        <div class="text-2xl font-bold mb-8">📚 BookScraper Pro</div>
        <input type="text" placeholder="Search books..." class="w-full bg-[#09090b] border border-[#27272a] rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-indigo-500 placeholder-gray-500" oninput="filterBooks(this.value)">
    </aside>

    <!-- Main content -->
    <main class="flex-1 h-screen overflow-y-auto p-10">
        <h1 class="text-3xl font-semibold mb-8 tracking-tight">Enterprise Analytics</h1>

        <!-- KPI Cards -->
        <div class="grid grid-cols-3 gap-6">
            <div class="bg-[#18181b] border border-[#27272a] rounded-xl p-6">
                <div class="text-sm text-[#a1a1aa] uppercase tracking-wider mb-2">Total Books</div>
                <div class="text-4xl font-semibold tracking-tight"><h2 id="total-books" class="inline">0</h2></div>
            </div>
            <div class="bg-[#18181b] border border-[#27272a] rounded-xl p-6">
                <div class="text-sm text-[#a1a1aa] uppercase tracking-wider mb-2">Average Price</div>
                <div class="text-4xl font-semibold tracking-tight"><h2 id="avg-price" class="inline">£0.00</h2></div>
            </div>
            <div class="bg-[#18181b] border border-[#27272a] rounded-xl p-6">
                <div class="text-sm text-[#a1a1aa] uppercase tracking-wider mb-2">Most Expensive</div>
                <div class="text-4xl font-semibold tracking-tight"><h2 id="max-price" class="inline">£0.00</h2></div>
            </div>
        </div>

        <!-- Chart -->
        <div class="relative w-full h-[400px] mt-8">
            <canvas id="booksChart"></canvas>
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

            chart = new Chart(document.getElementById('booksChart'), {
                type: 'bar',
                data: {
                    labels: top10.map(b => b.title),
                    datasets: [{
                        label: 'Price (£)',
                        data: top10.map(b => b.price),
                        backgroundColor: '#6366f1',
                        borderRadius: 4
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
                                font: { size: 12 }
                            }
                        },
                        y: {
                            grid: { display: false },
                            ticks: {
                                color: '#a1a1aa',
                                font: { size: 12 }
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
