from flask import Flask, request, jsonify
import spacy

app = Flask(__name__)
nlp = spacy.load('en_core_web_sm')

texts = {
    '1': ['''Drones, also known as unmanned aerial vehicles (UAVs), have rapidly evolved from military applications to a wide range of civilian uses. 
    Their ability to navigate autonomously or be remotely controlled makes them ideal for tasks that are dangerous, difficult, or time-consuming for humans. 
    In agriculture, drones are used to map fields, monitor crop health, and apply pesticides and fertilizers with greater precision than traditional methods.
    This not only reduces waste but also minimizes the environmental impact of farming. 
    In the field of search and rescue, drones can quickly cover large areas to locate missing people or assess damage after natural disasters. 
    Their small size and maneuverability allow them to reach areas inaccessible to ground vehicles or traditional manned aircraft. 
    Additionally, drones are increasingly being used for delivery purposes, particularly in densely populated urban areas. 
    Companies are exploring the use of drones to deliver packages, food, and even medical supplies, potentially revolutionizing the way goods are transported.
     However, the rise of drones also raises concerns. Privacy advocates worry about the potential for intrusive surveillance, particularly as drones become more affordable and readily available. 
     Additionally, safety regulations are still being developed to address the risks associated with drone operation, especially in crowded airspace. 
     While the benefits of drones are undeniable, it's crucial to find a balance between innovation and responsible use.'''],
    '2': ['''Indian cuisine is a symphony of flavors, aromas, and techniques, reflecting the country's rich history, diverse cultures, and regional variations.
     From the fiery curries of the south to the creamy Mughlai dishes of the north, each region boasts its own unique culinary identity. 
     Spices play a central role in Indian food, adding depth, complexity, and a touch of warmth. 
     Common ingredients include turmeric, coriander, cumin, chilies, ginger, and garam masala, a blend of aromatic spices.
      Rice is the staple food in most parts of India, often served alongside dals (lentil stews), vegetables, and meat curries. 
      Vegetarianism is prevalent, with a vast array of lentil-based dishes offering a complete protein source. 
      Street food is a vibrant aspect of Indian cuisine, with vendors offering an array of savory and sweet treats like samosas, chaat (savory snacks), and jalebis (deep-fried, syrup-soaked sweets). 
      Beyond the food itself, Indian cuisine is deeply intertwined with tradition and social customs. 
      Meals are often communal affairs, shared with family and friends. Specific dishes are associated with festivals and religious celebrations, adding a layer of cultural significance to the dining experience. 
      From the bustling street stalls to the elegant fine-dining establishments, Indian cuisine offers a captivating journey for the senses, showcasing the country's cultural richness and culinary heritage.''']
}

def summarize_text(text_id, num_sentences=2):
    text_list = texts.get(text_id)
    
    if not text_list:
        return 'Text not found'

    text = text_list[0]
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]

    sentence_scores = {}
    for sent in doc.sents:
        score = sum(1 for ent in sent.ents) + sum(1 for chunk in sent.noun_chunks)
        sentence_scores[sent.text] = score

    sorted_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
    summary_sentences = sorted_sentences[:num_sentences]
    summary = ' '.join([sent[0] for sent in summary_sentences])

    return summary





@app.route('/summarize', methods=['POST'])
def summarize_text_api():
    data = request.json
    text_id = data.get('text_id')
    text = texts.get(text_id, '')
    summary = summarize_text(text)
    return jsonify({'summary': summary})

@app.route('/text', methods=['GET'])
def get_texts():
    return jsonify(texts)

@app.route('/text', methods=['POST'])
def add_text():
    data = request.json
    text = data.get('text', '')
    text_id = max(map(int, texts.keys()), default=0) + 1
    texts[text_id] = [text]

    return jsonify({'text_id': text_id})


@app.route('/text/<int:text_id>', methods=['DELETE'])
def delete_text(text_id):
    if text_id in texts:
        del texts[text_id]
        return jsonify({'message': f'Text with ID {text_id} deleted successfully'})
    else:
        return jsonify({'message': f'Text with ID {text_id} not found'})

# Tests
import pytest

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_summarize_text(client):
    response = client.post('/summarize', json={'text_id': 1})
    assert response.status_code == 200
    assert 'summary' in response.json

def test_get_texts(client):
    response = client.get('/text')
    assert response.status_code == 200
    assert isinstance(response.json, dict)

def test_add_text(client):
    response = client.post('/text', json={'text': 'This is a new text to be added'})
    assert response.status_code == 200
    assert 'text_id' in response.json


def test_delete_text(client):
    response = client.delete('/text/1')
    assert response.status_code == 200
    assert 'message' in response.json

if __name__ == '__main__':
    app.run(debug=True)
