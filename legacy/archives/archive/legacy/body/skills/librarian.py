
import urllib.request
import xml.etree.ElementTree as ET
import requests
import urllib.parse

def search(query: str, max_results: int = 5) -> list[dict]:
    """
    Searches arXiv.org for a given query and returns a list of dictionaries
    containing the title, summary, authors, and id of each result.
    """
    try:
        url = f"http://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(query)}&start=0&max_results={max_results}"
        response = urllib.request.urlopen(url)
        xml_data = response.read()
        root = ET.fromstring(xml_data)

        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        results = []
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns)
            summary = entry.find('atom:summary', ns)
            authors_elements = entry.findall('atom:author/atom:name', ns)
            id_elem = entry.find('atom:id', ns)

            results.append({
                'title': title.text if title is not None else "Unknown",
                'summary': summary.text[:200] + "..." if summary is not None else "Unknown",
                'authors': [a.text for a in authors_elements if a.text],
                'id': id_elem.text if id_elem is not None else ""
            })
        return results
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
