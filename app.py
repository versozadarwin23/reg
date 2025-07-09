from flask import Flask, render_template_string, request, jsonify
import requests
import time
from datetime import datetime, timedelta
import re
from concurrent.futures import ThreadPoolExecutor # For parallel processing
from functools import partial # Not strictly needed for this pattern, but useful for more complex scenarios

app = Flask(__name__)

# --- Server-side storage for token last usage ---
# Key: access_token, Value: last_used_timestamp (e.g., datetime object)
token_last_used = {}
# --- End of new additions for token usage tracking ---

# --- Create a ThreadPoolExecutor for handling concurrent Facebook API requests ---
# Adjust max_workers based on your needs and system resources.
# 10 workers mean 10 Facebook API calls can happen simultaneously.
executor = ThreadPoolExecutor(max_workers=10)

# The HTML content as a Python string (unchanged, will add info to 'about' section below)
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook Reaction & Comment Tool By: Dars</title>
    <style>
        html, body {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            background-color: #f0f2f5;
            font-family: Arial, sans-serif;
        }
        h2 {
            color: #1877f2;
            text-align: center;
            margin-top: 20px;
            margin-bottom: 20px;
            font-size: 2em; /* Default for larger screens */
        }
        .nav {
            display: flex;
            justify-content: center;
            background: #1877f2;
            padding: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap; /* Allow buttons to wrap on smaller screens */
        }
        .nav button {
            background: white;
            border: none;
            padding: 10px 20px;
            margin: 5px; /* Adjust margin for wrapped buttons */
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            color: #1877f2;
            transition: background-color 0.3s ease;
            white-space: nowrap; /* Prevent text wrapping within buttons */
        }
        .nav button.active {
            background: #145dbf;
            color: white;
        }
        .container {
            max-width: 900px;
            width: 90%;
            background: white;
            padding: 20px 30px;
            margin: 20px auto;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        label {
            display: block;
            margin-top: 18px;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }
        input[type="text"],
        input[type="file"],
        select,
        textarea,
        input[type="number"] {
            width: 100%;
            padding: 10px 12px;
            border-radius: 5px;
            border: 1px solid #ddd;
            font-size: 14px;
            box-sizing: border-box;
            transition: border-color 0.3s ease;
        }
        input[type="text"]:focus,
        input[type="file"]:focus,
        select:focus,
        textarea:focus,
        input[type="number"]:focus {
            border-color: #1877f2;
            outline: none;
        }
        button {
            background-color: #1877f2;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 25px;
            font-size: 16px;
            font-weight: bold;
            transition: background-color 0.3s ease;
            width: auto; /* Allow buttons to size based on content */
        }
        button:hover {
            background-color: #145dbf;
        }
        #clearLogBtn, #clearCommentLogBtn, #clearShareLogBtn, #clearCommentReactionLogBtn {
            background-color: #888;
            margin-top: 15px;
        }
        #clearLogBtn:hover, #clearCommentLogBtn:hover, #clearShareLogBtn:hover, #clearCommentReactionLogBtn:hover {
            background-color: #666;
        }
        #result, #commentResult, #shareResult, #commentReactionResult {
            background: #f6f6f6;
            padding: 15px;
            border-radius: 5px;
            margin-top: 30px;
            font-size: 14px;
            min-height: 50px;
            max-height: 400px;
            overflow-y: auto;
            white-space: pre-wrap;
            border: 1px solid #eee;
        }
        #result strong, #commentResult strong, #shareResult strong, #commentReactionResult strong {
            display: block;
            margin-bottom: 10px;
            color: #555;
        }
        .log-entry {
            padding: 8px 0;
            border-bottom: 1px dashed #eee;
        }
        .log-entry:last-child {
            border-bottom: none;
        }
        .log-entry.success { color: green; }
        .log-entry.error { color: red; }
        .log-entry.info { color: gray; }
        .page {
            display: none;
        }
        .page.active {
            display: block;
        }
        .link-path-row {
            display: flex;
            gap: 15px;
            align-items: flex-end;
            margin-top: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #f0f0f0;
            flex-wrap: wrap; /* Allow columns to wrap on smaller screens */
        }
        .link-path-row:last-of-type {
            border-bottom: none;
        }
        .link-path-column {
            flex: 1;
            min-width: 250px; /* Ensure columns don't get too small before wrapping */
        }
        .link-path-column label {
            margin-top: 0;
            margin-bottom: 8px;
        }
        .remove-row-btn {
            background-color: #dc3545;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            margin-top: 0;
            width: auto;
            white-space: nowrap;
            align-self: center;
            height: 40px;
            line-height: 24px;
        }
        .remove-row-btn:hover {
            background-color: #c82333;
        }
        #addLinkPathBtn, #addReactionLinkPathBtn, #addShareLinkPathBtn, #addCommentReactionLinkPathBtn {
            background-color: #28a745;
            margin-top: 30px;
        }
        #addLinkPathBtn:hover, #addReactionLinkPathBtn:hover, #addShareLinkPathBtn:hover, #addCommentReactionLinkPathBtn:hover {
            background-color: #218838;
        }
        /* Styles for About Page */
        #aboutPage .container {
            padding: 40px;
            text-align: center;
        }
        #aboutPage h3 {
            color: #1877f2;
            font-size: 2em;
            margin-bottom: 20px;
        }
        #aboutPage p {
            font-size: 1.1em;
            line-height: 1.6;
            color: #555;
            margin-bottom: 15px;
            text-align: left;
        }
        #aboutPage ul {
            list-style: none;
            padding: 0;
            margin-top: 30px;
            text-align: left;
        }
        #aboutPage ul li {
            background: #e9f2ff;
            margin-bottom: 10px;
            padding: 10px 15px;
            border-radius: 5px;
            color: #333;
            font-weight: bold;
            display: flex;
            align-items: center;
        }
        #aboutPage ul li::before {
            content: '✨'; /* Sparkle emoji or other suitable icon */
            margin-right: 10px;
        }

        /* Social Media Links */
        .social-links {
            margin-top: 30px;
            text-align: center;
        }
        .social-links a {
            display: inline-block;
            background-color: #1877f2;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
            font-weight: bold;
            margin: 0 10px;
            transition: background-color 0.3s ease;
        }
        .social-links a.telegram {
            background-color: #0088cc;
        }
        .social-links a:hover {
            background-color: #145dbf;
        }
        .social-links a.telegram:hover {
            background-color: #006699;
        }


        /* --- Responsive Adjustments --- */
        @media (max-width: 768px) {
            h2 {
                font-size: 1.5em;
            }
            .nav {
                flex-direction: column; /* Stack buttons vertically on small screens */
                padding: 10px 0;
            }
            .nav button {
                width: 90%; /* Make buttons full width */
                margin: 5px auto; /* Center buttons */
            }
            .container {
                width: 95%;
                padding: 15px;
                margin: 10px auto;
            }
            .link-path-row {
                flex-direction: column; /* Stack columns vertically */
                gap: 10px;
                align-items: stretch; /* Stretch items to full width */
            }
            .link-path-column {
                min-width: unset; /* Remove min-width constraint */
                width: 100%; /* Take full width */
            }
            .remove-row-btn {
                width: 100%; /* Make remove button full width */
                margin-top: 10px;
            }
            button {
                padding: 10px 15px;
                font-size: 14px;
            }
            #aboutPage .container {
                padding: 20px;
            }
            #aboutPage h3 {
                font-size: 1.5em;
            }
            #aboutPage p {
                font-size: 1em;
            }
            .social-links a {
                display: block;
                margin: 10px auto;
                width: 80%;
            }
        }

        @media (max-width: 480px) {
            h2 {
                font-size: 1.2em;
            }
            .container {
                padding: 10px;
            }
            label {
                font-size: 0.9em;
            }
            input[type="text"],
            input[type="file"],
            select,
            textarea,
            input[type="number"] {
                font-size: 12px;
                padding: 8px 10px;
            }
            button {
                padding: 8px 12px;
                font-size: 13px;
            }
        }
    </style>
</head>
<body>
    <h2>📣 Facebook Tool By: Dars: V1</h2>

    <div class="nav">
        <button id="navReaction" class="active">❤️ Reaction Tool</button>
        <button id="navComment">💬 Comment Tool</button>
        <button id="navCommentReaction">👍 Upvotes Tool</button>
        <button id="navShare">↗️ Sharing Tool</button>
        <button id="navAbout">ℹ️ About</button>
    </div>

    <div id="reactionPage" class="page active">
        <div class="container">
            <label for="tokenFile">📄 Load Access Tokens from File</label>
            <input type="file" id="tokenFile" accept=".txt" />

            <label for="accessToken">🔑 Access Token (currently loaded)</label>
            <input type="text" id="accessToken" placeholder="Loaded access token" readonly>

            <div id="reactionLinkPathContainer">
            </div>

            <button type="button" id="addReactionLinkPathBtn">➕ Add Another Post Link</button>

            <button id="sendReactionBtn">✅ Send Post Reactions</button>
            <button id="clearLogBtn" style="background-color: #888; margin-top: 10px;">🗑️ Clear Post Reaction History</button>

            <div id="result">
                <strong>🗂️ Post Reaction History:</strong>
                <div id="log"></div>
            </div>
        </div>
    </div>

    <div id="commentPage" class="page">
        <div class="container">
            <label for="commentTokenFile">📄 Load Access Tokens from File</label>
            <input type="file" id="commentTokenFile" accept=".txt" />

            <label for="commentToken">🔑 Access Token (currently loaded)</label>
            <input type="text" id="commentToken" placeholder="Loaded access token" readonly>

            <div id="linkPathContainer">
            </div>

            <button type="button" id="addLinkPathBtn">➕ Add Another Post Link</button>

            <button id="sendCommentBtn">✅ Send Comments</button>
            <button id="clearCommentLogBtn" style="background-color: #888; margin-top: 10px;">🗑️ Clear Comment Log</button>

            <div id="commentResult">
                <strong>🗂️ Comment History:</strong>
                <div id="commentLog"></div>
            </div>
        </div>
    </div>

    <div id="commentReactionPage" class="page">
        <div class="container">
            <label for="commentReactionTokenFile">📄 Load Access Tokens from File</label>
            <input type="file" id="commentReactionTokenFile" accept=".txt" />

            <label for="commentReactionAccessToken">🔑 Access Token (currently loaded)</label>
            <input type="text" id="commentReactionAccessToken" placeholder="Loaded access token" readonly>

            <div id="commentReactionLinkPathContainer">
            </div>

            <button type="button" id="addCommentReactionLinkPathBtn">➕ Add Another Comment Link</button>

            <button id="sendCommentReactionBtn">✅ Send Comment Reactions</button>
            <button id="clearCommentReactionLogBtn" style="background-color: #888; margin-top: 10px;">🗑️ Clear Comment Reaction History</button>

            <div id="commentReactionResult">
                <strong>🗂️ Comment Reaction History:</strong>
                <div id="commentReactionLog"></div>
            </div>
        </div>
    </div>

    <div id="sharePage" class="page">
        <div class="container">
            <label for="shareTokenFile">📄 Load Access Tokens from File</label>
            <input type="file" id="shareTokenFile" accept=".txt" />

            <label for="shareAccessToken">🔑 Access Token (currently loaded)</label>
            <input type="text" id="shareAccessToken" placeholder="Loaded access token" readonly>

            <div id="shareLinkPathContainer">
            </div>

            <button type="button" id="addShareLinkPathBtn">➕ Add Another Post Link to Share</button>

            <button id="sendShareBtn">✅ Share Page</button>
            <button id="clearShareLogBtn" style="background-color: #888; margin-top: 10px;">🗑️ Clear Share Log</button>

            <div id="shareResult">
                <strong>🗂️ Share History:</strong>
                <div id="shareLog"></div>
            </div>
        </div>
    </div>

    <div id="aboutPage" class="page">
        <div class="container">
            <h3>About This Facebook Tool by Dars</h3>
            <p>Welcome to the **Facebook Tool by Dars: V1**! This application is designed to streamline your interactions on Facebook by automating reactions, comments, and shares. Built with simplicity and efficiency in mind, it provides a user-friendly interface to manage your engagement activities.</p>

            <p>Our goal is to help you save time and effort by providing a centralized platform for common Facebook tasks. Whether you're managing multiple pages, conducting marketing campaigns, or simply want to interact more efficiently, this tool is here to assist you.</p>

            <h4>Key Features:</h4>
            <ul>
                <li><strong>❤️ Reaction Tool:</strong> Easily send various reactions (Like, Love, Wow, Haha, Sad, Angry, Care) to multiple Facebook posts.</li>
                <li><strong>💬 Comment Tool:</strong> Automate sending comments to specified Facebook posts using pre-defined messages from a file.</li>
                <li><strong>👍 Upvotes Tool:</strong> Specifically designed to send reactions (upvotes/likes) to individual comments on Facebook.</li>
                <li><strong>↗️ Sharing Tool:</strong> Facilitate the sharing of Facebook posts to different destinations.</li>
                <li><strong>Token Management:</strong> Securely load and manage access tokens from text files for streamlined operations.</li>
                <li><strong>Real-time Logging:</strong> Keep track of all your activities with detailed success and error logs.</li>
                <li><strong>⏳ Daily Token Usage Limit:</strong> Each access token can only be used once every 24 hours to ensure fair usage and prevent potential abuse.</li>
            </ul>

            <p>We are continuously working to improve and expand the functionalities of this tool. Your feedback is invaluable as we strive to make it even better.</p>

            <div class="social-links">
                <a href="https://www.facebook.com/darwinversoza139" target="_blank">Facebook</a>
                <a href="https://t.me/versozadarwin" target="_blank" class="telegram">Telegram</a>
            </div>

            <p>Thank you for using the Facebook Tool by Dars!</p>
        </div>
    </div>

    <script>
        // --- Page Navigation and Last Visit Storage ---
        // Navigation
        document.getElementById('navReaction').addEventListener('click', () => switchPage('reaction'));
        document.getElementById('navComment').addEventListener('click', () => switchPage('comment'));
        document.getElementById('navCommentReaction').addEventListener('click', () => switchPage('commentReaction'));
        document.getElementById('navShare').addEventListener('click', () => switchPage('share'));
        document.getElementById('navAbout').addEventListener('click', () => switchPage('about')); // Added About navigation

        function switchPage(page) {
            // Remove 'active' from all pages and nav buttons
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.nav button').forEach(btn => btn.classList.remove('active'));

            // Add 'active' to the selected page and nav button
            document.getElementById(`${page}Page`).classList.add('active');
            document.getElementById(`nav${page.charAt(0).toUpperCase() + page.slice(1)}`).classList.add('active');

            // Store the last visited page in localStorage
            localStorage.setItem('lastVisitedPage', page);
        }

        // On page load, retrieve the last visited page and switch to it
        document.addEventListener('DOMContentLoaded', () => {
            const lastVisitedPage = localStorage.getItem('lastVisitedPage');
            if (lastVisitedPage) {
                switchPage(lastVisitedPage);
            } else {
                // If no last visited page is found, default to 'reaction'
                switchPage('reaction');
            }
        });

        // --- Core Facebook API Interaction (Client-side via Flask backend) ---

        // We will move the actual API calls to the Flask backend to avoid CORS and token exposure.
        // The JavaScript will send requests to our Flask app, and Flask will then make the requests to Facebook.

        // Shared postId resolver function - this will now call our Flask backend
        async function resolveObjectId(rawInput, token) {
            const response = await fetch('/resolve-object-id', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ raw_input: rawInput, access_token: token }),
            });
            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }
            return data.object_id;
        }

        // --- Post Reaction Tool ---
        let accessTokens = [];
        const reactionLinkPathData = [];
        let reactionLinkCounter = 0;

        function addLog(message, type) {
            const logContainer = document.getElementById('log');
            const entry = document.createElement('div');
            entry.classList.add('log-entry');
            if (type) entry.classList.add(type);
            entry.textContent = message;
            logContainer.appendChild(entry);
            document.getElementById('result').scrollTop = document.getElementById('result').scrollHeight;
        }

        document.getElementById('tokenFile').addEventListener('change', function () {
            const file = this.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = function (e) {
                accessTokens = e.target.result.split(/\\r?\\n/).map(line => line.trim()).filter(line => line.length > 0);
                if (accessTokens.length > 0) {
                    document.getElementById('accessToken').value = accessTokens[0];
                    addLog(`Loaded ${accessTokens.length} access tokens.`, 'info');
                } else {
                    addLog('No access tokens found in the file.', 'error');
                }
            };
            reader.readAsText(file);
        });

        function addReactionLinkPathRow(initialLink = '', initialReactionType = 'LIKE', initialMaxReactions = '') {
            reactionLinkCounter++;
            const rowId = `reaction-link-row-${reactionLinkCounter}`;
            const container = document.getElementById('reactionLinkPathContainer');

            const rowDiv = document.createElement('div');
            rowDiv.className = 'link-path-row';
            rowDiv.id = rowId;

            rowDiv.innerHTML = `
                <div class="link-path-column">
                    <label for="reactionLinkInput-${reactionLinkCounter}">🔗 Facebook Post ID/URL</label>
                    <input type="text" id="reactionLinkInput-${reactionLinkCounter}" placeholder="Enter Post ID or URL here" value="${initialLink}">
                </div>
                <div class="link-path-column">
                    <label for="reactionType-${reactionLinkCounter}">❤️ Choose Reaction</label>
                    <select id="reactionType-${reactionLinkCounter}">
                        <option value="LIKE">👍 Like</option>
                        <option value="LOVE">❤️ Love</option>
                        <option value="WOW">😮 Wow</option>
                        <option value="HAHA">😂 Haha</option>
                        <option value="SAD">😢 Sad</option>
                        <option value="ANGRY">😡 Angry</option>
                        <option value="CARE">🤗 Care</option>
                    </select>
                </div>
                <div class="link-path-column">
                    <label for="maxReactions-${reactionLinkCounter}">🎯 Max Reactions</label>
                    <input type="number" id="maxReactions-${reactionLinkCounter}" min="0" value="${initialMaxReactions}" placeholder="Enter max reactions">
                </div>
                <button type="button" class="remove-row-btn" data-row-id="${rowId}">➖ Remove</button>
            `;
            container.appendChild(rowDiv);

            const reactionTypeSelect = document.getElementById(`reactionType-${reactionLinkCounter}`);
            reactionTypeSelect.value = initialReactionType;

            // Store a reference to this row's data in the array
            const newRowData = { id: rowId, link: initialLink, reactionType: initialReactionType, successCount: 0, maxReactions: parseInt(initialMaxReactions, 10) || 0 };
            reactionLinkPathData.push(newRowData);

            rowDiv.querySelector('.remove-row-btn').addEventListener('click', function() {
                const rowIdToRemove = this.dataset.rowId;
                const indexToRemove = reactionLinkPathData.findIndex(item => item.id === rowIdToRemove);
                if (indexToRemove > -1) {
                    reactionLinkPathData.splice(indexToRemove, 1);
                }
                document.getElementById(rowIdToRemove).remove();
                addLog(`Removed reaction link row "${rowIdToRemove}".`, 'info');
            });

            document.getElementById(`reactionLinkInput-${reactionLinkCounter}`).addEventListener('input', function() {
                newRowData.link = this.value.trim();
            });

            document.getElementById(`reactionType-${reactionLinkCounter}`).addEventListener('change', function() {
                newRowData.reactionType = this.value;
            });

            document.getElementById(`maxReactions-${reactionLinkCounter}`).addEventListener('input', function() {
                newRowData.maxReactions = parseInt(this.value, 10) || 0;
            });
        }

        document.addEventListener('DOMContentLoaded', () => {
            // Initialize with one row for each tool
            addReactionLinkPathRow();
            addCommentLinkPathRow();
            addCommentReactionLinkPathRow();
            addShareLinkPathRow();

            // Set initial active page based on localStorage or default
            const lastVisitedPage = localStorage.getItem('lastVisitedPage');
            if (lastVisitedPage) {
                switchPage(lastVisitedPage);
            } else {
                switchPage('reaction'); // Default to reaction page if no last visited page
            }
        });

        document.getElementById('addReactionLinkPathBtn').addEventListener('click', () => {
            addReactionLinkPathRow();
        });

        document.getElementById('sendReactionBtn').addEventListener('click', async () => {
            const sendBtn = document.getElementById('sendReactionBtn');

            if (accessTokens.length === 0) {
                addLog('⚠️ Please load Access Tokens from a file first.', 'error');
                return;
            }

            // Reset success counts for new run
            reactionLinkPathData.forEach(item => item.successCount = 0);
            const activeReactionLinkData = reactionLinkPathData.filter(item => item.link);

            if (activeReactionLinkData.length === 0) {
                addLog('⚠️ Please add at least one Post ID/URL for reactions.', 'error');
                return;
            }

            sendBtn.disabled = true;
            sendBtn.textContent = "⏳ Sending reactions...";

            let overallSuccessCount = 0;
            let overallErrorCount = 0;
            let tasksToSend = [];

            // Prepare all tasks including resolving object IDs first (sequentially, or in parallel if needed)
            addLog("⚙️ Resolving object IDs and checking token usage...", "info");
            for (const token of accessTokens) {
                // Check token usage *before* preparing tasks for this token
                const tokenCheckResponse = await fetch('/check-token-usage', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ access_token: token })
                });
                const tokenCheckData = await tokenCheckResponse.json();

                if (!tokenCheckData.can_use) {
                    addLog(`❌ Access Token already used today. Please wait 24 hours: ${tokenCheckData.wait_until}`, "error");
                    overallErrorCount++;
                    continue; // Skip this token
                }

                for (let j = 0; j < activeReactionLinkData.length; j++) {
                    const entry = activeReactionLinkData[j];
                    const rawInput = entry.link;
                    const reactionType = entry.reactionType;
                    const maxReactions = entry.maxReactions;

                    if (maxReactions > 0 && entry.successCount >= maxReactions) {
                        addLog(`✅ Max reactions (${maxReactions}) reached for Link ${j + 1} ("${rawInput}"). Skipping further reactions for this link.`, "info");
                        continue;
                    }

                    let objectId;
                    try {
                        objectId = await resolveObjectId(rawInput, token); // Use resolveObjectId
                        // Add task to the list to be sent in a batch
                        tasksToSend.push({ object_id: objectId, reaction_type: reactionType, access_token: token, link_index: j });
                    } catch (e) {
                        addLog(`❌ Error resolving Post ID/URL for Link ${j + 1} ("${rawInput}") with token ${token.substring(0,10)}...: ${e.message}`, 'error');
                        overallErrorCount++;
                        // Do not add this task to tasksToSend if resolution failed
                    }
                }
            }

            if (tasksToSend.length === 0) {
                 addLog("No valid tasks to send after ID resolution and token checks.", "info");
                 sendBtn.disabled = false;
                 sendBtn.textContent = "✅ Send Post Reactions";
                 return;
            }

            addLog(`🚀 Sending ${tasksToSend.length} reaction tasks to backend for parallel processing...`, "info");
            try {
                // Send all collected tasks in one go to the backend
                const response = await fetch('/send-reaction', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ tasks: tasksToSend }) // Send the array of tasks
                });
                const results = await response.json(); // Backend returns an array of results

                // Process results from the backend
                results.forEach((result, index) => {
                    const originalTask = tasksToSend[index]; // Get original task data to link back to frontend data
                    const linkIndex = originalTask.link_index; // Get the original index from the task
                    const entry = activeReactionLinkData[linkIndex]; // Reference the correct entry in activeReactionLinkData

                    if (result.success === true) {
                        addLog(`✅ Reaction: ${originalTask.reaction_type} success for Post Link ${linkIndex + 1} ("${originalTask.object_id}")`, "success");
                        entry.successCount++;
                        overallSuccessCount++;
                    } else {
                        addLog(`❌ Reaction failed for Post Link ${linkIndex + 1} ("${originalTask.object_id}"). Error: ${result.error ? result.error : 'Unknown error'}`, "error");
                        overallErrorCount++;
                    }
                });

            } catch (fetchError) {
                addLog(`❌ Network error when sending batch reactions: ${fetchError.message}`, "error");
                overallErrorCount += tasksToSend.length; // Assume all failed if the batch send failed
            }

            addLog(`--- Post Reaction Process Finished ---`, 'info');
            activeReactionLinkData.forEach((item, index) => {
                const targetText = item.maxReactions > 0 ? ` (Target: ${item.maxReactions})` : ` (No max limit)`;
                addLog(`✅ Total Successful Reactions for Post Link ${index + 1} ("${item.link}"): ${item.successCount}${targetText}`, "info");
            });
            addLog(`✅ Overall Total Successful Post Reactions: ${overallSuccessCount}`, "info");
            addLog(`❌ Overall Total Failed Post Reactions: ${overallErrorCount}`, "error");
            sendBtn.disabled = false;
            sendBtn.textContent = "✅ Send Post Reactions";
        });

        document.getElementById('clearLogBtn').addEventListener('click', () => {
            document.getElementById('log').innerHTML = '';
            addLog('Post Reaction history cleared.', 'info');
        });

        // --- Comment Tool ---
        let commentTokens = [];
        const commentLinkPathData = [];
        let commentLinkCounter = 0;

        function addCommentLog(message, type) {
            const logContainer = document.getElementById('commentLog');
            const entry = document.createElement('div');
            entry.classList.add('log-entry');
            if (type) entry.classList.add(type);
            entry.textContent = message;
            logContainer.appendChild(entry);
            document.getElementById('commentResult').scrollTop = document.getElementById('commentResult').scrollHeight;
        }

        document.getElementById('commentTokenFile').addEventListener('change', function () {
            const file = this.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function (e) {
                commentTokens = e.target.result
                    .split(/\\r?\\n/)
                    .map(line => line.trim())
                    .filter(line => line.length > 0);

                if (commentTokens.length > 0) {
                    document.getElementById('commentToken').value = commentTokens[0];
                    addCommentLog(`Loaded ${commentTokens.length} access tokens.`, 'info');
                } else {
                    addCommentLog('No access tokens found in the file.', 'error');
                }
            };
            reader.readAsText(file);
        });

        function addCommentLinkPathRow(initialLink = '', initialCommentMessage = '', initialMaxComments = '') {
            commentLinkCounter++;
            const rowId = `comment-link-row-${commentLinkCounter}`;
            const container = document.getElementById('linkPathContainer');

            const rowDiv = document.createElement('div');
            rowDiv.className = 'link-path-row';
            rowDiv.id = rowId;

            rowDiv.innerHTML = `
                <div class="link-path-column">
                    <label for="commentLinkInput-${commentLinkCounter}">🔗 Facebook Post ID/URL</label>
                    <input type="text" id="commentLinkInput-${commentLinkCounter}" placeholder="Enter Post ID or URL here" value="${initialLink}">
                </div>
                <div class="link-path-column">
                    <label for="commentMessage-${commentLinkCounter}">💬 Comment Message</label>
                    <textarea id="commentMessage-${commentLinkCounter}" rows="2" placeholder="Enter your comment here">${initialCommentMessage}</textarea>
                </div>
                <div class="link-path-column">
                    <label for="maxComments-${commentLinkCounter}">🎯 Max Comments per Token</label>
                    <input type="number" id="maxComments-${commentLinkCounter}" min="0" value="${initialMaxComments}" placeholder="Enter max comments">
                </div>
                <button type="button" class="remove-row-btn" data-row-id="${rowId}">➖ Remove</button>
            `;
            container.appendChild(rowDiv);

            const newRowData = { id: rowId, link: initialLink, commentMessage: initialCommentMessage, successCount: 0, maxComments: parseInt(initialMaxComments, 10) || 0 };
            commentLinkPathData.push(newRowData);

            rowDiv.querySelector('.remove-row-btn').addEventListener('click', function() {
                const rowIdToRemove = this.dataset.rowId;
                const indexToRemove = commentLinkPathData.findIndex(item => item.id === rowIdToRemove);
                if (indexToRemove > -1) {
                    commentLinkPathData.splice(indexToRemove, 1);
                }
                document.getElementById(rowIdToRemove).remove();
                addCommentLog(`Removed comment link row "${rowIdToRemove}".`, 'info');
            });

            document.getElementById(`commentLinkInput-${commentLinkCounter}`).addEventListener('input', function() {
                newRowData.link = this.value.trim();
            });

            document.getElementById(`commentMessage-${commentLinkCounter}`).addEventListener('input', function() {
                newRowData.commentMessage = this.value.trim();
            });

            document.getElementById(`maxComments-${commentLinkCounter}`).addEventListener('input', function() {
                newRowData.maxComments = parseInt(this.value, 10) || 0;
            });
        }

        document.getElementById('addLinkPathBtn').addEventListener('click', () => {
            addCommentLinkPathRow();
        });

        document.getElementById('sendCommentBtn').addEventListener('click', async () => {
            const sendBtn = document.getElementById('sendCommentBtn');

            if (commentTokens.length === 0) {
                addCommentLog('⚠️ Please load Access Tokens from a file first.', 'error');
                return;
            }

            commentLinkPathData.forEach(item => item.successCount = 0);
            const activeCommentLinkData = commentLinkPathData.filter(item => item.link && item.commentMessage);

            if (activeCommentLinkData.length === 0) {
                addCommentLog('⚠️ Please add at least one Post ID/URL and comment message.', 'error');
                return;
            }

            sendBtn.disabled = true;
            sendBtn.textContent = "⏳ Sending comments...";

            let overallSuccessCount = 0;
            let overallErrorCount = 0;
            let tasksToSend = [];

            addCommentLog("⚙️ Resolving object IDs and checking token usage...", "info");
            for (const token of commentTokens) {
                const tokenCheckResponse = await fetch('/check-token-usage', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ access_token: token })
                });
                const tokenCheckData = await tokenCheckResponse.json();

                if (!tokenCheckData.can_use) {
                    addCommentLog(`❌ Access Token already used today. Please wait 24 hours: ${tokenCheckData.wait_until}`, "error");
                    overallErrorCount++;
                    continue;
                }

                for (let j = 0; j < activeCommentLinkData.length; j++) {
                    const entry = activeCommentLinkData[j];
                    const rawInput = entry.link;
                    const message = entry.commentMessage;
                    const maxComments = entry.maxComments;

                    if (maxComments > 0 && entry.successCount >= maxComments) {
                        addCommentLog(`✅ Max comments (${maxComments}) reached for Link ${j + 1} ("${rawInput}"). Skipping further comments for this link.`, "info");
                        continue;
                    }

                    let objectId;
                    try {
                        objectId = await resolveObjectId(rawInput, token);
                        tasksToSend.push({ object_id: objectId, message: message, access_token: token, link_index: j });
                    } catch (e) {
                        addCommentLog(`❌ Error resolving Post ID/URL for Link ${j + 1} ("${rawInput}") with token ${token.substring(0,10)}...: ${e.message}`, 'error');
                        overallErrorCount++;
                    }
                }
            }

            if (tasksToSend.length === 0) {
                 addCommentLog("No valid tasks to send after ID resolution and token checks.", "info");
                 sendBtn.disabled = false;
                 sendBtn.textContent = "✅ Send Comments";
                 return;
            }

            addCommentLog(`🚀 Sending ${tasksToSend.length} comment tasks to backend for parallel processing...`, "info");
            try {
                const response = await fetch('/send-comment', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ tasks: tasksToSend })
                });
                const results = await response.json();

                results.forEach((result, index) => {
                    const originalTask = tasksToSend[index];
                    const linkIndex = originalTask.link_index;
                    const entry = activeCommentLinkData[linkIndex];

                    if (result.success === true) {
                        addCommentLog(`✅ Comment success for Post Link ${linkIndex + 1} ("${originalTask.object_id}")`, "success");
                        entry.successCount++;
                        overallSuccessCount++;
                    } else {
                        addCommentLog(`❌ Comment failed for Post Link ${linkIndex + 1} ("${originalTask.object_id}"). Error: ${result.error ? result.error : 'Unknown error'}`, "error");
                        overallErrorCount++;
                    }
                });

            } catch (fetchError) {
                addCommentLog(`❌ Network error when sending batch comments: ${fetchError.message}`, "error");
                overallErrorCount += tasksToSend.length;
            }

            addCommentLog(`--- Comment Process Finished ---`, 'info');
            activeCommentLinkData.forEach((item, index) => {
                const targetText = item.maxComments > 0 ? ` (Target: ${item.maxComments})` : ` (No max limit)`;
                addCommentLog(`✅ Total Successful Comments for Post Link ${index + 1} ("${item.link}"): ${item.successCount}${targetText}`, "info");
            });
            addCommentLog(`✅ Overall Total Successful Comments: ${overallSuccessCount}`, "info");
            addCommentLog(`❌ Overall Total Failed Comments: ${overallErrorCount}`, "error");
            sendBtn.disabled = false;
            sendBtn.textContent = "✅ Send Comments";
        });

        document.getElementById('clearCommentLogBtn').addEventListener('click', () => {
            document.getElementById('commentLog').innerHTML = '';
            addCommentLog('Comment history cleared.', 'info');
        });

        // --- Comment Reaction Tool ---
        let commentReactionTokens = [];
        const commentReactionLinkPathData = [];
        let commentReactionLinkCounter = 0;

        function addCommentReactionLog(message, type) {
            const logContainer = document.getElementById('commentReactionLog');
            const entry = document.createElement('div');
            entry.classList.add('log-entry');
            if (type) entry.classList.add(type);
            entry.textContent = message;
            logContainer.appendChild(entry);
            document.getElementById('commentReactionResult').scrollTop = document.getElementById('commentReactionResult').scrollHeight;
        }

        document.getElementById('commentReactionTokenFile').addEventListener('change', function () {
            const file = this.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function (e) {
                commentReactionTokens = e.target.result
                    .split(/\\r?\\n/)
                    .map(line => line.trim())
                    .filter(line => line.length > 0);

                if (commentReactionTokens.length > 0) {
                    document.getElementById('commentReactionAccessToken').value = commentReactionTokens[0];
                    addCommentReactionLog(`Loaded ${commentReactionTokens.length} access tokens.`, 'info');
                } else {
                    addCommentReactionLog('No access tokens found in the file.', 'error');
                }
            };
            reader.readAsText(file);
        });

        function addCommentReactionLinkPathRow(initialLink = '', initialReactionType = 'LIKE', initialMaxReactions = '') {
            commentReactionLinkCounter++;
            const rowId = `comment-reaction-link-row-${commentReactionLinkCounter}`;
            const container = document.getElementById('commentReactionLinkPathContainer');

            const rowDiv = document.createElement('div');
            rowDiv.className = 'link-path-row';
            rowDiv.id = rowId;

            rowDiv.innerHTML = `
                <div class="link-path-column">
                    <label for="commentReactionLinkInput-${commentReactionLinkCounter}">🔗 Facebook Comment ID/URL</label>
                    <input type="text" id="commentReactionLinkInput-${commentReactionLinkCounter}" placeholder="Enter Comment ID or URL here" value="${initialLink}">
                </div>
                <div class="link-path-column">
                    <label for="commentReactionType-${commentReactionLinkCounter}">👍 Choose Reaction</label>
                    <select id="commentReactionType-${commentReactionLinkCounter}">
                        <option value="LIKE">👍 Like</option>
                        <option value="LOVE">❤️ Love</option>
                        <option value="WOW">😮 Wow</option>
                        <option value="HAHA">😂 Haha</option>
                        <option value="SAD">😢 Sad</option>
                        <option value="ANGRY">😡 Angry</option>
                        <option value="CARE">🤗 Care</option>
                    </select>
                </div>
                <div class="link-path-column">
                    <label for="maxCommentReactions-${commentReactionLinkCounter}">🎯 Max Reactions</label>
                    <input type="number" id="maxCommentReactions-${commentReactionLinkCounter}" min="0" value="${initialMaxReactions}" placeholder="Enter max reactions">
                </div>
                <button type="button" class="remove-row-btn" data-row-id="${rowId}">➖ Remove</button>
            `;
            container.appendChild(rowDiv);

            const reactionTypeSelect = document.getElementById(`commentReactionType-${commentReactionLinkCounter}`);
            reactionTypeSelect.value = initialReactionType;

            const newRowData = { id: rowId, link: initialLink, reactionType: initialReactionType, successCount: 0, maxReactions: parseInt(initialMaxReactions, 10) || 0 };
            commentReactionLinkPathData.push(newRowData);

            rowDiv.querySelector('.remove-row-btn').addEventListener('click', function() {
                const rowIdToRemove = this.dataset.rowId;
                const indexToRemove = commentReactionLinkPathData.findIndex(item => item.id === rowIdToRemove);
                if (indexToRemove > -1) {
                    commentReactionLinkPathData.splice(indexToRemove, 1);
                }
                document.getElementById(rowIdToRemove).remove();
                addCommentReactionLog(`Removed comment reaction link row "${rowIdToRemove}".`, 'info');
            });

            document.getElementById(`commentReactionLinkInput-${commentReactionLinkCounter}`).addEventListener('input', function() {
                newRowData.link = this.value.trim();
            });

            document.getElementById(`commentReactionType-${commentReactionLinkCounter}`).addEventListener('change', function() {
                newRowData.reactionType = this.value;
            });

            document.getElementById(`maxCommentReactions-${commentReactionLinkCounter}`).addEventListener('input', function() {
                newRowData.maxReactions = parseInt(this.value, 10) || 0;
            });
        }

        document.getElementById('addCommentReactionLinkPathBtn').addEventListener('click', () => {
            addCommentReactionLinkPathRow();
        });

        document.getElementById('sendCommentReactionBtn').addEventListener('click', async () => {
            const sendBtn = document.getElementById('sendCommentReactionBtn');

            if (commentReactionTokens.length === 0) {
                addCommentReactionLog('⚠️ Please load Access Tokens from a file first.', 'error');
                return;
            }

            commentReactionLinkPathData.forEach(item => item.successCount = 0);
            const activeCommentReactionLinkData = commentReactionLinkPathData.filter(item => item.link);

            if (activeCommentReactionLinkData.length === 0) {
                addCommentReactionLog('⚠️ Please add at least one Comment ID/URL for reactions.', 'error');
                return;
            }

            sendBtn.disabled = true;
            sendBtn.textContent = "⏳ Sending comment reactions...";

            let overallSuccessCount = 0;
            let overallErrorCount = 0;
            let tasksToSend = [];

            addCommentReactionLog("⚙️ Resolving object IDs and checking token usage...", "info");
            for (const token of commentReactionTokens) {
                const tokenCheckResponse = await fetch('/check-token-usage', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ access_token: token })
                });
                const tokenCheckData = await tokenCheckResponse.json();

                if (!tokenCheckData.can_use) {
                    addCommentReactionLog(`❌ Access Token already used today. Please wait 24 hours: ${tokenCheckData.wait_until}`, "error");
                    overallErrorCount++;
                    continue;
                }

                for (let j = 0; j < activeCommentReactionLinkData.length; j++) {
                    const entry = activeCommentReactionLinkData[j];
                    const rawInput = entry.link;
                    const reactionType = entry.reactionType;
                    const maxReactions = entry.maxReactions;

                    if (maxReactions > 0 && entry.successCount >= maxReactions) {
                        addCommentReactionLog(`✅ Max reactions (${maxReactions}) reached for Link ${j + 1} ("${rawInput}"). Skipping further reactions for this link.`, "info");
                        continue;
                    }

                    let objectId;
                    try {
                        objectId = await resolveObjectId(rawInput, token);
                        tasksToSend.push({ comment_id: objectId, reaction_type: reactionType, access_token: token, link_index: j });
                    } catch (e) {
                        addCommentReactionLog(`❌ Error resolving Comment ID/URL for Link ${j + 1} ("${rawInput}") with token ${token.substring(0,10)}...: ${e.message}`, 'error');
                        overallErrorCount++;
                    }
                }
            }

            if (tasksToSend.length === 0) {
                 addCommentReactionLog("No valid tasks to send after ID resolution and token checks.", "info");
                 sendBtn.disabled = false;
                 sendBtn.textContent = "✅ Send Comment Reactions";
                 return;
            }

            addCommentReactionLog(`🚀 Sending ${tasksToSend.length} comment reaction tasks to backend for parallel processing...`, "info");
            try {
                const response = await fetch('/send-comment-reaction', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ tasks: tasksToSend })
                });
                const results = await response.json();

                results.forEach((result, index) => {
                    const originalTask = tasksToSend[index];
                    const linkIndex = originalTask.link_index;
                    const entry = activeCommentReactionLinkData[linkIndex];

                    if (result.success === true) {
                        addCommentReactionLog(`✅ Reaction: ${originalTask.reaction_type} success for Comment Link ${linkIndex + 1} ("${originalTask.comment_id}")`, "success");
                        entry.successCount++;
                        overallSuccessCount++;
                    } else {
                        addCommentReactionLog(`❌ Reaction failed for Comment Link ${linkIndex + 1} ("${originalTask.comment_id}"). Error: ${result.error ? result.error : 'Unknown error'}`, "error");
                        overallErrorCount++;
                    }
                });

            } catch (fetchError) {
                addCommentReactionLog(`❌ Network error when sending batch comment reactions: ${fetchError.message}`, "error");
                overallErrorCount += tasksToSend.length;
            }

            addCommentReactionLog(`--- Comment Reaction Process Finished ---`, 'info');
            activeCommentReactionLinkData.forEach((item, index) => {
                const targetText = item.maxReactions > 0 ? ` (Target: ${item.maxReactions})` : ` (No max limit)`;
                addCommentReactionLog(`✅ Total Successful Reactions for Comment Link ${index + 1} ("${item.link}"): ${item.successCount}${targetText}`, "info");
            });
            addCommentReactionLog(`✅ Overall Total Successful Comment Reactions: ${overallSuccessCount}`, "info");
            addCommentReactionLog(`❌ Overall Total Failed Comment Reactions: ${overallErrorCount}`, "error");
            sendBtn.disabled = false;
            sendBtn.textContent = "✅ Send Comment Reactions";
        });

        document.getElementById('clearCommentReactionLogBtn').addEventListener('click', () => {
            document.getElementById('commentReactionLog').innerHTML = '';
            addCommentReactionLog('Comment Reaction history cleared.', 'info');
        });

        // --- Share Tool ---
        let shareTokens = [];
        const shareLinkPathData = [];
        let shareLinkCounter = 0;

        function addShareLog(message, type) {
            const logContainer = document.getElementById('shareLog');
            const entry = document.createElement('div');
            entry.classList.add('log-entry');
            if (type) entry.classList.add(type);
            entry.textContent = message;
            logContainer.appendChild(entry);
            document.getElementById('shareResult').scrollTop = document.getElementById('shareResult').scrollHeight;
        }

        document.getElementById('shareTokenFile').addEventListener('change', function () {
            const file = this.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function (e) {
                shareTokens = e.target.result
                    .split(/\\r?\\n/)
                    .map(line => line.trim())
                    .filter(line => line.length > 0);

                if (shareTokens.length > 0) {
                    document.getElementById('shareAccessToken').value = shareTokens[0];
                    addShareLog(`Loaded ${shareTokens.length} access tokens.`, 'info');
                } else {
                    addShareLog('No access tokens found in the file.', 'error');
                }
            };
            reader.readAsText(file);
        });

        function addShareLinkPathRow(initialLink = '', initialMaxShares = '') {
            shareLinkCounter++;
            const rowId = `share-link-row-${shareLinkCounter}`;
            const container = document.getElementById('shareLinkPathContainer');

            const rowDiv = document.createElement('div');
            rowDiv.className = 'link-path-row';
            rowDiv.id = rowId;

            rowDiv.innerHTML = `
                <div class="link-path-column">
                    <label for="shareLinkInput-${shareLinkCounter}">🔗 Facebook Post ID/URL to Share</label>
                    <input type="text" id="shareLinkInput-${shareLinkCounter}" placeholder="Enter Post ID or URL here" value="${initialLink}">
                </div>
                <div class="link-path-column">
                    <label for="maxShares-${shareLinkCounter}">🎯 Max Shares per Token</label>
                    <input type="number" id="maxShares-${shareLinkCounter}" min="0" value="${initialMaxShares}" placeholder="Enter max shares">
                </div>
                <button type="button" class="remove-row-btn" data-row-id="${rowId}">➖ Remove</button>
            `;
            container.appendChild(rowDiv);

            const newRowData = { id: rowId, link: initialLink, successCount: 0, maxShares: parseInt(initialMaxShares, 10) || 0 };
            shareLinkPathData.push(newRowData);

            rowDiv.querySelector('.remove-row-btn').addEventListener('click', function() {
                const rowIdToRemove = this.dataset.rowId;
                const indexToRemove = shareLinkPathData.findIndex(item => item.id === rowIdToRemove);
                if (indexToRemove > -1) {
                    shareLinkPathData.splice(indexToRemove, 1);
                }
                document.getElementById(rowIdToRemove).remove();
                addShareLog(`Removed share link row "${rowIdToRemove}".`, 'info');
            });

            document.getElementById(`shareLinkInput-${shareLinkCounter}`).addEventListener('input', function() {
                newRowData.link = this.value.trim();
            });

            document.getElementById(`maxShares-${shareLinkCounter}`).addEventListener('input', function() {
                newRowData.maxShares = parseInt(this.value, 10) || 0;
            });
        }

        document.getElementById('addShareLinkPathBtn').addEventListener('click', () => {
            addShareLinkPathRow();
        });

        document.getElementById('sendShareBtn').addEventListener('click', async () => {
            const sendBtn = document.getElementById('sendShareBtn');

            if (shareTokens.length === 0) {
                addShareLog('⚠️ Please load Access Tokens from a file first.', 'error');
                return;
            }

            shareLinkPathData.forEach(item => item.successCount = 0);
            const activeShareLinkData = shareLinkPathData.filter(item => item.link);

            if (activeShareLinkData.length === 0) {
                addShareLog('⚠️ Please add at least one Post ID/URL to share.', 'error');
                return;
            }

            sendBtn.disabled = true;
            sendBtn.textContent = "⏳ Sharing page...";

            let overallSuccessCount = 0;
            let overallErrorCount = 0;
            let tasksToSend = [];

            addShareLog("⚙️ Resolving object IDs and checking token usage...", "info");
            for (const token of shareTokens) {
                const tokenCheckResponse = await fetch('/check-token-usage', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ access_token: token })
                });
                const tokenCheckData = await tokenCheckResponse.json();

                if (!tokenCheckData.can_use) {
                    addShareLog(`❌ Access Token already used today. Please wait 24 hours: ${tokenCheckData.wait_until}`, "error");
                    overallErrorCount++;
                    continue;
                }

                for (let j = 0; j < activeShareLinkData.length; j++) {
                    const entry = activeShareLinkData[j];
                    const rawInput = entry.link;
                    const maxShares = entry.maxShares;

                    if (maxShares > 0 && entry.successCount >= maxShares) {
                        addShareLog(`✅ Max shares (${maxShares}) reached for Link ${j + 1} ("${rawInput}"). Skipping further shares for this link.`, "info");
                        continue;
                    }

                    let objectId;
                    try {
                        objectId = await resolveObjectId(rawInput, token);
                        tasksToSend.push({ object_id: objectId, access_token: token, link_index: j });
                    } catch (e) {
                        addShareLog(`❌ Error resolving Post ID/URL for Link ${j + 1} ("${rawInput}") with token ${token.substring(0,10)}...: ${e.message}`, 'error');
                        overallErrorCount++;
                    }
                }
            }

            if (tasksToSend.length === 0) {
                 addShareLog("No valid tasks to send after ID resolution and token checks.", "info");
                 sendBtn.disabled = false;
                 sendBtn.textContent = "✅ Share Page";
                 return;
            }

            addShareLog(`🚀 Sending ${tasksToSend.length} share tasks to backend for parallel processing...`, "info");
            try {
                const response = await fetch('/send-share', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ tasks: tasksToSend })
                });
                const results = await response.json();

                results.forEach((result, index) => {
                    const originalTask = tasksToSend[index];
                    const linkIndex = originalTask.link_index;
                    const entry = activeShareLinkData[linkIndex];

                    if (result.success === true) {
                        addShareLog(`✅ Share success for Post Link ${linkIndex + 1} ("${originalTask.object_id}")`, "success");
                        entry.successCount++;
                        overallSuccessCount++;
                    } else {
                        addShareLog(`❌ Share failed for Post Link ${linkIndex + 1} ("${originalTask.object_id}"). Error: ${result.error ? result.error : 'Unknown error'}`, "error");
                        overallErrorCount++;
                    }
                });

            } catch (fetchError) {
                addShareLog(`❌ Network error when sending batch shares: ${fetchError.message}`, "error");
                overallErrorCount += tasksToSend.length;
            }

            addShareLog(`--- Share Process Finished ---`, 'info');
            activeShareLinkData.forEach((item, index) => {
                const targetText = item.maxShares > 0 ? ` (Target: ${item.maxShares})` : ` (No max limit)`;
                addShareLog(`✅ Total Successful Shares for Post Link ${index + 1} ("${item.link}"): ${item.successCount}${targetText}`, "info");
            });
            addShareLog(`✅ Overall Total Successful Shares: ${overallSuccessCount}`, "info");
            addShareLog(`❌ Overall Total Failed Shares: ${overallErrorCount}`, "error");
            sendBtn.disabled = false;
            sendBtn.textContent = "✅ Share Page";
        });

        document.getElementById('clearShareLogBtn').addEventListener('click', () => {
            document.getElementById('shareLog').innerHTML = '';
            addShareLog('Share history cleared.', 'info');
        });
    </script>
</body>
</html>
"""

# --- Helper function for Facebook API calls ---
def make_facebook_api_call(endpoint, method, params=None, data=None, headers=None):
    """
    Makes a generic HTTP request to the Facebook Graph API.
    Handles basic error checking.
    """
    try:
        if method.lower() == 'post':
            response = requests.post(endpoint, params=params, json=data, headers=headers)
        elif method.lower() == 'get':
            response = requests.get(endpoint, params=params, headers=headers)
        else:
            return {"error": f"Unsupported HTTP method: {method}"}

        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        # Log the specific error for debugging
        app.logger.error(f"Facebook API call failed for {endpoint} with method {method}: {e} (Response: {e.response.text if e.response else 'N/A'})")
        return {"error": str(e)}

# --- Define the rate limit duration ---
RATE_LIMIT_DURATION = timedelta(hours=24) # 24 hours

# --- Backend Endpoint for token usage check ---
@app.route('/check-token-usage', methods=['POST'])
def check_token_usage():
    """
    Checks if an access token has been used within the last 24 hours.
    """
    data = request.get_json()
    access_token = data.get('access_token')

    if not access_token:
        return jsonify({"can_use": False, "error": "Access token is required."}), 400

    last_used = token_last_used.get(access_token)
    current_time = datetime.now()

    if last_used and (current_time - last_used) < RATE_LIMIT_DURATION:
        wait_until = last_used + RATE_LIMIT_DURATION
        return jsonify({
            "can_use": False,
            "wait_until": wait_until.strftime("%Y-%m-%d %H:%M:%S")
        })
    return jsonify({"can_use": True})

# --- Backend Endpoint for object ID resolution ---
@app.route('/resolve-object-id', methods=['POST'])
def resolve_object_id_endpoint():
    """
    Resolves a raw input (URL or ID) into a Facebook object ID.
    """
    data = request.get_json()
    raw_input = data.get('raw_input')
    access_token = data.get('access_token') # Required for Graph API fallback

    if not raw_input or not access_token:
        return jsonify({"error": "Raw input and access token are required."}), 400

    object_id = None

    # Regex patterns for various Facebook URLs
    post_url_pattern = r'facebook\.com/[^/]+/posts/(\d+)'
    permalink_pattern = r'story_fbid=(\d+)(?:&id=\d+)?' # Catches permalink.php?story_fbid=ID&id=USER_ID
    video_url_pattern = r'facebook\.com/[^/]+/videos/(\d+)'
    # Comment IDs can be directly in URL for permalinks or part of a larger URL
    comment_url_pattern = r'(?:comment_id=|comment_id=|/permalink/\d+/\d+/comment_id/|/comments/|id=)(\d+)'

    match_post = re.search(post_url_pattern, raw_input)
    match_permalink = re.search(permalink_pattern, raw_input)
    match_video = re.search(video_url_pattern, raw_input)
    match_comment = re.search(comment_url_pattern, raw_input)

    if match_post:
        object_id = match_post.group(1)
    elif match_permalink:
        object_id = match_permalink.group(1)
    elif match_video:
        object_id = match_video.group(1)
    elif match_comment:
        object_id = match_comment.group(1)
    else:
        # If no URL pattern matches, assume it's a direct ID if numeric
        if raw_input.isdigit():
            object_id = raw_input

    if object_id:
        return jsonify({"object_id": object_id})
    else:
        # Fallback: Try to query the Graph API for the object
        # This is more robust but also consumes API calls
        try:
            # For general URLs, Facebook Graph API can often resolve them to an object ID
            # by fetching data for the URL itself.
            graph_api_url = f"https://graph.facebook.com/v19.0/?id={raw_input}&access_token={access_token}"
            response = requests.get(graph_api_url)
            response.raise_for_status()
            data = response.json()
            if 'og_object' in data and 'id' in data['og_object']:
                return jsonify({"object_id": data['og_object']['id']})
            elif 'id' in data: # Sometimes the ID is directly in the response if raw_input was already an ID
                return jsonify({"object_id": data['id']})
            else:
                return jsonify({"error": f"Could not resolve object ID for input: {raw_input}. No 'id' or 'og_object.id' found in API response."}), 400
        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Could not resolve object ID for input: {raw_input}. Network or API error: {str(e)}"}), 400


# --- Core function to send a single reaction (executed by a thread in the pool) ---
def send_single_reaction(object_id, reaction_type, access_token):
    """Performs a single Facebook reaction API call."""
    url = f"https://graph.facebook.com/v19.0/{object_id}/reactions"
    params = {
        'type': reaction_type,
        'access_token': access_token
    }
    # Using 'post' method with params for reactions as per Facebook API
    response_data = make_facebook_api_call(url, 'post', params=params)

    # Return structured result for the frontend
    if "error" in response_data:
        return {"success": False, "error": response_data["error"], "object_id": object_id, "reaction_type": reaction_type, "token_prefix": access_token[:10]}
    else:
        # Facebook reaction API typically returns {"success": true} on success
        return {"success": response_data.get("success", False), "object_id": object_id, "reaction_type": reaction_type, "token_prefix": access_token[:10]}

@app.route('/send-reaction', methods=['POST'])
def send_reaction_endpoint():
    """
    Handles a batch of reaction tasks, processing them in parallel.
    """
    data = request.get_json()
    tasks = data.get('tasks') # Expecting a list of {object_id, reaction_type, access_token, link_index}

    if not tasks:
        return jsonify({"error": "No tasks provided."}), 400

    results = []
    futures = []

    # Submit tasks to the thread pool
    for task in tasks:
        object_id = task.get('object_id')
        reaction_type = task.get('reaction_type')
        access_token = task.get('access_token')

        # Ensure all necessary data is present for the task
        if not all([object_id, reaction_type, access_token]):
            results.append({"success": False, "error": "Invalid task data (missing object_id, reaction_type, or access_token).", "original_task": task})
            continue

        # Mark token as used before processing
        # This is where the 24-hour limit is applied on the server side
        token_last_used[access_token] = datetime.now()

        # Submit the task to the executor
        future = executor.submit(send_single_reaction, object_id, reaction_type, access_token)
        futures.append(future)

    # Collect results as they complete
    for future in futures:
        try:
            results.append(future.result()) # .result() blocks until the task is done
        except Exception as e:
            # Catch exceptions that might occur within the thread
            app.logger.error(f"Error processing reaction task: {e}")
            results.append({"success": False, "error": str(e)})

    return jsonify(results) # Return all results at once


# --- Helper function for sending a single comment ---
def send_single_comment(object_id, message, access_token):
    """Performs a single Facebook comment API call."""
    url = f"https://graph.facebook.com/v19.0/{object_id}/comments"
    params = {
        'message': message,
        'access_token': access_token
    }
    response_data = make_facebook_api_call(url, 'post', params=params)

    if "error" in response_data:
        return {"success": False, "error": response_data["error"], "object_id": object_id, "token_prefix": access_token[:10]}
    else:
        # Facebook comment API typically returns an 'id' for the new comment on success
        return {"success": "id" in response_data, "comment_id": response_data.get("id"), "object_id": object_id, "token_prefix": access_token[:10]}

@app.route('/send-comment', methods=['POST'])
def send_comment_endpoint():
    """
    Handles a batch of comment tasks, processing them in parallel.
    """
    data = request.get_json()
    tasks = data.get('tasks')

    if not tasks:
        return jsonify({"error": "No tasks provided."}), 400

    results = []
    futures = []

    for task in tasks:
        object_id = task.get('object_id')
        message = task.get('message')
        access_token = task.get('access_token')

        if not all([object_id, message, access_token]):
            results.append({"success": False, "error": "Invalid task data (missing object_id, message, or access_token).", "original_task": task})
            continue

        token_last_used[access_token] = datetime.now()
        future = executor.submit(send_single_comment, object_id, message, access_token)
        futures.append(future)

    for future in futures:
        try:
            results.append(future.result())
        except Exception as e:
            app.logger.error(f"Error processing comment task: {e}")
            results.append({"success": False, "error": str(e)})

    return jsonify(results)


# --- Helper function for sending a single comment reaction ---
def send_single_comment_reaction(comment_id, reaction_type, access_token):
    """Performs a single Facebook comment reaction API call (upvote/like for a comment)."""
    url = f"https://graph.facebook.com/v19.0/{comment_id}/reactions"
    params = {
        'type': reaction_type,
        'access_token': access_token
    }
    response_data = make_facebook_api_call(url, 'post', params=params)

    if "error" in response_data:
        return {"success": False, "error": response_data["error"], "comment_id": comment_id, "reaction_type": reaction_type, "token_prefix": access_token[:10]}
    else:
        return {"success": response_data.get("success", False), "comment_id": comment_id, "reaction_type": reaction_type, "token_prefix": access_token[:10]}

@app.route('/send-comment-reaction', methods=['POST'])
def send_comment_reaction_endpoint():
    """
    Handles a batch of comment reaction tasks, processing them in parallel.
    """
    data = request.get_json()
    tasks = data.get('tasks')

    if not tasks:
        return jsonify({"error": "No tasks provided."}), 400

    results = []
    futures = []

    for task in tasks:
        comment_id = task.get('comment_id')
        reaction_type = task.get('reaction_type')
        access_token = task.get('access_token')

        if not all([comment_id, reaction_type, access_token]):
            results.append({"success": False, "error": "Invalid task data (missing comment_id, reaction_type, or access_token).", "original_task": task})
            continue

        token_last_used[access_token] = datetime.now()
        future = executor.submit(send_single_comment_reaction, comment_id, reaction_type, access_token)
        futures.append(future)

    for future in futures:
        try:
            results.append(future.result())
        except Exception as e:
            app.logger.error(f"Error processing comment reaction task: {e}")
            results.append({"success": False, "error": str(e)})

    return jsonify(results)


# --- Helper function for sharing a single post ---
def send_single_share(object_id, access_token):
    """Performs a single Facebook share API call."""
    url = f"https://graph.facebook.com/v19.0/me/feed" # Sharing to user's feed
    params = {
        'link': f"https://www.facebook.com/{object_id}", # Link to the post being shared
        'access_token': access_token
    }
    response_data = make_facebook_api_call(url, 'post', params=params)

    if "error" in response_data:
        return {"success": False, "error": response_data["error"], "object_id": object_id, "token_prefix": access_token[:10]}
    else:
        # Facebook share API typically returns an 'id' (post ID of the shared item) on success
        return {"success": "id" in response_data, "share_post_id": response_data.get("id"), "object_id": object_id, "token_prefix": access_token[:10]}

@app.route('/send-share', methods=['POST'])
def send_share_endpoint():
    """
    Handles a batch of share tasks, processing them in parallel.
    """
    data = request.get_json()
    tasks = data.get('tasks')

    if not tasks:
        return jsonify({"error": "No tasks provided."}), 400

    results = []
    futures = []

    for task in tasks:
        object_id = task.get('object_id')
        access_token = task.get('access_token')

        if not all([object_id, access_token]):
            results.append({"success": False, "error": "Invalid task data (missing object_id or access_token).", "original_task": task})
            continue

        token_last_used[access_token] = datetime.now()
        future = executor.submit(send_single_share, object_id, access_token)
        futures.append(future)

    for future in futures:
        try:
            results.append(future.result())
        except Exception as e:
            app.logger.error(f"Error processing share task: {e}")
            results.append({"success": False, "error": str(e)})

    return jsonify(results)


# --- Root route to serve the HTML content ---
@app.route('/')
def index():
    return render_template_string(HTML_CONTENT)


if __name__ == '__main__':
    # When running with Flask's development server, set debug to True for easier development.
    # For production, use a production-ready WSGI server like Gunicorn or Waitress.
    app.run(debug=True, port=5000)
