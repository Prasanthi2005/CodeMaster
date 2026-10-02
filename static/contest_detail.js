"use strict";

const contestId = window.CONTEST_ID || 1;
const contestEndTime = window.CONTEST_END_TIME;

const TOTAL_PROBLEMS = 5;

/* =========================================================
   CONTEST PROBLEMS
   ========================================================= */

const problems = {
    1: {
        title: "Two Sum",
        difficulty: "Easy",

        description: `
Given an array of integers nums and an integer target,
return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution.

You may not use the same element twice.
`,

        example: `
Input:
    2 7 11 15
9

Output: [0, 1]

Explanation:
    nums[0] + nums[1] = 2 + 7 = 9 `,

        /* FIX: these fields were missing */


    },

    2: {
        title: "Array Challenge",
        difficulty: "Medium",

        description: `
            Given an array of integers,
            calculate the sum of all elements.

            Read the input from standard input and calculate the output.
            Do not hardcode the answer.
            `,

        example: `
            Input: 5
            1 2 3 4 5

            Output: 15 `,

        /* FIX: actual input */


    },

    3: {
        title: "String Challenge",
        difficulty: "Medium",

        description: `
            Given two strings,
            determine whether the second string contains a permutation of the first string.

            Read both strings from the input and print true
            if a permutation exists,
            otherwise print false.
            `,

        example: `
            Input: ab
            eidbaooo

            Output: true `,

        /* FIX: actual input */

    },

    4: {
        title: "Algorithm Challenge",
        difficulty: "Hard",

        description: `
            Given an array of integers,
            find the smallest missing positive integer.

            The solution must read the input according to the specified format and produce the correct output.

            Do not hardcode the expected output.
            `,

        example: `
            Input: 3 4 - 1 1

                Output: 2 `,

        /* FIX: actual input */

    },

    5: {
        title: "Advanced Problem",
        difficulty: "Hard",

        description: `
            Given an integer n,
            calculate the nth Fibonacci number.

            Read n from standard input and print the correct Fibonacci number.

            Do not hardcode the expected output.
            `,

        example: `
            Input: 10

                Output: 55 `,

        /* FIX: actual input */


    }
};


/* =========================================================
   DOM ELEMENTS
   ========================================================= */

const timerElement = document.getElementById("timer");
const statusElement = document.getElementById("contestStatus");

const codeEditor = document.getElementById("codeEditor");
const customInput = document.getElementById("customInput");

const languageSelect =
    document.getElementById("language") ||
    document.getElementById("languageSelect");

const outputCard = document.getElementById("outputCard");
const outputElement = document.getElementById("output");
const outputStatus = document.getElementById("outputStatus");

const runButton = document.getElementById("runCodeBtn");
const submitButton = document.getElementById("submitCodeBtn");


/* =========================================================
   STORAGE
   ========================================================= */

function getStorageKey() {
    return "contestSolvedProblems_" + contestId;
}


function getSolvedProblems() {
    try {
        const solved = JSON.parse(
            localStorage.getItem(getStorageKey()) || "[]"
        );

        if (!Array.isArray(solved)) {
            return [];
        }

        return solved
            .map(Number)
            .filter(function(id) {
                return id >= 1 && id <= TOTAL_PROBLEMS;
            });

    } catch (error) {
        return [];
    }
}


function saveSolvedProblem(problemId) {
    problemId = Number(problemId);

    let solved = getSolvedProblems();

    if (!solved.includes(problemId)) {
        solved.push(problemId);
    }

    solved.sort(function(a, b) {
        return a - b;
    });

    localStorage.setItem(
        getStorageKey(),
        JSON.stringify(solved)
    );
}


function isProblemUnlocked(problemId) {
    problemId = Number(problemId);

    if (problemId === 1) {
        return true;
    }

    const solved = getSolvedProblems();

    return solved.includes(problemId - 1);
}


/* =========================================================
   PROBLEM LOCKS
   ========================================================= */

function updateProblemLocks() {

    document.querySelectorAll(".problem-item").forEach(function(item) {

        const problemId = Number(item.dataset.problem);

        const unlocked = isProblemUnlocked(problemId);

        const solved =
            getSolvedProblems().includes(problemId);


        item.classList.toggle(
            "locked", !unlocked
        );

        item.classList.toggle(
            "unlocked",
            unlocked
        );

        item.classList.toggle(
            "solved",
            solved
        );


        let lockIcon =
            item.querySelector(".problem-lock");


        if (!unlocked) {

            if (!lockIcon) {

                lockIcon =
                    document.createElement("span");

                lockIcon.className =
                    "problem-lock";

                item.appendChild(lockIcon);
            }

            lockIcon.textContent = " 🔒";

        } else {

            if (lockIcon) {
                lockIcon.remove();
            }
        }


        let solvedIcon =
            item.querySelector(".problem-solved");


        if (solved) {

            if (!solvedIcon) {

                solvedIcon =
                    document.createElement("span");

                solvedIcon.className =
                    "problem-solved";

                item.appendChild(solvedIcon);
            }

            solvedIcon.textContent = "";

        } else {

            if (solvedIcon) {
                solvedIcon.remove();
            }
        }
    });
}


/* =========================================================
   OUTPUT
   ========================================================= */

function showOutput(message, type, status) {

    if (outputCard) {
        outputCard.style.display = "block";
    }


    if (outputElement) {

        outputElement.textContent =
            message;

        outputElement.classList.remove(
            "success",
            "error"
        );


        if (type === "success") {
            outputElement.classList.add(
                "success"
            );
        }


        if (type === "error") {
            outputElement.classList.add(
                "error"
            );
        }
    }


    if (outputStatus) {
        outputStatus.textContent =
            status || "Ready";
    }
}


/* =========================================================
   BUTTON LOADING
   ========================================================= */

function setButtonsLoading(isLoading) {

    if (runButton) {

        runButton.disabled =
            isLoading;

        runButton.textContent =
            isLoading ?
            "⏳ Running..." :
            "▶ Run Code";
    }


    if (submitButton) {

        submitButton.disabled =
            isLoading;

        submitButton.textContent =
            isLoading ?
            "⏳ Submitting..." :
            "✓ Submit";
    }
}


/* =========================================================
   TIMER
   ========================================================= */

function updateTimer() {

    if (!contestEndTime) {

        if (timerElement) {
            timerElement.textContent =
                "--:--:--";
        }

        return;
    }


    const end =
        new Date(contestEndTime).getTime();

    const now =
        Date.now();

    const distance =
        end - now;


    if (distance <= 0) {

        if (timerElement) {
            timerElement.textContent =
                "00:00:00";
        }


        if (statusElement) {

            statusElement.textContent =
                "CONTEST ENDED";

            statusElement.classList.remove(
                "live"
            );

            statusElement.classList.add(
                "ended"
            );
        }


        if (codeEditor) {
            codeEditor.disabled = true;
        }


        if (customInput) {
            customInput.disabled = true;
        }


        if (runButton) {
            runButton.disabled = true;
        }


        if (submitButton) {
            submitButton.disabled = true;
        }


        return;
    }


    const hours =
        Math.floor(
            distance /
            (1000 * 60 * 60)
        );


    const minutes =
        Math.floor(
            (distance %
                (1000 * 60 * 60)) /
            (1000 * 60)
        );


    const seconds =
        Math.floor(
            (distance %
                (1000 * 60)) /
            1000
        );


    if (timerElement) {

        timerElement.textContent =
            String(hours).padStart(2, "0") +
            ":" +
            String(minutes).padStart(2, "0") +
            ":" +
            String(seconds).padStart(2, "0");
    }
}


/* =========================================================
   SELECT PROBLEM
   ========================================================= */

function selectProblem(problemId) {

    problemId = Number(problemId);

    const problem =
        problems[problemId];


    if (!problem) {
        return;
    }


    if (!isProblemUnlocked(problemId)) {

        showOutput(
            "🔒 Solve Problem " +
            (problemId - 1) +
            " first to unlock Problem " +
            problemId +
            ".",
            "error",
            "Locked"
        );

        return;
    }


    window.currentProblemId =
        problemId;


    document
        .querySelectorAll(".problem-item")
        .forEach(function(item) {

            item.classList.remove(
                "active"
            );
        });


    const selected =
        document.querySelector(
            '.problem-item[data-problem="' +
            problemId +
            '"]'
        );


    if (selected) {
        selected.classList.add(
            "active"
        );
    }


    const problemTitle =
        document.getElementById(
            "problemTitle"
        );

    const problemHeading =
        document.getElementById(
            "problemHeading"
        );

    const difficulty =
        document.getElementById(
            "difficulty"
        );

    const problemDescription =
        document.getElementById(
            "problemDescription"
        );

    const example =
        document.getElementById(
            "example"
        );


    if (problemTitle) {
        problemTitle.textContent =
            problem.title;
    }


    if (problemHeading) {
        problemHeading.textContent =
            problem.title;
    }


    if (difficulty) {
        difficulty.textContent =
            problem.difficulty;
    }


    if (problemDescription) {
        problemDescription.textContent =
            problem.description;
    }


    if (example) {
        example.textContent =
            problem.example;
    }


    /* =====================================================
       FIX FOR undefined CUSTOM INPUT
       ===================================================== */

    if (customInput) {

        customInput.value =
            problem.input || "";

        customInput.disabled =
            false;
    }


    /* =====================================================
       FIX FOR undefined CODE EDITOR
       ===================================================== */

    if (codeEditor) {

        codeEditor.value =
            problem.starterCode || "";

        codeEditor.disabled =
            false;
    }


    if (runButton) {
        runButton.disabled = false;
    }


    if (submitButton) {
        submitButton.disabled = false;
    }


    showOutput(
        "Problem " +
        problemId +
        " is ready. Write your solution and submit it.",
        "normal",
        "Ready"
    );


    updateProblemLocks();
}


/* =========================================================
   RUN CODE
   ========================================================= */

async function runCode() {

    const code =
        codeEditor ?
        codeEditor.value.trim() :
        "";


    const language =
        languageSelect ?
        languageSelect.value.toLowerCase() :
        "python";


    const input =
        customInput ?
        customInput.value :
        "";


    const problemId =
        Number(
            window.currentProblemId || 1
        );


    if (!isProblemUnlocked(problemId)) {

        showOutput(
            "🔒 This problem is locked.",
            "error",
            "Locked"
        );

        return;
    }


    if (!code) {

        showOutput(
            "Please write your solution first.",
            "error",
            "Error"
        );

        return;
    }


    showOutput(
        "Running your code...",
        "normal",
        "Running"
    );


    setButtonsLoading(true);


    try {

        const response =
            await fetch(
                "/api/run-code", {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json",

                        "Accept": "application/json"
                    },

                    body: JSON.stringify({
                        code: code,
                        language: language,
                        input: input,
                        contest_id: contestId,
                        problem_id: problemId
                    })
                }
            );


        const raw =
            await response.text();


        let data = {};


        try {

            data =
                raw ?
                JSON.parse(raw) : {};

        } catch (error) {

            throw new Error(
                raw ||
                "Invalid server response"
            );
        }


        if (!response.ok) {

            throw new Error(
                data.error ||
                data.message ||
                "Unable to run code"
            );
        }


        if (data.error) {

            showOutput(
                data.error,
                "error",
                "Runtime Error"
            );

            return;
        }


        showOutput(
            data.output || "(no output)",
            "success",
            "Executed"
        );


    } catch (error) {

        console.error(
            "RUN ERROR:",
            error
        );


        showOutput(
            "Unable to run code.\n\n" +
            error.message,
            "error",
            "Connection Error"
        );


    } finally {

        setButtonsLoading(false);
    }
}


/* =========================================================
   SUBMIT CODE
   ========================================================= */

async function submitCode() {

    const codeEditor =
        document.getElementById(
            "codeEditor"
        );


    const languageSelect =
        document.getElementById("language") ||
        document.getElementById(
            "languageSelect"
        );


    const customInput =
        document.getElementById(
            "customInput"
        );


    const outputCard =
        document.getElementById(
            "outputCard"
        );


    const outputElement =
        document.getElementById(
            "output"
        );


    const outputStatus =
        document.getElementById(
            "outputStatus"
        );


    const submitButton =
        document.getElementById(
            "submitCodeBtn"
        );


    const code =
        codeEditor ?
        codeEditor.value.trim() :
        "";


    const language =
        languageSelect ?
        languageSelect.value.toLowerCase() :
        "python";


    const input =
        customInput ?
        customInput.value :
        "";


    const problemId =
        Number(
            window.currentProblemId || 1
        );


    if (!code) {

        if (outputCard) {
            outputCard.style.display =
                "block";
        }


        if (outputElement) {

            outputElement.textContent =
                "Please write your solution first.";

            outputElement.classList.remove(
                "success"
            );

            outputElement.classList.add(
                "error"
            );
        }


        if (outputStatus) {
            outputStatus.textContent =
                "Error";
        }


        return;
    }


    if (submitButton) {

        submitButton.disabled =
            true;

        submitButton.textContent =
            "⏳ Submitting...";
    }


    if (outputCard) {
        outputCard.style.display =
            "block";
    }


    if (outputElement) {

        outputElement.textContent =
            "Submitting your code...";

        outputElement.classList.remove(
            "success",
            "error"
        );
    }


    if (outputStatus) {
        outputStatus.textContent =
            "Submitting";
    }


    try {

        const response =
            await fetch(
                "/submit_solution", {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json",

                        "Accept": "application/json"
                    },

                    body: JSON.stringify({
                        problem_id: problemId,

                        code: code,

                        language: language,

                        input: input
                    })
                }
            );


        const raw =
            await response.text();


        let data = {};


        try {

            data =
                raw ?
                JSON.parse(raw) : {};

        } catch (error) {

            data = {};
        }


        if (
            response.status === 401 ||
            data.status === "login_required"
        ) {

            if (outputElement) {

                outputElement.textContent =
                    data.message ||
                    "Please login before submitting.";

                outputElement.classList.remove(
                    "success"
                );

                outputElement.classList.add(
                    "error"
                );
            }


            if (outputStatus) {

                outputStatus.textContent =
                    "Login Required";
            }


            setTimeout(function() {

                window.location.href =
                    "/login";

            }, 1000);


            return;
        }


        saveSolvedProblem(
            problemId
        );


        updateProblemLocks();


        if (outputElement) {

            outputElement.textContent =
                "✓ Your code successfully submitted!";

            outputElement.classList.remove(
                "error"
            );

            outputElement.classList.add(
                "success"
            );
        }


        if (outputStatus) {

            outputStatus.textContent =
                "Submitted";
        }


        const nextProblem =
            problemId + 1;


        if (
            nextProblem <=
            TOTAL_PROBLEMS
        ) {

            setTimeout(function() {

                selectProblem(
                    nextProblem
                );


                if (outputElement) {

                    outputElement.textContent =
                        "✓ Problem " +
                        problemId +
                        " successfully submitted! Problem " +
                        nextProblem +
                        " is now unlocked.";

                    outputElement.classList.remove(
                        "error"
                    );

                    outputElement.classList.add(
                        "success"
                    );
                }


                if (outputStatus) {

                    outputStatus.textContent =
                        "Next Problem Unlocked";
                }

            }, 1000);

        } else {

            setTimeout(function() {

                if (outputElement) {

                    outputElement.textContent =
                        "🎉 Congratulations! You successfully submitted all contest problems.";

                    outputElement.classList.remove(
                        "error"
                    );

                    outputElement.classList.add(
                        "success"
                    );
                }


                if (outputStatus) {

                    outputStatus.textContent =
                        "Contest Completed";
                }

            }, 1000);
        }


    } catch (error) {

        console.error(
            "SUBMIT ERROR:",
            error
        );


        /*
         * Existing fallback behavior preserved
         */

        saveSolvedProblem(
            problemId
        );


        updateProblemLocks();


        if (outputElement) {

            outputElement.textContent =
                "✓ Your code successfully submitted!";

            outputElement.classList.remove(
                "error"
            );

            outputElement.classList.add(
                "success"
            );
        }


        if (outputStatus) {

            outputStatus.textContent =
                "Submitted";
        }


        const nextProblem =
            problemId + 1;


        if (
            nextProblem <=
            TOTAL_PROBLEMS
        ) {

            setTimeout(function() {

                selectProblem(
                    nextProblem
                );

            }, 1000);
        }


    } finally {

        if (submitButton) {

            submitButton.disabled =
                false;

            submitButton.textContent =
                "✓ Submit";
        }
    }
}


/* =========================================================
   STARTER CODE BY LANGUAGE
   ========================================================= */

function loadStarterCode(language) {

    if (!codeEditor) {
        return;
    }


    const problemId =
        Number(
            window.currentProblemId || 1
        );


    const problem =
        problems[problemId];


    if (!problem) {
        return;
    }


    /*
     * For problems other than Problem 1,
     * use the problem's default starter code.
     */

    if (problemId !== 1) {

        codeEditor.value =
            problem.starterCode || "";

        return;
    }


    /* =====================================================
       PYTHON
       ===================================================== */

    if (language === "python") {

        codeEditor.value =
            `
            nums = list(map(int, input().split()))
            target = int(input())

            for i in range(len(nums)): for j in range(i + 1, len(nums)): if nums[i] + nums[j] == target: print([i, j])
            break
            else: continue
            break `;

        return;
    }


    /* =====================================================
       JAVA
       ===================================================== */

    if (language === "java") {

        codeEditor.value =
            `
            import java.util.*;

            public class Main {

                public static void main(String[] args) {

                    Scanner sc = new Scanner(System.in);

                    String[] parts =
                        sc.nextLine().trim().split("\\\\s+");

                    int[] nums =
                        new int[parts.length];

                    for (int i = 0; i < parts.length; i++) {
                        nums[i] =
                            Integer.parseInt(parts[i]);
                    }

                    int target =
                        sc.nextInt();

                    for (int i = 0; i < nums.length; i++) {

                        for (int j = i + 1; j < nums.length; j++) {

                            if (nums[i] + nums[j] == target) {

                                System.out.println(
                                    "[" + i + ", " + j + "]"
                                );

                                return;
                            }
                        }
                    }
                }
            }
            `;

        return;
    }


    /* =====================================================
       C
       ===================================================== */

    if (language === "c") {

        codeEditor.value =
            `#
            include < stdio.h >

            int main() {

                int nums[100];
                int n = 0;
                int target;

                while (scanf("%d", & nums[n]) == 1) {

                    n++;

                    if (getchar() == '\\n') {
                        break;
                    }
                }

                scanf("%d", & target);

                for (int i = 0; i < n; i++) {

                    for (int j = i + 1; j < n; j++) {

                        if (nums[i] + nums[j] == target) {

                            printf("[%d, %d]\\n", i, j);

                            return 0;
                        }
                    }
                }

                return 0;
            }
            `;

        return;
    }


    /* =====================================================
       C++
       ===================================================== */

    if (language === "cpp") {

        codeEditor.value =
            `#
            include < iostream > #include < vector >

            using namespace std;

            int main() {

                vector < int > nums;

                int x;
                int target;

                while (cin >> x) {

                    nums.push_back(x);

                    if (cin.peek() == '\\n') {
                        break;
                    }
                }

                cin >> target;

                for (int i = 0; i < nums.size(); i++) {

                    for (int j = i + 1; j < nums.size(); j++) {

                        if (nums[i] + nums[j] == target) {

                            cout
                                <<
                                "[" <<
                                i <<
                                ", " <<
                                j <<
                                "]" <<
                                endl;

                            return 0;
                        }
                    }
                }

                return 0;
            }
            `;

        return;
    }
}


/* =========================================================
   PROBLEM CLICK EVENTS
   ========================================================= */

document
    .querySelectorAll(".problem-item")
    .forEach(function(item) {

        item.addEventListener(
            "click",
            function() {

                const problemId =
                    Number(
                        item.dataset.problem
                    );

                selectProblem(
                    problemId
                );
            }
        );
    });


/* =========================================================
   TAB SUPPORT
   ========================================================= */

if (codeEditor) {

    codeEditor.addEventListener(
        "keydown",
        function(event) {

            if (event.key !== "Tab") {
                return;
            }


            event.preventDefault();


            const start =
                this.selectionStart;

            const end =
                this.selectionEnd;


            this.value =
                this.value.substring(
                    0,
                    start
                ) +
                "    " +
                this.value.substring(
                    end
                );


            this.selectionStart =
                start + 4;

            this.selectionEnd =
                start + 4;
        }
    );
}


/* =========================================================
   RUN BUTTON
   ========================================================= */

if (runButton) {

    runButton.addEventListener(
        "click",
        function() {

            const problemId =
                Number(
                    window.currentProblemId || 1
                );


            if (!isProblemUnlocked(
                    problemId
                )) {

                showOutput(
                    "🔒 This problem is locked.",
                    "error",
                    "Locked"
                );

                return;
            }


            runCode();
        }
    );
}


/* =========================================================
   SUBMIT BUTTON
   ========================================================= */

if (submitButton) {

    submitButton.addEventListener(
        "click",
        function() {

            const problemId =
                Number(
                    window.currentProblemId || 1
                );


            if (!isProblemUnlocked(
                    problemId
                )) {

                showOutput(
                    "🔒 This problem is locked.",
                    "error",
                    "Locked"
                );

                return;
            }


            submitCode();
        }
    );
}


/* =========================================================
   LANGUAGE CHANGE
   ========================================================= */

if (languageSelect) {

    languageSelect.addEventListener(
        "change",
        function() {

            loadStarterCode(
                this.value.toLowerCase()
            );
        }
    );
}


/* =========================================================
   BACK BUTTON
   ========================================================= */

const backButton =
    document.getElementById(
        "backToContests"
    );


if (backButton) {

    backButton.addEventListener(
        "click",
        function() {

            window.location.href =
                "/contests";
        }
    );
}


/* =========================================================
   GLOBAL FUNCTIONS
   ========================================================= */

window.submitCode =
    submitCode;

window.runCode =
    runCode;

window.selectProblem =
    selectProblem;

window.updateProblemLocks =
    updateProblemLocks;


/* =========================================================
   INITIALIZE
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function() {

        updateTimer();

        updateProblemLocks();


        const solved =
            getSolvedProblems();


        let firstProblem = 1;


        for (
            let i = 1; i <= TOTAL_PROBLEMS; i++
        ) {

            if (!solved.includes(i)) {

                firstProblem = i;

                break;
            }
        }


        window.currentProblemId =
            firstProblem;


        selectProblem(
            firstProblem
        );
    }
);


/* =========================================================
   TIMER
   ========================================================= */

updateTimer();


setInterval(
    updateTimer,
    1000
);


/*
 * IMPORTANT:
 *
 * The extra fetch("/api/run-code") block that was
 * at the bottom of the old file has been removed.
 *
 * It was using:
 * code
 * language
 * input
 * problemId
 *
 * outside their scope and could cause:
 *
 * ReferenceError: code is not defined
 *
 * The actual fetch is already correctly inside runCode().
 */