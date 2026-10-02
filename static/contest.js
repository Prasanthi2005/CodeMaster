document.addEventListener("DOMContentLoaded", () => {

    let contests = [];

    let currentFilter = "all";

    let searchText = "";

    const contestGrid =
        document.getElementById("contestGrid");

    const emptyState =
        document.getElementById("emptyState");

    const searchInput =
        document.getElementById("searchInput");


    /* ==========================================
       LOAD CONTESTS
    ========================================== */

    async function loadContests() {

        try {

            showLoading();

            const response =
                await fetch("/api/contests", {
                    method: "GET",
                    headers: {
                        "Accept": "application/json"
                    },
                    cache: "no-store"
                });


            if (!response.ok) {

                throw new Error(
                    "Failed to load contests"
                );

            }


            const data =
                await response.json();


            contests =
                Array.isArray(data) ?
                data :
                (data.contests || []);


            updateStats();

            renderContests();

        } catch (error) {

            console.error(
                "Contest loading error:",
                error
            );


            contestGrid.innerHTML = `
                <div class="loading">
                    <h3>Unable to load contests</h3>
                    <p>Please refresh the page.</p>
                </div>
            `;

        }

    }


    /* ==========================================
       LOADING
    ========================================== */

    function showLoading() {

        contestGrid.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                Loading contests...
            </div>
        `;

        emptyState.classList.remove("show");

    }


    /* ==========================================
       UPDATE STATS
    ========================================== */

    function updateStats() {

        const total =
            contests.length;


        const live =
            contests.filter(
                c => getStatus(c) === "live"
            ).length;


        const upcoming =
            contests.filter(
                c => getStatus(c) === "upcoming"
            ).length;


        const finished =
            contests.filter(
                c => getStatus(c) === "finished"
            ).length;


        document.getElementById(
            "totalContests"
        ).textContent = total;


        document.getElementById(
            "liveContests"
        ).textContent = live;


        document.getElementById(
            "upcomingContests"
        ).textContent = upcoming;


        document.getElementById(
            "finishedContests"
        ).textContent = finished;


        document.getElementById(
            "liveHeaderCount"
        ).textContent = live;

    }


    /* ==========================================
       STATUS
    ========================================== */

    function getStatus(contest) {

        const explicitStatus =
            String(
                contest.status || ""
            ).toLowerCase();


        if (
            explicitStatus === "live" ||
            explicitStatus === "upcoming" ||
            explicitStatus === "finished"
        ) {

            const start =
                parseDate(contest.start_time);

            const end =
                parseDate(contest.end_time);

            const now =
                new Date();


            if (
                start &&
                end
            ) {

                if (
                    now >= start &&
                    now <= end
                ) {
                    return "live";
                }

                if (
                    now < start
                ) {
                    return "upcoming";
                }

                return "finished";

            }


            return explicitStatus;

        }


        const start =
            parseDate(contest.start_time);


        const end =
            parseDate(contest.end_time);


        if (!start || !end) {
            return "upcoming";
        }


        const now =
            new Date();


        if (
            now >= start &&
            now <= end
        ) {
            return "live";
        }


        if (
            now < start
        ) {
            return "upcoming";
        }


        return "finished";

    }


    /* ==========================================
       PARSE DATE
    ========================================== */

    function parseDate(value) {

        if (!value) {
            return null;
        }


        let date =
            new Date(value);


        if (!isNaN(date.getTime())) {
            return date;
        }


        date =
            new Date(
                String(value)
                .replace(" ", "T")
            );


        if (!isNaN(date.getTime())) {
            return date;
        }


        return null;

    }


    /* ==========================================
       FILTER
    ========================================== */

    function getFilteredContests() {

        return contests.filter(
            contest => {

                const status =
                    getStatus(contest);


                const matchesFilter =
                    currentFilter === "all" ||
                    status === currentFilter;


                const title =
                    String(
                        contest.title ||
                        contest.name ||
                        ""
                    ).toLowerCase();


                const description =
                    String(
                        contest.description ||
                        ""
                    ).toLowerCase();


                const matchesSearch = !searchText ||
                    title.includes(searchText) ||
                    description.includes(searchText);


                return (
                    matchesFilter &&
                    matchesSearch
                );

            }
        );

    }


    /* ==========================================
       RENDER
    ========================================== */

    function renderContests() {

        const filtered =
            getFilteredContests();


        if (!filtered.length) {

            contestGrid.innerHTML = "";

            emptyState.classList.add(
                "show"
            );

            return;

        }


        emptyState.classList.remove(
            "show"
        );


        contestGrid.innerHTML =
            filtered
            .map(
                (contest, index) =>
                createContestCard(
                    contest,
                    index
                )
            )
            .join("");

    }


    /* ==========================================
       CREATE CARD
    ========================================== */

    function createContestCard(
        contest,
        index
    ) {

        const status =
            getStatus(contest);


        const title =
            escapeHtml(
                contest.title ||
                contest.name ||
                "Coding Contest"
            );


        const description =
            escapeHtml(
                contest.description ||
                "Compete with other developers and solve challenging programming problems."
            );


        const start =
            parseDate(
                contest.start_time
            );


        const end =
            parseDate(
                contest.end_time
            );


        const duration =
            contest.duration ||
            calculateDuration(
                start,
                end
            );


        const participants =
            Number(
                contest.participants ||
                contest.participant_count ||
                0
            );


        const problems =
            Number(
                contest.problems ||
                contest.problem_count ||
                5
            );


        const number =
            contest.id ||
            index + 1;


        const dateText =
            start ?
            formatDate(start) :
            "Date not available";


        const timeText =
            start && end ?
            `${formatTime(start)} - ${formatTime(end)}` :
            "Time not available";


        const countdown =
            createCountdown(
                contest,
                status
            );


        let actionText;


        if (status === "live") {

            actionText =
                "Enter Contest";

        } else if (status === "upcoming") {

            actionText =
                contest.registered ?
                "Registered" :
                "Register";

        } else {

            actionText =
                "View Results";

        }


        return `

            <article
                class="contest-card ${status}"
                data-id="${contest.id || ""}">

                <div class="card-top">

                    <span
                        class="status-badge ${status}">
                        ${status.toUpperCase()}
                    </span>

                    <span class="contest-number">
                        #${number}
                    </span>

                </div>


                <h2 class="contest-title">
                    ${title}
                </h2>


                <p class="contest-description">
                    ${description}
                </p>


                <div class="contest-info">

                    <div class="info-row">

                        <span class="info-icon">
                            ▣
                        </span>

                        <span>
                            ${dateText}
                        </span>

                    </div>


                    <div class="info-row">

                        <span class="info-icon">
                            ◷
                        </span>

                        <span>
                            ${timeText}
                        </span>

                    </div>


                    <div class="info-row">

                        <span class="info-icon">
                            ▱
                        </span>

                        <span>
                            ${problems} Problems
                        </span>

                    </div>


                    <div class="info-row">

                        <span class="info-icon participant-icon">
                            ♟
                        </span>

                        <span
                            id="participants-${contest.id}">
                            ${formatNumber(participants)}
                            Participants
                        </span>

                    </div>

                </div>


                <div
                    class="countdown-box">

                    <span class="countdown-label">
                        ${countdown.label}
                    </span>

                    <strong
                        class="countdown-time"
                        data-countdown-id="${contest.id}"
                        data-start="${contest.start_time || ""}"
                        data-end="${contest.end_time || ""}"
                        data-status="${status}">
                        ${countdown.time}
                    </strong>

                </div>


                <button
                    class="contest-action ${status}"
                    onclick="handleContestAction(${contest.id}, '${status}')">

                    ${actionText}

                </button>

            </article>
        `;

    }


    /* ==========================================
       COUNTDOWN
    ========================================== */

    function createCountdown(
        contest,
        status
    ) {

        const start =
            parseDate(
                contest.start_time
            );


        const end =
            parseDate(
                contest.end_time
            );


        if (
            status === "live" &&
            end
        ) {

            return {
                label: "TIME REMAINING",
                time: formatRemaining(
                    end - new Date()
                )
            };

        }


        if (
            status === "upcoming" &&
            start
        ) {

            return {
                label: "STARTS IN",
                time: formatRemaining(
                    start - new Date()
                )
            };

        }


        return {
            label: "CONTEST STATUS",
            time: "Completed"
        };

    }


    /* ==========================================
       REAL TIME COUNTDOWN
    ========================================== */

    function updateCountdowns() {

        let changed =
            false;


        document
            .querySelectorAll(
                "[data-countdown-id]"
            )
            .forEach(
                element => {

                    const start =
                        parseDate(
                            element.dataset.start
                        );


                    const end =
                        parseDate(
                            element.dataset.end
                        );


                    if (!start || !end) {
                        return;
                    }


                    const now =
                        new Date();


                    let status;


                    if (
                        now >= start &&
                        now <= end
                    ) {

                        status = "live";

                        element.textContent =
                            formatRemaining(
                                end - now
                            );

                        const label =
                            element
                            .parentElement
                            .querySelector(
                                ".countdown-label"
                            );

                        if (label) {
                            label.textContent =
                                "TIME REMAINING";
                        }

                    } else if (
                        now < start
                    ) {

                        status = "upcoming";

                        element.textContent =
                            formatRemaining(
                                start - now
                            );

                        const label =
                            element
                            .parentElement
                            .querySelector(
                                ".countdown-label"
                            );

                        if (label) {
                            label.textContent =
                                "STARTS IN";
                        }

                    } else {

                        status = "finished";

                        element.textContent =
                            "Completed";

                        const label =
                            element
                            .parentElement
                            .querySelector(
                                ".countdown-label"
                            );

                        if (label) {
                            label.textContent =
                                "CONTEST STATUS";
                        }

                    }


                    if (
                        element.dataset.status !== status
                    ) {

                        changed = true;

                    }

                }
            );


        if (changed) {

            updateStats();

            renderContests();

        }

    }


    /* ==========================================
       FORMAT REMAINING
    ========================================== */

    function formatRemaining(
        milliseconds
    ) {

        if (milliseconds <= 0) {
            return "00:00:00";
        }


        let totalSeconds =
            Math.floor(
                milliseconds / 1000
            );


        const days =
            Math.floor(
                totalSeconds / 86400
            );


        totalSeconds %= 86400;


        const hours =
            Math.floor(
                totalSeconds / 3600
            );


        totalSeconds %= 3600;


        const minutes =
            Math.floor(
                totalSeconds / 60
            );


        const seconds =
            totalSeconds % 60;


        const h =
            String(hours).padStart(2, "0");


        const m =
            String(minutes).padStart(2, "0");


        const s =
            String(seconds).padStart(2, "0");


        if (days > 0) {

            return `${days}d ${h}:${m}:${s}`;

        }


        return `${h}:${m}:${s}`;

    }


    /* ==========================================
       ACTION
    ========================================== */

    window.handleContestAction =
        async function(
            contestId,
            status
        ) {

            const contest =
                contests.find(
                    c =>
                    Number(c.id) ===
                    Number(contestId)
                );


            if (!contest) {
                return;
            }


            if (status === "live") {

                window.location.href =
                    `/contest/${contestId}`;

                return;

            }


            if (status === "finished") {

                openContestDetails(
                    contest
                );

                return;

            }


            await registerContest(
                contestId
            );

        };


    /* ==========================================
       REGISTER
    ========================================== */

    async function registerContest(
        contestId
    ) {

        try {

            const response =
                await fetch(
                    `/api/contests/${contestId}/register`, {
                        method: "POST",

                        headers: {
                            "Content-Type": "application/json"
                        }
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                alert(
                    data.message ||
                    "Unable to register."
                );

                return;

            }


            alert(
                data.message ||
                "Successfully registered!"
            );


            await loadContests();

        } catch (error) {

            console.error(error);

            alert(
                "Something went wrong while registering."
            );

        }

    }


    /* ==========================================
       MODAL
    ========================================== */

    function openContestDetails(
        contest
    ) {

        const modal =
            document.getElementById(
                "contestModal"
            );


        const modalBody =
            document.getElementById(
                "modalBody"
            );


        const start =
            parseDate(
                contest.start_time
            );


        const end =
            parseDate(
                contest.end_time
            );


        modalBody.innerHTML = `

            <h2 class="modal-title">
                ${escapeHtml(
                    contest.title ||
                    contest.name ||
                    "Contest"
                )}
            </h2>


            <p class="modal-description">
                ${escapeHtml(
                    contest.description ||
                    "Contest completed successfully."
                )}
            </p>


            <div class="modal-details">

                <div class="modal-detail">
                    <span>DATE</span>
                    <strong>
                        ${
                            start
                            ? formatDate(start)
                            : "-"
                        }
                    </strong>
                </div>


                <div class="modal-detail">
                    <span>DURATION</span>
                    <strong>
                        ${
                            contest.duration
                            ? contest.duration + " minutes"
                            : "-"
                        }
                    </strong>
                </div>


                <div class="modal-detail">
                    <span>START TIME</span>
                    <strong>
                        ${
                            start
                            ? formatTime(start)
                            : "-"
                        }
                    </strong>
                </div>


                <div class="modal-detail">
                    <span>PARTICIPANTS</span>
                    <strong>
                        ${
                            formatNumber(
                                contest.participants ||
                                0
                            )
                        }
                    </strong>
                </div>

            </div>

        `;


        modal.classList.add("show");

    }


    document
        .getElementById("closeModal")
        .addEventListener(
            "click",
            () => {

                document
                    .getElementById(
                        "contestModal"
                    )
                    .classList.remove(
                        "show"
                    );

            }
        );


    document
        .querySelector(".modal-overlay")
        .addEventListener(
            "click",
            () => {

                document
                    .getElementById(
                        "contestModal"
                    )
                    .classList.remove(
                        "show"
                    );

            }
        );


    /* ==========================================
       FILTER BUTTONS
    ========================================== */

    document
        .querySelectorAll(".filter-btn")
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        document
                            .querySelectorAll(
                                ".filter-btn"
                            )
                            .forEach(
                                btn =>
                                btn.classList.remove(
                                    "active"
                                )
                            );


                        button.classList.add(
                            "active"
                        );


                        currentFilter =
                            button.dataset.filter;


                        renderContests();

                    }
                );

            }
        );


    /* ==========================================
       SEARCH
    ========================================== */

    searchInput
        .addEventListener(
            "input",
            event => {

                searchText =
                    event.target.value
                    .trim()
                    .toLowerCase();


                renderContests();

            }
        );


    /* ==========================================
       DATE FORMAT
    ========================================== */

    function formatDate(
        date
    ) {

        return date.toLocaleDateString(
            "en-IN", {
                day: "2-digit",
                month: "short",
                year: "numeric"
            }
        );

    }


    function formatTime(
        date
    ) {

        return date.toLocaleTimeString(
            "en-IN", {
                hour: "2-digit",
                minute: "2-digit"
            }
        );

    }


    function calculateDuration(
        start,
        end
    ) {

        if (!start || !end) {
            return 0;
        }


        return Math.round(
            (
                end.getTime() -
                start.getTime()
            ) / 60000
        );

    }


    function formatNumber(
        number
    ) {

        return Number(
            number || 0
        ).toLocaleString("en-IN");

    }


    /* ==========================================
       HTML ESCAPE
    ========================================== */

    function escapeHtml(
        value
    ) {

        return String(value)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");

    }


    /* ==========================================
       INITIAL LOAD
    ========================================== */

    loadContests();


    /*
        Countdown changes every second.
    */

    setInterval(
        updateCountdowns,
        1000
    );


    /*
        Server data refresh every 20 seconds.
        This updates participant counts and
        contest registration state.
    */

    setInterval(
        loadContests,
        20000
    );

});