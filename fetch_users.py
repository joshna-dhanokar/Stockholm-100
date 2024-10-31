import requests
import csv
import time

# GitHub API endpoints
search_url = "https://api.github.com/search/users"
repo_url = "https://api.github.com/users/{}/repos"

# Replace 'YOUR_TOKEN' with your actual token
headers = {
    'Authorization': 'token you_token'
}

def clean_company(company):
    return company.strip().lstrip('@').upper() if company else ""

def get_stockholm_users(page=1):
    query = 'location:Stockholm followers:>100'
    response = requests.get(search_url, params={'q': query, 'page': page, 'per_page': 100}, headers=headers)

    if response.status_code == 403:  # Forbidden, likely due to rate limit
        print("Rate limit exceeded. Waiting for a minute...")
        time.sleep(60)  # Wait for 1 minute before retrying
        return get_stockholm_users(page)  # Retry fetching users

    if response.status_code != 200:
        print(f"Error fetching users: {response.status_code}, {response.json()}")
        return []

    total_count = response.json().get('total_count', 0)
    users = response.json().get('items', [])
    print(f"Fetched {len(users)} users from page {page} (Total available: {total_count})")  # Print fetched and total available
    return users

def get_user_repos(username):
    response = requests.get(repo_url.format(username), headers=headers)

    if response.status_code == 403:
        print(f"Rate limit exceeded for {username}. Waiting for a minute...")
        time.sleep(60)  # Wait for 1 minute
        return get_user_repos(username)  # Retry fetching repos

    return response.json()

def main():
    total_users_fetched = 0
    users = []
    page = 1

    while True:
        print(f"Fetching page {page}...")
        new_users = get_stockholm_users(page)
        
        if not new_users:  # Exit if no more users are returned
            break

        users += new_users  # Add new users
        total_users_fetched += len(new_users)
        
        print(f"Total users fetched so far: {total_users_fetched}")
        page += 1  # Increment page for the next batch

    if total_users_fetched == 0:
        print("No users found. Exiting.")
        return

    users_data = []
    repositories_data = []

    for user in users:
        user_info = {
            'login': user['login'],
            'name': user.get('name', ''),
            'company': clean_company(user.get('company', '')),
            'location': user.get('location', ''),
            'email': user.get('email', ''),
            'hireable': str(user.get('hireable', '')).lower() if user.get('hireable') is not None else '',
            'bio': user.get('bio', ''),
            'public_repos': user.get('public_repos', 0),
            'followers': user.get('followers', 0),
            'following': user.get('following', 0),
            'created_at': user.get('created_at', '')
        }
        users_data.append(user_info)

        repos = get_user_repos(user['login'])
        if isinstance(repos, list):
            for repo in repos:
                repo_info = {
                    'login': user['login'],
                    'full_name': repo['full_name'],
                    'created_at': repo['created_at'],
                    'stargazers_count': repo['stargazers_count'],
                    'watchers_count': repo['watchers_count'],
                    'language': repo['language'] or '',
                    'has_projects': str(repo.get('has_projects', False)).lower(),
                    'has_wiki': str(repo.get('has_wiki', False)).lower(),
                    'license_name': repo['license']['key'] if repo.get('license') else ''
                }
                repositories_data.append(repo_info)

    # Write data to CSV files
    if users_data:
        with open('users.csv', mode='w', newline='', encoding='utf-8') as users_file:
            fieldnames = users_data[0].keys()
            writer = csv.DictWriter(users_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(users_data)

    if repositories_data:
        with open('repositories.csv', mode='w', newline='', encoding='utf-8') as repos_file:
            fieldnames = repositories_data[0].keys()
            writer = csv.DictWriter(repos_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(repositories_data)

    print(f"Total users processed and written to CSV: {total_users_fetched}")

if __name__ == "__main__":
    main()
