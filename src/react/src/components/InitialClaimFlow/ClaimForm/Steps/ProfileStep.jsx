import React, { useState } from 'react';
import { func, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CardHeader from '@material-ui/core/CardHeader';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import ExpansionPanel from '@material-ui/core/ExpansionPanel';
import ExpansionPanelSummary from '@material-ui/core/ExpansionPanelSummary';
import ExpansionPanelDetails from '@material-ui/core/ExpansionPanelDetails';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import Business from '@material-ui/icons/Business';
import Nature from '@material-ui/icons/Nature';
import VerifiedUser from '@material-ui/icons/VerifiedUser';
import Tooltip from '@material-ui/core/Tooltip';
import HelpOutline from '@material-ui/icons/HelpOutline';
import IconButton from '@material-ui/core/IconButton';
import ReactSelect from 'react-select';

import COLOURS from '../../../../util/COLOURS';
import withScrollReset from '../../HOCs/withScrollReset';
import FreeEmissionsEstimate from '../../../FreeEmissionsEstimate/FreeEmissionsEstimate';

// TODO: Move these to constants file
const SECTOR_OPTIONS = [
    { value: 'apparel', label: 'Apparel' },
    { value: 'footwear', label: 'Footwear' },
    { value: 'accessories', label: 'Accessories' },
    { value: 'textiles', label: 'Textiles' },
];

const PROCESSING_TYPE_OPTIONS = [
    { value: 'cut_sew', label: 'Cut & Sew' },
    { value: 'dyeing', label: 'Dyeing' },
    { value: 'knitting', label: 'Knitting' },
    { value: 'weaving', label: 'Weaving' },
    { value: 'printing', label: 'Printing' },
    { value: 'embroidery', label: 'Embroidery' },
    { value: 'finishing', label: 'Finishing' },
    { value: 'assembly', label: 'Assembly' },
];

const AFFILIATIONS_OPTIONS = [
    { value: 'fla', label: 'Fair Labor Association (FLA)' },
    { value: 'wrap', label: 'WRAP' },
    { value: 'sedex', label: 'Sedex' },
    { value: 'bsci', label: 'BSCI' },
];

const CERTIFICATIONS_OPTIONS = [
    { value: 'iso_9001', label: 'ISO 9001' },
    { value: 'iso_14001', label: 'ISO 14001' },
    { value: 'sa8000', label: 'SA8000' },
    { value: 'oeko_tex', label: 'OEKO-TEX' },
    { value: 'gots', label: 'GOTS (Global Organic Textile Standard)' },
    { value: 'bluesign', label: 'bluesign' },
];

const profileStepStyles = theme =>
    Object.freeze({
        card: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            border: `1px solid ${COLOURS.GREY}`,
        }),
        cardHeader: Object.freeze({
            backgroundColor: COLOURS.WHITE,
            paddingTop: theme.spacing.unit * 2,
            paddingBottom: theme.spacing.unit * 2,
        }),
        cardDescription: Object.freeze({
            color: COLOURS.DARK_GREY,
            fontSize: '0.875rem',
            marginTop: theme.spacing.unit,
        }),
        headerIcon: Object.freeze({
            marginRight: theme.spacing.unit,
            verticalAlign: 'middle',
            fontSize: '1.25rem',
        }),
        content: Object.freeze({
            padding: theme.spacing.unit * 3,
        }),
        expansionPanel: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
            boxShadow: 'none',
            border: `1px solid ${COLOURS.GREY}`,
            borderRadius: theme.spacing.unit,
            '&:before': {
                display: 'none',
            },
        }),
        expansionPanelSummary: Object.freeze({
            padding: `${theme.spacing.unit * 2}px ${theme.spacing.unit * 2}px`,
            '&:hover': {
                backgroundColor: 'transparent',
            },
        }),
        sectionIconWrapper: Object.freeze({
            padding: theme.spacing.unit,
            borderRadius: theme.spacing.unit / 2,
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginRight: theme.spacing.unit * 1.5,
        }),
        blueBg: Object.freeze({
            backgroundColor: COLOURS.EXTRA_LIGHT_BLUE,
        }),
        amberBg: Object.freeze({
            backgroundColor: '#fff8e1',
        }),
        purpleBg: Object.freeze({
            backgroundColor: COLOURS.LIGHT_PURPLE_BG,
        }),
        greenBg: Object.freeze({
            backgroundColor: COLOURS.LIGHT_GREEN,
        }),
        sectionIcon: Object.freeze({
            fontSize: '1.25rem',
        }),
        blueIcon: Object.freeze({
            color: COLOURS.MATERIAL_BLUE,
        }),
        amberIcon: Object.freeze({
            color: '#f57c00',
        }),
        purpleIcon: Object.freeze({
            color: COLOURS.DARK_PURPLE,
        }),
        greenIcon: Object.freeze({
            color: COLOURS.MATERIAL_GREEN,
        }),
        sectionHeader: Object.freeze({
            display: 'flex',
            alignItems: 'flex-start',
        }),
        sectionTitleWrapper: Object.freeze({
            flex: 1,
        }),
        sectionTitle: Object.freeze({
            fontWeight: 600,
            fontSize: '1.125rem',
            marginBottom: theme.spacing.unit / 2,
        }),
        sectionDescription: Object.freeze({
            fontSize: '0.875rem',
            color: COLOURS.DARK_GREY,
        }),
        expansionPanelDetails: Object.freeze({
            padding: `${theme.spacing.unit * 2}px ${theme.spacing.unit * 3}px ${
                theme.spacing.unit * 3
            }px`,
            display: 'block',
        }),
        field: Object.freeze({
            marginBottom: theme.spacing.unit * 3,
        }),
        fieldLabel: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            marginBottom: theme.spacing.unit,
        }),
        helpIcon: Object.freeze({
            fontSize: '1rem',
            color: COLOURS.DARK_GREY,
            marginLeft: theme.spacing.unit / 2,
        }),
        subsectionTitle: Object.freeze({
            fontWeight: 500,
            fontSize: '1rem',
            marginBottom: theme.spacing.unit * 2,
            marginTop: theme.spacing.unit * 2,
        }),
        subsectionSubtitle: Object.freeze({
            color: COLOURS.DARK_GREY,
            fontWeight: 'normal',
        }),
        actionsRow: Object.freeze({
            display: 'flex',
            justifyContent: 'space-between',
            paddingTop: theme.spacing.unit * 2,
            marginTop: theme.spacing.unit * 2,
            borderTop: `1px solid ${COLOURS.GREY}`,
        }),
        submitButton: Object.freeze({
            backgroundColor: COLOURS.MATERIAL_GREEN,
            color: COLOURS.WHITE,
            '&:hover': {
                backgroundColor: COLOURS.DARK_GREEN,
            },
        }),
    });

const ProfileStep = ({ classes, formData, handleChange, onBack, onSubmit }) => {
    const [
        freeEmissionsEstimateHasErrors,
        setFreeEmissionsEstimateHasErrors,
    ] = useState(false);

    return (
        <Grid container spacing={24}>
            <Grid item xs={12}>
                <Card className={classes.card}>
                    <CardHeader
                        className={classes.cardHeader}
                        title={
                            <div>
                                <Typography variant="title">
                                    <Business className={classes.headerIcon} />
                                    Open Supply Hub Profile
                                </Typography>
                                <Typography className={classes.cardDescription}>
                                    Detailed information about the production
                                    location (Optional)
                                </Typography>
                            </div>
                        }
                    />
                    <CardContent className={classes.content}>
                        {/* Section 1: Production Location Overview */}
                        <ExpansionPanel
                            className={classes.expansionPanel}
                            defaultExpanded
                        >
                            <ExpansionPanelSummary
                                expandIcon={<ExpandMoreIcon />}
                                className={classes.expansionPanelSummary}
                            >
                                <div className={classes.sectionHeader}>
                                    <div
                                        className={`${classes.sectionIconWrapper} ${classes.blueBg}`}
                                    >
                                        <Business
                                            className={`${classes.sectionIcon} ${classes.blueIcon}`}
                                        />
                                    </div>
                                    <div
                                        className={classes.sectionTitleWrapper}
                                    >
                                        <Typography
                                            className={classes.sectionTitle}
                                        >
                                            Production Location Overview
                                        </Typography>
                                        <Typography
                                            className={
                                                classes.sectionDescription
                                            }
                                        >
                                            Basic facility identification and
                                            contact information
                                        </Typography>
                                    </div>
                                </div>
                            </ExpansionPanelSummary>
                            <ExpansionPanelDetails
                                className={classes.expansionPanelDetails}
                            >
                                {/* Local Language Name */}
                                <div className={classes.field}>
                                    <div className={classes.fieldLabel}>
                                        <Typography
                                            variant="body2"
                                            component="label"
                                        >
                                            Production Location Name in Native
                                            Language
                                        </Typography>
                                        <Tooltip
                                            title="Enter the production location name in the local language if different from the English name"
                                            placement="top"
                                        >
                                            <IconButton size="small">
                                                <HelpOutline
                                                    className={classes.helpIcon}
                                                />
                                            </IconButton>
                                        </Tooltip>
                                    </div>
                                    <TextField
                                        fullWidth
                                        variant="outlined"
                                        value={formData.localLanguageName || ''}
                                        onChange={e =>
                                            handleChange(
                                                'localLanguageName',
                                                e.target.value,
                                            )
                                        }
                                        placeholder="Enter location name in native language (if different from English)"
                                    />
                                </div>

                                <Grid container spacing={24}>
                                    {/* Facility Phone */}
                                    <Grid item xs={12} md={6}>
                                        <div className={classes.field}>
                                            <div className={classes.fieldLabel}>
                                                <Typography
                                                    variant="body2"
                                                    component="label"
                                                >
                                                    Company Phone
                                                </Typography>
                                                <Tooltip
                                                    title="Main phone number for contacting this production location directly"
                                                    placement="top"
                                                >
                                                    <IconButton size="small">
                                                        <HelpOutline
                                                            className={
                                                                classes.helpIcon
                                                            }
                                                        />
                                                    </IconButton>
                                                </Tooltip>
                                            </div>
                                            <TextField
                                                fullWidth
                                                variant="outlined"
                                                value={
                                                    formData.facilityPhone || ''
                                                }
                                                onChange={e =>
                                                    handleChange(
                                                        'facilityPhone',
                                                        e.target.value,
                                                    )
                                                }
                                                placeholder="+1 (555) 123-4567"
                                            />
                                        </div>
                                    </Grid>

                                    {/* Facility Website */}
                                    <Grid item xs={12} md={6}>
                                        <div className={classes.field}>
                                            <div className={classes.fieldLabel}>
                                                <Typography
                                                    variant="body2"
                                                    component="label"
                                                >
                                                    Company Website
                                                </Typography>
                                                <Tooltip
                                                    title="Official website URL for this specific production location (if available)"
                                                    placement="top"
                                                >
                                                    <IconButton size="small">
                                                        <HelpOutline
                                                            className={
                                                                classes.helpIcon
                                                            }
                                                        />
                                                    </IconButton>
                                                </Tooltip>
                                            </div>
                                            <TextField
                                                fullWidth
                                                variant="outlined"
                                                value={
                                                    formData.facilityWebsite ||
                                                    ''
                                                }
                                                onChange={e =>
                                                    handleChange(
                                                        'facilityWebsite',
                                                        e.target.value,
                                                    )
                                                }
                                                placeholder="https://company.com"
                                            />
                                        </div>
                                    </Grid>
                                </Grid>

                                {/* Description */}
                                <div className={classes.field}>
                                    <div className={classes.fieldLabel}>
                                        <Typography
                                            variant="body2"
                                            component="label"
                                        >
                                            Production Location Description
                                        </Typography>
                                        <Tooltip
                                            title="Provide a brief overview of what this production location manufactures and its main business activities"
                                            placement="top"
                                        >
                                            <IconButton size="small">
                                                <HelpOutline
                                                    className={classes.helpIcon}
                                                />
                                            </IconButton>
                                        </Tooltip>
                                    </div>
                                    <TextField
                                        fullWidth
                                        multiline
                                        rows={4}
                                        variant="outlined"
                                        value={formData.description || ''}
                                        onChange={e =>
                                            handleChange(
                                                'description',
                                                e.target.value,
                                            )
                                        }
                                        placeholder="Brief description of what this production location produces or its main activities"
                                    />
                                </div>
                            </ExpansionPanelDetails>
                        </ExpansionPanel>

                        {/* Section 2: Company Information */}
                        <ExpansionPanel
                            className={classes.expansionPanel}
                            defaultExpanded
                        >
                            <ExpansionPanelSummary
                                expandIcon={<ExpandMoreIcon />}
                                className={classes.expansionPanelSummary}
                            >
                                <div className={classes.sectionHeader}>
                                    <div
                                        className={`${classes.sectionIconWrapper} ${classes.amberBg}`}
                                    >
                                        <Business
                                            className={`${classes.sectionIcon} ${classes.amberIcon}`}
                                        />
                                    </div>
                                    <div
                                        className={classes.sectionTitleWrapper}
                                    >
                                        <Typography
                                            className={classes.sectionTitle}
                                        >
                                            Company Information
                                        </Typography>
                                        <Typography
                                            className={
                                                classes.sectionDescription
                                            }
                                        >
                                            Parent company and office
                                            information
                                        </Typography>
                                    </div>
                                </div>
                            </ExpansionPanelSummary>
                            <ExpansionPanelDetails
                                className={classes.expansionPanelDetails}
                            >
                                {/* Parent Company Information */}
                                <Typography className={classes.subsectionTitle}>
                                    Parent Company / Owner Information
                                </Typography>

                                <Grid container spacing={16}>
                                    <Grid item xs={12} md={6}>
                                        <div className={classes.field}>
                                            <div className={classes.fieldLabel}>
                                                <Typography
                                                    variant="body2"
                                                    component="label"
                                                >
                                                    Parent Company Name /
                                                    Supplier Group
                                                </Typography>
                                                <Tooltip
                                                    title="The name of the parent company or corporate group that owns this production location"
                                                    placement="top"
                                                >
                                                    <IconButton size="small">
                                                        <HelpOutline
                                                            className={
                                                                classes.helpIcon
                                                            }
                                                        />
                                                    </IconButton>
                                                </Tooltip>
                                            </div>
                                            <TextField
                                                fullWidth
                                                variant="outlined"
                                                value={
                                                    formData.parentCompanyName ||
                                                    ''
                                                }
                                                onChange={e =>
                                                    handleChange(
                                                        'parentCompanyName',
                                                        e.target.value,
                                                    )
                                                }
                                                placeholder="Parent company name"
                                            />
                                        </div>
                                    </Grid>
                                </Grid>

                                {/* Office Information */}
                                <Typography className={classes.subsectionTitle}>
                                    Office Information{' '}
                                    <span
                                        className={classes.subsectionSubtitle}
                                    >
                                        (if different from production location)
                                    </span>
                                </Typography>

                                <Grid container spacing={16}>
                                    <Grid item xs={12} md={6}>
                                        <div className={classes.field}>
                                            <div className={classes.fieldLabel}>
                                                <Typography
                                                    variant="body2"
                                                    component="label"
                                                >
                                                    Office Name
                                                </Typography>
                                                <Tooltip
                                                    title="Name of the corporate office or headquarters"
                                                    placement="top"
                                                >
                                                    <IconButton size="small">
                                                        <HelpOutline
                                                            className={
                                                                classes.helpIcon
                                                            }
                                                        />
                                                    </IconButton>
                                                </Tooltip>
                                            </div>
                                            <TextField
                                                fullWidth
                                                variant="outlined"
                                                value={
                                                    formData.officeName || ''
                                                }
                                                onChange={e =>
                                                    handleChange(
                                                        'officeName',
                                                        e.target.value,
                                                    )
                                                }
                                                placeholder="Office name"
                                            />
                                        </div>
                                    </Grid>
                                    <Grid item xs={12} md={6}>
                                        <div className={classes.field}>
                                            <div className={classes.fieldLabel}>
                                                <Typography
                                                    variant="body2"
                                                    component="label"
                                                >
                                                    Office Address
                                                </Typography>
                                                <Tooltip
                                                    title="Physical address of the office location"
                                                    placement="top"
                                                >
                                                    <IconButton size="small">
                                                        <HelpOutline
                                                            className={
                                                                classes.helpIcon
                                                            }
                                                        />
                                                    </IconButton>
                                                </Tooltip>
                                            </div>
                                            <TextField
                                                fullWidth
                                                variant="outlined"
                                                value={
                                                    formData.officeAddress || ''
                                                }
                                                onChange={e =>
                                                    handleChange(
                                                        'officeAddress',
                                                        e.target.value,
                                                    )
                                                }
                                                placeholder="Office address"
                                            />
                                        </div>
                                    </Grid>
                                    <Grid item xs={12} md={6}>
                                        <div className={classes.field}>
                                            <div className={classes.fieldLabel}>
                                                <Typography
                                                    variant="body2"
                                                    component="label"
                                                >
                                                    Office Country
                                                </Typography>
                                                <Tooltip
                                                    title="Country where the office is located"
                                                    placement="top"
                                                >
                                                    <IconButton size="small">
                                                        <HelpOutline
                                                            className={
                                                                classes.helpIcon
                                                            }
                                                        />
                                                    </IconButton>
                                                </Tooltip>
                                            </div>
                                            <TextField
                                                fullWidth
                                                variant="outlined"
                                                value={
                                                    formData.officeCountry || ''
                                                }
                                                onChange={e =>
                                                    handleChange(
                                                        'officeCountry',
                                                        e.target.value,
                                                    )
                                                }
                                                placeholder="Country"
                                            />
                                        </div>
                                    </Grid>
                                </Grid>
                            </ExpansionPanelDetails>
                        </ExpansionPanel>

                        {/* Section 3: Operations & Capabilities */}
                        <ExpansionPanel
                            className={classes.expansionPanel}
                            defaultExpanded
                        >
                            <ExpansionPanelSummary
                                expandIcon={<ExpandMoreIcon />}
                                className={classes.expansionPanelSummary}
                            >
                                <div className={classes.sectionHeader}>
                                    <div
                                        className={`${classes.sectionIconWrapper} ${classes.blueBg}`}
                                    >
                                        <Business
                                            className={`${classes.sectionIcon} ${classes.blueIcon}`}
                                        />
                                    </div>
                                    <div
                                        className={classes.sectionTitleWrapper}
                                    >
                                        <Typography
                                            className={classes.sectionTitle}
                                        >
                                            Operations & Capabilities
                                        </Typography>
                                        <Typography
                                            className={
                                                classes.sectionDescription
                                            }
                                        >
                                            Production and operations details
                                            for your location
                                        </Typography>
                                    </div>
                                </div>
                            </ExpansionPanelSummary>
                            <ExpansionPanelDetails
                                className={classes.expansionPanelDetails}
                            >
                                <Grid container spacing={24}>
                                    {/* Sector */}
                                    <Grid item xs={12} md={6}>
                                        <div className={classes.field}>
                                            <div className={classes.fieldLabel}>
                                                <Typography
                                                    variant="body2"
                                                    component="label"
                                                >
                                                    Industry / Sectors
                                                </Typography>
                                            </div>
                                            <ReactSelect
                                                isMulti
                                                options={SECTOR_OPTIONS}
                                                value={formData.sector || []}
                                                onChange={values =>
                                                    handleChange(
                                                        'sector',
                                                        values,
                                                    )
                                                }
                                                placeholder="Select sectors..."
                                                className="basic-multi-select"
                                                classNamePrefix="select"
                                            />
                                        </div>
                                    </Grid>

                                    {/* Facility Types */}
                                    <Grid item xs={12} md={6}>
                                        <div className={classes.field}>
                                            <div className={classes.fieldLabel}>
                                                <Typography
                                                    variant="body2"
                                                    component="label"
                                                >
                                                    Facility / Processing Types
                                                </Typography>
                                                <Tooltip
                                                    title="Examples: Cut & Sew, Dyeing, Knitting, Weaving, Printing, Embroidery, Finishing, Assembly"
                                                    placement="top"
                                                >
                                                    <IconButton size="small">
                                                        <HelpOutline
                                                            className={
                                                                classes.helpIcon
                                                            }
                                                        />
                                                    </IconButton>
                                                </Tooltip>
                                            </div>
                                            <ReactSelect
                                                isMulti
                                                options={
                                                    PROCESSING_TYPE_OPTIONS
                                                }
                                                value={
                                                    formData.facilityTypes || []
                                                }
                                                onChange={values =>
                                                    handleChange(
                                                        'facilityTypes',
                                                        values,
                                                    )
                                                }
                                                placeholder="Select processing types..."
                                                className="basic-multi-select"
                                                classNamePrefix="select"
                                            />
                                        </div>
                                    </Grid>
                                </Grid>

                                {/* Product Types */}
                                <div className={classes.field}>
                                    <div className={classes.fieldLabel}>
                                        <Typography
                                            variant="body2"
                                            component="label"
                                        >
                                            Product Types
                                        </Typography>
                                        <Tooltip
                                            title="Examples: T-shirts, Jeans, Dresses, Shirts, Jackets, Underwear, Sportswear, Children's clothing"
                                            placement="top"
                                        >
                                            <IconButton size="small">
                                                <HelpOutline
                                                    className={classes.helpIcon}
                                                />
                                            </IconButton>
                                        </Tooltip>
                                    </div>
                                    <TextField
                                        fullWidth
                                        variant="outlined"
                                        value={formData.productTypes || ''}
                                        onChange={e =>
                                            handleChange(
                                                'productTypes',
                                                e.target.value,
                                            )
                                        }
                                        placeholder="e.g., T-shirts, Jeans, Dresses"
                                    />
                                </div>

                                <Grid container spacing={24}>
                                    {/* Number of Workers */}
                                    <Grid item xs={12} md={6}>
                                        <div className={classes.field}>
                                            <div className={classes.fieldLabel}>
                                                <Typography
                                                    variant="body2"
                                                    component="label"
                                                >
                                                    Number of Workers
                                                </Typography>
                                                <Tooltip
                                                    title="Total number of employees working at this production location"
                                                    placement="top"
                                                >
                                                    <IconButton size="small">
                                                        <HelpOutline
                                                            className={
                                                                classes.helpIcon
                                                            }
                                                        />
                                                    </IconButton>
                                                </Tooltip>
                                            </div>
                                            <TextField
                                                fullWidth
                                                variant="outlined"
                                                type="number"
                                                value={
                                                    formData.numberOfWorkers ||
                                                    ''
                                                }
                                                onChange={e =>
                                                    handleChange(
                                                        'numberOfWorkers',
                                                        e.target.value,
                                                    )
                                                }
                                                placeholder="e.g., 500"
                                            />
                                        </div>
                                    </Grid>

                                    {/* Female Workers */}
                                    <Grid item xs={12} md={6}>
                                        <div className={classes.field}>
                                            <div className={classes.fieldLabel}>
                                                <Typography
                                                    variant="body2"
                                                    component="label"
                                                >
                                                    % of Female Workers
                                                </Typography>
                                                <Tooltip
                                                    title="Percentage of female employees out of the total workforce at this location"
                                                    placement="top"
                                                >
                                                    <IconButton size="small">
                                                        <HelpOutline
                                                            className={
                                                                classes.helpIcon
                                                            }
                                                        />
                                                    </IconButton>
                                                </Tooltip>
                                            </div>
                                            <TextField
                                                fullWidth
                                                variant="outlined"
                                                value={
                                                    formData.femaleWorkers || ''
                                                }
                                                onChange={e =>
                                                    handleChange(
                                                        'femaleWorkers',
                                                        e.target.value,
                                                    )
                                                }
                                                placeholder="e.g., 45%"
                                            />
                                        </div>
                                    </Grid>
                                </Grid>

                                <Grid container spacing={24}>
                                    {/* Minimum Order Quantity */}
                                    <Grid item xs={12} md={6}>
                                        <div className={classes.field}>
                                            <div className={classes.fieldLabel}>
                                                <Typography
                                                    variant="body2"
                                                    component="label"
                                                >
                                                    Minimum Order Quantity
                                                </Typography>
                                                <Tooltip
                                                    title="Smallest order quantity this production location will accept from customers"
                                                    placement="top"
                                                >
                                                    <IconButton size="small">
                                                        <HelpOutline
                                                            className={
                                                                classes.helpIcon
                                                            }
                                                        />
                                                    </IconButton>
                                                </Tooltip>
                                            </div>
                                            <TextField
                                                fullWidth
                                                variant="outlined"
                                                value={
                                                    formData.minimumOrderQuantity ||
                                                    ''
                                                }
                                                onChange={e =>
                                                    handleChange(
                                                        'minimumOrderQuantity',
                                                        e.target.value,
                                                    )
                                                }
                                                placeholder="e.g., 1000 units"
                                            />
                                        </div>
                                    </Grid>

                                    {/* Average Lead Time */}
                                    <Grid item xs={12} md={6}>
                                        <div className={classes.field}>
                                            <div className={classes.fieldLabel}>
                                                <Typography
                                                    variant="body2"
                                                    component="label"
                                                >
                                                    Average Lead Time
                                                </Typography>
                                                <Tooltip
                                                    title="Typical time required from order confirmation to product delivery"
                                                    placement="top"
                                                >
                                                    <IconButton size="small">
                                                        <HelpOutline
                                                            className={
                                                                classes.helpIcon
                                                            }
                                                        />
                                                    </IconButton>
                                                </Tooltip>
                                            </div>
                                            <TextField
                                                fullWidth
                                                variant="outlined"
                                                value={
                                                    formData.averageLeadTime ||
                                                    ''
                                                }
                                                onChange={e =>
                                                    handleChange(
                                                        'averageLeadTime',
                                                        e.target.value,
                                                    )
                                                }
                                                placeholder="e.g., 30 days"
                                            />
                                        </div>
                                    </Grid>
                                </Grid>
                            </ExpansionPanelDetails>
                        </ExpansionPanel>

                        {/* Section 4: Compliance & Partnerships */}
                        <ExpansionPanel
                            className={classes.expansionPanel}
                            defaultExpanded
                        >
                            <ExpansionPanelSummary
                                expandIcon={<ExpandMoreIcon />}
                                className={classes.expansionPanelSummary}
                            >
                                <div className={classes.sectionHeader}>
                                    <div
                                        className={`${classes.sectionIconWrapper} ${classes.purpleBg}`}
                                    >
                                        <VerifiedUser
                                            className={`${classes.sectionIcon} ${classes.purpleIcon}`}
                                        />
                                    </div>
                                    <div
                                        className={classes.sectionTitleWrapper}
                                    >
                                        <Typography
                                            className={classes.sectionTitle}
                                        >
                                            Compliance & Partnerships
                                        </Typography>
                                        <Typography
                                            className={
                                                classes.sectionDescription
                                            }
                                        >
                                            Certifications, affiliations, and
                                            industry standards
                                        </Typography>
                                    </div>
                                </div>
                            </ExpansionPanelSummary>
                            <ExpansionPanelDetails
                                className={classes.expansionPanelDetails}
                            >
                                {/* Affiliations */}
                                <div className={classes.field}>
                                    <div className={classes.fieldLabel}>
                                        <Typography
                                            variant="body2"
                                            component="label"
                                        >
                                            Affiliations
                                        </Typography>
                                        <Tooltip
                                            title="Organizations, parent companies, or partner entities your facility is formally connected to"
                                            placement="top"
                                        >
                                            <IconButton size="small">
                                                <HelpOutline
                                                    className={classes.helpIcon}
                                                />
                                            </IconButton>
                                        </Tooltip>
                                    </div>
                                    <ReactSelect
                                        isMulti
                                        options={AFFILIATIONS_OPTIONS}
                                        value={formData.affiliations || []}
                                        onChange={values =>
                                            handleChange('affiliations', values)
                                        }
                                        placeholder="Select affiliations..."
                                        className="basic-multi-select"
                                        classNamePrefix="select"
                                    />
                                </div>

                                {/* Certifications */}
                                <div className={classes.field}>
                                    <div className={classes.fieldLabel}>
                                        <Typography
                                            variant="body2"
                                            component="label"
                                        >
                                            Certifications / Standards /
                                            Regulations
                                        </Typography>
                                    </div>
                                    <ReactSelect
                                        isMulti
                                        options={CERTIFICATIONS_OPTIONS}
                                        value={formData.certifications || []}
                                        onChange={values =>
                                            handleChange(
                                                'certifications',
                                                values,
                                            )
                                        }
                                        placeholder="Select certifications..."
                                        className="basic-multi-select"
                                        classNamePrefix="select"
                                    />
                                </div>
                            </ExpansionPanelDetails>
                        </ExpansionPanel>

                        {/* Section 5: Environmental Data */}
                        <ExpansionPanel
                            className={classes.expansionPanel}
                            defaultExpanded
                        >
                            <ExpansionPanelSummary
                                expandIcon={<ExpandMoreIcon />}
                                className={classes.expansionPanelSummary}
                            >
                                <div className={classes.sectionHeader}>
                                    <div
                                        className={`${classes.sectionIconWrapper} ${classes.greenBg}`}
                                    >
                                        <Nature
                                            className={`${classes.sectionIcon} ${classes.greenIcon}`}
                                        />
                                    </div>
                                    <div
                                        className={classes.sectionTitleWrapper}
                                    >
                                        <Typography
                                            className={classes.sectionTitle}
                                        >
                                            Environmental Data
                                        </Typography>
                                        <Typography
                                            className={
                                                classes.sectionDescription
                                            }
                                        >
                                            Emissions estimates and energy
                                            consumption data
                                        </Typography>
                                    </div>
                                </div>
                            </ExpansionPanelSummary>
                            <ExpansionPanelDetails
                                className={classes.expansionPanelDetails}
                            >
                                <FreeEmissionsEstimate
                                    onValidationChange={
                                        setFreeEmissionsEstimateHasErrors
                                    }
                                />
                            </ExpansionPanelDetails>
                        </ExpansionPanel>

                        {/* Action Buttons */}
                        <div className={classes.actionsRow}>
                            <Button variant="outlined" onClick={onBack}>
                                Back
                            </Button>
                            <Button
                                variant="contained"
                                className={classes.submitButton}
                                onClick={onSubmit}
                                disabled={freeEmissionsEstimateHasErrors}
                            >
                                Submit Claim
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </Grid>
        </Grid>
    );
};

ProfileStep.propTypes = {
    classes: object.isRequired,
    formData: object.isRequired,
    handleChange: func.isRequired,
    onBack: func,
    onSubmit: func,
};

ProfileStep.defaultProps = {
    onBack: () => {},
    onSubmit: () => {},
};

export default withStyles(profileStepStyles)(withScrollReset(ProfileStep));
