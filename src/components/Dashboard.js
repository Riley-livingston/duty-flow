import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Badge, Button, Form, InputGroup, Dropdown, DropdownButton } from 'react-bootstrap';
import { FaSearch, FaFilter, FaFileDownload, FaSortAmountDown, FaSortAmountUp, FaChartBar } from 'react-icons/fa';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import './Dashboard.css';

// Register required Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend);

function Dashboard() {
  const [claims, setClaims] = useState([]);
  const [filteredClaims, setFilteredClaims] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [sortField, setSortField] = useState('date');
  const [sortDirection, setSortDirection] = useState('desc');
  const [summaryStats, setSummaryStats] = useState({
    totalClaims: 0,
    pendingClaims: 0,
    approvedClaims: 0,
    totalRefundAmount: 0
  });
  
  // Mock data loading - in a real app, this would come from an API
  useEffect(() => {
    // More comprehensive mock data with additional fields
    const mockClaims = [
      { id: '001', date: '2023-10-15', status: 'Submitted', amount: 1250.75, entryCount: 3, importDate: '2023-01-10', exportDate: '2023-07-05' },
      { id: '002', date: '2023-10-10', status: 'Processing', amount: 3420.50, entryCount: 5, importDate: '2023-02-15', exportDate: '2023-06-20' },
      { id: '003', date: '2023-09-28', status: 'Approved', amount: 2150.25, entryCount: 2, importDate: '2023-01-05', exportDate: '2023-05-12' },
      { id: '004', date: '2023-09-15', status: 'Rejected', amount: 950.00, entryCount: 1, importDate: '2023-03-20', exportDate: '2023-08-10' },
      { id: '005', date: '2023-08-30', status: 'Approved', amount: 4750.80, entryCount: 8, importDate: '2022-12-12', exportDate: '2023-04-18' },
      { id: '006', date: '2023-08-10', status: 'Submitted', amount: 1875.25, entryCount: 4, importDate: '2023-02-25', exportDate: '2023-07-30' },
    ];
    
    setClaims(mockClaims);
    setFilteredClaims(mockClaims);
    
    // Calculate summary statistics
    const totalClaims = mockClaims.length;
    const pendingClaims = mockClaims.filter(c => c.status === 'Submitted' || c.status === 'Processing').length;
    const approvedClaims = mockClaims.filter(c => c.status === 'Approved').length;
    const totalRefundAmount = mockClaims.reduce((sum, claim) => sum + claim.amount, 0);
    
    setSummaryStats({
      totalClaims,
      pendingClaims,
      approvedClaims,
      totalRefundAmount
    });
  }, []);
  
  // Filter and sort claims when dependencies change
  useEffect(() => {
    let result = [...claims];
    
    // Apply status filter
    if (statusFilter !== 'All') {
      result = result.filter(claim => claim.status === statusFilter);
    }
    
    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      result = result.filter(claim => 
        claim.id.toLowerCase().includes(term) || 
        claim.status.toLowerCase().includes(term)
      );
    }
    
    // Apply sorting
    result.sort((a, b) => {
      let compareA = a[sortField];
      let compareB = b[sortField];
      
      // Handle string vs number comparison
      if (sortField === 'amount') {
        compareA = parseFloat(compareA);
        compareB = parseFloat(compareB);
      }
      
      if (compareA < compareB) {
        return sortDirection === 'asc' ? -1 : 1;
      }
      if (compareA > compareB) {
        return sortDirection === 'asc' ? 1 : -1;
      }
      return 0;
    });
    
    setFilteredClaims(result);
  }, [claims, statusFilter, searchTerm, sortField, sortDirection]);
  
  // Status badge display
  const getStatusBadge = (status) => {
    switch(status) {
      case 'Submitted': return <Badge bg="info">Submitted</Badge>;
      case 'Processing': return <Badge bg="warning">Processing</Badge>;
      case 'Approved': return <Badge bg="success">Approved</Badge>;
      case 'Rejected': return <Badge bg="danger">Rejected</Badge>;
      default: return <Badge bg="secondary">Unknown</Badge>;
    }
  };
  
  // Handle sort toggle
  const handleSort = (field) => {
    if (sortField === field) {
      // Toggle direction if same field
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // Set new field and default to ascending
      setSortField(field);
      setSortDirection('asc');
    }
  };
  
  // Chart data for status distribution
  const chartData = {
    labels: ['Submitted', 'Processing', 'Approved', 'Rejected'],
    datasets: [
      {
        data: [
          claims.filter(claim => claim.status === 'Submitted').length,
          claims.filter(claim => claim.status === 'Processing').length,
          claims.filter(claim => claim.status === 'Approved').length,
          claims.filter(claim => claim.status === 'Rejected').length
        ],
        backgroundColor: [
          'rgba(54, 162, 235, 0.6)', // Blue for Submitted
          'rgba(255, 193, 7, 0.6)',  // Yellow for Processing
          'rgba(75, 192, 192, 0.6)',  // Green for Approved
          'rgba(255, 99, 132, 0.6)'   // Red for Rejected
        ],
        borderColor: [
          'rgba(54, 162, 235, 1)',
          'rgba(255, 193, 7, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(255, 99, 132, 1)'
        ],
        borderWidth: 1,
      }
    ]
  };
  
  return (
    <Container className="dashboard-container mt-4">
      <h2>Drawback Claims Dashboard</h2>
      <p>Track and manage your duty drawback claims in one place</p>
      
      {/* Summary Statistics Cards */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="text-center h-100 shadow-sm">
            <Card.Body>
              <Card.Title>Total Claims</Card.Title>
              <Card.Text className="display-4">{summaryStats.totalClaims}</Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center h-100 shadow-sm">
            <Card.Body>
              <Card.Title>Pending Claims</Card.Title>
              <Card.Text className="display-4">{summaryStats.pendingClaims}</Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center h-100 shadow-sm">
            <Card.Body>
              <Card.Title>Approved Claims</Card.Title>
              <Card.Text className="display-4">{summaryStats.approvedClaims}</Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center h-100 shadow-sm">
            <Card.Body>
              <Card.Title>Total Refund Amount</Card.Title>
              <Card.Text className="display-4">${summaryStats.totalRefundAmount.toFixed(2)}</Card.Text>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      {/* Visual Chart */}
      <Row className="mb-4">
        <Col md={5}>
          <Card className="shadow-sm">
            <Card.Body>
              <Card.Title>Claim Status Distribution</Card.Title>
              <div style={{ height: '250px', position: 'relative' }}>
                <Pie 
                  data={chartData} 
                  options={{ 
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'right',
                      }
                    }
                  }} 
                />
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={7}>
          <Card className="shadow-sm h-100">
            <Card.Body>
              <Card.Title>Quick Actions</Card.Title>
              <Row className="mt-3">
                <Col md={6} className="mb-3">
                  <Button variant="primary" className="w-100">
                    <FaFileDownload className="me-1" /> Export Claims Report
                  </Button>
                </Col>
                <Col md={6} className="mb-3">
                  <Button variant="success" className="w-100">
                    <FaChartBar className="me-1" /> Generate Analytics
                  </Button>
                </Col>
                <Col md={6} className="mb-3">
                  <Button variant="info" className="w-100">
                    New Drawback Claim
                  </Button>
                </Col>
                <Col md={6} className="mb-3">
                  <Button variant="outline-secondary" className="w-100">
                    View Documentation Guide
                  </Button>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      {/* Search and Filters */}
      <Row className="mb-3">
        <Col md={6}>
          <InputGroup>
            <InputGroup.Text><FaSearch /></InputGroup.Text>
            <Form.Control 
              placeholder="Search claims by ID or status..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </InputGroup>
        </Col>
        <Col md={3}>
          <InputGroup>
            <InputGroup.Text><FaFilter /></InputGroup.Text>
            <Form.Select 
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="All">All Statuses</option>
              <option value="Submitted">Submitted</option>
              <option value="Processing">Processing</option>
              <option value="Approved">Approved</option>
              <option value="Rejected">Rejected</option>
            </Form.Select>
          </InputGroup>
        </Col>
        <Col md={3} className="text-end">
          <Button variant="outline-secondary">
            <FaFileDownload className="me-1" /> Export Filtered Results
          </Button>
        </Col>
      </Row>
      
      {/* Claims Table */}
      <Card className="shadow-sm mb-4">
        <Card.Body>
          <Table hover responsive>
            <thead>
              <tr>
                <th onClick={() => handleSort('id')} style={{cursor: 'pointer'}}>
                  Claim ID {sortField === 'id' && (sortDirection === 'asc' ? <FaSortAmountUp size="0.8em" /> : <FaSortAmountDown size="0.8em" />)}
                </th>
                <th onClick={() => handleSort('date')} style={{cursor: 'pointer'}}>
                  Submission Date {sortField === 'date' && (sortDirection === 'asc' ? <FaSortAmountUp size="0.8em" /> : <FaSortAmountDown size="0.8em" />)}
                </th>
                <th onClick={() => handleSort('status')} style={{cursor: 'pointer'}}>
                  Status {sortField === 'status' && (sortDirection === 'asc' ? <FaSortAmountUp size="0.8em" /> : <FaSortAmountDown size="0.8em" />)}
                </th>
                <th onClick={() => handleSort('entryCount')} style={{cursor: 'pointer'}}>
                  Entries {sortField === 'entryCount' && (sortDirection === 'asc' ? <FaSortAmountUp size="0.8em" /> : <FaSortAmountDown size="0.8em" />)}
                </th>
                <th onClick={() => handleSort('amount')} style={{cursor: 'pointer'}}>
                  Refund Amount {sortField === 'amount' && (sortDirection === 'asc' ? <FaSortAmountUp size="0.8em" /> : <FaSortAmountDown size="0.8em" />)}
                </th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredClaims.length > 0 ? (
                filteredClaims.map(claim => (
                  <tr key={claim.id}>
                    <td>{claim.id}</td>
                    <td>{claim.date}</td>
                    <td>{getStatusBadge(claim.status)}</td>
                    <td>{claim.entryCount}</td>
                    <td>${claim.amount.toFixed(2)}</td>
                    <td>
                      <DropdownButton id={`dropdown-${claim.id}`} title="Actions" size="sm" variant="outline-secondary">
                        <Dropdown.Item>View Details</Dropdown.Item>
                        <Dropdown.Item>Download PDF</Dropdown.Item>
                        <Dropdown.Item>Track Status</Dropdown.Item>
                        <Dropdown.Divider />
                        <Dropdown.Item>Duplicate Claim</Dropdown.Item>
                      </DropdownButton>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="text-center py-3">No claims found matching your filters</td>
                </tr>
              )}
            </tbody>
          </Table>
        </Card.Body>
      </Card>
      
      {/* Additional Resources Section */}
      <Card className="shadow-sm mb-4">
        <Card.Header as="h5">Resources for Maximizing Your Refunds</Card.Header>
        <Card.Body>
          <Row>
            <Col md={4}>
              <Card className="h-100 border-0">
                <Card.Body>
                  <Card.Title className="h6">Documentation Guide</Card.Title>
                  <Card.Text>Learn what documentation is required for successful drawback claims.</Card.Text>
                  <Button variant="link" className="p-0">View Guide</Button>
                </Card.Body>
              </Card>
            </Col>
            <Col md={4}>
              <Card className="h-100 border-0">
                <Card.Body>
                  <Card.Title className="h6">Common Rejection Reasons</Card.Title>
                  <Card.Text>Understand why claims get rejected and how to avoid common pitfalls.</Card.Text>
                  <Button variant="link" className="p-0">Learn More</Button>
                </Card.Body>
              </Card>
            </Col>
            <Col md={4}>
              <Card className="h-100 border-0">
                <Card.Body>
                  <Card.Title className="h6">Refund Timeline</Card.Title>
                  <Card.Text>Get insights into typical processing times and payment schedules.</Card.Text>
                  <Button variant="link" className="p-0">View Timeline</Button>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Card.Body>
      </Card>
    </Container>
  );
}

export default Dashboard; 