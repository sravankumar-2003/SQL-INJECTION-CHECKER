from flask import Flask, request, jsonify
from lxml import html
import requests
from requests.exceptions import HTTPError

app = Flask(_name_)


sql_injection_payloads = [
    "' OR 1=1 --",
    "1'; DROP TABLE users; --",
    
]


def parse_input_fields(tree, url):
    input_fields = tree.xpath("//input[@type='text']")
    results = []
    for field in input_fields:
        name = field.get("name")
        if name:
            field_results = {"field": name, "tests": []}
            for payload in sql_injection_payloads:
                
                field_results["tests"].append({"payload": payload, "result": "Test simulated"})
            results.append(field_results)
    return results


@app.route('/check_vulnerability', methods=['POST'])
def check_vulnerability():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        response = requests.get(url)
        response.raise_for_status()
        tree = html.fromstring(response.content)
        results = parse_input_fields(tree, url)
        return jsonify({"url": url, "results": results})
    except HTTPError as e:
        return jsonify({"error": "HTTP Error occurred", "details": str(e)}), 500
    except requests.RequestException as e:
        return jsonify({"error": "Request failed", "details": str(e)}), 500

if _name_ == "_main_":
    app.run(debug=True)