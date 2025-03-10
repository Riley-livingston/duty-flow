import React, { useEffect, useState } from 'react';
import { Modal, Button, Spinner } from 'react-bootstrap';
import { Document, Page, pdfjs } from 'react-pdf';

// Set up the worker for PDF.js
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

function PDFViewer({ pdfUrl, show, onHide, title }) {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [loading, setLoading] = useState(true);

  function onDocumentLoadSuccess({ numPages }) {
    setNumPages(numPages);
    setLoading(false);
  }

  function changePage(offset) {
    setPageNumber(prevPageNumber => prevPageNumber + offset);
  }

  function previousPage() {
    changePage(-1);
  }

  function nextPage() {
    changePage(1);
  }

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>{title || 'Generated PDF'}</Modal.Title>
      </Modal.Header>
      <Modal.Body className="text-center">
        {loading && (
          <div className="text-center py-5">
            <Spinner animation="border" />
            <p className="mt-2">Loading PDF...</p>
          </div>
        )}
        
        <Document
          file={pdfUrl}
          onLoadSuccess={onDocumentLoadSuccess}
          onLoadError={(error) => console.error('Error loading PDF:', error)}
        >
          <Page pageNumber={pageNumber} />
        </Document>
        
        {numPages && (
          <div className="d-flex justify-content-between align-items-center mt-3">
            <Button onClick={previousPage} disabled={pageNumber <= 1}>
              Previous
            </Button>
            <p>
              Page {pageNumber} of {numPages}
            </p>
            <Button onClick={nextPage} disabled={pageNumber >= numPages}>
              Next
            </Button>
          </div>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
        <Button variant="primary" href={pdfUrl} download target="_blank">
          Download PDF
        </Button>
      </Modal.Footer>
    </Modal>
  );
}

export default PDFViewer; 