import PropTypes from 'prop-types';
import React from 'react';
import { Link } from 'react-router-dom';
import { useParams } from 'react-router-dom';

import ROUTES_COMPLIANCE from '../../app/routes/Compliance';

const ComplianceReportTabs = (props) => {
  const { active, reportStatuses } = props;
  const { id } = useParams();

  return (
    <ul
      className="nav nav-pills nav-justified compliance-report-tabs"
      key="tabs"
      role="tablist"
    >
      <li
        className={`nav-item ${(active === 'supplier-information') ? 'active' : ''} ${reportStatuses.supplierInformation}`}
        role="presentation"
      >
        <Link to={ROUTES_COMPLIANCE.REPORT_SUPPLIER_INFORMATION.replace(':id', id)}>Supplier Information</Link>
      </li>
      <li
        className={`nav-item ${(active === 'consumer-sales') ? 'active' : ''} ${reportStatuses.consumerSales}`}
        role="presentation"
      >
        <Link to={ROUTES_COMPLIANCE.REPORT_CONSUMER_SALES.replace(':id', id)}>Consumer Sales</Link>
      </li>
      <li
        className={`nav-item ${(active === 'credit-activity') ? 'active' : ''} ${reportStatuses.creditActivity}`}
        role="presentation"
      >
        <Link to={ROUTES_COMPLIANCE.REPORT_CREDIT_ACTIVITY}>Compliance Obligation</Link>
      </li>
      <li
        className={`nav-item ${(active === 'summary') ? 'active' : ''} ${reportStatuses.reportSummary}`}
        role="presentation"
      >
        <Link to={ROUTES_COMPLIANCE.REPORT_SUMMARY}>Summary</Link>
      </li>
      <li
        className={`nav-item ${(active === 'assessment') ? 'active' : ''} ${reportStatuses.assessment}`}
        role="presentation"
      >
        <Link to={ROUTES_COMPLIANCE.REPORT_ASSESSMENT}>Assessment</Link>
      </li>
    </ul>
  );
};

ComplianceReportTabs.defaultProps = {
  reportStatuses: {
    assessment: '',
    consumerSales: '',
    creditActivity: '',
    reportSummary: '',
    supplierInformation: '',
  },
};

ComplianceReportTabs.propTypes = {
  active: PropTypes.string.isRequired,
  reportStatuses: PropTypes.shape(),
};

export default ComplianceReportTabs;