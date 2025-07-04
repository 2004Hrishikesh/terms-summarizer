import unittest
import os
from io import BytesIO
from app import app  # Ensure this imports your Flask app object

class FileUploadTestCase(unittest.TestCase):

    def setUp(self):
        """Set up test client and environment"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['UPLOAD_FOLDER'] = 'test_uploads'
        self.client = app.test_client()

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    def tearDown(self):
        """Clean up after test"""
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.remove(file_path)
        os.rmdir(app.config['UPLOAD_FOLDER'])

    def test_file_upload_txt(self):
        """Test uploading a simple .txt file"""
        data = {
            'input_method': 'file',
            'file': (BytesIO(b"This is a test terms and conditions file. Please read carefully."), 'terms.txt'),
            'summary_length': '2',
            'model_type': 'lexrank'
        }
        response = self.client.post('/summarize', data=data, content_type='multipart/form-data', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Summary', response.data)
        self.assertIn(b'Key Points', response.data)
        print("✓ .txt file upload works correctly")

    def test_file_upload_pdf(self):
        """Test uploading a .pdf file"""
        # Create a simple PDF file in-memory
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        c.drawString(100, 750, "This is a test PDF for terms and conditions.")
        c.save()
        pdf_buffer.seek(0)

        data = {
            'input_method': 'file',
            'file': (pdf_buffer, 'test.pdf'),
            'summary_length': '3',
            'model_type': 'lexrank'
        }
        response = self.client.post('/summarize', data=data, content_type='multipart/form-data', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Summary', response.data)
        self.assertIn(b'Key Points', response.data)
        print("✓ .pdf file upload works correctly")

if __name__ == '__main__':
    unittest.main()
