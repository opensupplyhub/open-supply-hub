import React, { useState } from 'react';
import { withStyles } from '@material-ui/core/styles';
import Dialog from '@material-ui/core/Dialog';
import DialogContent from '@material-ui/core/DialogContent';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import InfoIcon from '@material-ui/icons/Info';
import StarIcon from '@material-ui/icons/Star';

import businessRegistrationExample from '../../images/business-registration-example.jpg';
import businessLicenseExample from '../../images/business-license-example.jpg';
import utilityBillExample from '../../images/utility-bill-example.jpg';
import employeeIdExample from '../../images/employee-id-example.jpg';
import employmentLetterExample from '../../images/employment-letter-example.jpg';
import businessCardExample from '../../images/business-card-example.jpg';

const claimInfoStyles = theme => ({
    root: {
        backgroundColor: '#fff',
        border: '1px solid #e0e0e0',
        borderRadius: theme.spacing.unit,
        padding: theme.spacing.unit * 3,
        '& > *:not(:last-child)': {
            marginBottom: theme.spacing.unit * 3,
        },
    },
    stepBox: {
        borderRadius: theme.spacing.unit,
        padding: theme.spacing.unit * 2,
        marginBottom: 0,
        display: 'flex',
        flexDirection: 'column',
    },
    blueStep: {
        backgroundColor: '#e3f2fd',
        border: '1px solid #90caf9',
    },
    purpleStep: {
        backgroundColor: '#f3e5f5',
        border: '1px solid #ce93d8',
    },
    greenStep: {
        backgroundColor: '#e8f5e9',
        border: '1px solid #81c784',
    },
    amberStep: {
        background: 'linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%)',
        border: '4px solid #ffc107',
        boxShadow: '0 4px 12px rgba(255, 193, 7, 0.3)',
    },
    stepNumber: {
        width: 32,
        height: 32,
        borderRadius: '50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#fff',
        fontWeight: 600,
        fontSize: 18,
        marginRight: theme.spacing.unit * 1.5,
        flexShrink: 0,
    },
    blueNumber: {
        backgroundColor: '#1976d2',
    },
    purpleNumber: {
        backgroundColor: '#7b1fa2',
    },
    greenNumber: {
        backgroundColor: '#388e3c',
    },
    amberNumber: {
        background: 'linear-gradient(135deg, #f57c00 0%, #fbc02d 100%)',
        boxShadow: '0 2px 8px rgba(245, 124, 0, 0.4)',
    },
    stepHeader: {
        display: 'flex',
        alignItems: 'flex-start',
        marginBottom: theme.spacing.unit * 1.5,
    },
    stepTitle: {
        fontSize: 24,
        fontWeight: 600,
        marginBottom: theme.spacing.unit * 0.5,
    },
    stepText: {
        fontSize: 18,
        lineHeight: 1.6,
    },
    bulletPoint: {
        display: 'flex',
        alignItems: 'center',
        marginBottom: theme.spacing.unit,
    },
    bullet: {
        width: 6,
        height: 6,
        borderRadius: '50%',
        marginRight: theme.spacing.unit,
        flexShrink: 0,
    },
    blueBullet: {
        backgroundColor: '#1976d2',
    },
    examplesContainer: {
        display: 'flex',
        gap: theme.spacing.unit * 3,
        marginTop: 'auto',
        paddingTop: theme.spacing.unit * 2,
        justifyContent: 'flex-start',
        alignItems: 'flex-start',
        flexWrap: 'wrap',
    },
    exampleItem: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        width: 80,
        justifyContent: 'flex-start',
    },
    exampleImage: {
        width: 64,
        height: 64,
        objectFit: 'cover',
        borderRadius: theme.spacing.unit,
        cursor: 'pointer',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        transition: 'all 0.2s',
        '&:hover': {
            boxShadow: '0 4px 8px rgba(0,0,0,0.15)',
            transform: 'translateY(-2px)',
        },
    },
    purpleBorder: {
        border: '2px solid #ce93d8',
    },
    greenBorder: {
        border: '2px solid #81c784',
    },
    exampleLabel: {
        fontSize: 14,
        textAlign: 'center',
        marginTop: theme.spacing.unit,
        fontWeight: 700,
        lineHeight: 1.2,
    },
    purpleLabel: {
        color: '#6a1b9a',
    },
    greenLabel: {
        color: '#2e7d32',
    },
    noteBox: {
        backgroundColor: '#c8e6c9',
        padding: theme.spacing.unit * 1.5,
        borderRadius: theme.spacing.unit,
        marginTop: theme.spacing.unit,
    },
    maxValueBadge: {
        display: 'inline-flex',
        alignItems: 'center',
        backgroundColor: '#ffa000',
        color: '#fff',
        padding: '6px 12px',
        borderRadius: 20,
        fontSize: 18,
        fontWeight: 700,
        marginBottom: theme.spacing.unit * 1.5,
        boxShadow: '0 2px 6px rgba(255, 160, 0, 0.4)',
    },
    warningBox: {
        backgroundColor: '#fce4ec',
        padding: theme.spacing.unit * 1.5,
        borderRadius: theme.spacing.unit,
        display: 'flex',
        alignItems: 'center',
    },
    warningIcon: {
        color: '#d32f2f',
        marginRight: theme.spacing.unit,
        fontSize: 16,
        flexShrink: 0,
    },
    link: {
        color: '#1976d2',
        textDecoration: 'none',
        fontWeight: 500,
        '&:hover': {
            textDecoration: 'underline',
        },
    },
    dialogImage: {
        width: '100%',
        height: 'auto',
        maxHeight: '80vh',
        objectFit: 'contain',
    },
    closeButton: {
        position: 'absolute',
        right: theme.spacing.unit,
        top: theme.spacing.unit,
        color: theme.palette.grey[500],
    },
    twoColumnGrid: {
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        columnGap: theme.spacing.unit * 3,
        rowGap: theme.spacing.unit * 2,
        [theme.breakpoints.down('sm')]: {
            gridTemplateColumns: '1fr',
        },
    },
});

const ImageDialog = ({ open, onClose, image, alt, classes }) => (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
        <IconButton className={classes.closeButton} onClick={onClose}>
            <CloseIcon />
        </IconButton>
        <DialogContent>
            <img src={image} alt={alt} className={classes.dialogImage} />
        </DialogContent>
    </Dialog>
);

const ExampleImage = ({
    src,
    alt,
    label,
    borderClass,
    labelColorClass,
    classes,
}) => {
    const [dialogOpen, setDialogOpen] = useState(false);

    return (
        <div className={classes.exampleItem}>
            <button
                type="button"
                onClick={() => setDialogOpen(true)}
                style={{
                    border: 'none',
                    background: 'none',
                    padding: 0,
                    cursor: 'pointer',
                }}
                aria-label={`View example: ${alt}`}
            >
                <img
                    src={src}
                    alt={alt}
                    className={`${classes.exampleImage} ${classes[borderClass]}`}
                />
            </button>
            <Typography
                className={`${classes.exampleLabel} ${classes[labelColorClass]}`}
                color="textSecondary"
            >
                {label}
            </Typography>
            <ImageDialog
                open={dialogOpen}
                onClose={() => setDialogOpen(false)}
                image={src}
                alt={alt}
                classes={classes}
            />
        </div>
    );
};

const ClaimInfoSection = ({ classes }) => (
    <div className={classes.root}>
        {/* Step 1: Eligibility */}
        <div className={`${classes.stepBox} ${classes.blueStep}`}>
            <div className={classes.stepHeader}>
                <div className={`${classes.stepNumber} ${classes.blueNumber}`}>
                    1
                </div>
                <div>
                    <Typography
                        variant="title"
                        className={classes.stepTitle}
                        style={{ color: '#0d47a1' }}
                    >
                        Confirm Your Eligibility
                    </Typography>
                    <div>
                        <div className={classes.bulletPoint}>
                            <span
                                className={`${classes.bullet} ${classes.blueBullet}`}
                            />
                            <Typography
                                variant="body2"
                                className={classes.stepText}
                                style={{ color: '#1565c0' }}
                            >
                                Claim requests must be submitted by a current
                                employee of the location or its parent company.
                            </Typography>
                        </div>
                        <div className={classes.bulletPoint}>
                            <span
                                className={`${classes.bullet} ${classes.blueBullet}`}
                            />
                            <Typography
                                variant="body2"
                                className={classes.stepText}
                                style={{ color: '#1565c0' }}
                            >
                                If you&apos;re not an owner or manager, you can
                                still proceed by providing your
                                supervisor&apos;s contact information for
                                verification.
                            </Typography>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        {/* Steps 2 & 3: Documents Grid */}
        <div className={classes.twoColumnGrid}>
            {/* Step 2: Prove Your Name and Role */}
            <div className={`${classes.stepBox} ${classes.purpleStep}`}>
                <div className={classes.stepHeader}>
                    <div
                        className={`${classes.stepNumber} ${classes.purpleNumber}`}
                    >
                        2
                    </div>
                    <Typography
                        variant="title"
                        className={classes.stepTitle}
                        style={{ color: '#4a148c' }}
                    >
                        Prove Your Name and Role
                    </Typography>
                </div>
                <Typography
                    variant="body2"
                    className={classes.stepText}
                    style={{ color: '#6a1b9a', marginBottom: 16 }}
                >
                    <strong>OPTIONS:</strong> Company website showing your name
                    and role, Employee ID badge, Employment letter, Job
                    contract, Link to your LinkedIn profile, Business card,
                    Audit reports.
                </Typography>
                <div className={classes.examplesContainer}>
                    <ExampleImage
                        src={employeeIdExample}
                        alt="Example employee ID badge"
                        label="Employee ID Badge"
                        borderClass="purpleBorder"
                        labelColorClass="purpleLabel"
                        classes={classes}
                    />
                    <ExampleImage
                        src={employmentLetterExample}
                        alt="Example employment letter"
                        label="Employment Letter"
                        borderClass="purpleBorder"
                        labelColorClass="purpleLabel"
                        classes={classes}
                    />
                    <ExampleImage
                        src={businessCardExample}
                        alt="Example business card"
                        label="Business Card"
                        borderClass="purpleBorder"
                        labelColorClass="purpleLabel"
                        classes={classes}
                    />
                </div>
            </div>

            {/* Step 3: Prove Your Company Name and Address */}
            <div className={`${classes.stepBox} ${classes.greenStep}`}>
                <div className={classes.stepHeader}>
                    <div
                        className={`${classes.stepNumber} ${classes.greenNumber}`}
                    >
                        3
                    </div>
                    <Typography
                        variant="title"
                        className={classes.stepTitle}
                        style={{ color: '#1b5e20' }}
                    >
                        Prove Your Company Name and Address
                    </Typography>
                </div>
                <Typography
                    variant="body2"
                    className={classes.stepText}
                    style={{ color: '#2e7d32', marginBottom: 8 }}
                >
                    <strong>OPTIONS:</strong> Business registration, Business
                    license, Utility bill, link to company website, link to
                    company LinkedIn page.
                </Typography>
                <div className={classes.noteBox}>
                    <Typography
                        variant="body2"
                        className={classes.stepText}
                        style={{ color: '#2e7d32' }}
                    >
                        <strong>NOTE:</strong> The document must show the same
                        company name and address as listed on your OS Hub
                        profile.
                    </Typography>
                </div>
                <div className={classes.examplesContainer}>
                    <ExampleImage
                        src={businessRegistrationExample}
                        alt="Example business registration certificate"
                        label="Business Registration"
                        borderClass="greenBorder"
                        labelColorClass="greenLabel"
                        classes={classes}
                    />
                    <ExampleImage
                        src={businessLicenseExample}
                        alt="Example business license"
                        label="Business License"
                        borderClass="greenBorder"
                        labelColorClass="greenLabel"
                        classes={classes}
                    />
                    <ExampleImage
                        src={utilityBillExample}
                        alt="Example utility bill"
                        label="Utility Bill"
                        borderClass="greenBorder"
                        labelColorClass="greenLabel"
                        classes={classes}
                    />
                </div>
            </div>
        </div>

        {/* Steps 4 & 5: Maximum Value Benefits */}
        <div className={`${classes.stepBox} ${classes.amberStep}`}>
            <div style={{ textAlign: 'center' }}>
                <span className={classes.maxValueBadge}>
                    <StarIcon style={{ fontSize: 16, marginRight: 4 }} />
                    Maximum Value
                </span>
            </div>

            <div className={classes.stepHeader}>
                <div className={`${classes.stepNumber} ${classes.amberNumber}`}>
                    4
                </div>
                <Typography
                    variant="body2"
                    className={classes.stepText}
                    style={{ color: '#e65100' }}
                >
                    <strong style={{ fontSize: 20 }}>Add Key Details:</strong>{' '}
                    Provide information about the production location such as
                    Certifications, Number of Workers, Contact Information, and
                    more.
                </Typography>
            </div>

            <div className={classes.stepHeader}>
                <div className={`${classes.stepNumber} ${classes.amberNumber}`}>
                    5
                </div>
                <Typography
                    variant="body2"
                    className={classes.stepText}
                    style={{ color: '#e65100' }}
                >
                    <strong style={{ fontSize: 20 }}>Get Verified:</strong>{' '}
                    After the claim is approved, you get a credible and
                    confirmed profile—with a green banner and Claimed badge—that
                    helps buyers trust and find your company.{' '}
                    <a
                        href="https://info.opensupplyhub.org/resources/claim-a-facility"
                        target="_blank"
                        rel="noopener noreferrer"
                        className={classes.link}
                    >
                        Learn more about claiming your production location
                    </a>
                </Typography>
            </div>
        </div>

        {/* Warning Note */}
        <div className={classes.warningBox}>
            <InfoIcon className={classes.warningIcon} />
            <Typography variant="caption" style={{ fontSize: 16 }}>
                <strong style={{ color: '#d32f2f', fontSize: 16 }}>
                    IMPORTANT!
                </strong>{' '}
                Any documentation appearing to be forged or counterfeit may
                result in your claim request being denied.
            </Typography>
        </div>
    </div>
);

export default withStyles(claimInfoStyles)(ClaimInfoSection);
