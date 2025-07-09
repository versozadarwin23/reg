from flask import Flask, render_template_string, request, jsonify
import requests
import time  # Import time for tracking last usage
from datetime import datetime, timedelta  # Import datetime for date comparison
import re  # Already imported in your code

app = Flask(__name__)

# --- Server-side storage for token last usage ---
# Key: access_token, Value: last_used_timestamp (e.g., datetime object)
token_last_used = {}
# --- End of new additions for token usage tracking ---

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

            for (const token of accessTokens) {
                document.getElementById('accessToken').value = token;

                // --- Client-side token usage check before sending to backend ---
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
                // --- End of client-side token usage check ---

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
                    } catch (e) {
                        addLog(`❌ Error resolving Post ID/URL for Link ${j + 1} ("${rawInput}"): ${e.message}`, 'error');
                        overallErrorCount++;
                        continue;
                    }

                    try {
                        const response = await fetch('/send-reaction', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                object_id: objectId,
                                reaction_type: reactionType,
                                access_token: token
                            })
                        });
                        const data = await response.json();

                        if (data.success === true) {
                            addLog(`✅ Reaction: ${reactionType} success for Post Link ${j + 1} (${entry.successCount + 1}${maxReactions > 0 ? '/' + maxReactions : ''})`, "success");
                            entry.successCount++;
                            overallSuccessCount++;
                        } else {
                            addLog(`❌ Reaction failed for Post Link ${j + 1}. Error: ${data.error ? data.error : 'Unknown error'}`, "error");
                            overallErrorCount++;
                        }
                    } catch (fetchError) {
                        addLog(`❌ Network error for Post Link ${j + 1}: ${fetchError.message}`, "error");
                        overallErrorCount++;
                    }
                    await new Promise(resolve => setTimeout(resolve, 500));
                }
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

        function addCommentLinkPathRow(initialLink = '', initialMaxComments = '') {
            commentLinkCounter++;
            const rowId = `comment-link-path-row-${commentLinkCounter}`;
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
                    <label for="commentPathFile-${commentLinkCounter}">📁 Load Comments from File </label>
                    <input type="file" id="commentPathFile-${commentLinkCounter}" accept=".txt">
                </div>
                <div class="link-path-column">
                    <label for="maxComments-${commentLinkCounter}">🎯 Max Comments</label>
                    <input type="number" id="maxComments-${commentLinkCounter}" min="0" value="${initialMaxComments}" placeholder="Enter max comments">
                </div>
                <button type="button" class="remove-row-btn" data-row-id="${rowId}">➖ Remove</button>
            `;
            container.appendChild(rowDiv);

            const newRowData = { id: rowId, link: initialLink, commentPaths: [], successCount: 0, maxComments: parseInt(initialMaxComments, 10) || 0 };
            commentLinkPathData.push(newRowData);
            const currentIndex = commentLinkPathData.length - 1;

            document.getElementById(`commentPathFile-${commentLinkCounter}`).addEventListener('change', function () {
                const file = this.files[0];
                if (!file) return;

                const reader = new FileReader();
                reader.onload = function (e) {
                    newRowData.commentPaths = e.target.result
                        .split(/\\r?\\n/)
                        .map(line => line.trim())
                        .filter(line => line.length > 0);
                    addCommentLog(`Loaded ${newRowData.commentPaths.length} comments for Link ${currentIndex + 1}.`, 'info');
                };
                reader.readAsText(file);
            });

            rowDiv.querySelector('.remove-row-btn').addEventListener('click', function() {
                const rowIdToRemove = this.dataset.rowId;
                const indexToRemove = commentLinkPathData.findIndex(item => item.id === rowIdToRemove);
                if (indexToRemove > -1) {
                    commentLinkPathData.splice(indexToRemove, 1);
                }
                document.getElementById(rowIdToRemove).remove();
                addCommentLog(`Removed comment link/file path row "${rowIdToRemove}".`, 'info');
            });

            document.getElementById(`commentLinkInput-${commentLinkCounter}`).addEventListener('input', function() {
                newRowData.link = this.value.trim();
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
            const activeCommentLinkData = commentLinkPathData.filter(item => item.link && item.commentPaths.length > 0);

            if (activeCommentLinkData.length === 0) {
                addCommentLog('⚠️ Please add at least one Post ID/URL and load comments from a file.', 'error');
                return;
            }

            sendBtn.disabled = true;
            sendBtn.textContent = "⏳ Sending comments...";

            let overallSuccessCount = 0;
            let overallErrorCount = 0;

            for (const token of commentTokens) {
                document.getElementById('commentToken').value = token;

                // Client-side token usage check before sending to backend
                const tokenCheckResponse = await fetch('/check-token-usage', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ access_token: token })
                });
                const tokenCheckData = await tokenCheckResponse.json();

                if (!tokenCheckData.can_use) {
                    addCommentLog(`❌ Access Token already used today. Please wait 24 hours: ${tokenCheckData.wait_until}`, "error");
                    overallErrorCount++;
                    continue; // Skip this token
                }

                for (let j = 0; j < activeCommentLinkData.length; j++) {
                    const entry = activeCommentLinkData[j];
                    const rawInput = entry.link;
                    const commentsToSend = entry.commentPaths;
                    const maxComments = entry.maxComments;

                    if (maxComments > 0 && entry.successCount >= maxComments) {
                        addCommentLog(`✅ Max comments (${maxComments}) reached for Link ${j + 1} ("${rawInput}"). Skipping further comments for this link.`, "info");
                        continue;
                    }

                    let objectId;
                    try {
                        objectId = await resolveObjectId(rawInput, token);
                    } catch (e) {
                        addCommentLog(`❌ Error resolving Post ID/URL for Link ${j + 1} ("${rawInput}"): ${e.message}`, 'error');
                        overallErrorCount++;
                        continue;
                    }

                    for (const comment of commentsToSend) {
                        if (maxComments > 0 && entry.successCount >= maxComments) {
                            addCommentLog(`✅ Max comments (${maxComments}) reached for Link ${j + 1} ("${rawInput}"). Skipping further comments for this link.`, "info");
                            break; // Break from inner comment loop
                        }

                        try {
                            const response = await fetch('/send-comment', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({
                                    object_id: objectId,
                                    message: comment,
                                    access_token: token
                                })
                            });
                            const data = await response.json();

                            if (data.success === true) {
                                addCommentLog(`✅ Comment sent for Post Link ${j + 1} (${entry.successCount + 1}${maxComments > 0 ? '/' + maxComments : ''}): "${comment}"`, "success");
                                entry.successCount++;
                                overallSuccessCount++;
                            } else {
                                addCommentLog(`❌ Comment failed for Post Link ${j + 1} ("${comment}"). Error: ${data.error ? data.error : 'Unknown error'}`, "error");
                                overallErrorCount++;
                            }
                        } catch (fetchError) {
                            addCommentLog(`❌ Network error for Post Link ${j + 1} ("${comment}"): ${fetchError.message}`, "error");
                            overallErrorCount++;
                        }
                        await new Promise(resolve => setTimeout(resolve, 500)); // Small delay between comments
                    }
                }
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

        // --- Comment Reaction Tool (Upvotes) ---
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
                    <label for="commentReactionType-${commentReactionLinkCounter}">❤️ Choose Reaction</label>
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

            for (const token of commentReactionTokens) {
                document.getElementById('commentReactionAccessToken').value = token;

                // Client-side token usage check before sending to backend
                const tokenCheckResponse = await fetch('/check-token-usage', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ access_token: token })
                });
                const tokenCheckData = await tokenCheckResponse.json();

                if (!tokenCheckData.can_use) {
                    addCommentReactionLog(`❌ Access Token already used today. Please wait 24 hours: ${tokenCheckData.wait_until}`, "error");
                    overallErrorCount++;
                    continue; // Skip this token
                }

                for (let j = 0; j < activeCommentReactionLinkData.length; j++) {
                    const entry = activeCommentReactionLinkData[j];
                    const rawInput = entry.link;
                    const reactionType = entry.reactionType;
                    const maxReactions = entry.maxReactions;

                    if (maxReactions > 0 && entry.successCount >= maxReactions) {
                        addCommentReactionLog(`✅ Max reactions (${maxReactions}) reached for Comment Link ${j + 1} ("${rawInput}"). Skipping further reactions for this link.`, "info");
                        continue;
                    }

                    let objectId;
                    try {
                        objectId = await resolveObjectId(rawInput, token);
                    } catch (e) {
                        addCommentReactionLog(`❌ Error resolving Comment ID/URL for Link ${j + 1} ("${rawInput}"): ${e.message}`, 'error');
                        overallErrorCount++;
                        continue;
                    }

                    try {
                        const response = await fetch('/send-comment-reaction', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                object_id: objectId,
                                reaction_type: reactionType,
                                access_token: token
                            })
                        });
                        const data = await response.json();

                        if (data.success === true) {
                            addCommentReactionLog(`✅ Reaction: ${reactionType} success for Comment Link ${j + 1} (${entry.successCount + 1}${maxReactions > 0 ? '/' + maxReactions : ''})`, "success");
                            entry.successCount++;
                            overallSuccessCount++;
                        } else {
                            addCommentReactionLog(`❌ Reaction failed for Comment Link ${j + 1}. Error: ${data.error ? data.error : 'Unknown error'}`, "error");
                            overallErrorCount++;
                        }
                    } catch (fetchError) {
                        addCommentReactionLog(`❌ Network error for Comment Link ${j + 1}: ${fetchError.message}`, "error");
                        overallErrorCount++;
                    }
                    await new Promise(resolve => setTimeout(resolve, 500));
                }
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

        function addShareLinkPathRow(initialLink = '', initialShareMessage = '', initialMaxShares = '') {
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
                    <label for="shareMessage-${shareLinkCounter}">📝 Share Message (Optional)</label>
                    <textarea id="shareMessage-${shareLinkCounter}" placeholder="Enter optional share message">${initialShareMessage}</textarea>
                </div>
                <div class="link-path-column">
                    <label for="maxShares-${shareLinkCounter}">🎯 Max Shares</label>
                    <input type="number" id="maxShares-${shareLinkCounter}" min="0" value="${initialMaxShares}" placeholder="Enter max shares">
                </div>
                <button type="button" class="remove-row-btn" data-row-id="${rowId}">➖ Remove</button>
            `;
            container.appendChild(rowDiv);

            const newRowData = { id: rowId, link: initialLink, shareMessage: initialShareMessage, successCount: 0, maxShares: parseInt(initialMaxShares, 10) || 0 };
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

            document.getElementById(`shareMessage-${shareLinkCounter}`).addEventListener('input', function() {
                newRowData.shareMessage = this.value.trim();
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
            sendBtn.textContent = "⏳ Sharing posts...";

            let overallSuccessCount = 0;
            let overallErrorCount = 0;

            for (const token of shareTokens) {
                document.getElementById('shareAccessToken').value = token;

                // Client-side token usage check before sending to backend
                const tokenCheckResponse = await fetch('/check-token-usage', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ access_token: token })
                });
                const tokenCheckData = await tokenCheckResponse.json();

                if (!tokenCheckData.can_use) {
                    addShareLog(`❌ Access Token already used today. Please wait 24 hours: ${tokenCheckData.wait_until}`, "error");
                    overallErrorCount++;
                    continue; // Skip this token
                }

                for (let j = 0; j < activeShareLinkData.length; j++) {
                    const entry = activeShareLinkData[j];
                    const rawInput = entry.link;
                    const shareMessage = entry.shareMessage;
                    const maxShares = entry.maxShares;

                    if (maxShares > 0 && entry.successCount >= maxShares) {
                        addShareLog(`✅ Max shares (${maxShares}) reached for Link ${j + 1} ("${rawInput}"). Skipping further shares for this link.`, "info");
                        continue;
                    }

                    let objectId;
                    try {
                        objectId = await resolveObjectId(rawInput, token);
                    } catch (e) {
                        addShareLog(`❌ Error resolving Post ID/URL for Link ${j + 1} ("${rawInput}"): ${e.message}`, 'error');
                        overallErrorCount++;
                        continue;
                    }

                    try {
                        const response = await fetch('/send-share', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                object_id: objectId,
                                message: shareMessage, // Pass the share message
                                access_token: token
                            })
                        });
                        const data = await response.json();

                        if (data.success === true) {
                            addShareLog(`✅ Post shared for Link ${j + 1} (${entry.successCount + 1}${maxShares > 0 ? '/' + maxShares : ''})`, "success");
                            entry.successCount++;
                            overallSuccessCount++;
                        } else {
                            addShareLog(`❌ Sharing failed for Link ${j + 1}. Error: ${data.error ? data.error : 'Unknown error'}`, "error");
                            overallErrorCount++;
                        }
                    } catch (fetchError) {
                        addShareLog(`❌ Network error for Link ${j + 1}: ${fetchError.message}`, "error");
                        overallErrorCount++;
                    }
                    await new Promise(resolve => setTimeout(resolve, 500));
                }
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


# Helper function to extract Facebook object ID from URL or return as is
def extract_object_id(raw_input):
    # Regex to find common Facebook post/comment/video/photo IDs in URLs
    # This regex is more comprehensive and covers various Facebook URL patterns
    # It tries to capture the object ID which is usually a sequence of digits
    # Examples:
    # facebook.com/a/posts/ID/
    # facebook.com/photo.php?fbid=ID
    # facebook.com/permalink.php?story_fbid=ID
    # facebook.com/groups/GROUP_ID/posts/POST_ID/
    # facebook.com/ID/posts/ID/
    # facebook.com/ID/photos/a.ID/ID/
    match = re.search(
        r'(?:facebook\.com/(?:[a-zA-Z0-9\.]+/)?(?:posts|photos|videos|permalink|media)/|story_fbid=|fbid=|comment_id=|photo_id=|feedback_id=|set=.*?\.t)\b(\d+)',
        raw_input)
    if match:
        return match.group(1)
    # If it's just a number, assume it's already an ID
    if re.match(r'^\d+$', raw_input):
        return raw_input
    # For profiles/pages, try to get the username/ID
    profile_match = re.search(r'facebook\.com/([a-zA-Z0-9\._-]+)', raw_input)
    if profile_match:
        # This will return the username/ID, which might need further resolution
        # via the Graph API to get the numeric ID if needed for certain actions.
        # For now, we'll return it as is, and the Graph API call will likely fail
        # if a numeric ID is strictly required for the specific endpoint.
        return profile_match.group(1)
    return None  # If no ID or username found


# Flask Routes
@app.route('/')
def index():
    return render_template_string(HTML_CONTENT)


@app.route('/resolve-object-id', methods=['POST'])
def resolve_object_id_backend():
    data = request.get_json()
    raw_input = data.get('raw_input')
    access_token = data.get('access_token')

    if not raw_input or not access_token:
        return jsonify({'error': 'Missing raw_input or access_token'}), 400

    object_id = extract_object_id(raw_input)

    if not object_id:
        # If no numeric ID found, try to resolve via Graph API for pages/profiles
        # This is a general endpoint, usually it will return the numeric ID if a public URL is provided.
        # However, for posts/comments, direct ID extraction is usually more reliable.
        try:
            graph_api_url = f"https://graph.facebook.com/v19.0/{raw_input}?access_token={access_token}"
            response = requests.get(graph_api_url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()
            if 'id' in data:
                return jsonify({'object_id': data['id']})
            else:
                return jsonify({
                                   'error': f'Could not resolve object ID for "{raw_input}". No "id" found in Graph API response.'}), 400
        except requests.exceptions.RequestException as e:
            return jsonify(
                {'error': f'Failed to resolve object ID via Graph API: {e}. Raw input was treated as an ID.'}), 400

    return jsonify({'object_id': object_id})


@app.route('/check-token-usage', methods=['POST'])
def check_token_usage():
    data = request.get_json()
    access_token = data.get('access_token')

    if not access_token:
        return jsonify({'error': 'Missing access_token'}), 400

    last_used = token_last_used.get(access_token)
    now = datetime.now()

    if last_used and (now - last_used) < timedelta(hours=24):
        wait_until = (last_used + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
        return jsonify({'can_use': False, 'wait_until': wait_until})
    else:
        # If token hasn't been used in the last 24 hours or is new, mark it as usable.
        # We'll update the timestamp when it's actually used by a send operation.
        return jsonify({'can_use': True})


def update_token_usage(access_token):
    token_last_used[access_token] = datetime.now()


@app.route('/send-reaction', methods=['POST'])
def send_reaction():
    data = request.get_json()
    object_id = data.get('object_id')
    reaction_type = data.get('reaction_type')
    access_token = data.get('access_token')

    if not all([object_id, reaction_type, access_token]):
        return jsonify({'success': False, 'error': 'Missing data.'}), 400

    # Before sending, double-check usage (redundant if client-side check is strict, but good for robustness)
    last_used = token_last_used.get(access_token)
    now = datetime.now()
    if last_used and (now - last_used) < timedelta(hours=24):
        return jsonify({'success': False,
                        'error': 'Access token already used within the last 24 hours.'}), 429  # Too Many Requests

    # Facebook Graph API endpoint for reactions
    url = f"https://graph.facebook.com/v19.0/{object_id}/reactions"
    params = {
        'type': reaction_type,
        'access_token': access_token
    }

    try:
        response = requests.post(url, params=params)
        response_data = response.json()
        if response.status_code == 200 and response_data.get('success') is True:
            update_token_usage(access_token)  # Update usage on successful operation
            return jsonify({'success': True, 'message': 'Reaction sent successfully!'})
        else:
            return jsonify(
                {'success': False, 'error': response_data.get('error', {}).get('message', 'Failed to send reaction.')})
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': f'Network or API error: {e}'})


@app.route('/send-comment', methods=['POST'])
def send_comment():
    data = request.get_json()
    object_id = data.get('object_id')
    message = data.get('message')
    access_token = data.get('access_token')

    if not all([object_id, message, access_token]):
        return jsonify({'success': False, 'error': 'Missing data.'}), 400

    last_used = token_last_used.get(access_token)
    now = datetime.now()
    if last_used and (now - last_used) < timedelta(hours=24):
        return jsonify({'success': False, 'error': 'Access token already used within the last 24 hours.'}), 429

    url = f"https://graph.facebook.com/v19.0/{object_id}/comments"
    params = {
        'message': message,
        'access_token': access_token
    }

    try:
        response = requests.post(url, params=params)
        response_data = response.json()
        if response.status_code == 200 and 'id' in response_data:  # Facebook returns the comment ID on success
            update_token_usage(access_token)
            return jsonify(
                {'success': True, 'message': 'Comment sent successfully!', 'comment_id': response_data['id']})
        else:
            return jsonify(
                {'success': False, 'error': response_data.get('error', {}).get('message', 'Failed to send comment.')})
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': f'Network or API error: {e}'})


@app.route('/send-comment-reaction', methods=['POST'])
def send_comment_reaction():
    data = request.get_json()
    object_id = data.get('object_id')  # This should be the comment ID
    reaction_type = data.get('reaction_type')
    access_token = data.get('access_token')

    if not all([object_id, reaction_type, access_token]):
        return jsonify({'success': False, 'error': 'Missing data.'}), 400

    last_used = token_last_used.get(access_token)
    now = datetime.now()
    if last_used and (now - last_used) < timedelta(hours=24):
        return jsonify({'success': False, 'error': 'Access token already used within the last 24 hours.'}), 429

    # Facebook Graph API endpoint for comment reactions is similar to post reactions
    url = f"https://graph.facebook.com/v19.0/{object_id}/reactions"
    params = {
        'type': reaction_type,
        'access_token': access_token
    }

    try:
        response = requests.post(url, params=params)
        response_data = response.json()
        if response.status_code == 200 and response_data.get('success') is True:
            update_token_usage(access_token)
            return jsonify({'success': True, 'message': 'Comment reaction sent successfully!'})
        else:
            return jsonify({'success': False,
                            'error': response_data.get('error', {}).get('message', 'Failed to send comment reaction.')})
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': f'Network or API error: {e}'})


@app.route('/send-share', methods=['POST'])
def send_share():
    data = request.get_json()
    object_id = data.get('object_id')  # This should be the post ID to share
    message = data.get('message', '')  # Optional share message
    access_token = data.get('access_token')

    if not all([object_id, access_token]):
        return jsonify({'success': False, 'error': 'Missing object_id or access_token.'}), 400

    last_used = token_last_used.get(access_token)
    now = datetime.now()
    if last_used and (now - last_used) < timedelta(hours=24):
        return jsonify({'success': False, 'error': 'Access token already used within the last 24 hours.'}), 429

    url = f"https://graph.facebook.com/v19.0/me/feed"  # Sharing to user's feed

    # When sharing, you typically post to the user's feed with a link to the original post.
    # The 'link' parameter is for the URL you want to share.
    # The 'message' parameter is the optional text that goes with the share.
    params = {
        'link': f"https://www.facebook.com/{object_id}",  # Construct FB URL from ID
        'access_token': access_token
    }
    if message:
        params['message'] = message

    try:
        response = requests.post(url, params=params)
        response_data = response.json()
        if response.status_code == 200 and 'id' in response_data:  # Facebook returns the post ID of the new shared post
            update_token_usage(access_token)
            return jsonify(
                {'success': True, 'message': 'Post shared successfully!', 'share_post_id': response_data['id']})
        else:
            return jsonify(
                {'success': False, 'error': response_data.get('error', {}).get('message', 'Failed to share post.')})
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': f'Network or API error: {e}'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
