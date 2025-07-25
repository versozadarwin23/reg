import os
import re
import json
import time
import requests
import subprocess
from flask import Flask, request, jsonify, render_template_string
from threading import Thread

app = Flask(__name__)

# Directory to store uploaded token and caption files
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global variables to store tokens and captions (managed server-side)
current_access_tokens = []  # For reactions
current_comment_tokens = []  # For comments
current_upvote_tokens = []  # For upvotes
current_post_share_tokens = []  # For post shares
loaded_comments_content = {}  # Stores {row_id: [comment_texts]}
loaded_captions_content = {}  # Stores {row_id: [caption_texts]}

app_logs = []
AIRPLANE_MODE_TRIGGER_LIMIT = 1
max_parallel = 1


def add_app_log(msg, log_type='info'):
    """Adds a log entry to a global list and optionally prints to console.
    This log is then fetched by the client-side JavaScript.
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {'message': f"[{timestamp}] {msg}", 'type': log_type}
    app_logs.append(log_entry)
    # Keep the log list from growing indefinitely (e.g., max 500 entries)
    if len(app_logs) > 500:
        app_logs.pop(0)
    print(f"[{log_type.upper()}] {msg}")  # Also print to console for server-side visibility


# --- airplane_mode.py content ---
def toggle_airplane_mode():
    airplane_mode_enable = ['adb', 'shell', 'settings', 'put', 'global', 'airplane_mode_on 1']
    subprocess.run(airplane_mode_enable, check=True, capture_output=True, text=True, timeout=10)

    disable_data = ['adb', 'shell', 'svc', 'data', 'disable']
    subprocess.run(disable_data, check=True, capture_output=True, text=True, timeout=10)
    time.sleep(5)

    broadcast_command = ['adb', 'shell', 'am', 'broadcast', '-a', 'android.intent.action.AIRPLANE_MODE', '--ez state true',]
    subprocess.run(broadcast_command, check=True, capture_output=True, text=True, timeout=10)

    airplane_mode_disable = ['adb', 'shell', 'settings', 'put', 'global', 'airplane_mode_on 0']
    subprocess.run(airplane_mode_disable, check=True, capture_output=True, text=True, timeout=10)

    data_enable = ['adb', 'shell', 'svc', 'data', 'enable']
    subprocess.run(data_enable, check=True, capture_output=True, text=True, timeout=10)

    broadcast_command = ['adb', 'shell', 'am', 'broadcast', '-a', 'android.intent.action.AIRPLANE_MODE', '--ez state false',]
    subprocess.run(broadcast_command, check=True, capture_output=True, text=True, timeout=10)


# --- Core Facebook API Functions (translated from JS) ---

# Keep resolvePostId as is, as requested
def resolve_post_id(input_str, access_token):
    """
    Helper function to resolve Facebook Post/Comment/Video ID from URL or return if already an ID.
    This is a direct translation of the provided JavaScript function.
    """
    post_id_patterns = [
        r"(?:(?:www\.)?facebook\.com/(?:photo|permalink)\.php\?story_fbid=(\d+)(?:&id=\d+)?|facebook\.com/(?:[a-zA-Z0-9\.]+)/(?:posts|photos|videos|activity)/(\d+))",
        r"facebook\.com/story\.php\?story_fbid=(\d+)",
        r"fb\.watch/(\w+)",  # Facebook video watch link
        r"facebook\.com/.*/videos/(\d+)"  # Facebook video link
    ]
    comment_id_patterns = [
        r"(?:facebook\.com/(?:[a-zA-Z0-9\.]+)/comments/(\d+))",
        r"comment_id=(\d+)",
        r"comment_fbid=(\d+)"
    ]

    # Try to extract from URL first
    for pattern in post_id_patterns:
        match = re.search(pattern, input_str)
        if match:
            # Return the first non-None group from the match
            for group in match.groups():
                if group:
                    return group

    for pattern in comment_id_patterns:
        match = re.search(pattern, input_str)
        if match:
            for group in match.groups():
                if group:
                    return group

    # If it's just a number, assume it's a direct ID
    if input_str.isdigit():
        return input_str

    # If it's a short URL like fb.me/XXXXX, try to resolve it via API
    if re.match(r"fb\.me/\w+", input_str) or input_str.startswith("https://fb.me/"):
        try:
            # Use the Graph API to get info about the short URL, which should include the ID
            graph_url = f"https://graph.facebook.com/v19.0/?id={input_str}&access_token={access_token}"
            response = requests.get(graph_url).json()
            if 'og_object' in response and 'id' in response['og_object']:
                return response['og_object']['id']
            elif 'id' in response:  # Sometimes the ID is directly in the response for direct links
                return response['id']
        except Exception as e:
            print(f"Error resolving short URL {input_str} via Graph API: {e}")


# This is a simple placeholder for Page ID resolution.
# The original JS `resolvePageId` was not used in the core logic of the tools (reaction, comment, upvote, share).
# Keeping it for completeness but note it's not currently invoked.
def resolve_page_id(input_str, access_token):
    if re.fullmatch(r'^\d+$', input_str):
        return input_str

    page_match = re.search(
        r'(?:facebook\.com\/pages\/[^\/]+\/(\d+))|'
        r'(?:facebook\.com\/([a-zA-Z0-9\.]+)(?:\/.*)?$)', re.IGNORECASE
    )
    if page_match:
        if page_match.group(1):
            return page_match.group(1)
        elif page_match.group(2):
            if page_match.group(2).lower() not in ['profile.php', 'photo.php', 'video.php',
                                                   'posts'] and access_token and access_token != 'dummy':
                try:
                    graph_url = f"https://graph.facebook.com/v20.0/{requests.utils.quote(page_match.group(2))}?access_token={access_token}"
                    response = requests.get(graph_url)
                    data = response.json()
                    if 'id' in data:
                        return data['id']
                except Exception as e:
                    add_app_log(f"Error resolving Page ID by name via Graph API: {e}", 'error')

    if access_token and access_token != 'dummy':
        try:
            graph_url = f"https://graph.facebook.com/v20.0/?id={requests.utils.quote(input_str)}&access_token={access_token}"
            response = requests.get(graph_url)
            data = response.json()
            if 'id' in data:
                return data['id']
            else:
                raise Exception(data.get('error', {}).get('message', 'Could not resolve Page ID from URL'))
        except Exception as e:
            add_app_log(f"Error resolving Page ID via Graph API: {e}", 'error')
            raise e
    else:
        raise Exception('Cannot resolve Page ID without a valid access token.')


# --- Flask Routes ---

@app.route('/')
def index():
    """Renders the HTML interface."""
    # We will embed the HTML directly since the prompt specifies not to use template/index.html
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Facebook Tool By: Dars: V1</title>
<style>
  html, body {
    margin: 0; padding: 0; width: 100%; min-height: 100%;
    background-color: #f0f2f5; font-family: Arial, sans-serif;
    line-height: 1.6;
  }
  h2 {
    color: #1877f2; text-align: center; padding-top: 15px;
  }
  .nav {
    display: flex; justify-content: center; flex-wrap: wrap;
    background: #1877f2; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }
  .nav button {
    background: white; border: none; padding: 10px 15px; margin: 
 5px;
    border-radius: 5px; cursor: pointer; font-weight: bold; color: #1877f2;
    transition: background 0.3s ease, transform 0.2s ease;
    flex-grow: 1;
    max-width: 200px;
  }
  .nav button:hover { transform: translateY(-2px); }
  .nav button.active { background: #145dbf; color: white; }
  .container {
    max-width: 900px;
 width: 95%;
    background: white; padding: 20px;
    margin: 20px auto; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);
 }
  label {
    display: block; margin-top: 15px; font-weight: bold;
    font-size: 14px;
 }
  input[type=text], input[type=number], select, textarea {
    width: 100%; padding: 10px; margin-top: 5px; border-radius: 5px;
 border: 1px solid #ccc; font-size: 14px; box-sizing: border-box;
  }
  textarea {
    resize: vertical; min-height: 60px;
 }
  .main-button {
    background-color: #1877f2; color: white; border: none; cursor: pointer;
    margin-top: 20px; padding: 12px;
 border-radius: 5px; width: 100%; font-size: 16px;
    transition: background 0.3s ease;
  }
  .main-button:hover:not(:disabled) { background-color: #145dbf;
 }
  .main-button:disabled {
      background-color: #a0a0a0;
      cursor: not-allowed;
 }
  .secondary-button {
    background-color: #888; color: white; border: none; cursor: pointer;
    margin-top: 10px; padding: 10px;
 border-radius: 5px; width: 100%; font-size: 14px;
    transition: background 0.3s ease;
  }
  .secondary-button:hover { background-color: #666;
 }
  #result, #commentResult, #upvoteResult, #postShareResult {
    background: #f6f6f6; padding: 15px; border-radius: 5px; margin-top: 20px;
    font-size: 14px;
 min-height: 50px;
    max-height: 300px;
    overflow-y: auto; white-space: pre-wrap;
    border: 1px solid #eee;
 }
  .log-entry {
    padding: 8px 0; margin-bottom: 5px; border-bottom: 1px dashed #e0e0e0;
    font-size: 13px;
 }
  .log-entry:last-child { border-bottom: none; }
  .log-entry.success { color: green; }
  .log-entry.info { color: gray;
 }
  .log-entry.error { color: red; }


  .page { display: none; }
  .page.active { display: block;
 }

  /* Dynamic link rows styles */
  #reactionLinkPathContainer, #commentLinkPathContainer, #upvoteLinkPathContainer, #postShareLinkPathContainer {
    border: 1px solid #eee;
 padding: 15px; border-radius: 8px; margin-top: 20px; background-color: #f9f9f9;
  }
  .link-row {
    display: flex; flex-wrap: wrap;
 align-items: flex-end; gap: 15px; margin-bottom: 15px;
    border-bottom: 1px dashed #e0e0e0; padding-bottom: 15px;
  }
  .link-row:last-child { border-bottom: none; padding-bottom: 0;
 }

  .link-column {
    flex: 1; min-width: 150px;
 }
  .link-column label {
    margin-top: 0; display: flex; justify-content: space-between; align-items: baseline;
    font-size: 13px;
 }
  .success-count {
    font-size: 12px; color: #555;
 }
  .remove-row-btn {
    padding: 8px 12px; background-color: #dc3545; color: white; border: none; border-radius: 5px; cursor: pointer;
 transition: background-color 0.3s ease; width: auto; font-size: 13px;
  }
  .remove-row-btn:hover { background-color: #c82333;
 }
  .add-row-btn {
    background-color: #28a745; color: white; border: none; cursor: pointer; padding: 10px 15px; border-radius: 5px;
 margin-top: 10px; width: auto; font-size: 14px;
  }
  .add-row-btn:hover { background-color: #218838;
 }

  /* About Section Specific Styles */
  .about-content {
    text-align: center;
    font-size: 16px;
    line-height: 1.8;
 }
  .about-content h3 {
    color: #1877f2;
    margin-bottom: 15px;
 }
  .about-content p {
    margin-bottom: 10px;
  }
  .about-content ul {
    list-style: none;
 padding: 0;
    margin-top: 20px;
    text-align: left; /* Align list items to the left */
    max-width: 600px;
 /* Limit width for readability */
    margin-left: auto;
    margin-right: auto;
 }
  .about-content ul li {
    background-color: #e9f2ff;
 /* Light blue background for list items */
    margin-bottom: 10px;
    padding: 10px 15px;
    border-radius: 8px;
 border: 1px solid #cce0ff;
    font-size: 15px;
    display: flex;
    align-items: center;
    gap: 10px;
 }
  .about-content ul li::before {
    content: "✔️"; /* Checkmark icon */
    font-size: 18px;
 color: #28a745; /* Green color for checkmark */
  }

  .social-links {
    margin-top: 30px;
    display: flex;
 justify-content: center;
    gap: 20px;
    flex-wrap: wrap;
  }
  .social-links a {
    display: inline-flex;
    align-items: center;
    gap: 8px;
 text-decoration: none;
    color: #1877f2;
    font-weight: bold;
    font-size: 15px;
    padding: 8px 15px;
    border: 1px solid #1877f2;
    border-radius: 5px;
 transition: background-color 0.3s ease, color 0.3s ease;
  }
  .social-links a:hover {
    background-color: #1877f2;
    color: white;
 }

  /* --- Responsive Adjustments --- */
  @media (max-width: 768px) {
    .container {
      width: 98%;
 padding: 15px;
    }
    h2 {
      font-size: 20px;
 }
    .nav button {
      font-size: 13px;
      padding: 8px 10px;
      margin: 4px;
 flex-basis: 45%;
    }
    label {
      font-size: 13px;
 }
    input[type=text], input[type=number], select, textarea {
      font-size: 13px;
      padding: 8px;
 }
    .main-button, .secondary-button {
      font-size: 14px;
      padding: 10px;
 }
    #result, #commentResult, #upvoteResult, #postShareResult {
      font-size: 12px;
      max-height: 250px;
 }
    .log-entry {
      font-size: 11px;
      padding: 6px 0;
 }
    .link-row {
      flex-direction: column;
      align-items: stretch;
      gap: 10px;
 }
    .link-column {
      min-width: unset;
      width: 100%;
 }
    .remove-row-btn, .add-row-btn {
      width: 100%;
      font-size: 13px;
      padding: 8px;
 }
    .link-column label span.success-count {
        display: block;
        margin-top: 5px;
 }
    .about-content {
      font-size: 14px;
 }
    .social-links a {
      font-size: 14px;
      padding: 6px 10px;
      gap: 6px;
 }
    .about-content ul li {
      font-size: 14px;
      padding: 8px 12px;
 }
  }

  @media (max-width: 480px) {
    .nav button {
      flex-basis: 100%;
 }
  }

  /* Dark Mode Styles */
  body.dark-mode {
    background-color: #1a1a1a;
    color: #f0f0f0;
  }
  .dark-mode h2 {
    color: #90caf9;
  }
  .dark-mode .container {
    background: #2a2a2a;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
  }
  .dark-mode label {
    color: #bbb;
  }
  .dark-mode input[type=text],
  .dark-mode input[type=number],
  .dark-mode select,
  .dark-mode textarea {
    background-color: #333;
    color: #f0f0f0;
    border: 1px solid #555;
  }
  .dark-mode .main-button {
    background-color: #42a5f5;
  }
  .dark-mode .main-button:hover:not(:disabled) {
    background-color: #2196f3;
  }
  .dark-mode .secondary-button {
    background-color: #555;
  }
  .dark-mode .secondary-button:hover {
    background-color: #777;
  }
  .dark-mode #result,
  .dark-mode #commentResult,
  .dark-mode #upvoteResult,
  .dark-mode #postShareResult {
    background: #333;
    border: 1px solid #444;
  }
  .dark-mode .log-entry {
    border-bottom: 1px dashed #444;
  }
  .dark-mode .log-entry.info {
    color: #ccc;
  }
  .dark-mode .log-entry.success {
    color: #81c784;
  }
  .dark-mode .log-entry.error {
    color: #ef9a9a;
  }
  .dark-mode #reactionLinkPathContainer,
  .dark-mode #commentLinkPathContainer,
  .dark-mode #upvoteLinkPathContainer,
  .dark-mode #postShareLinkPathContainer {
    background-color: #333;
    border: 1px solid #444;
  }
  .dark-mode .link-row {
    border-bottom: 1px dashed #444;
  }
  .dark-mode .add-row-btn {
    background-color: #66bb6a;
  }
  .dark-mode .add-row-btn:hover {
    background-color: #4caf50;
  }
  .dark-mode .remove-row-btn {
    background-color: #e57373;
  }
  .dark-mode .remove-row-btn:hover {
    background-color: #ef5350;
  }
  .dark-mode .about-content h3 {
    color: #90caf9;
  }
  .dark-mode .about-content ul li {
    background-color: #3a3a3a;
    border: 1px solid #5a5a5a;
  }
  .dark-mode .social-links a {
    color: #90caf9;
    border: 1px solid #90caf9;
  }
  .dark-mode .social-links a:hover {
    background-color: #90caf9;
    color: #2a2a2a;
  }
  .dark-mode .toggle-theme-btn {
    background-color: #555;
    color: white;
  }
  .dark-mode .toggle-theme-btn:hover {
    background-color: #777;
  }

  /* Theme Toggle Button Styles */
  .toggle-theme-btn {
    background-color: #f0f0f0;
    color: #333;
    border: 1px solid #ccc;
    padding: 10px 15px;
    border-radius: 5px;
    cursor: pointer;
    font-weight: bold;
    font-size: 14px;
    transition: background 0.3s ease, color 0.3s ease;
    margin-top: 10px;
    display: block;
    width: fit-content;
    margin-left: auto;
    margin-right: auto;
  }
  .toggle-theme-btn:hover {
    background-color: #e0e0e0;
  }

</style>
</head>
<body>
<h2>📣 Facebook Tool By: Dars: V1</h2>

<div class="nav">
  <button id="navReaction" class="active">❤️ Reaction Tool</button>
  <button id="navComment">💬 Comment Tool</button>
  <button id="navUpvote">👍 Upvote Tool</button>
  <button id="navPostShare">📤 Post Share</button>
  <button id="navAbout">ℹ️ About</button>
</div>

<div id="reactionPage" class="page active">
  <div class="container">
    <h3>❤️ Facebook Reaction Tool</h3>
    <label for="tokenFile">📄 Load Access Tokens from File (one per line)</label>
    <input type="file" id="tokenFile" accept=".txt" />

    <label for="accessToken">🔑 Access Token (currently loaded)</label>
    <input type="text" id="accessToken" placeholder="Loaded access token" readonly>

    <div id="reactionLinkPathContainer"></div>
    <button class="add-row-btn" id="addReactionLinkBtn">➕ Add Another 
 Link to React</button>

    <button id="sendReactionBtn" class="main-button">✅ Send Reaction</button>
    <button id="clearLogBtn" class="secondary-button">🗑️ Clear Reaction History</button>

    <div id="result">
      <strong>🗂️ Reaction History:</strong>
      <div id="log"></div>
    </div>
  </div>
</div>

<style>
#log {
  height: 200px;
 overflow-y: auto;
  border: 1px solid #ccc;
  padding: 5px;
  background: #f9f9f9;
}
</style>

<script>
const log = document.getElementById('log');
 const observer = new MutationObserver(() => {
  log.scrollTop = log.scrollHeight;
});
observer.observe(log, { childList: true });
 </script>


<div id="commentPage" class="page">
  <div class="container">
    <h3>💬 Facebook Comment Tool</h3>
    <label for="commentTokenFile">📄 Load Access Tokens from File (one per line)</label>
    <input type="file" id="commentTokenFile" accept=".txt" />

    <label for="commentToken">🔑 Access Token (currently loaded)</label>
    <input type="text" id="commentToken" placeholder="Loaded access token" readonly>

    <div id="commentLinkPathContainer"></div>
    <button class="add-row-btn" id="addCommentLinkBtn">➕ Add Another Link to Comment</button>

    <button id="sendCommentBtn" class="main-button">✅ Send Comment</button>
    <button id="clearCommentLogBtn" class="secondary-button">🗑️ Clear Comment Log</button>

    <div id="commentResult">
      <strong>🗂️ Comment History:</strong>

     <div id="commentLog"></div>
    </div>
  </div>
</div>

<div id="upvotePage" class="page">
  <div class="container">
    <h3>👍 Facebook Comment Upvote Tool</h3>
    <label for="upvoteTokenFile">📄 Load Access Tokens for Upvote from File</label>
    <input type="file" id="upvoteTokenFile" accept=".txt" />

    <label for="upvoteAccessToken">🔑 Access Token</label>
    <input type="text" id="upvoteAccessToken" 
 placeholder="Loaded access token" readonly />

    <div id="upvoteLinkPathContainer"></div>
    <button class="add-row-btn" id="addUpvoteLinkBtn">➕ Add Upvote Link</button>

    <button id="sendUpvoteBtn" class="main-button">🔼 Send Upvote</button>
    <button id="clearUpvoteLogBtn" class="secondary-button">🗑️ Clear Upvote Log</button>

    <div id="upvoteResult">

     <strong>🗂️ Upvote History:</strong>
      <div id="upvoteLog"></div>
    </div>
  </div>
</div>

<div id="postSharePage" class="page">
  <div class="container">
    <h3>📤 Facebook Post Sharing Tool</h3>

    <label for="postShareTokenFile">📄 Load Access Tokens for Sharing from File</label>
    <input type="file" id="postShareTokenFile" accept=".txt" />

    <label for="postShareAccessToken">🔑 Access Token</label>
    <input type="text" id="postShareAccessToken" placeholder="Loaded access token" readonly />

    <div id="postShareLinkPathContainer"></div>
    <button class="add-row-btn" id="addPostShareLinkBtn">➕ Add Post to Share</button>

    <button id="sendPostShareBtn" class="main-button">✅ Share Posts</button>
    <button id="clearPostShareLogBtn" class="secondary-button">🗑️ 
 Clear Share Log</button>

    <div id="postShareResult">
      <strong>🗂️ Share History:</strong>
      <div id="postShareLog"></div>
    </div>
  </div>
</div>

<div id="aboutPage" class="page">
    <div class="container">
        <h3>ℹ️ About This Tool</h3>
        <div class="about-content">
            <p>Welcome to the **Facebook Automation Tool by Dars: V1**!
 This is a simple yet powerful web-based application designed to help you automate various actions on Facebook posts, comments, and pages.</p>
            <p>Whether you need to send **reactions**, **comments**, **upvotes**, or **share posts**, this tool provides an easy-to-use interface to manage your tasks efficiently.</p>
            <p>It's built with user experience in mind, offering clear feedback through dynamic button texts and auto-scrolling logs, along with a responsive design for seamless use on any device.</p>


     <h4>✨ Key Features:</h4>
            <ul>
                <li>**❤️ Reaction Automation:** Easily send various reactions (Like, Love, Wow, Haha, Sad, Angry, Care) to multiple Facebook posts or videos.</li>
                <li>**💬 Comment Automation:** Automate posting 
 comments from a list of predefined texts to Facebook posts or videos.</li>

  <li>**👍 Upvote (Reaction on Comments) Automation:** Send reactions to specific Facebook comments to boost their visibility.</li>
                <li>**📤 Post Sharing Automation:** Share Facebook posts to your timeline with custom or random captions.</li>
                <li>**📄 Token Management:** Conveniently load multiple access tokens from a file for bulk operations.</li>
                <li>**📊 Real-time Progress Tracking:** Monitor the success rate of 
 your actions with dynamic counters for each task.</li>
                <li>**🖥️ User-Friendly Interface:** Intuitive design with clear labels and immediate feedback for a smooth experience.</li>
            </ul>

            <p style="margin-top: 30px;">Your feedback is highly valued.
 Feel free to connect with me through the links below!</p>

            <div class="social-links">
                <a href="https://www.facebook.com/darwinversoza139" target="_blank" rel="noopener noreferrer">Facebook</a>
                <a href="https://www.youtube.com/@darwinversoza" target="_blank" rel="noopener noreferrer">YouTube</a>
                <a href="https://t.me/versozadarwin" target="_blank" rel="noopener noreferrer">Telegram</a>
            </div>

       <p style="margin-top: 30px; font-size: 13px; color: #777;">Developed by **Dars: V1**</p>
        </div>
    </div>
</div>

<button id="toggleThemeBtn" class="toggle-theme-btn">☀️ Light Mode</button>

<script>
  // Navigation
  document.getElementById('navReaction').addEventListener('click', () => switchPage('reaction'));
 document.getElementById('navComment').addEventListener('click', () => switchPage('comment'));
  document.getElementById('navUpvote').addEventListener('click', () => switchPage('upvote'));
  document.getElementById('navPostShare').addEventListener('click', () => switchPage('postshare'));
  document.getElementById('navAbout').addEventListener('click', () => switchPage('about'));
 function switchPage(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav button').forEach(b => b.classList.remove('active'));
 if (page === 'reaction') {
      document.getElementById('reactionPage').classList.add('active');
      document.getElementById('navReaction').classList.add('active');
 } else if (page === 'comment') {
      document.getElementById('commentPage').classList.add('active');
      document.getElementById('navComment').classList.add('active');
 } else if (page === 'upvote') {
      document.getElementById('upvotePage').classList.add('active');
      document.getElementById('navUpvote').classList.add('active');
 } else if (page === 'postshare') {
      document.getElementById('postSharePage').classList.add('active');
      document.getElementById('navPostShare').classList.add('active');
 } else if (page === 'about') {
        document.getElementById('aboutPage').classList.add('active');
        document.getElementById('navAbout').classList.add('active');
 }
  }

  // --- Utility Functions for Button State & Logging ---
  function setButtonState(buttonId, text, isDisabled) {
      const button = document.getElementById(buttonId);
 if (button) { // Check if button exists
        button.innerText = text;
 button.disabled = isDisabled;
      }
  }

  function addLog(containerId, msg, type = 'info') {
      // Flask sends logs, this client-side function now just displays them.
 // The actual logging happens server-side.
      const container = document.getElementById(containerId);
      const logDiv = container ?
 container.querySelector('#log, #commentLog, #upvoteLog, #postShareLog') : null;
      if (!logDiv) {
        console.error('Log container or logDiv not found:', containerId);
 return;
      }

      const entry = document.createElement('div');
      entry.className = `log-entry ${type}`;
      entry.innerText = msg;
      logDiv.appendChild(entry);
 logDiv.scrollTop = logDiv.scrollHeight; // Auto-scroll to bottom
  }

  // Polling for server-side logs
  let lastLogCount = 0;
 async function fetchLogs() {
      try {
          const response = await fetch('/get_logs');
 const logs = await response.json();
          if (logs.length > lastLogCount) {
              // Only append new logs
              for (let i = lastLogCount; i < logs.length; i++) {
                  const log = logs[i];
 // Determine which log display area to use based on content or context
                  // For simplicity, we'll just log to the currently active tool's log area.
 // A more sophisticated approach would involve tagging logs with their source.
                  const activePage = document.querySelector('.page.active');
                  let logContainerId = 'log';
 // Default for reaction tool
                  if (activePage) {
                      if (activePage.id === 'reactionPage') logContainerId = 'log';
 else if (activePage.id === 'commentPage') logContainerId = 'commentLog';
                      else if (activePage.id === 'upvotePage') logContainerId = 'upvoteLog';
 else if (activePage.id === 'postSharePage') logContainerId = 'postShareLog';
                  }

                  // Find the specific log div for the active page
                  const targetLogDiv = document.getElementById(logContainerId);
 if (targetLogDiv) {
                       const entry = document.createElement('div');
 entry.className = `log-entry ${log.type}`;
                       entry.innerText = log.message;
                       targetLogDiv.appendChild(entry);
                       targetLogDiv.scrollTop = targetLogDiv.scrollHeight;
 } else {
                      console.warn(`Could not find log container for ID: ${logContainerId}`);
 }
              }
              lastLogCount = logs.length;
 }
      } catch (error) {
          console.error('Error fetching logs:', error);
 }
  }
  // Fetch logs every 1 second
  setInterval(fetchLogs, 1000);
 // End Utility Functions

  // -------- Token File Handling (re-written for Flask) --------
  async function handleTokenFile(fileInputId, hiddenTokenInputId, endpoint, tokenType) {
    const fileInput = document.getElementById(fileInputId);
 if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
      addLog(hiddenTokenInputId.replace('Token', 'Result').replace('AccessToken', 'Result'), '⚠️ No file selected.', 'info');
 return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);
    formData.append('token_type', tokenType);
 // To differentiate token types on server

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData,
      });
 const data = await response.json();
      if (data.success) {
        document.getElementById(hiddenTokenInputId).value = data.first_token || '';
 addLog(hiddenTokenInputId.replace('Token', 'Result').replace('AccessToken', 'Result'), `Loaded ${data.token_count} tokens.`, 'info');
      } else {
        addLog(hiddenTokenInputId.replace('Token', 'Result').replace('AccessToken', 'Result'), `Error loading tokens: ${data.message}`, 'error');
 }
    } catch (error) {
      addLog(hiddenTokenInputId.replace('Token', 'Result').replace('AccessToken', 'Result'), `Network error: ${error.message}`, 'error');
 }
  }

  // Event listeners for token file inputs
  document.getElementById('tokenFile').addEventListener('change', (e) => handleTokenFile('tokenFile', 'accessToken', '/upload_tokens', 'reaction'));
 document.getElementById('commentTokenFile').addEventListener('change', (e) => handleTokenFile('commentTokenFile', 'commentToken', '/upload_tokens', 'comment'));
  document.getElementById('upvoteTokenFile').addEventListener('change', (e) => handleTokenFile('upvoteTokenFile', 'upvoteAccessToken', '/upload_tokens', 'upvote'));
 document.getElementById('postShareTokenFile').addEventListener('change', (e) => handleTokenFile('postShareTokenFile', 'postShareAccessToken', '/upload_tokens', 'post_share'));

  // -------- Comment/Caption File Handling (re-written for Flask) --------
  async function handleContentFile(fileInputId, rowId, contentType) {
      const fileInput = document.getElementById(fileInputId);
 if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
          addLog(contentType.includes('comment') ? 'commentResult' : 'postShareResult', `⚠️ No file selected for ${contentType} for row ${rowId}.`, 'info');
 return;
      }

      const file = fileInput.files[0];
      const formData = new FormData();
      formData.append('file', file);
      formData.append('row_id', rowId);
 formData.append('content_type', contentType);

      try {
          const response = await fetch('/upload_content', {
              method: 'POST',
              body: formData,
          });
 const data = await response.json();
          if (data.success) {
              addLog(contentType.includes('comment') ? 'commentResult' : 'postShareResult', `Loaded ${data.content_count} ${contentType}s for row ${rowId}.`, 'info');
 } else {
              addLog(contentType.includes('comment') ? 'commentResult' : 'postShareResult', `Error loading ${contentType}s for row ${row_id}: ${data.message}`, 'error');
 }
      } catch (error) {
          addLog(contentType.includes('comment') ? 'commentResult' : 'postShareResult', `Network error loading ${contentType}s for row ${row_id}: ${error.message}`, 'error');
 }
  }

  // -------- Reaction Tool --------
  let reactionLinkCounter = 0;
  let linkSuccessCounts = {}; // { rowId: { current: 0, max: 0 } }

  document.getElementById('addReactionLinkBtn').addEventListener('click', () => {
    reactionLinkCounter++;
    const id = reactionLinkCounter;
    const container = document.getElementById('reactionLinkPathContainer');
    const row = document.createElement('div');
    row.className = 'link-row';
    row.id = `reaction-link-row-${id}`;
    row.innerHTML = `
      <div class="link-column">
        <label for="reactionLinkInput-${id}">
          🔗 Facebook Post ID <span id="successCount-${id}" class="success-count">Successful Reactions: (0/0)</span>
        </label>
        <input type="text" id="reactionLinkInput-${id}" placeholder="Enter Post URL or ID" />
      </div>
      <div class="link-column">
        <label for="reactionType-${id}">❤️ Choose Reaction</label>
        <select id="reactionType-${id}">
          <option value="LIKE">👍 Like</option>
          <option value="LOVE">❤️ Love</option>
          <option value="WOW">😮 Wow</option>
          <option value="HAHA">😂 Haha</option>
          <option value="SAD">😢 Sad</option>
          <option value="ANGRY">😡 Angry</option>
          <option value="CARE">🤗 Care</option>
        </select>
      </div>
      <div class="link-column">
        <label for="maxReactions-${id}">🎯 Max Reactions</label>
        <input type="number" id="maxReactions-${id}" min="1" value="1" />
      </div>
      <button type="button" class="remove-row-btn" data-row-id="reaction-link-row-${id}">➖ Remove</button>
    `;
    container.appendChild(row);

    row.querySelector('.remove-row-btn').addEventListener('click', () => {
      document.getElementById(`reaction-link-row-${id}`).remove();
      delete linkSuccessCounts[id];
    });

    linkSuccessCounts[id] = { current:0, max: parseInt(document.getElementById(`maxReactions-${id}`).value, 10) || 1 };
    document.getElementById(`maxReactions-${id}`).addEventListener('input', () => {
      updateSuccessCountDisplay(id);
    });

    function updateSuccessCountDisplay(id) {
      const maxVal = parseInt(document.getElementById(`maxReactions-${id}`).value, 10);
      linkSuccessCounts[id].max = isNaN(maxVal) ? 0 : maxVal;
      document.getElementById(`successCount-${id}`).innerText = `Successful Reactions: (${linkSuccessCounts[id].current}/${linkSuccessCounts[id].max})`;
    }
  });

  document.getElementById('sendReactionBtn').addEventListener('click', async () => {
    setButtonState('sendReactionBtn', '🚀 Sending Reaction...', true);
    const rows = document.querySelectorAll('#reactionLinkPathContainer .link-row');
    const reactionData = [];
    rows.forEach(row => {
      const rowId = row.id.split('-').pop();
      const rawInput = document.getElementById(`reactionLinkInput-${rowId}`).value.trim();
      const reactionType = document.getElementById(`reactionType-${rowId}`).value;
      const maxReactions = parseInt(document.getElementById(`maxReactions-${rowId}`).value,10);

      if (rawInput && !isNaN(maxReactions) && maxReactions >= 1) {
        reactionData.push({
          row_id: rowId,
          link: rawInput,
          type: reactionType,
          max_reactions: maxReactions
        });
        // Reset client-side success counts before sending, server will update
        linkSuccessCounts[rowId] = { current: 0, max: maxReactions };
        document.getElementById(`successCount-${rowId}`).innerText = `Successful Reactions: (0/${maxReactions})`;
      }
    });

    if (reactionData.length === 0) {
      addLog('result', '⚠️ Add links and ensure max reactions are valid.', 'info');
      setButtonState('sendReactionBtn', '✅ Send Reaction', false);
      return;
    }

    try {
      const response = await fetch('/send_reactions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(reactionData)
      });
      const data = await response.json();
      if (data.success) {
        addLog('result', `Total reactions sent: ${data.total_success_count}`, 'success');
        // Update client-side counts based on server response
        if (data.row_success_counts) {
          for (const rowId in data.row_success_counts) {
            const { current, max } = data.row_success_counts[rowId];
            if (linkSuccessCounts[rowId]) { // Ensure row still exists
              linkSuccessCounts[rowId].current = current;
              linkSuccessCounts[rowId].max = max;
              document.getElementById(`successCount-${rowId}`).innerText = `Successful Reactions: (${current}/${max})`;
            }
          }
        }
      } else {
        addLog('result', `Operation failed: ${data.message}`, 'error');
      }
    } catch (error) {
      addLog('result', `Network error during reaction send: ${error.message}`, 'error');
    } finally {
      setButtonState('sendReactionBtn', '✅ Send Reaction', false);
    }
  });

  document.getElementById('clearLogBtn').addEventListener('click', ()=>{
    document.getElementById('log').innerHTML='';
  });


  // -------- Comment Tool --------
  let commentLinkCounter=0;
  let commentLinkSuccessCounts={};

  function addCommentLinkRow() {
    commentLinkCounter++;
    const id=commentLinkCounter;
    const container=document.getElementById('commentLinkPathContainer');
    const row=document.createElement('div');
    row.className='link-row';
    row.id=`comment-link-row-${id}`;
    row.innerHTML=`
      <div class="link-column">
        <label for="commentLinkInput-${id}">
          🆔 Facebook Post ID <span id="commentSuccessCount-${id}" class="success-count">Successful Comments: (0/0)</span>
        </label>
        <input type="text" id="commentLinkInput-${id}" placeholder="Enter post or video ID or URL" />
      </div>
      <div class="link-column">
        <label for="commentTextFile-${id}">💬 Load Comment Text from File</label>
        <input type="file" id="commentTextFile-${id}" accept=".txt" />
      </div>
      <div class="link-column">
        <label for="maxComments-${id}">🎯 Max Comments</label>
        <input type="number" id="maxComments-${id}" min="1" value="1" />
      </div>
      <button type="button" class="remove-row-btn" data-row-id="comment-link-row-${id}">➖ Remove</button>
    `;
    container.appendChild(row);

    row.querySelector('.remove-row-btn').addEventListener('click', () => {
      document.getElementById(`comment-link-row-${id}`).remove();
      delete commentLinkSuccessCounts[id]; // Server-side management for loadedComments will handle removal implicitly if row no longer requested
    });

    document.getElementById(`commentTextFile-${id}`).addEventListener('change', e => {
      handleContentFile(e.target.id, id, 'comment'); // Send file to server
    });

    commentLinkSuccessCounts[id]={ current:0, max:0 };
    document.getElementById(`maxComments-${id}`).addEventListener('input', ()=> {
      updateCommentSuccessCountDisplay(id);
    });

    function updateCommentSuccessCountDisplay(id) {
      const maxVal=parseInt(document.getElementById(`maxComments-${id}`).value,10);
      commentLinkSuccessCounts[id].max = isNaN(maxVal) ? 0 : maxVal;
      document.getElementById(`commentSuccessCount-${id}`).innerText=`Successful Comments: (${commentLinkSuccessCounts[id].current}/${commentLinkSuccessCounts[id].max})`;
    }
  }

  document.getElementById('addCommentLinkBtn').addEventListener('click', addCommentLinkRow);

  document.getElementById('sendCommentBtn').addEventListener('click', async () => {
    setButtonState('sendCommentBtn', '🚀 Sending Comments...', true);
    const rows=document.querySelectorAll('#commentLinkPathContainer .link-row');
    const commentData=[];
    rows.forEach(row => {
      const rowId=row.id.split('-').pop();
      const rawInput=document.getElementById(`commentLinkInput-${rowId}`).value.trim();
      const maxComments=parseInt(document.getElementById(`maxComments-${rowId}`).value,10);

      if (rawInput && !isNaN(maxComments) && maxComments >= 1) {
        commentData.push({
          row_id: rowId,
          link: rawInput,
          max_comments: maxComments,
        });
        commentLinkSuccessCounts[rowId]={current:0, max:maxComments};
        document.getElementById(`commentSuccessCount-${rowId}`).innerText=`Successful Comments: (0/${maxComments})`;
      }
    });

    if (commentData.length === 0) {
      addLog('commentResult', '⚠️ Add links and ensure max comments are valid.', 'info');
      setButtonState('sendCommentBtn', '✅ Send Comment', false);
      return;
    }

    try {
      const response=await fetch('/send_comments', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(commentData)
      });
      const data=await response.json();
      if (data.success) {
        addLog('commentResult', `Total comments sent: ${data.total_success_count}`, 'success');
        if (data.row_success_counts) {
          for (const rowId in data.row_success_counts) {
            const { current, max }=data.row_success_counts[rowId];
            if (commentLinkSuccessCounts[rowId]) {
              commentLinkSuccessCounts[rowId].current=current;
              commentLinkSuccessCounts[rowId].max=max;
              document.getElementById(`commentSuccessCount-${rowId}`).innerText=`Successful Comments: (${current}/${max})`;
            }
          }
        }
      } else {
        addLog('commentResult', `Operation failed: ${data.message}`, 'error');
      }
    } catch (error) {
      addLog('commentResult', `Network error during comment send: ${error.message}`, 'error');
    } finally {
      setButtonState('sendCommentBtn', '✅ Send Comment', false);
    }
  });

  document.getElementById('clearCommentLogBtn').addEventListener('click', ()=>{
    document.getElementById('commentLog').innerHTML='';
  });


  // -------- Upvote Tool --------
  let upvoteLinkCounter = 0;
  let upvoteLinkSuccessCounts = {};

  function addUpvoteLinkRow() {
    upvoteLinkCounter++;
    const id = upvoteLinkCounter;
    const container = document.getElementById('upvoteLinkPathContainer');
    const row = document.createElement('div');
    row.className = 'link-row';
    row.id = `upvote-link-row-${id}`;
    row.innerHTML = `
      <div class="link-column">
        <label for="upvoteLinkInput-${id}">
          🆔 Facebook Comment ID <span id="upvoteSuccessCount-${id}" class="success-count">Successful Upvotes: (0/0)</span>
        </label>
        <input type="text" id="upvoteLinkInput-${id}" placeholder="Enter comment ID or URL" />
      </div>
      <div class="link-column">
        <label for="maxUpvotes-${id}">🎯 Max Upvotes</label>
        <input type="number" id="maxUpvotes-${id}" min="1" value="1" />
      </div>
      <button type="button" class="remove-row-btn" data-row-id="upvote-link-row-${id}">➖ Remove</button>
    `;
    container.appendChild(row);

    row.querySelector('.remove-row-btn').addEventListener('click', () => {
      document.getElementById(`upvote-link-row-${id}`).remove();
      delete upvoteLinkSuccessCounts[id];
    });

    upvoteLinkSuccessCounts[id] = { current: 0, max: 0 };
    document.getElementById(`maxUpvotes-${id}`).addEventListener('input', () => {
      updateUpvoteSuccessCountDisplay(id);
    });

    function updateUpvoteSuccessCountDisplay(id) {
      const maxVal = parseInt(document.getElementById(`maxUpvotes-${id}`).value, 10);
      upvoteLinkSuccessCounts[id].max = isNaN(maxVal) ? 0 : maxVal;
      document.getElementById(`upvoteSuccessCount-${id}`).innerText = `Successful Upvotes: (${upvoteLinkSuccessCounts[id].current}/${upvoteLinkSuccessCounts[id].max})`;
    }
  }

  document.getElementById('addUpvoteLinkBtn').addEventListener('click', addUpvoteLinkRow);

  document.getElementById('sendUpvoteBtn').addEventListener('click', async () => {
    setButtonState('sendUpvoteBtn', '🚀 Sending Upvotes...', true);
    const rows = document.querySelectorAll('#upvoteLinkPathContainer .link-row');
    const upvoteData = [];
    rows.forEach(row => {
      const rowId = row.id.split('-').pop();
      const rawInput = document.getElementById(`upvoteLinkInput-${rowId}`).value.trim();
      const maxUpvotes = parseInt(document.getElementById(`maxUpvotes-${rowId}`).value, 10);

      if (rawInput && !isNaN(maxUpvotes) && maxUpvotes >= 1) {
        upvoteData.push({
          row_id: rowId,
          link: rawInput,
          max_upvotes: maxUpvotes,
        });
        upvoteLinkSuccessCounts[rowId] = { current: 0, max: maxUpvotes };
        document.getElementById(`upvoteSuccessCount-${rowId}`).innerText = `Successful Upvotes: (0/${maxUpvotes})`;
      }
    });

    if (upvoteData.length === 0) {
      addLog('upvoteResult', '⚠️ Add links and ensure max upvotes are valid.', 'info');
      setButtonState('sendUpvoteBtn', '✅ Send Upvote', false);
      return;
    }

    try {
      const response = await fetch('/send_upvotes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(upvoteData)
      });
      const data = await response.json();
      if (data.success) {
        addLog('upvoteResult', `Total upvotes sent: ${data.total_success_count}`, 'success');
        if (data.row_success_counts) {
          for (const rowId in data.row_success_counts) {
            const { current, max } = data.row_success_counts[rowId];
            if (upvoteLinkSuccessCounts[rowId]) {
              upvoteLinkSuccessCounts[rowId].current = current;
              upvoteLinkSuccessCounts[rowId].max = max;
              document.getElementById(`upvoteSuccessCount-${rowId}`).innerText = `Successful Upvotes: (${current}/${max})`;
            }
          }
        }
      } else {
        addLog('upvoteResult', `Operation failed: ${data.message}`, 'error');
      }
    } catch (error) {
      addLog('upvoteResult', `Network error during upvote send: ${error.message}`, 'error');
    } finally {
      setButtonState('sendUpvoteBtn', '✅ Send Upvote', false);
    }
  });

  document.getElementById('clearUpvoteLogBtn').addEventListener('click', () => {
    document.getElementById('upvoteLog').innerHTML = '';
  });


  // -------- Post Share Tool --------
  let postShareLinkCounter = 0;
  let postShareLinkSuccessCounts = {};

  function addPostShareLinkRow() {
    postShareLinkCounter++;
    const id = postShareLinkCounter;
    const container = document.getElementById('postShareLinkPathContainer');
    const row = document.createElement('div');
    row.className = 'link-row';
    row.id = `postshare-link-row-${id}`;
    row.innerHTML = `
      <div class="link-column">
        <label for="postShareLinkInput-${id}">
          🆔 Facebook Post ID <span id="postShareSuccessCount-${id}" class="success-count">Successful Shares: (0/0)</span>
        </label>
        <input type="text" id="postShareLinkInput-${id}" placeholder="Enter post ID or URL to share" />
      </div>
      <div class="link-column">
        <label for="captionTextFile-${id}">📝 Load Captions from File (optional)</label>
        <input type="file" id="captionTextFile-${id}" accept=".txt" />
      </div>
      <div class="link-column">
        <label for="maxPostShares-${id}">🎯 Max Shares</label>
        <input type="number" id="maxPostShares-${id}" min="1" value="1" />
      </div>
      <button type="button" class="remove-row-btn" data-row-id="postshare-link-row-${id}">➖ Remove</button>
    `;
    container.appendChild(row);

    row.querySelector('.remove-row-btn').addEventListener('click', () => {
      document.getElementById(`postshare-link-row-${id}`).remove();
      delete postShareLinkSuccessCounts[id];
    });

    document.getElementById(`captionTextFile-${id}`).addEventListener('change', e => {
      handleContentFile(e.target.id, id, 'caption'); // Send file to server
    });

    postShareLinkSuccessCounts[id] = { current: 0, max: 0 };
    document.getElementById(`maxPostShares-${id}`).addEventListener('input', () => {
      updatePostShareSuccessCountDisplay(id);
    });

    function updatePostShareSuccessCountDisplay(id) {
      const maxVal = parseInt(document.getElementById(`maxPostShares-${id}`).value, 10);
      postShareLinkSuccessCounts[id].max = isNaN(maxVal) ? 0 : maxVal;
      document.getElementById(`postShareSuccessCount-${id}`).innerText = `Successful Shares: (${postShareLinkSuccessCounts[id].current}/${postShareLinkSuccessCounts[id].max})`;
    }
  }

  document.getElementById('addPostShareLinkBtn').addEventListener('click', addPostShareLinkRow);

  document.getElementById('sendPostShareBtn').addEventListener('click', async () => {
    setButtonState('sendPostShareBtn', '🚀 Sharing Posts...', true);
    const rows = document.querySelectorAll('#postShareLinkPathContainer .link-row');
    const postShareData = [];
    rows.forEach(row => {
      const rowId = row.id.split('-').pop();
      const rawInput = document.getElementById(`postShareLinkInput-${rowId}`).value.trim();
      const maxShares = parseInt(document.getElementById(`maxPostShares-${rowId}`).value, 10);

      if (rawInput && !isNaN(maxShares) && maxShares >= 1) {
        postShareData.push({
          row_id: rowId,
          link: rawInput,
          max_shares: maxShares,
        });
        postShareLinkSuccessCounts[rowId] = { current: 0, max: maxShares };
        document.getElementById(`postShareSuccessCount-${rowId}`).innerText = `Successful Shares: (0/${maxShares})`;
      }
    });

    if (postShareData.length === 0) {
      addLog('postShareResult', '⚠️ Add links and ensure max shares are valid.', 'info');
      setButtonState('sendPostShareBtn', '✅ Share Posts', false);
      return;
    }

    try {
      const response = await fetch('/send_post_shares', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(postShareData)
      });
      const data = await response.json();
      if (data.success) {
        addLog('postShareResult', `Total shares sent: ${data.total_success_count}`, 'success');
        if (data.row_success_counts) {
          for (const rowId in data.row_success_counts) {
            const { current, max } = data.row_success_counts[rowId];
            if (postShareLinkSuccessCounts[rowId]) {
              postShareLinkSuccessCounts[rowId].current = current;
              postShareLinkSuccessCounts[rowId].max = max;
              document.getElementById(`postShareSuccessCount-${rowId}`).innerText = `Successful Shares: (${current}/${max})`;
            }
          }
        }
      } else {
        addLog('postShareResult', `Operation failed: ${data.message}`, 'error');
      }
    } catch (error) {
      addLog('postShareResult', `Network error during post share send: ${error.message}`, 'error');
    } finally {
      setButtonState('sendPostShareBtn', '✅ Share Posts', false);
    }
  });

  document.getElementById('clearPostShareLogBtn').addEventListener('click', () => {
    document.getElementById('postShareLog').innerHTML = '';
  });


  // --- Toggle Airplane Mode ---
  document.getElementById('toggleAirplaneModeBtn').addEventListener('click', async () => {
      const action = document.getElementById('airplaneModeAction').value;
      addLog('result', `Attempting to ${action} airplane mode...`, 'info');
      try {
          const response = await fetch('/toggle_airplane_mode', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify({ action: action })
          });
          const data = await response.json();
          if (data.success) {
              addLog('result', data.message, 'success');
          } else {
              addLog('result', `Error toggling airplane mode: ${data.message}`, 'error');
          }
      } catch (error) {
          addLog('result', `Network error during airplane mode toggle: ${error.message}`, 'error');
      }
  });


  // --- Initial Setup on Page Load ---
  // Add an initial reaction link row when the page loads
  document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('addReactionLinkBtn').click();
    document.getElementById('addCommentLinkBtn').click();
    document.getElementById('addUpvoteLinkBtn').click();
    document.getElementById('addPostShareLinkBtn').click();
  });


  // Theme Toggle
  document.getElementById('toggleThemeBtn').addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    const isDarkMode = document.body.classList.contains('dark-mode');
    document.getElementById('toggleThemeBtn').innerText = isDarkMode ? '🌙 Dark Mode' : '☀️ Light Mode';
  });

</script>
</body>
</html>
"""
    return render_template_string(html_content)


@app.route('/upload_tokens', methods=['POST'])
def upload_tokens():
    file = request.files.get('file')
    token_type = request.form.get('token_type')
    if not file:
        return jsonify({"success": False, "message": "No file uploaded."}), 400

    try:
        content = file.read().decode('utf-8')
        tokens = [line.strip() for line in content.splitlines() if line.strip()]

        if token_type == 'reaction':
            global current_access_tokens
            current_access_tokens = tokens
        elif token_type == 'comment':
            global current_comment_tokens
            current_comment_tokens = tokens
        elif token_type == 'upvote':
            global current_upvote_tokens
            current_upvote_tokens = tokens
        elif token_type == 'post_share':
            global current_post_share_tokens
            current_post_share_tokens = tokens
        else:
            return jsonify({"success": False, "message": "Invalid token type."}), 400

        first_token = tokens[0] if tokens else ''
        add_app_log(f"Loaded {len(tokens)} {token_type} tokens.", 'info')
        return jsonify({"success": True, "token_count": len(tokens), "first_token": first_token})
    except Exception as e:
        add_app_log(f"Error reading token file: {e}", 'error')
        return jsonify({"success": False, "message": f"Error processing file: {e}"}), 500


@app.route('/upload_content', methods=['POST'])
def upload_content():
    file = request.files.get('file')
    row_id = request.form.get('row_id')
    content_type = request.form.get('content_type')
    if not file:
        return jsonify({"success": False, "message": "No file uploaded."}), 400

    try:
        content = file.read().decode('utf-8')
        items = [line.strip() for line in content.splitlines() if line.strip()]

        if content_type == 'comment':
            loaded_comments_content[row_id] = items
            add_app_log(f"Loaded {len(items)} comments for row {row_id}.", 'info')
        elif content_type == 'caption':
            loaded_captions_content[row_id] = items
            add_app_log(f"Loaded {len(items)} captions for row {row_id}.", 'info')
        else:
            return jsonify({"success": False, "message": "Invalid content type."}), 400

        return jsonify({"success": True, "content_count": len(items)})
    except Exception as e:
        add_app_log(f"Error reading content file: {e}", 'error')
        return jsonify({"success": False, "message": f"Error processing file: {e}"}), 500


@app.route('/get_logs')
def get_logs():
    return jsonify(app_logs)


@app.route('/send_reactions', methods=['POST'])
def send_reactions_endpoint():
    data = request.json
    overall_success_count = 0
    row_success_counts = {}

    for row in data:
        row_id = row['row_id']
        link = row['link']
        reaction_type = row['type']
        max_reactions = row['max_reactions']

        row_success_counts[row_id] = {'current': 0, 'max': max_reactions}

        if not current_access_tokens:
            add_app_log(f"No access tokens loaded for reactions.", 'error')
            continue

        try:
            post_id = resolve_post_id(link, current_access_tokens[0])
            if not post_id:
                add_app_log(f"Could not resolve post ID for link: {link}", 'error')
                continue

            add_app_log(f"Starting reactions for post {post_id} with type {reaction_type} (Max: {max_reactions})...",
                        'info')

            success_count = 0
            for i in range(max_reactions):
                if not current_access_tokens:
                    add_app_log("No more access tokens available for reactions.", 'info')
                    break

                access_token = current_access_tokens[i % len(current_access_tokens)]
                try:
                    graph_url = f"https://graph.facebook.com/v19.0/{post_id}/reactions"
                    payload = {'type': reaction_type, 'access_token': access_token}
                    response = requests.post(graph_url, data=payload)
                    result = response.json()

                    if response.status_code == 200 and result.get('success'):
                        add_app_log(
                            f"Successfully sent {reaction_type} reaction to post {post_id} (Token: ...{access_token[-5:]})",
                            'success')
                        success_count += 1
                        overall_success_count += 1
                        row_success_counts[row_id]['current'] = success_count
                    else:
                        error_message = result.get('error', {}).get('message', 'Unknown error')
                        add_app_log(
                            f"Failed to send {reaction_type} reaction to post {post_id}: {error_message} (Token: ...{access_token[-5:]})",
                            'error')

                except requests.exceptions.RequestException as e:
                    add_app_log(f"Network error sending reaction to post {post_id}: {e}", 'error')
                except Exception as e:
                    add_app_log(f"Error processing reaction for post {post_id}: {e}", 'error')

                time.sleep(0.5)  # Small delay between reactions

        except Exception as e:
            add_app_log(f"Error processing link {link} for reactions: {e}", 'error')

    add_app_log("--- Reaction process finished ---", 'info')
    return jsonify(
        {"success": True, "total_success_count": overall_success_count, "row_success_counts": row_success_counts})


@app.route('/send_comments', methods=['POST'])
def send_comments_endpoint():
    data = request.json
    overall_success_count = 0
    row_success_counts = {}

    for row in data:
        row_id = row['row_id']
        link = row['link']
        max_comments = row['max_comments']

        row_success_counts[row_id] = {'current': 0, 'max': max_comments}

        comments_to_use = loaded_comments_content.get(row_id, [])
        if not comments_to_use:
            add_app_log(f"No comments loaded for row {row_id}.", 'error')
            continue

        if not current_comment_tokens:
            add_app_log(f"No access tokens loaded for comments.", 'error')
            continue

        try:
            post_id = resolve_post_id(link, current_comment_tokens[0])
            if not post_id:
                add_app_log(f"Could not resolve post ID for link: {link}", 'error')
                continue

            add_app_log(f"Starting comments for post {post_id} (Max: {max_comments})...", 'info')

            success_count = 0
            for i in range(max_comments):
                if not current_comment_tokens:
                    add_app_log("No more access tokens available for comments.", 'info')
                    break
                if not comments_to_use:
                    add_app_log(f"No more comments available for row {row_id}.", 'info')
                    break

                access_token = current_comment_tokens[i % len(current_comment_tokens)]
                comment_text = comments_to_use[i % len(comments_to_use)]

                try:
                    graph_url = f"https://graph.facebook.com/v19.0/{post_id}/comments"
                    payload = {'message': comment_text, 'access_token': access_token}
                    response = requests.post(graph_url, data=payload)
                    result = response.json()

                    if response.status_code == 200 and 'id' in result:
                        add_app_log(
                            f"Successfully commented on post {post_id}: '{comment_text[:30]}...' (Token: ...{access_token[-5:]})",
                            'success')
                        success_count += 1
                        overall_success_count += 1
                        row_success_counts[row_id]['current'] = success_count
                    else:
                        error_message = result.get('error', {}).get('message', 'Unknown error')
                        add_app_log(
                            f"Failed to comment on post {post_id}: {error_message} (Token: ...{access_token[-5:]})",
                            'error')

                except requests.exceptions.RequestException as e:
                    add_app_log(f"Network error sending comment to post {post_id}: {e}", 'error')
                except Exception as e:
                    add_app_log(f"Error processing comment for post {post_id}: {e}", 'error')

                time.sleep(0.5)  # Small delay between comments

        except Exception as e:
            add_app_log(f"Error processing link {link} for comments: {e}", 'error')

    add_app_log("--- Comment process finished ---", 'info')
    return jsonify(
        {"success": True, "total_success_count": overall_success_count, "row_success_counts": row_success_counts})


@app.route('/send_upvotes', methods=['POST'])
def send_upvotes_endpoint():
    data = request.json
    overall_success_count = 0
    row_success_counts = {}

    for row in data:
        row_id = row['row_id']
        link = row['link']
        max_upvotes = row['max_upvotes']

        row_success_counts[row_id] = {'current': 0, 'max': max_upvotes}

        if not current_upvote_tokens:
            add_app_log(f"No access tokens loaded for upvotes.", 'error')
            continue

        try:
            comment_id = resolve_post_id(link, current_upvote_tokens[
                0])  # Using resolve_post_id to resolve comment ID as well
            if not comment_id:
                add_app_log(f"Could not resolve comment ID for link: {link}", 'error')
                continue

            add_app_log(f"Starting upvotes for comment {comment_id} (Max: {max_upvotes})...", 'info')

            success_count = 0
            for i in range(max_upvotes):
                if not current_upvote_tokens:
                    add_app_log("No more access tokens available for upvotes.", 'info')
                    break

                access_token = current_upvote_tokens[i % len(current_upvote_tokens)]
                try:
                    # Upvoting a comment is essentially reacting to it with a 'LIKE'
                    graph_url = f"https://graph.facebook.com/v19.0/{comment_id}/reactions"
                    payload = {'type': 'LIKE', 'access_token': access_token}
                    response = requests.post(graph_url, data=payload)
                    result = response.json()

                    if response.status_code == 200 and result.get('success'):
                        add_app_log(f"Successfully upvoted comment {comment_id} (Token: ...{access_token[-5:]})",
                                    'success')
                        success_count += 1
                        overall_success_count += 1
                        row_success_counts[row_id]['current'] = success_count
                    else:
                        error_message = result.get('error', {}).get('message', 'Unknown error')
                        add_app_log(
                            f"Failed to upvote comment {comment_id}: {error_message} (Token: ...{access_token[-5:]})",
                            'error')

                except requests.exceptions.RequestException as e:
                    add_app_log(f"Network error sending upvote to comment {comment_id}: {e}", 'error')
                except Exception as e:
                    add_app_log(f"Error processing upvote for comment {comment_id}: {e}", 'error')

                time.sleep(0.05)  # Small delay between upvotes

        except Exception as e:
            add_app_log(f"Error processing link {link} for upvotes: {e}", 'error')

    add_app_log("--- Upvote process finished ---", 'info')
    return jsonify(
        {"success": True, "total_success_count": overall_success_count, "row_success_counts": row_success_counts})


@app.route('/send_post_shares', methods=['POST'])
def send_post_shares_endpoint():
    data = request.json
    overall_success_count = 0
    row_success_counts = {}
    for row in data:
        row_id = row['row_id']
        link = row['link']
        max_shares = row['max_shares']

        row_success_counts[row_id] = {'current': 0, 'max': max_shares}

        captions_to_use = loaded_captions_content.get(row_id, [])

        if not current_post_share_tokens:
            add_app_log(f"No access tokens loaded for post shares.", 'error')
            continue

        try:
            post_id = resolve_post_id(link, current_post_share_tokens[0])
            if not post_id:
                add_app_log(f"Could not resolve post ID for link: {link}", 'error')
                continue

            add_app_log(f"Starting post shares for post {post_id} (Max: {max_shares})...", 'info')

            success_count = 0
            for i in range(max_shares):
                if not current_post_share_tokens:
                    add_app_log("No more access tokens available for post shares.", 'info')
                    break

                access_token = current_post_share_tokens[i % len(current_post_share_tokens)]
                caption = captions_to_use[i % len(
                    captions_to_use)] if captions_to_use else f"Sharing this cool post! {int(time.time())}"  # Default caption

                try:
                    graph_url = f"https://graph.facebook.com/v19.0/me/feed"
                    payload = {
                        'link': f"https://www.facebook.com/{post_id}",
                        'message': caption,
                        'access_token': access_token
                    }
                    response = requests.post(graph_url, data=payload)
                    result = response.json()

                    if response.status_code == 200 and 'id' in result:
                        add_app_log(
                            f"Successfully shared post {post_id} with caption '{caption[:30]}...' (Token: ...{access_token[-5:]})",
                            'success')
                        success_count += 1
                        overall_success_count += 1
                        row_success_counts[row_id]['current'] = success_count
                    else:
                        error_message = result.get('error', {}).get('message', 'Unknown error')
                        add_app_log(f"Failed to share post {post_id}: {error_message} (Token: ...{access_token[-5:]})",
                                    'error')

                except requests.exceptions.RequestException as e:
                    add_app_log(f"Network error sharing post {post_id}: {e}", 'error')
                except Exception as e:
                    add_app_log(f"Error processing share for post {post_id}: {e}", 'error')

                time.sleep(0.5)

                if (i + 1) % AIRPLANE_MODE_TRIGGER_LIMIT == 0 and AIRPLANE_MODE_TRIGGER_LIMIT > 0:
                    toggle_airplane_mode()
        except Exception as e: # This is the missing 'except' block
            add_app_log(f"An error occurred during post ID resolution or initial setup for link {link}: {e}", 'error')
            continue # Continue to the next row if an error occurs here

    add_app_log("--- Post Share process finished ---", 'info')
    return jsonify(
        {"success": True, "total_success_count": overall_success_count, "row_success_counts": row_success_counts})



@app.route('/toggle_airplane_mode', methods=['POST'])
def toggle_airplane_mode_endpoint():
    """Endpoint to trigger airplane mode toggle."""
    action = request.json.get('action')
    if action not in ['enable', 'disable']:
        return jsonify({"success": False, "message": "Invalid action. Must be 'enable' or 'disable'."}), 400

    # This is the crucial line:
    # Ensure 'args' is a tuple with a trailing comma if it has only one element.
    thread = Thread(target=toggle_airplane_mode, args=(action,))
    thread.start()

    return jsonify({"success": True, "message": f"Airplane mode command '{action}' initiated."})


if __name__ == '__main__':
    # Initial setup for default rows on server start if desired,
    # though the client-side JS also handles this on
    app.run(debug=True, host='0.0.0.0', port=5000)
