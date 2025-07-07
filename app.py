from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# The HTML content as a Python string
# We need to escape any backticks (`) in the JavaScript if they are used for template literals,
# or simply replace them with single/double quotes where appropriate, as they can conflict with Python strings.
# For simplicity, I'm using a multiline string and assuming the JS doesn't heavily rely on backticks for dynamic content that can't be adapted.
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
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
        }
        .nav {
            display: flex;
            justify-content: center;
            background: #1877f2;
            padding: 10px;
            margin-bottom: 20px;
        }
        .nav button {
            background: white;
            border: none;
            padding: 10px 20px;
            margin: 0 5px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            color: #1877f2;
            transition: background-color 0.3s ease;
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
        }
        button:hover {
            background-color: #145dbf;
        }
        #clearLogBtn, #clearCommentLogBtn, #clearShareLogBtn {
            background-color: #888;
            margin-top: 15px;
        }
        #clearLogBtn:hover, #clearCommentLogBtn:hover, #clearShareLogBtn:hover {
            background-color: #666;
        }
        #result, #commentResult, #shareResult {
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
        #result strong, #commentResult strong, #shareResult strong {
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
        }
        .link-path-row:last-of-type {
            border-bottom: none;
        }
        .link-path-column {
            flex: 1;
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
        #addLinkPathBtn, #addReactionLinkPathBtn, #addShareLinkPathBtn {
            background-color: #28a745;
            margin-top: 30px;
        }
        #addLinkPathBtn:hover, #addReactionLinkPathBtn:hover, #addShareLinkPathBtn:hover {
            background-color: #218838;
        }
    </style>
</head>
<body>
    <h2>📣 Facebook Tool By: Dars: V1</h2>

    <div class="nav">
        <button id="navReaction" class="active">❤️ Reaction Tool</button>
        <button id="navComment">💬 Comment Tool</button>
        <button id="navShare">↗️ Sharing Tool</button>
    </div>

    <div id="reactionPage" class="page active">
        <div class="container">
            <label for="tokenFile">📄 Load Access Tokens from File (one per line)</label>
            <input type="file" id="tokenFile" accept=".txt" />

            <label for="accessToken">🔑 Access Token (currently loaded)</label>
            <input type="text" id="accessToken" placeholder="Loaded access token" readonly>

            <div id="reactionLinkPathContainer">
            </div>

            <button type="button" id="addReactionLinkPathBtn">➕ Add Another Link</button>

            <button id="sendReactionBtn">✅ Send Reaction</button>
            <button id="clearLogBtn" style="background-color: #888; margin-top: 10px;">🗑️ Clear Reaction History</button>

            <div id="result">
                <strong>🗂️ Reaction History:</strong>
                <div id="log"></div>
            </div>
        </div>
    </div>

    <div id="commentPage" class="page">
        <div class="container">
            <label for="commentTokenFile">📄 Load Access Tokens from File (one per line)</label>
            <input type="file" id="commentTokenFile" accept=".txt" />

            <label for="commentToken">🔑 Access Token (currently loaded)</label>
            <input type="text" id="commentToken" placeholder="Loaded access token" readonly>

            <div id="linkPathContainer">
            </div>

            <button type="button" id="addLinkPathBtn">➕ Add Another Link</button>

            <button id="sendCommentBtn">✅ Send Comment</button>
            <button id="clearCommentLogBtn" style="background-color: #888; margin-top: 10px;">🗑️ Clear Comment Log</button>

            <div id="commentResult">
                <strong>🗂️ Comment History:</strong>
                <div id="commentLog"></div>
            </div>
        </div>
    </div>

    <div id="sharePage" class="page">
        <div class="container">
            <label for="shareTokenFile">📄 Load Access Tokens from File (one per line)</label>
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
    <script>
        // Navigation
        document.getElementById('navReaction').addEventListener('click', () => switchPage('reaction'));
        document.getElementById('navComment').addEventListener('click', () => switchPage('comment'));
        document.getElementById('navShare').addEventListener('click', () => switchPage('share'));

        function switchPage(page) {
            document.getElementById('reactionPage').classList.remove('active');
            document.getElementById('commentPage').classList.remove('active');
            document.getElementById('sharePage').classList.remove('active');
            document.getElementById('navReaction').classList.remove('active');
            document.getElementById('navComment').classList.remove('active');
            document.getElementById('navShare').classList.remove('active');

            if (page === 'reaction') {
                document.getElementById('reactionPage').classList.add('active');
                document.getElementById('navReaction').classList.add('active');
            } else if (page === 'comment') {
                document.getElementById('commentPage').classList.add('active');
                document.getElementById('navComment').classList.add('active');
            } else if (page === 'share') {
                document.getElementById('sharePage').classList.add('active');
                document.getElementById('navShare').classList.add('active');
            }
        }

        // --- Core Facebook API Interaction (Client-side via Flask backend) ---

        // We will move the actual API calls to the Flask backend to avoid CORS and token exposure.
        // The JavaScript will send requests to our Flask app, and Flask will then make the requests to Facebook.

        // Shared postId resolver function - this will now call our Flask backend
        async function resolvePostId(rawInput, token) {
            const response = await fetch('/resolve-post-id', {
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

        // --- Reaction Tool ---
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
            addReactionLinkPathRow();
            addCommentLinkPathRow();
            addShareLinkPathRow();
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
                        objectId = await resolvePostId(rawInput, token);
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
                            addLog(`✅ Reaction: ${reactionType} success for Link ${j + 1} (${entry.successCount + 1}${maxReactions > 0 ? '/' + maxReactions : ''})`, "success");
                            entry.successCount++;
                            overallSuccessCount++;
                        } else {
                            addLog(`❌ Reaction failed for Link ${j + 1}. Error: ${data.error ? data.error : 'Unknown error'}`, "error");
                            overallErrorCount++;
                        }
                    } catch (fetchError) {
                        addLog(`❌ Network error for Link ${j + 1}: ${fetchError.message}`, "error");
                        overallErrorCount++;
                    }
                    await new Promise(resolve => setTimeout(resolve, 500));
                }
            }

            addLog(`--- Reaction Process Finished ---`, 'info');
            activeReactionLinkData.forEach((item, index) => {
                const targetText = item.maxReactions > 0 ? ` (Target: ${item.maxReactions})` : ` (No max limit)`;
                addLog(`✅ Total Successful Reactions for Link ${index + 1} ("${item.link}"): ${item.successCount}${targetText}`, "info");
            });
            addLog(`✅ Overall Total Successful Reactions: ${overallSuccessCount}`, "info");
            addLog(`❌ Overall Total Failed Reactions: ${overallErrorCount}`, "error");
            sendBtn.disabled = false;
            sendBtn.textContent = "✅ Send Reaction";
        });

        document.getElementById('clearLogBtn').addEventListener('click', () => {
            document.getElementById('log').innerHTML = '';
            addLog('Reaction history cleared.', 'info');
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
                    <label for="commentPathFile-${commentLinkCounter}">📁 Load Comments from File (one per line)</label>
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
                        objectId = await resolvePostId(rawInput, token);
                    } catch (e) {
                        addCommentLog(`❌ Error resolving Post ID/URL for Link ${j + 1} ("${rawInput}"): ${e.message}`, 'error');
                        overallErrorCount++;
                        continue;
                    }

                    for (const comment of commentsToSend) {
                        if (maxComments > 0 && entry.successCount >= maxComments) {
                            addCommentLog(`✅ Max comments (${maxComments}) reached for Link ${j + 1} ("${rawInput}"). Stopping for this link.`, "info");
                            break;
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

                            if (data.id) {
                                addCommentLog(`✅ Comment success on Link ${j + 1} (${entry.successCount + 1}${maxComments > 0 ? '/' + maxComments : ''}) for message: "${comment.substring(0, 30)}..."`, "success");
                                entry.successCount++;
                                overallSuccessCount++;
                            } else {
                                addCommentLog(`❌ Comment failed on Link ${j + 1} for message "${comment.substring(0, 30)}...". Error: ${data.error ? data.error.message : 'Unknown error'}`, "error");
                                overallErrorCount++;
                            }
                        } catch (fetchError) {
                            addCommentLog(`❌ Network error on Link ${j + 1} for message "${comment.substring(0, 30)}...": ${fetchError.message}`, "error");
                            overallErrorCount++;
                        }
                        await new Promise(resolve => setTimeout(resolve, 500));
                    }
                }
            }

            addCommentLog(`--- Comment Process Finished ---`, 'info');
            activeCommentLinkData.forEach((item, index) => {
                const targetText = item.maxComments > 0 ? ` (Target: ${item.maxComments})` : ` (No max limit)`;
                addCommentLog(`✅ Total Successful Comments for Link ${index + 1} ("${item.link}"): ${item.successCount}${targetText}`, "info");
            });
            addCommentLog(`✅ Overall Total Successful Comments: ${overallSuccessCount}`, "info");
            addCommentLog(`❌ Overall Total Failed Comments: ${overallErrorCount}`, "error");
            sendBtn.disabled = false;
            sendBtn.textContent = "✅ Send Comment";
        });

        document.getElementById('clearCommentLogBtn').addEventListener('click', () => {
            document.getElementById('commentLog').innerHTML = '';
            addCommentLog('Comment log cleared.', 'info');
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

        function addShareLinkPathRow(initialLink = '', initialMessage = '', initialMaxShares = '') {
            shareLinkCounter++;
            const rowId = `share-link-path-row-${shareLinkCounter}`;
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
                    <input type="text" id="shareMessage-${shareLinkCounter}" placeholder="Enter message for the shared post" value="${initialMessage}">
                </div>
                <div class="link-path-column">
                    <label for="maxShares-${shareLinkCounter}">🎯 Max Shares</label>
                    <input type="number" id="maxShares-${shareLinkCounter}" min="0" value="${initialMaxShares}" placeholder="Enter max shares">
                </div>
                <button type="button" class="remove-row-btn" data-row-id="${rowId}">➖ Remove</button>
            `;
            container.appendChild(rowDiv);

            const newRowData = { id: rowId, link: initialLink, message: initialMessage, successCount: 0, maxShares: parseInt(initialMaxShares, 10) || 0 };
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
                newRowData.message = this.value.trim();
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
            sendBtn.textContent = "⏳ Sharing...";

            let overallSuccessCount = 0;
            let overallErrorCount = 0;

            for (const token of shareTokens) {
                document.getElementById('shareAccessToken').value = token;

                for (let j = 0; j < activeShareLinkData.length; j++) {
                    const entry = activeShareLinkData[j];
                    const rawInput = entry.link;
                    const shareMessage = entry.message;
                    const maxShares = entry.maxShares;

                    if (maxShares > 0 && entry.successCount >= maxShares) {
                        addShareLog(`✅ Max shares (${maxShares}) reached for Link ${j + 1} ("${rawInput}"). Skipping further shares for this link.`, "info");
                        continue;
                    }

                    let objectId;
                    try {
                        objectId = await resolvePostId(rawInput, token);
                    } catch (e) {
                        addShareLog(`❌ Error resolving Post ID/URL for Link ${j + 1} ("${rawInput}"): ${e.message}`, 'error');
                        overallErrorCount++;
                        continue;
                    }

                    try {
                        const response = await fetch('/share-post', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                object_id: objectId,
                                message: shareMessage,
                                access_token: token
                            })
                        });
                        const data = await response.json();

                        if (data.id) {
                            addShareLog(`✅ Share success for Link ${j + 1} (${entry.successCount + 1}${maxShares > 0 ? '/' + maxShares : ''})` + (shareMessage ? ` with message: "${shareMessage.substring(0, 30)}..."` : ''), "success");
                            entry.successCount++;
                            overallSuccessCount++;
                        } else {
                            addShareLog(`❌ Share failed for Link ${j + 1}. Error: ${data.error ? data.error.message : 'Unknown error'}`, "error");
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
                addShareLog(`✅ Total Successful Shares for Link ${index + 1} ("${item.link}"): ${item.successCount}${targetText}`, "info");
            });
            addShareLog(`✅ Overall Total Successful Shares: ${overallSuccessCount}`, "info");
            addShareLog(`❌ Overall Total Failed Shares: ${overallErrorCount}`, "error");
            sendBtn.disabled = false;
            sendBtn.textContent = "✅ Share Page";
        });

        document.getElementById('clearShareLogBtn').addEventListener('click', () => {
            document.getElementById('shareLog').innerHTML = '';
            addShareLog('Share log cleared.', 'info');
        });
    </script>
</body>
</html>
"""

import requests
import re
from urllib.parse import urlparse, parse_qs


@app.route('/')
def index():
    """Renders the main HTML page."""
    return render_template_string(HTML_CONTENT)


@app.route('/resolve-post-id', methods=['POST'])
def resolve_post_id_backend():
    """
    Backend endpoint to resolve Facebook post IDs from URLs or direct IDs.
    This replaces the client-side resolvePostId function's direct API calls.
    """
    data = request.get_json()
    raw_input = data.get('raw_input', '').strip()
    access_token = data.get('access_token')

    if not access_token:
        return jsonify({'error': 'Access token is required.'}), 400

    object_id = raw_input

    # NEW: Check for combined Page_ID_Post_ID format (e.g., 100071468800251_3220058891556612)
    if re.fullmatch(r'\d+_\d+', object_id):
        return jsonify({'object_id': object_id})

    # If it's a direct numerical ID, return it immediately
    if re.fullmatch(r'\d+', object_id):
        return jsonify({'object_id': object_id})

    # If it's not a URL, and not a numerical ID, it's likely an invalid input
    if not object_id.startswith('http'):
        return jsonify({'error': 'Invalid input: Not a URL and not a direct numerical Post ID.'}), 400

    try:
        url_obj = urlparse(object_id)
        pathname = url_obj.path
        query_params = parse_qs(url_obj.query)

        # Check for video watch URL (e.g., facebook.com/watch/?v=12345)
        if pathname == '/watch/' and 'v' in query_params:
            return jsonify({'object_id': query_params['v'][0]})

        # Check for traditional /permalink.php?story_fbid=ID&id=USER_ID format
        if pathname == '/permalink.php' and 'story_fbid' in query_params:
            story_fbid = query_params['story_fbid'][0]
            graph_url = f"https://graph.facebook.com/v20.0/{story_fbid}?access_token={access_token}"
            response = requests.get(graph_url)
            response.raise_for_status()
            data = response.json()
            if 'id' in data:
                return jsonify({'object_id': data['id']})
            else:
                return jsonify(
                    {'error': data.get('error', {}).get('message', 'Failed to resolve permalink story_fbid.')}), 500

        # New logic for /user/posts/pfbid... or /groups/GROUP_ID/posts/pfbid...
        pfbid_match = re.search(r'(?:posts|photos|videos)/(pfbid\d+)', pathname, re.IGNORECASE)
        if pfbid_match:
            pfbid = pfbid_match.group(1)
            try:
                # Try to resolve the pfbid directly
                graph_url = f"https://graph.facebook.com/v19.0/{pfbid}?access_token={access_token}"
                response = requests.get(graph_url)
                response.raise_for_status()
                data = response.json()
                if 'id' in data:
                    return jsonify({'object_id': data['id']})
                else:
                    # If direct resolution fails, try fetching the entire URL to get its ID
                    graph_url_full = f"https://graph.facebook.com/v20.0/?id={object_id}&access_token={access_token}"
                    response_full = requests.get(graph_url_full)
                    response_full.raise_for_status()
                    data_full = response_full.json()
                    if 'og_object' in data_full and 'id' in data_full['og_object']:
                        return jsonify({'object_id': data_full['og_object']['id']})
                    return jsonify({'error': data.get('error', {}).get('message',
                                                                       'Failed to resolve pfbid post ID from Graph API and full URL resolution.')}), 500
            except requests.exceptions.RequestException as e:
                return jsonify({'error': f'API error resolving pfbid: {e}'}), 500

        # Old-style Post URL (e.g., /username/posts/12345 or /page_name/posts/12345)
        legacy_post_match = re.match(r'^/([^/]+)/posts/(\d+)', pathname)
        if legacy_post_match:
            username_or_page_name = legacy_post_match.group(1)
            post_id_part = legacy_post_match.group(2)
            try:
                graph_url = f"https://graph.facebook.com/v20.0/{username_or_page_name}?access_token={access_token}"
                response = requests.get(graph_url)
                response.raise_for_status()
                page_id_data = response.json()
                if 'id' in page_id_data:
                    return jsonify({'object_id': f"{page_id_data['id']}_{post_id_part}"})
                else:
                    return jsonify({'object_id': post_id_part})
            except requests.exceptions.RequestException:
                return jsonify({'object_id': post_id_part})

        # Final fallback: try to query the URL itself for an object ID.
        graph_url_fallback = f"https://graph.facebook.com/v20.0/?id={object_id}&access_token={access_token}"
        response_fallback = requests.get(graph_url_fallback)
        response_fallback.raise_for_status()
        data_fallback = response_fallback.json()
        if 'og_object' in data_fallback and 'id' in data_fallback['og_object']:
            return jsonify({'object_id': data_fallback['og_object']['id']})
        if 'id' in data_fallback:
            return jsonify({'object_id': data_fallback['id']})

        return jsonify({'error': 'Unsupported URL format or invalid Post ID/URL.'}), 400

    except Exception as e:
        return jsonify({'error': f'General error resolving URL: {e}'}), 500


@app.route('/send-reaction', methods=['POST'])
def send_reaction():
    """Backend endpoint to send a reaction to a Facebook post."""
    data = request.get_json()
    object_id = data.get('object_id')
    reaction_type = data.get('reaction_type')
    access_token = data.get('access_token')

    if not all([object_id, reaction_type, access_token]):
        return jsonify({'success': False, 'error': 'Missing required parameters.'}), 400

    reaction_url = f"https://graph.facebook.com/v20.0/{object_id}/reactions"
    params = {'type': reaction_type, 'access_token': access_token}

    try:
        response = requests.post(reaction_url, data=params)
        response.raise_for_status()
        result = response.json()
        result['success'] = True  # Facebook API returns success: true, but sometimes just an ID
        return jsonify(result)
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_message = error_data.get('error', {}).get('message', error_message)
            except ValueError:
                pass
        return jsonify({'success': False, 'error': f'Network or API error: {error_message}'}), 500


@app.route('/send-comment', methods=['POST'])
def send_comment():
    """Backend endpoint to send a comment to a Facebook post."""
    data = request.get_json()
    object_id = data.get('object_id')
    message = data.get('message')
    access_token = data.get('access_token')

    if not all([object_id, message, access_token]):
        return jsonify({'success': False, 'error': 'Missing required parameters.'}), 400

    comment_url = f"https://graph.facebook.com/v20.0/{object_id}/comments"
    params = {'message': message, 'access_token': access_token}

    try:
        response = requests.post(comment_url, data=params)
        response.raise_for_status()
        result = response.json()
        return jsonify(result)  # Facebook API returns { 'id': '...' } on success for comments
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_message = error_data.get('error', {}).get('message', error_message)
            except ValueError:
                pass
        return jsonify({'success': False, 'error': f'Network or API error: {error_message}'}), 500


@app.route('/share-post', methods=['POST'])
def share_post():
    """Backend endpoint to share a Facebook post."""
    data = request.get_json()
    object_id = data.get('object_id')
    message = data.get('message')  # Optional message for the shared post
    access_token = data.get('access_token')

    if not all([object_id, access_token]):
        return jsonify({'success': False, 'error': 'Missing required parameters.'}), 400

    share_url = f"https://graph.facebook.com/v20.0/me/feed"  # Sharing to user's own feed
    params = {'link': f"https://www.facebook.com/{object_id}", 'access_token': access_token}
    if message:
        params['message'] = message

    try:
        response = requests.post(share_url, data=params)
        response.raise_for_status()
        result = response.json()
        return jsonify(result)  # Facebook API returns { 'id': '...' } on success for shares
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_message = error_data.get('error', {}).get('message', error_message)
            except ValueError:
                pass
        return jsonify({'success': False, 'error': f'Network or API error: {error_message}'}), 500


if __name__ == '__main__':
    # Run Flask app on all available interfaces (0.0.0.0) and port 5000
    # In Termux, you can then access it from your device's browser at http://localhost:5000
    # or http://<your_termux_ip>:5000 if you want to access from another device on the same network.
    app.run(host='0.0.0.0', port=5000, debug=True)
