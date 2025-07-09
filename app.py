o

    #çmhÄ ã                   @   s   d dl mZmZmZmZ d dlZd dlZd dlmZmZ d dl	Z	ee
ƒZi ZdZ
dd„ Ze d¡dd	„ ƒZejd
dgdd
d„ ƒZejddgddd„ ƒZdd„ Zejddgddd„ ƒZejddgddd„ ƒZejddgddd„ ƒZejddgddd„ ƒZe
d krŽejd!d"d# dS dS )$é    )ÚFlaskÚrender_template_stringÚrequestÚjsonifyN)ÚdatetimeÚ	timedeltauYì  
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
            content: 'âœ¨'; /* Sparkle emoji or other suitable icon */
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
    <h2>ðŸ“£ Facebook Tool By: Dars: V1</h2>

    <div class="nav">
        <button id="navReaction" class="active">â¤ï¸ Reaction Tool</button>
        <button id="navComment">ðŸ’¬ Comment Tool</button>
        <button id="navCommentReaction">ðŸ‘ Upvotes Tool</button>
        <button id="navShare">â†—ï¸ Sharing Tool</button>
        <button id="navAbout">â„¹ï¸ About</button>
    </div>

    <div id="reactionPage" class="page active">
        <div class="container">
            <label for="tokenFile">ðŸ“„ Load Access Tokens from File</label>
            <input type="file" id="tokenFile" accept=".txt" />

            <label for="accessToken">ðŸ”‘ Access Token (currently loaded)</label>
            <input type="text" id="accessToken" placeholder="Loaded access token" readonly>

            <div id="reactionLinkPathContainer">
            </div>

            <button type="button" id="addReactionLinkPathBtn">âž• Add Another Post Link</button>

            <button id="sendReactionBtn">âœ… Send Post Reactions</button>
            <button id="clearLogBtn" style="background-color: #888; margin-top: 10px;">ðŸ—‘ï¸ Clear Post Reaction History</button>

            <div id="result">
                <strong>ðŸ—‚ï¸ Post Reaction History:</strong>
                <div id="log"></div>
            </div>
        </div>
    </div>

    <div id="commentPage" class="page">
        <div class="container">
            <label for="commentTokenFile">ðŸ“„ Load Access Tokens from File</label>
            <input type="file" id="commentTokenFile" accept=".txt" />

            <label for="commentToken">ðŸ”‘ Access Token (currently loaded)</label>
            <input type="text" id="commentToken" placeholder="Loaded access token" readonly>

            <div id="linkPathContainer">
            </div>

            <button type="button" id="addLinkPathBtn">âž• Add Another Post Link</button>

            <button id="sendCommentBtn">âœ… Send Comments</button>
            <button id="clearCommentLogBtn" style="background-color: #888; margin-top: 10px;">ðŸ—‘ï¸ Clear Comment Log</button>

            <div id="commentResult">
                <strong>ðŸ—‚ï¸ Comment History:</strong>
                <div id="commentLog"></div>
            </div>
        </div>
    </div>

    <div id="commentReactionPage" class="page">
        <div class="container">
            <label for="commentReactionTokenFile">ðŸ“„ Load Access Tokens from File</label>
            <input type="file" id="commentReactionTokenFile" accept=".txt" />

            <label for="commentReactionAccessToken">ðŸ”‘ Access Token (currently loaded)</label>
            <input type="text" id="commentReactionAccessToken" placeholder="Loaded access token" readonly>

            <div id="commentReactionLinkPathContainer">
            </div>

            <button type="button" id="addCommentReactionLinkPathBtn">âž• Add Another Comment Link</button>

            <button id="sendCommentReactionBtn">âœ… Send Comment Reactions</button>
            <button id="clearCommentReactionLogBtn" style="background-color: #888; margin-top: 10px;">ðŸ—‘ï¸ Clear Comment Reaction History</button>

            <div id="commentReactionResult">
                <strong>ðŸ—‚ï¸ Comment Reaction History:</strong>
                <div id="commentReactionLog"></div>
            </div>
        </div>
    </div>

    <div id="sharePage" class="page">
        <div class="container">
            <label for="shareTokenFile">ðŸ“„ Load Access Tokens from File</label>
            <input type="file" id="shareTokenFile" accept=".txt" />

            <label for="shareAccessToken">ðŸ”‘ Access Token (currently loaded)</label>
            <input type="text" id="shareAccessToken" placeholder="Loaded access token" readonly>

            <div id="shareLinkPathContainer">
            </div>

            <button type="button" id="addShareLinkPathBtn">âž• Add Another Post Link to Share</button>

            <button id="sendShareBtn">âœ… Share Page</button>
            <button id="clearShareLogBtn" style="background-color: #888; margin-top: 10px;">ðŸ—‘ï¸ Clear Share Log</button>

            <div id="shareResult">
                <strong>ðŸ—‚ï¸ Share History:</strong>
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
                <li><strong>â¤ï¸ Reaction Tool:</strong> Easily send various reactions (Like, Love, Wow, Haha, Sad, Angry, Care) to multiple Facebook posts.</li>
                <li><strong>ðŸ’¬ Comment Tool:</strong> Automate sending comments to specified Facebook posts using pre-defined messages from a file.</li>
                <li><strong>ðŸ‘ Upvotes Tool:</strong> Specifically designed to send reactions (upvotes/likes) to individual comments on Facebook.</li>
                <li><strong>â†—ï¸ Sharing Tool:</strong> Facilitate the sharing of Facebook posts to different destinations.</li>
                <li><strong>Token Management:</strong> Securely load and manage access tokens from text files for streamlined operations.</li>
                <li><strong>Real-time Logging:</strong> Keep track of all your activities with detailed success and error logs.</li>
                <li><strong>â³ Daily Token Usage Limit:</strong> Each access token can only be used once every 24 hours to ensure fair usage and prevent potential abuse.</li>
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
                accessTokens = e.target.result.split(/\r?\n/).map(line => line.trim()).filter(line => line.length > 0);
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
                    <label for="reactionLinkInput-${reactionLinkCounter}">ðŸ”— Facebook Post ID/URL</label>
                    <input type="text" id="reactionLinkInput-${reactionLinkCounter}" placeholder="Enter Post ID or URL here" value="${initialLink}">
                </div>
                <div class="link-path-column">
                    <label for="reactionType-${reactionLinkCounter}">â¤ï¸ Choose Reaction</label>
                    <select id="reactionType-${reactionLinkCounter}">
                        <option value="LIKE">ðŸ‘ Like</option>
                        <option value="LOVE">â¤ï¸ Love</option>
                        <option value="WOW">ðŸ˜® Wow</option>
                        <option value="HAHA">ðŸ˜‚ Haha</option>
                        <option value="SAD">ðŸ˜¢ Sad</option>
                        <option value="ANGRY">ðŸ˜¡ Angry</option>
                        <option value="CARE">ðŸ¤— Care</option>
                    </select>
                </div>
                <div class="link-path-column">
                    <label for="maxReactions-${reactionLinkCounter}">ðŸŽ¯ Max Reactions</label>
                    <input type="number" id="maxReactions-${reactionLinkCounter}" min="0" value="${initialMaxReactions}" placeholder="Enter max reactions">
                </div>
                <button type="button" class="remove-row-btn" data-row-id="${rowId}">âž– Remove</button>
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
                addLog('âš ï¸ Please load Access Tokens from a file first.', 'error');
                return;
            }

            reactionLinkPathData.forEach(item => item.successCount = 0);
            const activeReactionLinkData = reactionLinkPathData.filter(item => item.link);

            if (activeReactionLinkData.length === 0) {
                addLog('âš ï¸ Please add at least one Post ID/URL for reactions.', 'error');
                return;
            }

            sendBtn.disabled = true;
            sendBtn.textContent = "â³ Sending reactions...";

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
                    addLog(`âŒ Access Token already used today. Please wait 24 hours: ${tokenCheckData.wait_until}`, "error");
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
                        addLog(`âœ… Max reactions (${maxReactions}) reached for Link ${j + 1} ("${rawInput}"). Skipping further reactions for this link.`, "info");
                        continue;
                    }

                    let objectId;
                    try {
                        objectId = await resolveObjectId(rawInput, token); // Use resolveObjectId
                    } catch (e) {
                        addLog(`âŒ Error resolving Post ID/URL for Link ${j + 1} ("${rawInput}"): ${e.message}`, 'error');
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
                            addLog(`âœ… Reaction: ${reactionType} success for Post Link ${j + 1} (${entry.successCount + 1}${maxReactions > 0 ? '/' + maxReactions : ''})`, "success");
                            entry.successCount++;
                            overallSuccessCount++;
                        } else {
                            addLog(`âŒ Reaction failed for Post Link ${j + 1}. Error: ${data.error ? data.error : 'Unknown error'}`, "error");
                            overallErrorCount++;
                        }
                    } catch (fetchError) {
                        addLog(`âŒ Network error for Post Link ${j + 1}: ${fetchError.message}`, "error");
                        overallErrorCount++;
                    }
                    await new Promise(resolve => setTimeout(resolve, 500));
                }
            }

            addLog(`--- Post Reaction Process Finished ---`, 'info');
            activeReactionLinkData.forEach((item, index) => {
                const targetText = item.maxReactions > 0 ? ` (Target: ${item.maxReactions})` : ` (No max limit)`;
                addLog(`âœ… Total Successful Reactions for Post Link ${index + 1} ("${item.link}"): ${item.successCount}${targetText}`, "info");
            });
            addLog(`âœ… Overall Total Successful Post Reactions: ${overallSuccessCount}`, "info");
            addLog(`âŒ Overall Total Failed Post Reactions: ${overallErrorCount}`, "error");
            sendBtn.disabled = false;
            sendBtn.textContent = "âœ… Send Post Reactions";
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
                    .split(/\r?\n/)
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
                    <label for="commentLinkInput-${commentLinkCounter}">ðŸ”— Facebook Post ID/URL</label>
                    <input type="text" id="commentLinkInput-${commentLinkCounter}" placeholder="Enter Post ID or URL here" value="${initialLink}">
                </div>
                <div class="link-path-column">
                    <label for="commentPathFile-${commentLinkCounter}">ðŸ“ Load Comments from File </label>
                    <input type="file" id="commentPathFile-${commentLinkCounter}" accept=".txt">
                </div>
                <div class="link-path-column">
                    <label for="maxComments-${commentLinkCounter}">ðŸŽ¯ Max Comments</label>
                    <input type="number" id="maxComments-${commentLinkCounter}" min="0" value="${initialMaxComments}" placeholder="Enter max comments">
                </div>
                <button type="button" class="remove-row-btn" data-row-id="${rowId}">âž– Remove</button>
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
                        .split(/\r?\n/)
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
                addCommentLog('âš ï¸ Please load Access Tokens from a file first.', 'error');
                return;
            }

            commentLinkPathData.forEach(item => item.successCount = 0);
            const activeCommentLinkData = commentLinkPathData.filter(item => item.link && item.commentPaths.length > 0);

            if (activeCommentLinkData.length === 0) {
                addCommentLog('âš ï¸ Please add at least one Post ID/URL and load comments from a file.', 'error');
                return;
            }

            sendBtn.disabled = true;
            sendBtn.textContent = "â³ Sending comments...";

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
                    addCommentLog(`âŒ Access Token already used today. Please wait 24 hours: ${tokenCheckData.wait_until}`, "error");
                    overallErrorCount++;
                    continue; // Skip this token
                }

                for (let j = 0; j < activeCommentLinkData.length; j++) {
                    const entry = activeCommentLinkData[j];
                    const rawInput = entry.link;
                    const commentsToSend = entry.commentPaths;
                    const maxComments = entry.maxComments;

                    if (maxComments > 0 && entry.successCount >= maxComments) {
                        addCommentLog(`âœ… Max comments (${maxComments}) reached for Link ${j + 1} ("${rawInput}"). Skipping further comments for this link.`, "info");
                        continue;
                    }

                    let objectId;
                    try {
                        objectId = await resolveObjectId(rawInput, token);
                    } catch (e) {
                        addCommentLog(`âŒ Error resolving Post ID/URL for Link ${j + 1} ("${rawInput}"): ${e.message}`, 'error');
                        overallErrorCount++;
                        continue;
                    }

                    for (const comment of commentsToSend) {
                        if (maxComments > 0 && entry.successCount >= maxComments) {
                            addCommentLog(`âœ… Max comments (${maxComments}) reached for Link ${j + 1} ("${rawInput}"). Skipping further comments for this link.`, "info");
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
                                addCommentLog(`âœ… Comment sent for Post Link ${j + 1} (${entry.successCount + 1}${maxComments > 0 ? '/' + maxComments : ''}): "${comment}"`, "success");
                                entry.successCount++;
                                overallSuccessCount++;
                            } else {
                                addCommentLog(`âŒ Comment failed for Post Link ${j + 1} ("${comment}"). Error: ${data.error ? data.error : 'Unknown error'}`, "error");
                                overallErrorCount++;
                            }
                        } catch (fetchError) {
                            addCommentLog(`âŒ Network error for Post Link ${j + 1} ("${comment}"): ${fetchError.message}`, "error");
                            overallErrorCount++;
                        }
                        await new Promise(resolve => setTimeout(resolve, 500)); // Small delay between comments
                    }
                }
            }

            addCommentLog(`--- Comment Process Finished ---`, 'info');
            activeCommentLinkData.forEach((item, index) => {
                const targetText = item.maxComments > 0 ? ` (Target: ${item.maxComments})` : ` (No max limit)`;
                addCommentLog(`âœ… Total Successful Comments for Post Link ${index + 1} ("${item.link}"): ${item.successCount}${targetText}`, "info");
            });
            addCommentLog(`âœ… Overall Total Successful Comments: ${overallSuccessCount}`, "info");
            addCommentLog(`âŒ Overall Total Failed Comments: ${overallErrorCount}`, "error");
            sendBtn.disabled = false;
            sendBtn.textContent = "âœ… Send Comments";
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
                    .split(/\r?\n/)
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
                    <label for="commentReactionLinkInput-${commentReactionLinkCounter}">ðŸ”— Facebook Comment ID/URL</label>
                    <input type="text" id="commentReactionLinkInput-${commentReactionLinkCounter}" placeholder="Enter Comment ID or URL here" value="${initialLink}">
                </div>
                <div class="link-path-column">
                    <label for="commentReactionType-${commentReactionLinkCounter}">â¤ï¸ Choose Reaction</label>
                    <select id="commentReactionType-${commentReactionLinkCounter}">
                        <option value="LIKE">ðŸ‘ Like</option>
                        <option value="LOVE">â¤ï¸ Love</option>
                        <option value="WOW">ðŸ˜® Wow</option>
                        <option value="HAHA">ðŸ˜‚ Haha</option>
                        <option value="SAD">ðŸ˜¢ Sad</option>
                        <option value="ANGRY">ðŸ˜¡ Angry</option>
                        <option value="CARE">ðŸ¤— Care</option>
                    </select>
                </div>
                <div class="link-path-column">
                    <label for="maxCommentReactions-${commentReactionLinkCounter}">ðŸŽ¯ Max Reactions</label>
                    <input type="number" id="maxCommentReactions-${commentReactionLinkCounter}" min="0" value="${initialMaxReactions}" placeholder="Enter max reactions">
                </div>
                <button type="button" class="remove-row-btn" data-row-id="${rowId}">âž– Remove</button>
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
                addCommentReactionLog('âš ï¸ Please load Access Tokens from a file first.', 'error');
                return;
            }

            commentReactionLinkPathData.forEach(item => item.successCount = 0);
            const activeCommentReactionLinkData = commentReactionLinkPathData.filter(item => item.link);

            if (activeCommentReactionLinkData.length === 0) {
                addCommentReactionLog('âš ï¸ Please add at least one Comment ID/URL for reactions.', 'error');
                return;
            }

            sendBtn.disabled = true;
            sendBtn.textContent = "â³ Sending comment reactions...";

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
                    addCommentReactionLog(`âŒ Access Token already used today. Please wait 24 hours: ${tokenCheckData.wait_until}`, "error");
                    overallErrorCount++;
                    continue; // Skip this token
                }

                for (let j = 0; j < activeCommentReactionLinkData.length; j++) {
                    const entry = activeCommentReactionLinkData[j];
                    const rawInput = entry.link;
                    const reactionType = entry.reactionType;
                    const maxReactions = entry.maxReactions;

                    if (maxReactions > 0 && entry.successCount >= maxReactions) {
                        addCommentReactionLog(`âœ… Max reactions (${maxReactions}) reached for Comment Link ${j + 1} ("${rawInput}"). Skipping further reactions for this link.`, "info");
                        continue;
                    }

                    let objectId;
                    try {
                        objectId = await resolveObjectId(rawInput, token);
                    } catch (e) {
                        addCommentReactionLog(`âŒ Error resolving Comment ID/URL for Link ${j + 1} ("${rawInput}"): ${e.message}`, 'error');
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
                            addCommentReactionLog(`âœ… Reaction: ${reactionType} success for Comment Link ${j + 1} (${entry.successCount + 1}${maxReactions > 0 ? '/' + maxReactions : ''})`, "success");
                            entry.successCount++;
                            overallSuccessCount++;
                        } else {
                            addCommentReactionLog(`âŒ Reaction failed for Comment Link ${j + 1}. Error: ${data.error ? data.error : 'Unknown error'}`, "error");
                            overallErrorCount++;
                        }
                    } catch (fetchError) {
                        addCommentReactionLog(`âŒ Network error for Comment Link ${j + 1}: ${fetchError.message}`, "error");
                        overallErrorCount++;
                    }
                    await new Promise(resolve => setTimeout(resolve, 500));
                }
            }

            addCommentReactionLog(`--- Comment Reaction Process Finished ---`, 'info');
            activeCommentReactionLinkData.forEach((item, index) => {
                const targetText = item.maxReactions > 0 ? ` (Target: ${item.maxReactions})` : ` (No max limit)`;
                addCommentReactionLog(`âœ… Total Successful Reactions for Comment Link ${index + 1} ("${item.link}"): ${item.successCount}${targetText}`, "info");
            });
            addCommentReactionLog(`âœ… Overall Total Successful Comment Reactions: ${overallSuccessCount}`, "info");
            addCommentReactionLog(`âŒ Overall Total Failed Comment Reactions: ${overallErrorCount}`, "error");
            sendBtn.disabled = false;
            sendBtn.textContent = "âœ… Send Comment Reactions";
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
                    .split(/\r?\n/)
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
                    <label for="shareLinkInput-${shareLinkCounter}">ðŸ”— Facebook Post ID/URL to Share</label>
                    <input type="text" id="shareLinkInput-${shareLinkCounter}" placeholder="Enter Post ID or URL here" value="${initialLink}">
                </div>
                <div class="link-path-column">
                    <label for="shareMessage-${shareLinkCounter}">ðŸ“ Share Message (Optional)</label>
                    <textarea id="shareMessage-${shareLinkCounter}" placeholder="Enter optional share message">${initialShareMessage}</textarea>
                </div>
                <div class="link-path-column">
                    <label for="maxShares-${shareLinkCounter}">ðŸŽ¯ Max Shares</label>
                    <input type="number" id="maxShares-${shareLinkCounter}" min="0" value="${initialMaxShares}" placeholder="Enter max shares">
                </div>
                <button type="button" class="remove-row-btn" data-row-id="${rowId}">âž– Remove</button>
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
                addShareLog('âš ï¸ Please load Access Tokens from a file first.', 'error');
                return;
            }

            shareLinkPathData.forEach(item => item.successCount = 0);
            const activeShareLinkData = shareLinkPathData.filter(item => item.link);

            if (activeShareLinkData.length === 0) {
                addShareLog('âš ï¸ Please add at least one Post ID/URL to share.', 'error');
                return;
            }

            sendBtn.disabled = true;
            sendBtn.textContent = "â³ Sharing posts...";

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
                    addShareLog(`âŒ Access Token already used today. Please wait 24 hours: ${tokenCheckData.wait_until}`, "error");
                    overallErrorCount++;
                    continue; // Skip this token
                }

                for (let j = 0; j < activeShareLinkData.length; j++) {
                    const entry = activeShareLinkData[j];
                    const rawInput = entry.link;
                    const shareMessage = entry.shareMessage;
                    const maxShares = entry.maxShares;

                    if (maxShares > 0 && entry.successCount >= maxShares) {
                        addShareLog(`âœ… Max shares (${maxShares}) reached for Link ${j + 1} ("${rawInput}"). Skipping further shares for this link.`, "info");
                        continue;
                    }

                    let objectId;
                    try {
                        objectId = await resolveObjectId(rawInput, token);
                    } catch (e) {
                        addShareLog(`âŒ Error resolving Post ID/URL for Link ${j + 1} ("${rawInput}"): ${e.message}`, 'error');
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
                            addShareLog(`âœ… Post shared for Link ${j + 1} (${entry.successCount + 1}${maxShares > 0 ? '/' + maxShares : ''})`, "success");
                            entry.successCount++;
                            overallSuccessCount++;
                        } else {
                            addShareLog(`âŒ Sharing failed for Link ${j + 1}. Error: ${data.error ? data.error : 'Unknown error'}`, "error");
                            overallErrorCount++;
                        }
                    } catch (fetchError) {
                        addShareLog(`âŒ Network error for Link ${j + 1}: ${fetchError.message}`, "error");
                        overallErrorCount++;
                    }
                    await new Promise(resolve => setTimeout(resolve, 500));
                }
            }

            addShareLog(`--- Share Process Finished ---`, 'info');
            activeShareLinkData.forEach((item, index) => {
                const targetText = item.maxShares > 0 ? ` (Target: ${item.maxShares})` : ` (No max limit)`;
                addShareLog(`âœ… Total Successful Shares for Post Link ${index + 1} ("${item.link}"): ${item.successCount}${targetText}`, "info");
            });
            addShareLog(`âœ… Overall Total Successful Shares: ${overallSuccessCount}`, "info");
            addShareLog(`âŒ Overall Total Failed Shares: ${overallErrorCount}`, "error");
            sendBtn.disabled = false;
            sendBtn.textContent = "âœ… Share Page";
        });

        document.getElementById('clearShareLogBtn').addEventListener('click', () => {
            document.getElementById('shareLog').innerHTML = '';
            addShareLog('Share history cleared.', 'info');
        });

    </script>
</body>
</html>
c                 C   sH   t  d| ¡}|r
| d¡S t  d| ¡r| S t  d| ¡}|r"| d¡S d S )Nz•(?:facebook\.com/(?:[a-zA-Z0-9\.]+/)?(?:posts|photos|videos|permalink|media)/|story_fbid=|fbid=|comment_id=|photo_id=|feedback_id=|set=.*?\.t)\b(\d+)é   z^\d+$z facebook\.com/([a-zA-Z0-9\._-]+))ÚreÚsearchÚgroupÚmatch)Ú	raw_inputr   Z
profile_match© r   úapp.pyÚextract_object_id:  s   þ

r   ú/c                   C   s   t tƒS ©N)r   ÚHTML_CONTENTr   r   r   r   ÚindexY  s   r   z/resolve-object-idZPOST)Úmethodsc               
   C   sì   t  ¡ } |  d¡}|  d¡}|r|stddiƒdfS t|ƒ}|spz/d|› d|› }t |¡}| ¡  | ¡ } d| v rCtd	| d iƒW S tdd
|› diƒdfW S  tjj	yo } ztdd|› d
iƒdfW  Y d }~S d }~ww td	|iƒS )Nr
   Úaccess_tokenÚerrorz!Missing raw_input or access_tokené  ú!https://graph.facebook.com/v19.0/z?access_token=ÚidÚ	object_idz!Could not resolve object ID for "z'". No "id" found in Graph API response.z+Failed to resolve object ID via Graph API: z!. Raw input was treated as an ID.)
r   Úget_jsonÚgetr   r   ÚrequestsZraise_for_statusÚjsonÚ
exceptionsÚRequestException)Údatar
   r   r   Z
graph_api_urlÚresponseÚer   r   r   Úresolve_object_id_backend^  s8   


ÿÿÿÿ€ÿr%   z/check-token-usagec                  C   s|   t  ¡ } |  d¡}|stddiƒdfS t |¡}t ¡ }|r8|| tddk r8|tdd  d¡}td|d	œƒS td
diƒS )Nr   r   zMissing access_tokenr   é   ©Zhoursz%Y-%m-%d %H:%M:%SF)Úcan_useÚ
wait_untilr(   T)	r   r   r   r   Útoken_last_usedr   Únowr   Ústrftime)r"   r   Ú	last_usedr+   r)   r   r   r   Úcheck_token_usage~  s   

r.   c                 C   s   t  ¡ t| < d S r   )r   r+   r*   )r   r   r   r   Úupdate_token_usage’  s   r/   z/send-reactionc               
   C   ó:  t  ¡ } |  d¡}|  d¡}|  d¡}t|||gƒs#tdddœƒdfS t |¡}t ¡ }|r@|| tdd	k r@tdd
dœƒdfS d|› d
}||dœ}z3t	j
||d}| ¡ }	|jdkro|	 d¡du rot
|ƒ tdddœƒW S td|	 di ¡ dd¡dœƒW S  t	jjyœ }
 ztdd|
› dœƒW  Y d }
~
S d }
~
ww )Nr   Ú
reaction_typer   Fú
Missing data.©Úsuccessr   r   r&   r'   ú3Access token already used within the last 24 hours.é­  r   ú
/reactions©Útyper   ©ÚparamséÈ   r4   TzReaction sent successfully!©r4   Úmessager   r>   zFailed to send reaction.úNetwork or API error: ©r   r   r   Úallr   r*   r   r+   r   r   Zpostr   Zstatus_coder/   r    r!   ©r"   r   r1   r   r-   r+   Úurlr;   r#   Ú
response_datar$   r   r   r   Ú
send_reaction–  s>   



ÿÿþÿ €ÿrE   z
/send-commentc               
   C   s:  t  ¡ } |  d¡}|  d¡}|  d¡}t|||gƒs#tdddœƒdfS t |¡}t ¡ }|r@|| tdd	k r@tdd
dœƒdfS d|› d
}||dœ}z3t	j
||d}| ¡ }	|jdkrod|	v rot
|ƒ tdd|	d dœƒW S td|	 di ¡ dd¡dœƒW S  t	jjyœ }
 ztdd|
› dœƒW  Y d }
~
S d }
~
ww )Nr   r>   r   Fr2   r3   r   r&   r'   r5   r6   r   z	/comments)r>   r   r:   r<   r   TzComment sent successfully!)r4   r>   Z
comment_idr   zFailed to send comment.r?   r@   ©r"   r   r>   r   r-   r+   rC   r;   r#   rD   r$   r   r   r   Úsend_comment»  s:   



þÿÿ €ÿrG   z/send-comment-reactionc               
   C   r0   )Nr   r1   r   Fr2   r3   r   r&   r'   r5   r6   r   r7   r8   r:   r<   r4   Tz#Comment reaction sent successfully!r=   r   r>   z Failed to send comment reaction.r?   r@   rB   r   r   r   Úsend_comment_reactionÞ  s6   



þ
ÿ €ÿrH   z/send-sharec               
   C   sD  t  ¡ } |  d¡}|  dd¡}|  d¡}t||gƒs#tdddœƒdfS t |¡}t ¡ }|r@|| td	d
k r@tdddœƒdfS d
}d|› |dœ}|rP||d< z3t	j
||d}| ¡ }	|jdkrtd|	v rtt
|ƒ tdd|	d dœƒW S td|	 di ¡ dd¡dœƒW S  t	jjy¡ }
 ztdd|
› dœƒW  Y d }
~
S d }
~
ww )Nr   r>   Ú r   Fz"Missing object_id or access_token.r3   r   r&   r'   r5   r6   z(https://graph.facebook.com/v19.0/me/feedzhttps://www.facebook.com/)Úlinkr   r:   r<   r   TzPost shared successfully!)r4   r>   Z
share_post_idr   zFailed to share post.r?   r@   rF   r   r   r   Ú
send_share  s>   


þÿÿ €ÿrK   Ú__main__Tiˆ  )ÚdebugZport)Zflaskr   r   r   r   r   Útimer   r   r	   Ú__name__Zappr*   r   r   Zrouter   r%   r.   r/   rE   rG   rH   rK   Úrunr   r   r   r   Ú<module>   sJ              5



$
"
"
(ÿ
