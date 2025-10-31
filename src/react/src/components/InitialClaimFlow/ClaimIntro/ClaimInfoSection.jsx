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
                1. Confirm Your Eligibility
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
        <div className={classes.boxContainer}>
            <Typography component="h2" className={classes.boxHeader}>
                2. Prove Your Name and Role
            </Typography>
            <Typography variant="body2" className={classes.boxDescription}>
                <strong>OPTIONS:</strong> Company website showing your name and
                role, Employee ID badge, Employment letter, Job contract, Link
                to your LinkedIn profile, Business card, Audit reports.
            </Typography>
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

        <div className={classes.boxContainer}>
            <Typography component="h2" className={classes.boxHeader}>
                3. Prove Your Company Name and Address
            </Typography>
            <Typography variant="body2" className={classes.boxDescription}>
                <strong>OPTIONS:</strong> Business registration, Business
                license, Utility bill, link to company website, link to company
                LinkedIn page.
            </Typography>
            <Typography variant="body2" className={classes.boxDescription}>
                <strong>NOTE:</strong> The document must show the same company
                name and address as listed on your OS Hub profile.
            </Typography>
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
        <div className={classes.boxContainer}>
            <Typography component="h2" className={classes.boxHeader}>
                4. Add Key Details
            </Typography>
            <Typography variant="body2" className={classes.boxDescription}>
                Provide information about the production location such as
                Certifications, Number of Workers, Contact Information, and
                more.
            </Typography>
        </div>

        <div className={classes.boxContainer}>
            <Typography component="h2" className={classes.boxHeader}>
                5. Get a Credible and Confirmed Profile
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
