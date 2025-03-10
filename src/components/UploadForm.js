import React, { useState } from 'react';
import { Form, Button, Container, Row, Col, Card, Alert, Spinner } from 'react-bootstrap';
import axios from 'axios';
import PDFViewer from './PDFViewer';

function UploadForm() {
  const [importFile, setImportFile] = useState(null);
  const [exportFile, setExportFile] = useState(null);
  const [companyInfo, setCompanyInfo] = useState({
    name: '',
    address: '',
    city_state_zip: '',
    contact_name: '',
    contact_title: '',
    phone: '',
    email: '',
    port_code: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showPdf, setShowPdf] = useState(false);
  const [pdfUrl, setPdfUrl] = useState('');

  const handleCompanyInfoChange = (e) => {
    const { name, value } = e.target;
    setCompanyInfo(prev => ({ ...prev, [name]: value }));
  };

  const handleImportFileChange = (e) => {
    setImportFile(e.target.files[0]);
  };

  const handleExportFileChange = (e) => {
    setExportFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!importFile || !exportFile) {
      setError('Please select both import and export files');
      return;
    }
    
    if (!companyInfo.name || !companyInfo.address) {
      setError('Please provide company name and address');
      return;
    }
    
    setLoading(true);
    setError('');
    setSuccess('');
    
    const formData = new FormData();
    formData.append('import_file', importFile);
    formData.append('export_file', exportFile);
    formData.append('company_info', JSON.stringify(companyInfo));
    
    try {
      const response = await axios.post('/api/generate-cbp-form', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setSuccess('Form generated successfully!');
      setPdfUrl(response.data.pdf_url);
      setShowPdf(true);
    } catch (err) {
      console.error('Error generating form:', err);
      setError(err.response?.data?.message || 'Failed to generate form. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container className="my-4">
      <Card>
        <Card.Header as="h4">Generate CBP Form 7551</Card.Header>
        <Card.Body>
          {error && <Alert variant="danger">{error}</Alert>}
          {success && <Alert variant="success">{success}</Alert>}
          
          <Form onSubmit={handleSubmit}>
            <h5 className="mb-3">Company Information</h5>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Company Name</Form.Label>
                  <Form.Control 
                    type="text" 
                    name="name" 
                    value={companyInfo.name} 
                    onChange={handleCompanyInfoChange}
                    required
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Port Code</Form.Label>
                  <Form.Control 
                    type="text" 
                    name="port_code" 
                    value={companyInfo.port_code} 
                    onChange={handleCompanyInfoChange}
                  />
                </Form.Group>
              </Col>
            </Row>
            
            <Row>
              <Col md={8}>
                <Form.Group className="mb-3">
                  <Form.Label>Street Address</Form.Label>
                  <Form.Control 
                    type="text" 
                    name="address" 
                    value={companyInfo.address} 
                    onChange={handleCompanyInfoChange}
                    required
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>City, State, ZIP</Form.Label>
                  <Form.Control 
                    type="text" 
                    name="city_state_zip" 
                    value={companyInfo.city_state_zip} 
                    onChange={handleCompanyInfoChange}
                    required
                  />
                </Form.Group>
              </Col>
            </Row>
            
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Contact Name</Form.Label>
                  <Form.Control 
                    type="text" 
                    name="contact_name" 
                    value={companyInfo.contact_name} 
                    onChange={handleCompanyInfoChange}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Contact Title</Form.Label>
                  <Form.Control 
                    type="text" 
                    name="contact_title" 
                    value={companyInfo.contact_title} 
                    onChange={handleCompanyInfoChange}
                  />
                </Form.Group>
              </Col>
            </Row>
            
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Phone</Form.Label>
                  <Form.Control 
                    type="text" 
                    name="phone" 
                    value={companyInfo.phone} 
                    onChange={handleCompanyInfoChange}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Email</Form.Label>
                  <Form.Control 
                    type="email" 
                    name="email" 
                    value={companyInfo.email} 
                    onChange={handleCompanyInfoChange}
                  />
                </Form.Group>
              </Col>
            </Row>
            
            <h5 className="mb-3 mt-4">Upload Data Files</h5>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Import Data (CSV)</Form.Label>
                  <Form.Control 
                    type="file" 
                    accept=".csv" 
                    onChange={handleImportFileChange}
                    required
                  />
                  <Form.Text className="text-muted">
                    CSV file with import entry data
                  </Form.Text>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Export Data (CSV)</Form.Label>
                  <Form.Control 
                    type="file" 
                    accept=".csv" 
                    onChange={handleExportFileChange}
                    required
                  />
                  <Form.Text className="text-muted">
                    CSV file with export shipment data
                  </Form.Text>
                </Form.Group>
              </Col>
            </Row>
            
            <div className="d-grid gap-2 mt-4">
              <Button 
                variant="primary" 
                type="submit" 
                size="lg"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" />
                    <span className="ms-2">Processing...</span>
                  </>
                ) : 'Generate CBP Form 7551'}
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>
      
      {/* PDF Viewer Modal */}
      <PDFViewer 
        pdfUrl={pdfUrl} 
        show={showPdf} 
        onHide={() => setShowPdf(false)}
        title="CBP Form 7551"
      />
    </Container>
  );
}

export default UploadForm; 