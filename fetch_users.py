import requests
import csv

# GitHub API endpoints
search_url = "https://api.github.com/search/users"
repo_url = "https://api.github.com/users/{}/repos"

# Function to clean up company names
def clean_company(company):
    if company:
        return company.strip().lstrip('@').upper()
    return ""

# Function to fetch users from Stockholm with over 100 followers
def get_stockholm_users():
    query = 'location:Stockholm followers:>100'
    response = requests.get(search_url, params={'q': query})
    return response.json().get('items', [])

# Function to fetch repositories for a user
def get_user_repos(username):
    response = requests.get(repo_url.format(username))
    return response.json()

# Main function to gather data
def main():
    users = get_stockholm_users()
    users_data = []
    repositories_data = []

    for user in users:
    # Prepare user data
        user_info = {
            'login': user['login'],
            'name': user.get('name', ''),  # Use .get() to avoid KeyError
            'company': clean_company(user.get('company', '')),  # Use .get() for safety
            'location': user.get('location', ''),
            'email': user.get('email', ''),
            'hireable': str(user.get('hireable', '')).lower() if user.get('hireable') is not None else '',
            'bio': user.get('bio', ''),
            'public_repos': user.get('public_repos', 0),  # Default to 0 if not present
            'followers': user.get('followers', 0),  # Default to 0 if not present
            'following': user.get('following', 0),  # Default to 0 if not present
            'created_at': user.get('created_at', '')
        }
        users_data.append(user_info)


        # Fetch user's repositories
        repos = get_user_repos(user['login'])
        for repo in repos:
            repo_info = {
                'login': user['login'],
                'full_name': repo['full_name'],
                'created_at': repo['created_at'],
                'stargazers_count': repo['stargazers_count'],
                'watchers_count': repo['watchers_count'],
                'language': repo['language'] or '',
                'has_projects': str(repo['has_projects']).lower(),
                'has_wiki': str(repo['has_wiki']).lower(),
                'license_name': repo['license']['key'] if repo['license'] else ''
            }
            repositories_data.append(repo_info)

    # Write users data to existing CSV
    with open('users.csv', mode='w', newline='', encoding='utf-8') as users_file:
        fieldnames = users_data[0].keys()
        writer = csv.DictWriter(users_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(users_data)

    # Write repositories data to existing CSV
    with open('repositories.csv', mode='w', newline='', encoding='utf-8') as repos_file:
        fieldnames = repositories_data[0].keys()
        writer = csv.DictWriter(repos_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(repositories_data)

if __name__ == "__main__":
    main()
