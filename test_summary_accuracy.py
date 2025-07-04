import unittest
from io import BytesIO
from app import app
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SummaryAccuracyTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def cosine_similarity_score(self, text1, text2):
        """Calculate cosine similarity between two summaries"""
        vectorizer = TfidfVectorizer().fit_transform([text1, text2])
        vectors = vectorizer.toarray()
        return cosine_similarity([vectors[0]], [vectors[1]])[0][0]

    def test_summary_similarity_txt(self):
        # Input text
        full_text = (
            "This is a sample terms and conditions document. "
            "It contains important legal information about user rights and responsibilities. "
            "Users must agree to these terms before using the service. "
            "The service provider reserves the right to modify these terms at any time."
        )

        # Expected summary (you can make this closer to what your model actually produces)
        expected_summary = (
            "This is a sample terms and conditions document. "
            "It contains important legal information about user rights and responsibilities."
        )

        data = {
            'input_method': 'text',
            'text_input': full_text,
            'summary_length': '2',
            'model_type': 'lexrank'
        }

        response = self.client.post('/summarize', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Extract actual summary from response HTML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.data, 'html.parser')
        summary_element = soup.find(id='summary')
        self.assertIsNotNone(summary_element)

        generated_summary = summary_element.get_text(strip=True)

        # Compute similarity score
        similarity = self.cosine_similarity_score(generated_summary, expected_summary)

        print(f"✓ Cosine similarity: {similarity:.2f}")
        self.assertGreater(similarity, 0.7, "Summary is too different from expected.")


if __name__ == '__main__':
    unittest.main()
