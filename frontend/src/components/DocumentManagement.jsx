import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './DocumentManagement.css';
import DocumentRequirements from './DocumentRequirements';
import DocumentUpload from './DocumentUpload';

// Document type constants
const DOCUMENT_TYPES = {
  IMPORT: 'import_entry',
  EXPORT: 'export_declaration',
  DUTY_PROOF: 'proof_of_duty',
  EXPORT_PROOF: 'proof_of_export',
  SUMMARY: 'entry_summary',
};

// Tab constants
const TABS = {
  ALL: 'all',
  BY_TYPE: 'by_type',
  GROUPS: 'groups',
  REQUIREMENTS: 'requirements',
};

const DocumentManagement = () => {
  const [documents, setDocuments] = useState([]);
  const [documentGroups, setDocumentGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(TABS.ALL);
  const [showSmartUpload, setShowSmartUpload] = useState(false);
  const [potentialApplications, setPotentialApplications] = useState([]);
  
  // Fetch documents on component mount
  useEffect(() => {
    fetchDocuments();
    fetchDocumentGroups();
  }, []);
  
  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:5000/api/documents');
      setDocuments(response.data.documents || []);
      detectPotentialApplications(response.data.documents || []);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching documents:', err);
      setError('Failed to load documents. Please try again.');
      setLoading(false);
    }
  };
  
  const fetchDocumentGroups = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/document-groups');
      setDocumentGroups(response.data.groups || []);
    } catch (err) {
      console.error('Error fetching document groups:', err);
      // Don't set error state here to avoid blocking the UI
    }
  };
  
  const handleDocumentUploaded = (data) => {
    // Refresh the document list after upload
    fetchDocuments();
    setShowSmartUpload(false);
    setActiveTab(TABS.ALL);
  };
  
  const handleDeleteDocument = async (documentId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      await axios.delete(`http://localhost:5000/api/documents/${documentId}`);
      // Remove the document from state
      const updatedDocs = documents.filter(doc => doc.id !== documentId);
      setDocuments(updatedDocs);
      // Check if this affects any potential applications
      detectPotentialApplications(updatedDocs);
    } catch (err) {
      console.error('Error deleting document:', err);
      setError('Failed to delete document. Please try again.');
    }
  };
  
  const handleCreateGroup = async (name, documentIds) => {
    try {
      const response = await axios.post('http://localhost:5000/api/document-groups', {
        name,
        document_ids: documentIds
      });
      
      // Add the new group to state
      setDocumentGroups([...documentGroups, response.data]);
      
      // Refresh document list to update group associations
      fetchDocuments();
    } catch (err) {
      console.error('Error creating document group:', err);
      setError('Failed to create document group. Please try again.');
    }
  };
  
  // Helper function for document type display name
  const getDocumentTypeDisplayName = (type) => {
    if (!type) return 'Unknown';
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  // Group documents by type for the by-type view
  const documentsByType = documents.reduce((acc, doc) => {
    if (!acc[doc.document_type]) {
      acc[doc.document_type] = [];
    }
    acc[doc.document_type].push(doc);
    return acc;
  }, {});
  
  // Function to detect if documents could form a drawback application
  const detectPotentialApplications = (docs) => {
    // Group documents by type
    const docsByType = docs.reduce((acc, doc) => {
      if (!acc[doc.document_type]) {
        acc[doc.document_type] = [];
      }
      acc[doc.document_type].push(doc);
      return acc;
    }, {});

    const applications = [];

    // Check for import + export combinations
    if (docsByType[DOCUMENT_TYPES.IMPORT] && docsByType[DOCUMENT_TYPES.EXPORT]) {
      docsByType[DOCUMENT_TYPES.IMPORT].forEach(importDoc => {
        docsByType[DOCUMENT_TYPES.EXPORT].forEach(exportDoc => {
          // Simple example - in a real app, you'd check dates, identifiers, etc.
          applications.push({
            name: `Potential Application: ${importDoc.original_filename || importDoc.filename} + ${exportDoc.original_filename || exportDoc.filename}`,
            documents: [importDoc, exportDoc],
            type: 'basic'
          });
        });
      });
    }

    // Check for complete applications (import + export + duty proof + export proof)
    if (docsByType[DOCUMENT_TYPES.IMPORT] && 
        docsByType[DOCUMENT_TYPES.EXPORT] && 
        docsByType[DOCUMENT_TYPES.DUTY_PROOF] && 
        docsByType[DOCUMENT_TYPES.EXPORT_PROOF]) {
      
      // In a real app, you'd do more sophisticated matching based on dates, reference numbers, etc.
      applications.push({
        name: 'Complete Drawback Application',
        documents: [
          docsByType[DOCUMENT_TYPES.IMPORT][0],
          docsByType[DOCUMENT_TYPES.EXPORT][0],
          docsByType[DOCUMENT_TYPES.DUTY_PROOF][0],
          docsByType[DOCUMENT_TYPES.EXPORT_PROOF][0]
        ],
        type: 'complete'
      });
    }

    setPotentialApplications(applications);
  };
  
  // Create a document group from a potential application
  const createGroupFromPotentialApplication = async (application) => {
    const documentIds = application.documents.map(doc => doc.id);
    const groupName = application.name;
    await handleCreateGroup(groupName, documentIds);
    
    // Switch to groups tab after creation
    setActiveTab(TABS.GROUPS);
  };
  
  // Generate a drawback application from a document group
  const generateDrawbackApplication = (groupId) => {
    // Navigate to the wizard with the group ID
    window.location.href = `/wizard/document-group/${groupId}`;
  };
  
  // Render documents list
  const renderDocumentsList = () => {
    if (documents.length === 0) {
      return (
        <div className="no-documents">
          <p>No documents have been uploaded yet.</p>
          <button 
            className="primary-button" 
            onClick={() => setShowSmartUpload(true)}
          >
            Upload Your First Document
          </button>
        </div>
      );
    }

    return (
      <div className="documents-list">
        <h2>All Documents</h2>
        <table className="documents-table">
          <thead>
            <tr>
              <th>Filename</th>
              <th>Document Type</th>
              <th>Uploaded</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {documents.map(doc => (
              <tr key={doc.id}>
                <td>{doc.original_filename || doc.filename}</td>
                <td>{getDocumentTypeDisplayName(doc.document_type)}</td>
                <td>{new Date(doc.uploaded_at).toLocaleString()}</td>
                <td>
                  <button 
                    className="action-button view"
                    onClick={() => window.open(`http://localhost:5000/api/documents/${doc.id}/view`, '_blank')}
                  >
                    View
                  </button>
                  <button 
                    className="action-button delete"
                    onClick={() => handleDeleteDocument(doc.id)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {/* Potential Applications Section */}
        {potentialApplications.length > 0 && (
          <div className="potential-applications">
            <h2>Potential Applications</h2>
            {potentialApplications.map((app, index) => (
              <div className="potential-application" key={index}>
                <h4>{app.name}</h4>
                <ul>
                  {app.documents.map(doc => (
                    <li key={doc.id}>{doc.original_filename || doc.filename} ({getDocumentTypeDisplayName(doc.document_type)})</li>
                  ))}
                </ul>
                <button 
                  className="action-button create-group"
                  onClick={() => createGroupFromPotentialApplication(app)}
                >
                  Create Document Group
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };
  
  // Render documents by type
  const renderDocumentsByType = () => {
    if (Object.keys(documentsByType).length === 0) {
      return (
        <div className="no-documents">
          <p>No documents have been uploaded yet.</p>
          <button 
            className="primary-button" 
            onClick={() => setShowSmartUpload(true)}
          >
            Upload Your First Document
          </button>
        </div>
      );
    }

    return (
      <div className="documents-by-type">
        <h2>Documents by Type</h2>
        
        {Object.entries(documentsByType).map(([type, docs]) => (
          <div className="document-type-group" key={type}>
            <h3>{getDocumentTypeDisplayName(type)}</h3>
            <div className="document-cards">
              {docs.map(doc => (
                <div className="document-card" key={doc.id}>
                  <div className="document-card-header">
                    <span className="document-type">{getDocumentTypeDisplayName(type)}</span>
                    <span className="document-filename">{doc.original_filename || doc.filename}</span>
                    <span className="document-date">
                      {new Date(doc.uploaded_at).toLocaleString()}
                    </span>
                  </div>
                  <div className="document-card-actions">
                    <button 
                      className="action-button view"
                      onClick={() => window.open(`http://localhost:5000/api/documents/${doc.id}/view`, '_blank')}
                    >
                      View
                    </button>
                    <button 
                      className="action-button delete"
                      onClick={() => handleDeleteDocument(doc.id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  };
  
  // Render document groups
  const renderDocumentGroups = () => {
    if (documentGroups.length === 0) {
      return (
        <div className="no-groups">
          <p>No document groups have been created yet.</p>
          <p>Groups help you organize related documents for an application.</p>
          {potentialApplications.length > 0 && (
            <div>
              <h3>Suggested Groups Based on Your Documents:</h3>
              {potentialApplications.map((app, index) => (
                <div className="potential-application" key={index}>
                  <h4>{app.name}</h4>
                  <ul>
                    {app.documents.map(doc => (
                      <li key={doc.id}>{doc.original_filename || doc.filename} ({getDocumentTypeDisplayName(doc.document_type)})</li>
                    ))}
                  </ul>
                  <button 
                    className="action-button create-group"
                    onClick={() => createGroupFromPotentialApplication(app)}
                  >
                    Create This Group
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      );
    }

    return (
      <div className="documents-by-group">
        <h2>Document Groups</h2>
        
        {documentGroups.map(group => {
          const groupDocuments = group.documents || [];
          return (
            <div className="document-group" key={group.id}>
              <h3>{group.name}</h3>
              
              <table className="documents-table">
                <thead>
                  <tr>
                    <th>Filename</th>
                    <th>Document Type</th>
                    <th>Uploaded</th>
                  </tr>
                </thead>
                <tbody>
                  {groupDocuments.map(doc => (
                    <tr key={doc.id}>
                      <td>{doc.original_filename || doc.filename}</td>
                      <td>{getDocumentTypeDisplayName(doc.document_type)}</td>
                      <td>{new Date(doc.uploaded_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              <div className="group-actions">
                <button 
                  className="action-button generate"
                  onClick={() => generateDrawbackApplication(group.id)}
                >
                  Generate Drawback Application
                </button>
              </div>
            </div>
          );
        })}
      </div>
    );
  };
  
  // Render document requirements tab
  const renderDocumentRequirements = () => {
    return (
      <div className="document-requirements-tab">
        <h2>Document Requirements</h2>
        <DocumentRequirements 
          onDocumentUploaded={handleDocumentUploaded}
          showDirectActionButtons={true}
        />
      </div>
    );
  };
  
  // Render active tab content
  const renderTabContent = () => {
    if (loading) {
      return <div className="loading-indicator">Loading documents...</div>;
    }

    switch (activeTab) {
      case TABS.ALL:
        return renderDocumentsList();
      case TABS.BY_TYPE:
        return renderDocumentsByType();
      case TABS.GROUPS:
        return renderDocumentGroups();
      case TABS.REQUIREMENTS:
        return renderDocumentRequirements();
      default:
        return renderDocumentsList();
    }
  };
  
  // Render Smart Upload Container
  const renderSmartUpload = () => {
    if (!showSmartUpload) return null;

    return (
      <div className="smart-upload-container">
        <h2>Smart Document Upload</h2>
        <p>Our system will automatically detect the type of document you are uploading based on its content.</p>
        <DocumentUpload 
          onDocumentUploaded={handleDocumentUploaded}
          useSmartDetection={true}
          onCancel={() => setShowSmartUpload(false)}
        />
      </div>
    );
  };
  
  // Render error message if there is one
  const renderError = () => {
    if (!error) return null;

    return (
      <div className="error-message">
        <p>{error}</p>
        <button 
          className="dismiss-button"
          onClick={() => setError(null)}
        >
          Dismiss
        </button>
      </div>
    );
  };
  
  // Main render method
  return (
    <div className="document-management">
      <h1>Document Library</h1>
      
      {/* Tab Navigation */}
      <div className="document-management-tabs">
        <button 
          className={`tab-button ${activeTab === TABS.ALL ? 'active' : ''}`}
          onClick={() => setActiveTab(TABS.ALL)}
        >
          All Documents
        </button>
        <button 
          className={`tab-button ${activeTab === TABS.BY_TYPE ? 'active' : ''}`}
          onClick={() => setActiveTab(TABS.BY_TYPE)}
        >
          By Type
        </button>
        <button 
          className={`tab-button ${activeTab === TABS.GROUPS ? 'active' : ''}`}
          onClick={() => setActiveTab(TABS.GROUPS)}
        >
          Document Groups
        </button>
        <button 
          className={`tab-button ${activeTab === TABS.REQUIREMENTS ? 'active' : ''}`}
          onClick={() => setActiveTab(TABS.REQUIREMENTS)}
        >
          Requirements
        </button>
      </div>
      
      {/* Action Buttons */}
      <div className="document-management-actions">
        <button 
          className="primary-button"
          onClick={() => setShowSmartUpload(true)}
        >
          Smart Upload
        </button>
      </div>
      
      {/* Smart Upload */}
      {renderSmartUpload()}
      
      {/* Error Message */}
      {renderError()}
      
      {/* Tab Content */}
      <div className="document-management-content">
        {renderTabContent()}
      </div>
    </div>
  );
};

export default DocumentManagement; 