import streamlit as st
import streamlit.components.v1 as components

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BookScraper Pro</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-[#09090b] text-white font-sans antialiased flex h-screen overflow-hidden">

    <!-- Sidebar -->
    <aside class="w-64 border-r border-[#27272a] bg-[#18181b] p-6 flex flex-col">
        <div class="text-2xl font-bold mb-8">📚 BookScraper Pro</div>
        <input type="text" placeholder="Search books..." class="w-full bg-[#09090b] border border-[#27272a] rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-indigo-500 placeholder-gray-500" oninput="filterBooks(this.value)">
    </aside>

    <!-- Main content -->
    <main class="flex-1 overflow-y-auto p-8">
        <h1 class="text-3xl font-semibold mb-8">Enterprise Analytics</h1>

        <!-- KPI Cards -->
        <div class="grid grid-cols-3 gap-6 mb-8">
            <div class="bg-[#18181b] border border-[#27272a] rounded-xl p-6">
                <div class="text-sm text-gray-400 uppercase tracking-wide mb-2">Total Books</div>
                <div class="text-4xl font-bold"><h2 id="total-books">0</h2></div>
            </div>
            <div class="bg-[#18181b] border border-[#27272a] rounded-xl p-6">
                <div class="text-sm text-gray-400 uppercase tracking-wide mb-2">Average Price</div>
                <div class="text-4xl font-bold"><h2 id="avg-price">£0.00</h2></div>
            </div>
            <div class="bg-[#18181b] border border-[#27272a] rounded-xl p-6">
                <div class="text-sm text-gray-400 uppercase tracking-wide mb-2">Most Expensive</div>
                <div class="text-4xl font-bold"><h2 id="max-price">£0.00</h2></div>
            </div>
        </div>

        <!-- Chart -->
        <div class="bg-[#18181b] border border-[#27272a] rounded-xl p-6">
            <canvas id="booksChart" height="100"></canvas>
        </div>
    </main>

    <script>
        async function initDashboard() {
            try {
                const res = await fetch('http://localhost:8000/books');
                const data = await res.json();

                // Update KPI numbers
                document.getElementById('total-books').textContent = data.length;
                const avg = data.reduce((sum, b) => sum + b.price, 0) / data.length;
                document.getElementById('avg-price').textContent = '£' + avg.toFixed(2);
                const maxBook = data.reduce((max, b) => b.price > max.price ? b : max, data[0]);
                document.getElementById('max-price').textContent = '£' + maxBook.price.toFixed(2);

                // Sort top 10 by price descending
                const top10 = data.sort((a, b) => b.price - a.price).slice(0, 10);

                new Chart(document.getElementById('booksChart'), {
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
                        maintainAspectRatio: true,
                        plugins: {
                            legend: { display: false }
                        },
                        scales: {
                            x: {
                                grid: { display: false }
                            },
                            y: {
                                grid: { display: false }
                            }
                        }
                    }
                });
            } catch (err) {
                console.error('Failed to load data', err);
            }
        }

        initDashboard();
    </script>
</body>
</html>
"""

components.html(html_content, height=1000, scrolling=True)
