import os
import re
import json
import zipfile
import xml.etree.ElementTree as ET

def dms_to_decimal(dms_str):
    """
    Converts DMS or Decimal coordinate strings to float decimal degrees.
    Examples:
      "27° 30' N" -> 27.5
      "(27.51° N)" -> 27.51
      "27° 12′ 58″ N" -> 27.216111
      "26.495° N latitude" -> 26.495
      "26.3291" -> 26.3291
    """
    if not dms_str:
        return None
    
    clean_str = dms_str.replace('′', "'").replace('″', '"').strip()
    
    # Try simple decimal degree matching
    dec_match = re.search(r'([-+]?\d+(?:\.\d+)?)\s*°?\s*([NSEW])?', clean_str, re.IGNORECASE)
    
    # Check if there are minutes/seconds
    dms_match = re.search(r'(\d+)\s*°\s*(?:(\d+)\s*[\'\′])?\s*(?:(\d+(?:\.\d+)?)\s*["\″])?\s*([NSEW])?', clean_str, re.IGNORECASE)
    
    if "'" in clean_str or '"' in clean_str or (dms_match and dms_match.group(2)):
        if dms_match:
            deg = float(dms_match.group(1))
            min_val = float(dms_match.group(2)) if dms_match.group(2) else 0.0
            sec_val = float(dms_match.group(3)) if dms_match.group(3) else 0.0
            direction = dms_match.group(4)
            
            val = deg + (min_val / 60.0) + (sec_val / 3600.0)
            if direction and direction.upper() in ['S', 'W']:
                val = -val
            return round(val, 6)
    
    if dec_match:
        val = float(dec_match.group(1))
        direction = dec_match.group(2)
        if direction and direction.upper() in ['S', 'W']:
            val = -val
        return round(val, 6)
        
    return None

def parse_docx_story(docx_path):
    with zipfile.ZipFile(docx_path) as z:
        xml_content = z.read('word/document.xml')
        tree = ET.fromstring(xml_content)
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
        paragraphs = []
        for p in tree.findall('.//w:p', ns):
            texts = [node.text for node in p.findall('.//w:t', ns) if node.text]
            p_text = ''.join(texts).strip()
            if p_text:
                paragraphs.append(p_text)
                
    # Document starts with title
    doc_title = paragraphs[0] if paragraphs else "Story Map: Following the River"
    
    # The structure has sections starting with title, followed by coordinate paragraph(s), then narrative text.
    # Hardcoded known POIs from docx inspection to ensure 100% exact parsing:
    pois_raw = [
        {
            "id": 1,
            "title": "Tsatichhu",
            "subtitle": "When the mountain became a dam",
            "lat_str": "27° 30' N (27.51° N)",
            "lon_str": "91° 10' E (91.16° E)",
            "lat": 27.51,
            "lon": 91.16,
            "text": paragraphs[4]
        },
        {
            "id": 2,
            "title": "Kurichhu Hydropower Project, Bhutan",
            "subtitle": "Where the story begins",
            "lat_str": "27° 12′ 58″ N",
            "lon_str": "91° 12′ 18″ E",
            "lat": dms_to_decimal("27° 12′ 58″ N"),
            "lon": dms_to_decimal("91° 12′ 18″ E"),
            "text": paragraphs[7]
        },
        {
            "id": 3,
            "title": "Mathanguri",
            "subtitle": "Where the river crosses a border",
            "lat_str": "26° 46' 57\" N",
            "lon_str": "90° 57' 28\" E",
            "lat": dms_to_decimal("26° 46' 57\" N"),
            "lon": dms_to_decimal("90° 57' 28\" E"),
            "text": paragraphs[11] + "\n\n" + paragraphs[11] if len(paragraphs) > 11 else paragraphs[10]
        },
        {
            "id": 4,
            "title": "Hakuwa",
            "subtitle": "The river that stopped being the main river",
            "lat_str": "26.63° N",
            "lon_str": "90.91° E",
            "lat": 26.63,
            "lon": 90.91,
            "text": paragraphs[14]
        },
        {
            "id": 5,
            "title": "Raghobill",
            "subtitle": "Where the river meets the forest",
            "lat_str": "26.58° N",
            "lon_str": "90.97° E",
            "lat": 26.58,
            "lon": 90.97,
            "text": paragraphs[18]
        },
        {
            "id": 6,
            "title": "Gobardhana",
            "subtitle": "The line between protection and failure",
            "lat_str": "26.58° N",
            "lon_str": "90.98° E",
            "lat": 26.58,
            "lon": 90.98,
            "text": paragraphs[21]
        },
        {
            "id": 7,
            "title": "Elengamari Chapori",
            "subtitle": "Living on land made by the river",
            "lat_str": "26.63° N",
            "lon_str": "90.98° E",
            "lat": 26.63,
            "lon": 90.98,
            "text": paragraphs[24]
        },
        {
            "id": 8,
            "title": "Balabheta",
            "subtitle": "When the river begins to take the land",
            "lat_str": "26.495° N",
            "lon_str": "90.934° E",
            "lat": 26.495,
            "lon": 90.934,
            "text": paragraphs[27]
        },
        {
            "id": 9,
            "title": "Suwapur",
            "subtitle": "When erosion becomes displacement",
            "lat_str": "26.3291° N",
            "lon_str": "91.0103° E",
            "lat": 26.3291,
            "lon": 91.0103,
            "text": paragraphs[31]
        },
        {
            "id": 10,
            "title": "Kalgachia Circle",
            "subtitle": "Where the transformation becomes visible",
            "lat_str": "26.35° N",
            "lon_str": "90.89° E",
            "lat": 26.35,
            "lon": 90.89,
            "text": paragraphs[34]
        }
    ]
    
    # Specific adjustment for Mathanguri paragraph combined text:
    pois_raw[2]["text"] = paragraphs[10] + "\n\n" + paragraphs[11]

    # Add default image placeholders
    for item in pois_raw:
        item["media"] = {
            "type": "image",
            "url": f"assets/images/poi_{item['id']}.jpg",
            "caption": f"Field observation at {item['title']}",
            "alt": item["title"]
        }
        
    return {
        "title": doc_title,
        "subtitle": "Beki River Catchment Field StoryMap & Hydrological Dashboard",
        "pois": pois_raw
    }

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docx_path = os.path.join(base_dir, 'inputs', 'Story Map.docx')
    output_json = os.path.join(base_dir, 'data', 'story_data.json')
    output_md = os.path.join(base_dir, 'data', 'story_points.md')
    
    os.makedirs(os.path.join(base_dir, 'data'), exist_ok=True)
    
    print(f"Reading docx from {docx_path}...")
    data = parse_docx_story(docx_path)
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Wrote structured JSON to {output_json}")
    
    # Also create Markdown file for easy non-expert editing
    md_content = f"# {data['title']}\n\n{data['subtitle']}\n\n---\n\n"
    for poi in data['pois']:
        md_content += f"## {poi['id']}. {poi['title']}\n"
        md_content += f"*{poi['subtitle']}*\n\n"
        md_content += f"**Coordinates**: {poi['lat_str']}, {poi['lon_str']} (`lat: {poi['lat']}`, `lon: {poi['lon']}`)\n\n"
        md_content += f"**Media Image**: `assets/images/poi_{poi['id']}.jpg`\n\n"
        md_content += f"{poi['text']}\n\n---\n\n"
        
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Wrote Markdown data to {output_md}")

if __name__ == '__main__':
    main()
