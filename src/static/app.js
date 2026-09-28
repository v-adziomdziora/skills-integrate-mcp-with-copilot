document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft =
          details.max_participants - details.participants.length;

        // Create participants HTML with delete icons instead of bullet points
        const participantsHTML =
          details.participants.length > 0
            ? `<div class="participants-section">
              <h5>Participants:</h5>
              <ul class="participants-list">
                ${details.participants
                  .map(
                    (email) =>
                      `<li><span class="participant-email">${email}</span><button class="delete-btn" data-activity="${name}" data-email="${email}">❌</button></li>`
                  )
                  .join("")}
              </ul>
            </div>`
            : `<p><em>No participants yet</em></p>`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-container">
            ${participantsHTML}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      // Add event listeners to delete buttons
      document.querySelectorAll(".delete-btn").forEach((button) => {
        button.addEventListener("click", handleUnregister);
      });
    } catch (error) {
      activitiesList.innerHTML =
        "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle unregister functionality
  async function handleUnregister(event) {
    const button = event.target;
    const activity = button.getAttribute("data-activity");
    const email = button.getAttribute("data-email");

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(
          activity
        )}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";

        // Refresh activities list to show updated participants
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to unregister. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error unregistering:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(
          activity
        )}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();

        // Refresh activities list to show updated participants
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // --- Staff analytics dashboard ---
  const analyticsForm = document.getElementById("analytics-filters");
  const analyticsMetrics = document.getElementById("analytics-metrics");
  const analyticsBreakdown = document.getElementById("analytics-breakdown");
  const academicYearSelect = document.getElementById("filter-academic-year");
  const categorySelect = document.getElementById("filter-category");
  const statusSelect = document.getElementById("filter-status");

  // Fill a select with the values available in the stored records
  function populateFilter(select, values) {
    values.forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      select.appendChild(option);
    });
  }

  // Build a single metric card
  function createMetricCard(label, value) {
    const card = document.createElement("div");
    card.className = "metric-card";

    const valueEl = document.createElement("span");
    valueEl.className = "metric-value";
    valueEl.textContent = value;

    const labelEl = document.createElement("span");
    labelEl.className = "metric-label";
    labelEl.textContent = label;

    card.appendChild(valueEl);
    card.appendChild(labelEl);
    return card;
  }

  // Build a breakdown table for a grouping (category or academic year)
  function createBreakdownTable(title, groupKey, groups) {
    const wrapper = document.createElement("div");
    wrapper.className = "breakdown";

    const heading = document.createElement("h4");
    heading.textContent = title;
    wrapper.appendChild(heading);

    if (groups.length === 0) {
      const empty = document.createElement("p");
      empty.className = "empty-state";
      empty.textContent = "No outcomes recorded for the selected filters.";
      wrapper.appendChild(empty);
      return wrapper;
    }

    const table = document.createElement("table");
    table.className = "breakdown-table";
    const headerRow = document.createElement("tr");
    [title, "Total", "Approved", "Pending", "Rejected"].forEach((text) => {
      const th = document.createElement("th");
      th.textContent = text;
      headerRow.appendChild(th);
    });
    table.appendChild(headerRow);

    groups.forEach((group) => {
      const row = document.createElement("tr");
      [
        group[groupKey],
        group.total,
        group.approved,
        group.pending,
        group.rejected,
      ].forEach((value) => {
        const cell = document.createElement("td");
        cell.textContent = value;
        row.appendChild(cell);
      });
      table.appendChild(row);
    });

    wrapper.appendChild(table);
    return wrapper;
  }

  // Render the metrics for the current filter context
  function renderAnalytics(analytics) {
    analyticsMetrics.innerHTML = "";
    analyticsBreakdown.innerHTML = "";

    if (analytics.empty) {
      const empty = document.createElement("p");
      empty.className = "empty-state";
      empty.textContent =
        "No outcome records match the selected filters yet. Totals below are 0.";
      analyticsMetrics.appendChild(empty);
    }

    const cards = document.createElement("div");
    cards.className = "metrics-grid";
    cards.appendChild(
      createMetricCard("Outcome records", analytics.totals.total_records)
    );
    cards.appendChild(
      createMetricCard("Students", analytics.totals.distinct_students)
    );
    cards.appendChild(
      createMetricCard("Pending reviews", analytics.totals.pending_reviews)
    );
    cards.appendChild(
      createMetricCard("Approved records", analytics.totals.approved_records)
    );
    analyticsMetrics.appendChild(cards);

    analyticsBreakdown.appendChild(
      createBreakdownTable("Category", "category", analytics.by_category)
    );
    analyticsBreakdown.appendChild(
      createBreakdownTable(
        "Academic Year",
        "academic_year",
        analytics.by_academic_year
      )
    );
  }

  // Fetch the metrics using the filters currently selected
  async function fetchAnalytics() {
    const params = new URLSearchParams();
    const filterValues = {
      start_date: document.getElementById("filter-start-date").value,
      end_date: document.getElementById("filter-end-date").value,
      academic_year: academicYearSelect.value,
      category: categorySelect.value,
      status: statusSelect.value,
    };

    Object.entries(filterValues).forEach(([key, value]) => {
      if (value) {
        params.append(key, value);
      }
    });

    try {
      const response = await fetch(`/outcomes/analytics?${params.toString()}`);
      const result = await response.json();

      if (!response.ok) {
        analyticsMetrics.textContent =
          typeof result.detail === "string"
            ? result.detail
            : "Failed to load analytics.";
        analyticsBreakdown.innerHTML = "";
        return;
      }

      renderAnalytics(result);
    } catch (error) {
      analyticsMetrics.textContent =
        "Failed to load analytics. Please try again later.";
      analyticsBreakdown.innerHTML = "";
      console.error("Error fetching analytics:", error);
    }
  }

  async function initAnalytics() {
    try {
      const response = await fetch("/outcomes/filters");
      const filters = await response.json();
      populateFilter(academicYearSelect, filters.academic_years);
      populateFilter(categorySelect, filters.categories);
      populateFilter(statusSelect, filters.statuses);
    } catch (error) {
      console.error("Error fetching analytics filters:", error);
    }

    analyticsForm.addEventListener("submit", (event) => {
      event.preventDefault();
      fetchAnalytics();
    });

    analyticsForm.addEventListener("reset", () => {
      // Wait for the browser to clear the inputs before refetching
      setTimeout(fetchAnalytics, 0);
    });

    fetchAnalytics();
  }

  // Initialize app
  fetchActivities();
  initAnalytics();
});
