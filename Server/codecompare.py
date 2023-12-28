from flask import Flask, request, jsonify
import difflib

app = Flask(__name__)

@app.route('/compare_code', methods=['POST'])
def compare_code():
    try:
        json_data = request.get_json()
        code1 = json_data.get('code1', "").splitlines()
        code2 = json_data.get('code2', "").splitlines()

        matcher = difflib.SequenceMatcher(None, code1, code2)
        similarity_ratio = matcher.ratio()

        output = []
        for tag, i1, i2, j1, j2 in reversed(matcher.get_opcodes()):
            if tag == 'replace':
                output.append(('replace', code1[i1:i2], code2[j1:j2]))
            elif tag == 'delete':
                output.append(('delete', code1[i1:i2]))
            elif tag == 'insert':
                output.append(('insert', code2[j1:j2]))

        response_data = {
            'similarity_ratio': similarity_ratio,
            'code_diff': output
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
