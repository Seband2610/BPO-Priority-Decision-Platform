
document.addEventListener("DOMContentLoaded", () => {

    // ELEMENTS
    const searchInput = document.getElementById("requestSearch");
    const priorityFilter = document.getElementById("priorityFilter");
    const decisionFilter = document.getElementById("decisionFilter");
    const clearButton = document.getElementById("clearFilters");
    const refreshButton = document.getElementById("refreshDashboard");
    const visibleCount = document.getElementById("visibleCount");
    const noResults = document.getElementById("noResults");
    const table = document.getElementById("requestsTable");

    if (!table) return;

    const tbody = table.querySelector("tbody");
    const headers = table.querySelectorAll("thead th");

    let sortColumn = null;
    let sortDirection = "asc";

    const rows = Array.from(
        tbody.querySelectorAll("tr[data-request-id]")
    );

    const totalRequests = rows.length;


    // NORMALIZE TEXT FOR SEARCH
    function normalizeText(value) {
        return String(value || "")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLowerCase()
            .trim();
    }


    // FILTER REQUESTS
    function filterRequests() {

        const searchTerm = normalizeText(searchInput.value);
        const selectedPriority = priorityFilter.value;
        const selectedDecision = decisionFilter.value;

        let visible = 0;

        rows.forEach(row => {

            const searchableText = normalizeText(
                [
                    row.dataset.requestId,
                    row.dataset.customer,
                    row.dataset.issue,
                    row.dataset.category
                ].join(" ")
            );

            const matchesSearch =
                searchableText.includes(searchTerm);

            const matchesPriority =
                !selectedPriority ||
                row.dataset.priority === selectedPriority;

            const matchesDecision =
                !selectedDecision ||
                row.dataset.decision === selectedDecision;

            const matches =
                matchesSearch &&
                matchesPriority &&
                matchesDecision;

            row.hidden = !matches;

            if (matches) visible++;

        });

        // UPDATE COUNTER
        visibleCount.textContent =
            `Showing ${visible} of ${totalRequests} requests`;

        // SHOW EMPTY STATE
        noResults.hidden = visible !== 0;

    }


    // CLEAR FILTERS
    function clearFilters() {

        searchInput.value = "";
        priorityFilter.value = "";
        decisionFilter.value = "";

        filterRequests();

        searchInput.focus();

    }


    // SORT TABLE
    function sortTable(header) {

        const column = header.dataset.sort;
        const dataType = header.dataset.type || "text";

        if (!column) return;

        if (sortColumn === column) {
            sortDirection = sortDirection === "asc" ? "desc" : "asc";
        } else {
            sortColumn = column;
            sortDirection = "asc";
        }

        const priorityOrder = {
            LOW: 1,
            MEDIUM: 2,
            HIGH: 3,
            CRITICAL: 4
        };

        const decisionOrder = {
            "NORMAL PROCESSING": 1,
            "CRITICAL ATTENTION": 2
        };

        rows.sort((a, b) => {

            let valueA;
            let valueB;

            switch (column) {

                case "request_id":
                    valueA = a.dataset.requestId;
                    valueB = b.dataset.requestId;
                    break;

                case "customer":
                    valueA = a.dataset.customer;
                    valueB = b.dataset.customer;
                    break;

                case "issue":
                    valueA = a.dataset.issue;
                    valueB = b.dataset.issue;
                    break;

                case "category":
                    valueA = a.dataset.category;
                    valueB = b.dataset.category;
                    break;

                case "urgency":
                    valueA = Number(a.dataset.urgency);
                    valueB = Number(b.dataset.urgency);
                    break;

                case "sla_hours":
                    valueA = Number(a.dataset.sla);
                    valueB = Number(b.dataset.sla);
                    break;

                case "priority_score":
                    valueA = Number(a.dataset.score);
                    valueB = Number(b.dataset.score);
                    break;

                case "priority":
                    valueA = priorityOrder[a.dataset.priority] || 0;
                    valueB = priorityOrder[b.dataset.priority] || 0;
                    break;

                case "decision":
                    valueA = decisionOrder[a.dataset.decision] || 0;
                    valueB = decisionOrder[b.dataset.decision] || 0;
                    break;

                default:
                    return 0;
            }

            let comparison;

            if (dataType === "number" ||
                column === "priority" ||
                column === "decision") {

                comparison = valueA - valueB;

            } else {

                comparison = String(valueA).localeCompare(
                    String(valueB),
                    undefined,
                    { sensitivity: "base" }
                );

            }

            return sortDirection === "asc"
                ? comparison
                : -comparison;

        });

        // REORDER TABLE ROWS
        rows.forEach(row => tbody.appendChild(row));

        // UPDATE SORT INDICATORS
        headers.forEach(th => {

            th.removeAttribute("aria-sort");

            const originalText = th.dataset.originalText;

            if (originalText) {
                th.textContent = originalText;
            }

        });

        headers.forEach(th => {

            if (th.dataset.sort === column) {

                if (!th.dataset.originalText) {
                    th.dataset.originalText = th.textContent.trim();
                }

                th.setAttribute(
                    "aria-sort",
                    sortDirection === "asc"
                        ? "ascending"
                        : "descending"
                );

                th.textContent =
                    th.dataset.originalText +
                    (sortDirection === "asc" ? " ▲" : " ▼");

            }

        });

        filterRequests();

    }


    // SEARCH EVENTS
    searchInput.addEventListener("input", filterRequests);

    // FILTER EVENTS
    priorityFilter.addEventListener("change", filterRequests);
    decisionFilter.addEventListener("change", filterRequests);

    // CLEAR BUTTON
    clearButton.addEventListener("click", clearFilters);

    // REFRESH BUTTON
    refreshButton.addEventListener("click", () => {
        window.location.reload();
    });

    // SORT EVENTS
    headers.forEach(header => {

        if (header.dataset.sort) {

            header.addEventListener("click", () => {
                sortTable(header);
            });

        }

    });


    // INITIALIZATION
    filterRequests();

    console.log("BPO Dashboard initialized successfully.");
    console.log(`Total requests loaded: ${totalRequests}`);

});
