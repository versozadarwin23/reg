import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import requests
import re
from urllib.parse import urlparse, parse_qs
import random
import subprocess
import time
import socket

# Sa halip na app = Flask(__name__), gawin itong:
app = Flask(__name__, template_folder='.') # Sinasabi nito sa Flask na hanapin ang templates sa kasalukuyang direktoryo

# >>> IMPORTANT: CHANGE THIS TO A STRONG, RANDOM KEY! <<<
# Example: import os; os.urandom(24).hex()
app.secret_key = 'your_strong_random_secret_key_here_please_change_me'

# --- Configuration for airplanemode.py ---
# Make sure this path is correct relative to app.py or an absolute path
AIRPLANEMODE_SCRIPT_PATH = 'airplanemode.py'
# Set to 1 to run for every token, or higher for batches
TOKENS_PER_AIRPLANEMODE_CYCLE = 1
# ----------------------------------------

# Global counter for tokens processed
# This is simplistic and would reset if the Flask app reloads.
# For a production system, consider a more persistent counter (e.g., database, file).
token_usage_counter = 0


# --- Internet Connection Check Functions ---
def check_internet_connection():
    """
    Checks for an active internet connection by attempting to connect to a known host.
    """
    try:
        # Tries to open a socket connection to Google's public DNS server (8.8.8.8) on port 53 (DNS port).
        # A timeout of 5 seconds is set to prevent indefinite waiting.
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        # If socket connection fails, it means there's no internet access.
        print("No internet connection detected (OSError).")
        pass
    except Exception as e:
        # Catches any other unexpected errors during the check.
        print(f"Error checking internet connection: {e}")
    return False


def wait_for_internet_connection(log_list):
    """
    Waits indefinitely for an internet connection to be established.
    Logs the status to the provided log_list.
    """
    if check_internet_connection():
        # print("Internet connection already active.")
        return  # No need to wait if already connected

    log_list.append("🌐 Waiting for internet connection...")
    print("Waiting for internet connection...")
    while True:
        if check_internet_connection():
            log_list.append("✅ Internet connection re-established.")
            print("Internet connection re-established.")
            break
        else:
            print("No internet, retrying in 10 seconds...")
            time.sleep(10)  # Wait 10 seconds before trying again


# --- Facebook Post ID Resolution Function ---
def resolve_post_id(raw_input, access_token):
    """
    Resolves various Facebook URL formats or direct IDs into a consistent Facebook Post ID.
    """
    object_id = raw_input.strip()

    # If it's a direct numerical ID, return it immediately
    if object_id.isdigit():
        return object_id

    # If it's not a URL, and not a numerical ID, it's likely an invalid input
    if not object_id.startswith('http'):
        raise ValueError('Invalid input: Not a URL and not a direct numerical Post ID.')

    try:
        url_obj = urlparse(object_id)
        pathname = url_obj.path
        query_params = parse_qs(url_obj.query)

        # Check for video watch URL (e.g., facebook.com/watch/?v=12345)
        if pathname == '/watch/' and 'v' in query_params:
            return query_params['v'][0]

        # Check for traditional /permalink.php?story_fbid=ID&id=USER_ID format
        if pathname == '/permalink.php' and 'story_fbid' in query_params:
            story_fbid = query_params['story_fbid'][0]
            graph_url = f"https://graph.facebook.com/v20.0/{story_fbid}?access_token={access_token}"
            response = requests.get(graph_url)
            data = response.json()
            if response.status_code == 200 and 'id' in data:
                return data['id']
            else:
                raise Exception(data.get('error', {}).get('message', 'Failed to resolve permalink story_fbid.'))

        # New logic for /user/posts/pfbid... or /groups/GROUP_ID/posts/pfbid...
        pfbid_match = re.search(r'(?:posts|photos|videos)/(pfbid\d+)', pathname, re.IGNORECASE)
        if pfbid_match:
            pfbid = pfbid_match.group(1)
            # Try to resolve the pfbid directly
            graph_url = f"https://graph.facebook.com/v20.0/{pfbid}?access_token={access_token}"
            response = requests.get(graph_url)
            data = response.json()
            if response.status_code == 200 and 'id' in data:
                return data['id']
            else:
                # If direct resolution fails, try fetching the entire URL to get its ID
                full_url_graph_url = f"https://graph.facebook.com/v20.0/?id={object_id}&access_token={access_token}"
                full_url_response = requests.get(full_url_graph_url)
                full_url_data = full_url_response.json()
                if full_url_response.status_code == 200 and full_url_data.get('og_object', {}).get('id'):
                    return full_url_data['og_object']['id']
                raise Exception(full_url_data.get('error', {}).get('message',
                                                                   'Failed to resolve pfbid post ID from Graph API and full URL resolution.'))

        # Old-style Post URL (e.g., /username/posts/12345 or /page_name/posts/12345)
        legacy_post_match = re.match(r'^/([^/]+)/posts/(\d+)', pathname)
        if legacy_post_match:
            username_or_page_name = legacy_post_match.group(1)
            post_id_part = legacy_post_match.group(2)

            # Check for combined ID format (e.g., 12345_67890)
            if '_' in post_id_part:
                return post_id_part  # Already in combined ID format

            try:
                # Attempt to get the page/user ID from the username/page_name part
                page_id_graph_url = f"https://graph.facebook.com/v20.0/{username_or_page_name}?access_token={access_token}"
                page_id_response = requests.get(page_id_graph_url)
                page_id_data = page_id_response.json()
                if page_id_response.status_code == 200 and page_id_data.get('id'):
                    return f"{page_id_data['id']}_{post_id_part}"  # Format for user/page posts
                else:
                    return post_id_part  # Fallback if no page ID found
            except Exception:
                return post_id_part  # If fetching page ID fails, assume it's just the post ID

        # Final fallback: try to query the URL itself for an object ID.
        graph_url_fallback = f"https://graph.facebook.com/v20.0/?id={object_id}&access_token={access_token}"
        response_fallback = requests.get(graph_url_fallback)
        data_fallback = response_fallback.json()

        if response_fallback.status_code == 200 and data_fallback.get('og_object', {}).get('id'):
            return data_fallback['og_object']['id']
        if response_fallback.status_code == 200 and data_fallback.get('id'):
            return data_fallback['id']
        raise Exception(
            data_fallback.get('error', {}).get('message', 'No ID found for the provided URL or unsupported format.'))

    except Exception as e:
        raise ValueError(f"URL parsing or API error: {e}")


# --- Airplanemode Script Execution Function ---
def run_airplanemode_script(log_list):
    """
    Executes the airplanemode.py script if the path is configured and valid.
    Logs the execution status and output.
    """
    if not AIRPLANEMODE_SCRIPT_PATH:
        log_list.append("⚠️ AIRPLANEMODE_SCRIPT_PATH is not set. Skipping airplanemode.py execution.")
        print("⚠️ AIRPLANEMODE_SCRIPT_PATH is not set. Skipping airplanemode.py execution.")
        return

    if not os.path.exists(AIRPLANEMODE_SCRIPT_PATH):
        log_list.append(f"❌ airplanemode.py not found at: {AIRPLANEMODE_SCRIPT_PATH}. Please check the path.")
        print(f"❌ airplanemode.py not found at: {AIRPLANEMODE_SCRIPT_PATH}. Please check the path.")
        return

    log_list.append(f"🛫 Running airplanemode.py script: {AIRPLANEMODE_SCRIPT_PATH}")
    print(f"Running airplanemode.py script: {AIRPLANEMODE_SCRIPT_PATH}")
    try:
        # Use subprocess.run for simple command execution.
        # capture_output=True to get stdout/stderr, text=True to decode as string
        result = subprocess.run(['python', AIRPLANEMODE_SCRIPT_PATH], capture_output=True, text=True, check=True,
                                timeout=30)  # Add timeout
        if result.stdout:
            log_list.append(f"   Airplanemode Script Output: {result.stdout.strip()}")
            print(f"   Airplanemode Script Output: {result.stdout.strip()}")
        if result.stderr:
            log_list.append(f"   Airplanemode Script Errors: {result.stderr.strip()}")
            print(f"   Airplanemode Script Errors: {result.stderr.strip()}")
    except subprocess.CalledProcessError as e:
        log_list.append(f"❌ Error running airplanemode.py (Exit Code {e.returncode}): {e.stderr.strip()}")
        print(f"❌ Error running airplanemode.py (Exit Code {e.returncode}): {e.stderr.strip()}")
    except FileNotFoundError:
        log_list.append(f"❌ Python interpreter not found or script path is incorrect: {AIRPLANEMODE_SCRIPT_PATH}")
        print(f"❌ Python interpreter not found or script path is incorrect: {AIRPLANEMODE_SCRIPT_PATH}")
    except subprocess.TimeoutExpired:
        log_list.append(f"❌ airplanemode.py script timed out after 30 seconds.")
        print(f"❌ airplanemode.py script timed out after 30 seconds.")
    except Exception as e:
        log_list.append(f"❌ An unexpected error occurred while running airplanemode.py: {e}")
        print(f"❌ An unexpected error occurred while running airplanemode.py: {e}")


# --- Flask Routes ---
@app.route('/', methods=['GET'])
def index():
    """
    Renders the main index page, displaying reaction and comment logs.
    """
    return render_template('index.html', reaction_logs=request.args.getlist('reaction_log'),
                           comment_logs=request.args.getlist('comment_log'))


@app.route('/send_reaction', methods=['POST'])
def send_reaction():
    """
    Handles sending reactions to Facebook posts.
    Includes an internet connection check and airplanemode script execution.
    """
    global token_usage_counter  # Declare intent to modify global variable
    reaction_logs = []

    # Call the wait_for_internet_connection function at the beginning of the route
    # This ensures there's an internet connection before even loading tokens or processing files.
    wait_for_internet_connection(reaction_logs)

    access_tokens = []
    if 'token_file' in request.files and request.files['token_file'].filename != '':
        token_file = request.files['token_file']
        tokens_content = token_file.read().decode('utf-8')
        access_tokens = [line.strip() for line in tokens_content.splitlines() if line.strip()]
        reaction_logs.append(
            f"Loaded {len(access_tokens)} access tokens." if access_tokens else "No access tokens found in the file.")
    else:
        flash('⚠️ Please upload an Access Token file for reactions.', 'error')
        # Redirect back to index with logs
        return redirect(url_for('index', reaction_log=reaction_logs, _anchor='reactionPage'))

    # Get all submitted post IDs and reaction types.
    post_id_urls = request.form.getlist('reaction_link_input[]')
    reaction_types = request.form.getlist('reaction_type[]')

    if not post_id_urls:
        flash('⚠️ Please add at least one Facebook Post ID/URL for reactions.', 'error')
        return redirect(url_for('index', reaction_log=reaction_logs, _anchor='reactionPage'))

    overall_success_count = 0
    overall_error_count = 0

    reaction_logs.append("--- Starting Reaction Process ---")

    # Process each access token
    for token_idx, token in enumerate(access_tokens):
        reaction_logs.append(f"--- Processing with Access Token {token_idx + 1} (Token ending: {token[-5:]}) ---")
        print(f"Processing with Access Token {token_idx + 1} (Token ending: {token[-5:]})")

        # Increment counter for each token processed
        token_usage_counter += 1

        # Check if airplanemode.py should be run
        if TOKENS_PER_AIRPLANEMODE_CYCLE > 0 and token_usage_counter % TOKENS_PER_AIRPLANEMODE_CYCLE == 0:
            reaction_logs.append(f"--- Triggering airplanemode.py (Token usage count: {token_usage_counter}) ---")
            print(f"Triggering airplanemode.py (Token usage count: {token_usage_counter})")
            run_airplanemode_script(reaction_logs)
            reaction_logs.append(f"--- Finished airplanemode.py trigger ---")
            # Optional: Add a small delay after running airplanemode.py
            time.sleep(5)  # Wait 5 seconds for network to potentially reset after airplanemode (important!)
            wait_for_internet_connection(reaction_logs)  # Re-check internet after airplane mode

        # Process each post/reaction pair
        for i in range(len(post_id_urls)):
            # This inner loop ensures that if a network error occurs for a specific post,
            # it will retry for that post after checking for internet connection.
            max_retries = 3
            current_retries = 0
            while current_retries < max_retries:
                post_id_url = post_id_urls[i].strip()
                reaction_type = reaction_types[i] if i < len(reaction_types) else 'LIKE'

                if not post_id_url:
                    reaction_logs.append(f"ℹ️ Skipping empty Post ID/URL entry {i + 1}.")
                    break  # Break inner while loop to move to the next post

                object_id = None
                try:
                    # Resolve post ID - this also needs internet, so it's inside the retry loop
                    object_id = resolve_post_id(post_id_url, token)
                except ValueError as e:
                    reaction_logs.append(f"❌ Error resolving Post ID/URL {i + 1} ('{post_id_url}'): {e}")
                    overall_error_count += 1
                    break  # Non-network error, move to next post

                try:
                    reaction_url = f"https://graph.facebook.com/v20.0/{object_id}/reactions"
                    params = {'type': reaction_type, 'access_token': token}
                    response = requests.post(reaction_url, data=params, timeout=10)  # Added timeout for robustness
                    data = response.json()

                    if response.status_code == 200 and data.get('success') is True:
                        reaction_logs.append(
                            f"✅ Reaction '{reaction_type}' success for post {object_id} (Link {i + 1})")
                        overall_success_count += 1
                        break  # Success, move to the next post
                    else:
                        error_message = data.get('error', {}).get('message', 'Unknown error')
                        reaction_logs.append(
                            f"❌ Reaction failed for post {object_id} (Link {i + 1}). Error: {error_message}")
                        overall_error_count += 1
                        # If the error is not network related, break and move to next post
                        if "Network error" not in error_message and "Please try again later" not in error_message and "An unexpected error has occurred" not in error_message:
                            break  # Break inner while loop for non-network errors that are not transient

                        current_retries += 1
                        if current_retries < max_retries:
                            reaction_logs.append(
                                f"Retrying reaction for post {object_id} (Attempt {current_retries}/{max_retries}) due to transient error...")
                            print(
                                f"Retrying reaction for post {object_id} (Attempt {current_retries}/{max_retries}) due to transient error...")
                            time.sleep(5)  # Small delay before retrying
                            wait_for_internet_connection(reaction_logs)  # Check and wait for internet before next retry
                        else:
                            reaction_logs.append(f"❌ Max retries reached for post {object_id}. Moving to next.")
                            print(f"Max retries reached for post {object_id}. Moving to next.")
                            break

                except requests.exceptions.RequestException as e:
                    # This catches actual network errors (e.g., DNS resolution failed, connection refused, timeout)
                    current_retries += 1
                    reaction_logs.append(f"❌ Network error for post {object_id} (Link {i + 1}): {e}")
                    print(f"Network error for post {object_id} (Link {i + 1}): {e}")
                    if current_retries < max_retries:
                        reaction_logs.append(
                            f"Retrying reaction for post {object_id} (Attempt {current_retries}/{max_retries}) due to network issue...")
                        print(
                            f"Retrying reaction for post {object_id} (Attempt {current_retries}/{max_retries}) due to network issue...")
                        wait_for_internet_connection(
                            reaction_logs)  # Wait for internet connection if a network error occurs
                        time.sleep(5)  # Add a small delay before retrying the same post
                    else:
                        reaction_logs.append(f"❌ Max retries reached for post {object_id}. Moving to next.")
                        print(f"Max retries reached for post {object_id}. Moving to next.")
                        break
                except Exception as e:
                    reaction_logs.append(f"❌ An unexpected error occurred for post {object_id} (Link {i + 1}): {e}")
                    overall_error_count += 1
                    break  # Unexpected error, move to the next post

    reaction_logs.append("--- Reaction Process Finished ---")
    reaction_logs.append(f"✅ Total Successful Reactions: {overall_success_count}")
    reaction_logs.append(f"❌ Total Failed Reactions: {overall_error_count}")

    # Pass logs back via redirect to avoid form resubmission on refresh
    return redirect(url_for('index', reaction_log=reaction_logs, _anchor='reactionPage'))


@app.route('/send_comment', methods=['POST'])
def send_comment():
    """
    Handles sending comments to Facebook posts.
    Includes an internet connection check and airplanemode script execution.
    """
    global token_usage_counter  # Declare intent to modify global variable
    comment_logs = []

    # Call the wait_for_internet_connection function at the beginning of the route
    wait_for_internet_connection(comment_logs)

    comment_tokens = []
    if 'comment_token_file' in request.files and request.files['comment_token_file'].filename != '':
        token_file = request.files['comment_token_file']
        tokens_content = token_file.read().decode('utf-8')
        comment_tokens = [line.strip() for line in tokens_content.splitlines() if line.strip()]
        comment_logs.append(
            f"Loaded {len(comment_tokens)} access tokens." if comment_tokens else "No access tokens found in the file.")
    else:
        flash('⚠️ Please upload an Access Token file for comments.', 'error')
        return redirect(url_for('index', comment_log=comment_logs, _anchor='commentPage'))

    # Get all submitted post IDs and comment files
    post_id_urls = request.form.getlist('comment_link_input[]')

    # Files are handled differently. request.files.getlist('comment_path_file[]') will give FileStorage objects
    comment_files_data = []
    uploaded_comment_files = request.files.getlist('comment_path_file[]')

    # Process each uploaded comment file
    for file_idx, file_obj in enumerate(uploaded_comment_files):
        if file_obj.filename != '':
            comments_content = file_obj.read().decode('utf-8')
            comments_list = [line.strip() for line in comments_content.splitlines() if line.strip()]
            comment_files_data.append(comments_list)
            comment_logs.append(
                f"Loaded {len(comments_list)} comments from file {file_idx + 1} ('{file_obj.filename}').")
        else:
            comment_files_data.append([])  # Append empty list if file input was empty for this row

    if not any(post_id_urls) and not any(comment_files_data):
        flash('⚠️ Please add at least one Post ID/URL AND upload comment files.', 'error')
        return redirect(url_for('index', comment_log=comment_logs, _anchor='commentPage'))

    # Ensure there's a comment file for each link row, even if empty
    # This aligns comment_files_data with post_id_urls by index
    num_entries = max(len(post_id_urls), len(comment_files_data))

    # Extend lists with empty values if one is shorter than the other
    post_id_urls.extend([''] * (num_entries - len(post_id_urls)))
    comment_files_data.extend([[]] * (num_entries - len(comment_files_data)))

    overall_success_count = 0
    overall_error_count = 0

    comment_logs.append("--- Starting Comment Process ---")

    for token_idx, token in enumerate(comment_tokens):
        comment_logs.append(f"--- Processing with Access Token {token_idx + 1} (Token ending: {token[-5:]}) ---")
        print(f"Processing with Access Token {token_idx + 1} (Token ending: {token[-5:]})")

        # Increment counter for each token processed
        token_usage_counter += 1

        # Check if airplanemode.py should be run
        if TOKENS_PER_AIRPLANEMODE_CYCLE > 0 and token_usage_counter % TOKENS_PER_AIRPLANEMODE_CYCLE == 0:
            comment_logs.append(f"--- Triggering airplanemode.py (Token usage count: {token_usage_counter}) ---")
            print(f"Triggering airplanemode.py (Token usage count: {token_usage_counter})")
            run_airplanemode_script(comment_logs)
            comment_logs.append(f"--- Finished airplanemode.py trigger ---")
            # Optional: Add a small delay after running airplanemode.py
            time.sleep(5)  # Wait 5 seconds for network to potentially reset after airplanemode
            wait_for_internet_connection(comment_logs)  # Re-check internet after airplane mode

        for i in range(num_entries):
            # This inner loop ensures that if a network error occurs for a specific post,
            # it will retry for that post after checking for internet connection.
            max_retries = 3
            current_retries = 0
            while current_retries < max_retries:
                raw_input_post_or_link = post_id_urls[i].strip()
                available_comments = comment_files_data[i]

                if not raw_input_post_or_link and not available_comments:
                    comment_logs.append(
                        f"ℹ️ Skipping Link {i + 1}: No Post ID/URL or comments provided for this entry.")
                    break  # Break inner while loop to move to the next post

                target_post_id = None
                if raw_input_post_or_link:
                    try:
                        # Resolve post ID - this also needs internet, so it's inside the retry loop
                        target_post_id = resolve_post_id(raw_input_post_or_link, token)
                    except ValueError as e:
                        comment_logs.append(f"❌ Error resolving Post ID/URL {i + 1} ('{raw_input_post_or_link}'): {e}")
                        overall_error_count += 1
                        break  # Non-network error, move to next post
                else:
                    comment_logs.append(
                        f"⚠️ Warning: Comment file provided for row {i + 1} but no Post ID/URL. Skipping this entry.")
                    overall_error_count += 1
                    break  # Move to next post

                if not available_comments:
                    comment_logs.append(
                        f"ℹ️ Skipping comment for post {target_post_id} (Link {i + 1}): No comments loaded from file.")
                    break  # Move to next post

                comment_content_to_send = random.choice(available_comments)
                comment_logs.append(
                    f"Sending random comment for post {target_post_id} (Link {i + 1}): \"{comment_content_to_send[:50]}...\"")

                try:
                    comment_url = f"https://graph.facebook.com/v20.0/{target_post_id}/comments"
                    params = {'message': comment_content_to_send, 'access_token': token}
                    response = requests.post(comment_url, data=params, timeout=10)  # Added timeout
                    data = response.json()

                    if response.status_code == 200 and 'id' in data:  # A successful comment returns the comment ID
                        comment_logs.append(
                            f"✅ Comment success for post {target_post_id} (Link {i + 1}). Comment ID: {data['id']}")
                        overall_success_count += 1
                        break  # Success, move to the next post
                    else:
                        error_message = data.get('error', {}).get('message', 'Unknown error')
                        comment_logs.append(
                            f"❌ Comment failed for post {target_post_id} (Link {i + 1}). Error: {error_message}")
                        overall_error_count += 1
                        # If the error is not network related, break and move to next post
                        if "Network error" not in error_message and "Please try again later" not in error_message and "An unexpected error has occurred" not in error_message:
                            break  # Break inner while loop for non-network errors that are not transient

                        current_retries += 1
                        if current_retries < max_retries:
                            comment_logs.append(
                                f"Retrying comment for post {target_post_id} (Attempt {current_retries}/{max_retries}) due to transient error...")
                            print(
                                f"Retrying comment for post {target_post_id} (Attempt {current_retries}/{max_retries}) due to transient error...")
                            time.sleep(5)  # Short delay before retrying
                            wait_for_internet_connection(comment_logs)  # Check and wait for internet before next retry
                        else:
                            comment_logs.append(f"❌ Max retries reached for post {target_post_id}. Moving to next.")
                            print(f"Max retries reached for post {target_post_id}. Moving to next.")
                            break

                except requests.exceptions.RequestException as e:
                    # This catches actual network errors
                    current_retries += 1
                    comment_logs.append(f"❌ Network error for post {target_post_id} (Link {i + 1}): {e}")
                    print(f"❌ Network error for post {target_post_id} (Link {i + 1}): {e}")
                    if current_retries < max_retries:
                        comment_logs.append(
                            f"Retrying comment for post {target_post_id} (Attempt {current_retries}/{max_retries}) due to network issue...")
                        print(
                            f"Retrying comment for post {target_post_id} (Attempt {current_retries}/{max_retries}) due to network issue...")
                        wait_for_internet_connection(
                            comment_logs)  # Wait for internet connection if a network error occurs
                        time.sleep(5)  # Add a small delay before retrying the same post
                    else:
                        comment_logs.append(f"❌ Max retries reached for post {target_post_id}. Moving to next.")
                        print(f"❌ Max retries reached for post {target_post_id}. Moving to next.")
                        break
                except Exception as e:
                    comment_logs.append(f"❌ An unexpected error occurred for post {target_post_id} (Link {i + 1}): {e}")
                    overall_error_count += 1
                    break  # Unexpected error, move to the next post

    comment_logs.append("--- Comment Process Finished ---")
    comment_logs.append(f"✅ Total Successful Comments: {overall_success_count}")
    comment_logs.append(f"❌ Total Failed Comments: {overall_error_count}")

    return redirect(url_for('index', comment_log=comment_logs, _anchor='commentPage'))


if __name__ == '__main__':
    # You might want to change host='0.0.0.0' to make it accessible from other devices on your local network
    # For local testing on the same device, host='127.0.0.1' or no host argument is fine.
    # Set debug=False for production.
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
