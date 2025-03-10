import React, { useState } from 'react';
import { Box, Button, Typography, Paper, List, ListItem, 
         ListItemIcon, ListItemText, CircularProgress, Divider,
         Chip, Grid } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import DeleteIcon from '@mui/icons-material/Delete';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

function FileUpload({ onFilesProcessed }) {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [documentTypes, setDocumentTypes] = useState({});

  const onDrop = (acceptedFiles) => {
    const newFiles = acceptedFiles.map(file => Object.assign(file, {
      preview: URL.createObjectURL(file)
    }));
    setFiles(prevFiles => [...prevFiles, ...newFiles]);
    
    // Auto-detect document types based on filenames
    const updatedDocTypes = {...documentTypes};
    
    acceptedFiles.forEach(file => {
      const fileName = file.name.toLowerCase();
      if (fileName.includes('import') || fileName.includes('entry') || fileName.includes('7501')) {
        updatedDocTypes[file.name] = 'Import Entry';
      } else if (fileName.includes('export') || fileName.includes('declaration')) {
        updatedDocTypes[file.name] = 'Export Document';
      } else if (fileName.includes('invoice')) {
        updatedDocTypes[file.name] = 'Commercial Invoice';
      } else if (fileName.includes('bill') || fileName.includes('lading')) {
        updatedDocTypes[file.name] = 'Bill of Lading';
      } else {
        updatedDocTypes[file.name] = 'Unknown';
      }
    });
    
    setDocumentTypes(updatedDocTypes);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png']
    }
  });

  const removeFile = (fileToRemove) => {
    setFiles(files.filter(file => file !== fileToRemove));
    const updatedDocTypes = {...documentTypes};
    delete updatedDocTypes[fileToRemove.name];
    setDocumentTypes(updatedDocTypes);
  };

  const updateDocumentType = (fileName, newType) => {
    setDocumentTypes({
      ...documentTypes,
      [fileName]: newType
    });
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    
    setUploading(true);
    setUploadStatus('uploading');
    
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
      formData.append('documentTypes', JSON.stringify(documentTypes));
    });

    try {
      const response = await axios.post('/api/process-documents', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setUploadStatus('success');
      onFilesProcessed(response.data);
    } catch (error) {
      console.error('Error uploading files:', error);
      setUploadStatus('error');
    } finally {
      setUploading(false);
    }
  };

  const generateTestDocuments = async () => {
    setUploading(true);
    setUploadStatus('generating');
    
    try {
      const response = await axios.post('/api/generate-test-documents', {
        companyName: localStorage.getItem('companyName') || 'Test Company Inc.',
        numEntries: 3 // Generate 3 import entries with matching exports
      });
      
      if (response.data.success) {
        setUploadStatus('success');
        onFilesProcessed(response.data.documentData);
      } else {
        throw new Error('Failed to generate test documents');
      }
    } catch (error) {
      console.error('Error generating test documents:', error);
      setUploadStatus('error');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h5" gutterBottom>
        Upload Documents
      </Typography>
      <Typography variant="body1" sx={{ mb: 2 }}>
        Upload your import and export documents to begin the drawback claim process.
      </Typography>
      
      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={12} md={6}>
          <Button
            variant="contained"
            color="secondary"
            startIcon={<CloudUploadIcon />}
            onClick={generateTestDocuments}
            disabled={uploading}
            fullWidth
          >
            Generate Test Documents
          </Button>
        </Grid>
        <Grid item xs={12} md={6}>
          <Typography variant="body2" color="textSecondary">
            Generate realistic test documents for demonstration purposes
          </Typography>
        </Grid>
      </Grid>
      
      <Divider sx={{ my: 2 }} />
      
      <Box
        {...getRootProps()}
        sx={{
          border: '2px dashed #cccccc',
          borderRadius: 2,
          p: 3,
          mb: 2,
          textAlign: 'center',
          cursor: 'pointer',
          backgroundColor: isDragActive ? '#f0f8ff' : 'transparent'
        }}
      >
        <input {...getInputProps()} />
        <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
        <Typography>
          {isDragActive
            ? "Drop the files here..."
            : "Drag & drop files here, or click to select files"}
        </Typography>
        <Typography variant="caption" color="textSecondary">
          Supported formats: PDF, Excel, Images
        </Typography>
      </Box>

      {files.length > 0 && (
        <>
          <Typography variant="subtitle1" gutterBottom>
            Selected Documents ({files.length})
          </Typography>
          <List>
            {files.map((file) => (
              <ListItem
                key={file.name}
                secondaryAction={
                  <Button 
                    onClick={() => removeFile(file)}
                    startIcon={<DeleteIcon />}
                    size="small"
                  >
                    Remove
                  </Button>
                }
              >
                <ListItemIcon>
                  <InsertDriveFileIcon />
                </ListItemIcon>
                <ListItemText 
                  primary={file.name}
                  secondary={`${(file.size / 1024).toFixed(1)} KB`} 
                />
                <Chip 
                  label={documentTypes[file.name] || 'Unclassified'} 
                  size="small" 
                  color={documentTypes[file.name] ? "primary" : "default"}
                  sx={{ mr: 2 }}
                />
              </ListItem>
            ))}
          </List>

          <Button
            variant="contained"
            color="primary"
            startIcon={uploading ? <CircularProgress size={20} color="inherit" /> : <CloudUploadIcon />}
            onClick={handleUpload}
            disabled={uploading}
            sx={{ mt: 2 }}
            fullWidth
          >
            {uploading ? 'Processing...' : 'Process Documents'}
          </Button>
          
          {uploadStatus && (
            <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
              {uploadStatus === 'success' ? (
                <CheckCircleIcon color="success" sx={{ mr: 1 }} />
              ) : uploadStatus === 'error' ? (
                <ErrorIcon color="error" sx={{ mr: 1 }} />
              ) : (
                <CircularProgress size={20} sx={{ mr: 1 }} />
              )}
              <Typography color={uploadStatus === 'success' ? 'success.main' : 
                          uploadStatus === 'error' ? 'error.main' : 'textPrimary'}>
                {uploadStatus === 'uploading' && 'Uploading and processing documents...'}
                {uploadStatus === 'generating' && 'Generating test documents...'}
                {uploadStatus === 'success' && 'Documents processed successfully!'}
                {uploadStatus === 'error' && 'Error processing documents. Please try again.'}
              </Typography>
            </Box>
          )}
        </>
      )}
    </Paper>
  );
}

export default FileUpload; 