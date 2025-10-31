import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import InfoIcon from '@material-ui/icons/Info';
import { ClaimFacilityInfoLink } from '../../../util/constants';
import { claimInfoStyles } from './styles';
import ExampleImage from './ExampleImage';

import businessRegistrationExample from '../../../images/business-registration-example.jpg';
import businessLicenseExample from '../../../images/business-license-example.jpg';
import utilityBillExample from '../../../images/utility-bill-example.jpg';
import employeeIdExample from '../../../images/employee-id-example.jpg';
import employmentLetterExample from '../../../images/employment-letter-example.jpg';
import businessCardExample from '../../../images/business-card-example.jpg';

const ClaimInfoSection = ({ classes, children }) => (
    <div className={classes.root}>
        <div className={classes.boxContainer}>
            <Typography component="h2" className={classes.boxHeader}>
                <span className={classes.stepNumber}>1</span>
                Confirm Your Eligibility
            </Typography>
            <Typography variant="body2" className={classes.boxDescription}>
                Confirm that you are eligible to claim this production location,
                keeping in mind:
            </Typography>
            <ul className={classes.boxList}>
                <li>
                    <Typography variant="body2" className={classes.boxText}>
                        Claim requests must be submitted by a current employee
                        of the location or its parent company.
                    </Typography>
                </li>
                <li>
                    <Typography variant="body2" className={classes.boxText}>
                        If you&apos;re not an owner or manager, you can still
                        proceed by providing your supervisor&apos;s contact
                        information for verification.
                    </Typography>
                </li>
            </ul>
        </div>
        <hr className={classes.separator} />
        <div className={classes.boxContainer}>
            <Typography component="h2" className={classes.boxHeader}>
                <span className={classes.stepNumber}>2</span> Prove Your Name
                and Role
            </Typography>
            <Typography variant="body2" className={classes.boxDescription}>
                Provide the document about your name and role,{' '}
                <strong>OPTIONS:</strong>
            </Typography>
            <ul className={classes.boxList}>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Company website showing your name and role
                    </Typography>
                </li>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Employee ID badge
                    </Typography>
                </li>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Employment letter
                    </Typography>
                </li>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Job contract
                    </Typography>
                </li>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Link to your LinkedIn profile
                    </Typography>
                </li>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Business card
                    </Typography>
                </li>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Audit reports
                    </Typography>
                </li>
            </ul>
            <div className={classes.boxExamplesContainer}>
                <ExampleImage
                    src={employeeIdExample}
                    alt="Example employee ID badge"
                    label="Employee ID Badge"
                />
                <ExampleImage
                    src={employmentLetterExample}
                    alt="Example employment letter"
                    label="Employment Letter"
                />
                <ExampleImage
                    src={businessCardExample}
                    alt="Example business card"
                    label="Business Card"
                />
            </div>
        </div>
        <hr className={classes.separator} />
        <div className={classes.boxContainer}>
            <Typography component="h2" className={classes.boxHeader}>
                <span className={classes.stepNumber}>3</span> Prove Your Company
                Name and Address
            </Typography>
            <Typography variant="body2" className={classes.boxDescription}>
                Provide the document about your company name and address,{' '}
                <strong>OPTIONS:</strong>
            </Typography>
            <ul className={classes.boxList}>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Business registration
                    </Typography>
                </li>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Business license
                    </Typography>
                </li>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Utility bill
                    </Typography>
                </li>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Link to company website
                    </Typography>
                </li>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Link to company LinkedIn page
                    </Typography>
                </li>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        <strong>NOTE:</strong> The document must show the same
                        company name and address as listed on your OS Hub
                        profile.
                    </Typography>
                </li>
            </ul>
            <div className={classes.boxExamplesContainer}>
                <ExampleImage
                    src={businessRegistrationExample}
                    alt="Example business registration certificate"
                    label="Business Registration"
                />
                <ExampleImage
                    src={businessLicenseExample}
                    alt="Example business license"
                    label="Business License"
                />
                <ExampleImage
                    src={utilityBillExample}
                    alt="Example utility bill"
                    label="Utility Bill"
                />
            </div>
        </div>
        <hr className={classes.separator} />
        <div className={classes.boxContainer}>
            <Typography component="h2" className={classes.boxHeader}>
                <span className={classes.stepNumber}>4</span> Add Key Details
            </Typography>
            <Typography variant="body2" className={classes.boxDescription}>
                Provide information about the production location, such as:
            </Typography>
            <ul className={classes.boxList}>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Certifications
                    </Typography>
                </li>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Number of Workers
                    </Typography>
                </li>
                <li>
                    <Typography
                        variant="body2"
                        className={classes.boxDescription}
                    >
                        Contact Information and more.
                    </Typography>
                </li>
            </ul>
        </div>
        <hr className={classes.separator} />
        <div className={classes.boxContainer}>
            <Typography component="h2" className={classes.boxHeader}>
                <span className={classes.stepNumber}>5</span> Get a Credible and
                Confirmed Profile
            </Typography>
            <Typography variant="body2" className={classes.boxDescription}>
                After the claim is approved, you get a credible and confirmed
                profile—with a green banner and Claimed badge—that helps buyers
                trust and find your company.{' '}
                <a
                    href={ClaimFacilityInfoLink}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={classes.link}
                >
                    Learn more about claiming your production location
                </a>
            </Typography>
        </div>
        <div
            className={`${classes.boxContainer} ${classes.boxWarningContainer}`}
        >
            <Typography variant="body2" className={classes.boxWarningText}>
                <InfoIcon className={classes.warningIcon} />
                <strong>IMPORTANT!</strong>&nbsp;Any documentation appearing to
                be forged or counterfeit may result in your claim request being
                denied.
            </Typography>
        </div>
        <div>{children}</div>
    </div>
);

ClaimInfoSection.propTypes = {
    classes: PropTypes.object.isRequired,
    children: PropTypes.node.isRequired,
};

export default withStyles(claimInfoStyles)(ClaimInfoSection);
