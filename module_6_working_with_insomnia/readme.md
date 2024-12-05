# Working with Insomnia and APIs

# Learning objectives:
- HTTP methods (GET, POST, PUT, DELETE)
- Making API requests using Insomnia and Python
- Understanding the response from an API request
- Understanding the payload of an API request


# Lab 2 instructions:

## Part 1: Introduction to Insomnia and APIs

This tutorial walks you through the Insomnia App, a powerful tool for testing and debugging APIs. You will learn how to install Insomnia, create a new workspace, and send requests to an API.

We'll start with a refresher on APIs and how they work. Then we'll talk about some of the API request we have already made via Python like in module 4.


1. Read https://blog.postman.com/what-are-http-methods/ This explains the different HTTP methods and how they are used in APIs.


2. In module 4 we made a GET request to the Carbon Mapper API to fetch data on methane plumes. We used the `requests` library in Python to make the request. Here is the code snippet: 

```python
def get_plume_data(offset: int = 0, limit: int = 9000) -> Dict[str, Any]:
    """Fetch data from Carbon Mapper API with pagination and filtering"""
    url = "https://api.carbonmapper.org/api/v1/catalog/plumes/annotated"

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'origin': 'https://data.carbonmapper.org',
        'referer': 'https://data.carbonmapper.org/'
    }

    # Calculate date range (last 180 days)
    yesterday = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    today = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')

    params = {
        'limit': limit,
        'offset': offset,
        'bbox': [-126.7568, 10.2448, -62.5152, 60.1746],  # North America bbox
        'datetime': f"{yesterday}/{today}",
        'sort': 'desc'
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()
```
3. You can see the payload of the request in the `params` dictionary. The `requests.get()` function sends a GET request to the specified URL with the headers and parameters provided. The response is then converted to JSON format using the `.json()` method.


4. Now, we will use Insomnia to make the same request to the Carbon Mapper API. Follow the steps below to install Insomnia and create a new workspace.
## Setup Instructions
2. Download and install Insomnia from [here](https://insomnia.rest/download/)


## Part 2: Making API Requests with Insomnia:

1. Open Insomnia and create a new workspace and a new collection. You can name it `Carbon Mapper API`.
2. Click on the `+` button to create a new request.
3. Click on the from curl option and paste the following curl command:
```bash
curl --request GET \
  --url 'https://api.carbonmapper.org/api/v1/catalog/plumes/annotated?bbox%5B%5D=-126.7568&bbox%5B%5D=10.2448&bbox%5B%5D=-62.5152&bbox%5B%5D=60.1746&datetime=2024-09-16T11%3A09%3A19.000Z%2F2024-12-05T11%3A09%3A19.000Z&limit=90&offset=0&sort=desc' \
  --header 'accept: application/json, text/plain, */*' \
  --header 'accept-language: en-US,en;q=0.9' \
  --header 'authority: platform.carbonmapper.org'
```
4. Click send to make the same request we made from python, but now using Insomnia.
5. You should see the response from the API in the right panel. The response will be in JSON format and will contain the methane plume data that we loaded in module 4.
6. Insonmia has taken this curl command and converted it into a GET request. You can see the URL, headers, and parameters in the request. This is how you can make API requests using Insomnia.
https://api.carbonmapper.org/api/v1/catalog/plumes/annotated?bbox%5B%5D=-126.7568&bbox%5B%5D=10.2448&bbox%5B%5D=-62.5152&bbox%5B%5D=60.1746&datetime=2024-09-16T11%3A09%3A19.000Z%2F2024-12-05T11%3A09%3A19.000Z&limit=900&offset=0&sort=desc
![Screenshot 2024-12-05 at 11.29.35 AM.png](Screenshot%202024-12-05%20at%2011.29.35%E2%80%AFAM.png)


# Assessment:


Take a screenshot of the Query tab in Insomnia showing the request URL, headers, and parameters for the Carbon Mapper API request. Save the screenshot in the `assessment` folder.

Commit and push your changes to the repository.


