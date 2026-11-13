import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'react-toastify';
import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Switch from '@material-ui/core/Switch';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';

import AppGrid from './AppGrid';
import apiRequest from '../util/apiRequest';
import {
    makeSpotlightFieldsURL,
    makeSpotlightVisibilityURL,
} from '../util/util';
import {
    SPOTLIGHT_NAME_RULES,
    SPOTLIGHT_DISPLAY_NAME_RULES,
    validateSpotlightInternalName,
    validateSpotlightDisplayName,
    getSpotlightFieldStatus,
    getSpotlightFieldTypeLabel,
    getSpotlightPreviewRows,
    SPOTLIGHT_DEFAULT_FIELD_TYPE,
    SPOTLIGHT_FIELD_TYPE_HELP,
} from '../util/spotlightFields';

const sectionStyle = { marginBottom: 32 };

// Pulls the first readable message out of an API error response.
const getErrorMessages = error => {
    const data = error && error.response && error.response.data;
    if (!data) return { general: 'Something went wrong. Please try again.' };
    if (Array.isArray(data)) return { general: data.join(' ') };
    if (data.detail) return { general: data.detail };
    return Object.keys(data).reduce(
        (messages, key) => ({
            ...messages,
            [key]: Array.isArray(data[key]) ? data[key].join(' ') : data[key],
        }),
        {},
    );
};

/**
 * The Spotlight tab in Settings. Spotlight partners create the fields that
 * describe their data, rename how a field is displayed, and switch fields on
 * or off once an admin has approved them. Fields can never be deleted.
 */
function SpotlightFieldsSettings() {
    const [loading, setLoading] = useState(true);
    const [summary, setSummary] = useState(null);
    const [name, setName] = useState('');
    const [displayName, setDisplayName] = useState('');
    const [fieldType, setFieldType] = useState(SPOTLIGHT_DEFAULT_FIELD_TYPE);
    const [formErrors, setFormErrors] = useState({});
    const [notice, setNotice] = useState(null);
    const [edits, setEdits] = useState({});

    const handleError = error => {
        const messages = getErrorMessages(error);
        if (messages.general) {
            toast.error(messages.general, { position: 'bottom-left' });
        }
        return messages;
    };

    const load = useCallback(() => {
        setLoading(true);
        apiRequest
            .get(makeSpotlightFieldsURL())
            .then(({ data }) => setSummary(data))
            .catch(handleError)
            .finally(() => setLoading(false));
    }, []);

    useEffect(() => load(), [load]);

    const submitNewField = e => {
        e.preventDefault();
        const errors = {};
        const nameError = validateSpotlightInternalName(name);
        const displayError = validateSpotlightDisplayName(displayName);
        if (nameError) errors.name = nameError;
        if (displayError) errors.display_name = displayError;
        setFormErrors(errors);
        if (Object.keys(errors).length > 0) return;

        setLoading(true);
        apiRequest
            .post(makeSpotlightFieldsURL(), {
                name,
                display_name: displayName.trim(),
                field_type: fieldType,
            })
            .then(({ data }) => {
                setSummary(data);
                setNotice(data.message);
                setName('');
                setDisplayName('');
                setFieldType(SPOTLIGHT_DEFAULT_FIELD_TYPE);
            })
            .catch(error => setFormErrors(handleError(error)))
            .finally(() => setLoading(false));
    };

    const updateField = (fieldName, changes) => {
        setLoading(true);
        apiRequest
            .patch(makeSpotlightFieldsURL(fieldName), changes)
            .then(({ data }) => {
                setSummary(data);
                setEdits(previous => {
                    const { [fieldName]: removed, ...rest } = previous;
                    return rest;
                });
            })
            .catch(handleError)
            .finally(() => setLoading(false));
    };

    const updateVisibility = changes => {
        setLoading(true);
        apiRequest
            .patch(makeSpotlightVisibilityURL(), changes)
            .then(({ data }) => setSummary(data))
            .catch(handleError)
            .finally(() => setLoading(false));
    };

    if (!summary) {
        return (
            <AppGrid title="Spotlight">
                {loading ? (
                    <CircularProgress />
                ) : (
                    <Typography>
                        We could not load your Spotlight fields.
                    </Typography>
                )}
            </AppGrid>
        );
    }

    const previewRows = getSpotlightPreviewRows(summary.fields, {
        displayName,
        fieldType,
    });

    return (
        <AppGrid title="Spotlight">
            <div style={sectionStyle}>
                <Typography paragraph>
                    Create the fields that describe your data on OS Hub. New
                    fields stay inactive until the OS Hub team approves them.
                    Once approved, you can switch them on yourself
                    {summary.go_live_date
                        ? ', or they go live automatically on the date we set.'
                        : '.'}
                </Typography>
                {summary.go_live_date && (
                    <Typography paragraph>
                        <strong>Go-live date: {summary.go_live_date}.</strong>{' '}
                        {summary.go_live_pending
                            ? 'Until then you cannot switch fields on yourself; ' +
                              'they will all go live on this date.'
                            : 'This date has passed.'}
                    </Typography>
                )}
                {notice && (
                    <Typography
                        paragraph
                        role="status"
                        style={{ fontWeight: 600 }}
                    >
                        {notice}
                    </Typography>
                )}
            </div>

            <form
                onSubmit={submitNewField}
                style={sectionStyle}
                noValidate
                aria-label="Add a Spotlight field"
            >
                <Typography variant="title" gutterBottom>
                    Add a field
                </Typography>
                <TextField
                    id="spotlight-internal-name"
                    label="Internal name"
                    value={name}
                    onChange={e => setName(e.target.value)}
                    error={Boolean(formErrors.name)}
                    helperText={formErrors.name || SPOTLIGHT_NAME_RULES}
                    placeholder="e.g. assessment_date"
                    fullWidth
                    margin="normal"
                    inputProps={{ maxLength: 50 }}
                />
                <TextField
                    id="spotlight-display-name"
                    label="Display name"
                    value={displayName}
                    onChange={e => setDisplayName(e.target.value)}
                    error={Boolean(formErrors.display_name)}
                    helperText={
                        formErrors.display_name || SPOTLIGHT_DISPLAY_NAME_RULES
                    }
                    placeholder="e.g. Assessment date"
                    fullWidth
                    margin="normal"
                    inputProps={{ maxLength: 50 }}
                />
                <TextField
                    id="spotlight-field-type"
                    select
                    label="Type"
                    value={fieldType}
                    onChange={e => setFieldType(e.target.value)}
                    error={Boolean(formErrors.field_type)}
                    helperText={
                        formErrors.field_type || SPOTLIGHT_FIELD_TYPE_HELP
                    }
                    SelectProps={{ native: true }}
                    fullWidth
                    margin="normal"
                >
                    {summary.field_types.map(type => (
                        <option key={type.value} value={type.value}>
                            {type.label}
                        </option>
                    ))}
                </TextField>
                <Button
                    type="submit"
                    variant="contained"
                    color="primary"
                    disabled={loading}
                >
                    Submit field
                </Button>
            </form>

            <div style={sectionStyle} aria-label="Preview of your fields">
                <Typography variant="title" gutterBottom>
                    Preview
                </Typography>
                <Typography variant="caption" gutterBottom>
                    How your fields will look on a production location page once
                    they are live. The values shown are examples.
                </Typography>
                <div
                    style={{
                        border: '1px solid #e0e0e0',
                        borderTop: '2px solid #7c3aed',
                        borderRadius: 4,
                        marginTop: 8,
                        padding: 16,
                    }}
                >
                    <Typography
                        variant="subheading"
                        style={{
                            fontWeight: 700,
                            textTransform: 'uppercase',
                        }}
                    >
                        {summary.contributor_name}
                    </Typography>
                    {previewRows.length === 0 ? (
                        <Typography style={{ fontStyle: 'italic' }}>
                            Add a field to see the preview.
                        </Typography>
                    ) : (
                        previewRows.map(row => (
                            <Typography
                                key={row.key}
                                style={{ opacity: row.isDraft ? 0.6 : 1 }}
                            >
                                {row.label}: {row.value}
                                {row.isDraft ? ' (new)' : ''}
                            </Typography>
                        ))
                    )}
                </div>
            </div>

            <div style={sectionStyle}>
                <Typography variant="title" gutterBottom>
                    Your fields
                </Typography>
                {summary.fields.length === 0 ? (
                    <Typography>You have not added any fields yet.</Typography>
                ) : (
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Display name</TableCell>
                                <TableCell>Internal name</TableCell>
                                <TableCell>Type</TableCell>
                                <TableCell>Status</TableCell>
                                <TableCell>Active</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {summary.fields.map(field => {
                                const edited = edits[field.name];
                                const current =
                                    edited === undefined
                                        ? field.display_name
                                        : edited;
                                const blockedByDate =
                                    !field.active && summary.go_live_pending;
                                return (
                                    <TableRow key={field.name}>
                                        <TableCell>
                                            <TextField
                                                value={current}
                                                onChange={e =>
                                                    setEdits(previous => ({
                                                        ...previous,
                                                        [field.name]:
                                                            e.target.value,
                                                    }))
                                                }
                                                error={Boolean(
                                                    edited !== undefined &&
                                                        validateSpotlightDisplayName(
                                                            edited,
                                                        ),
                                                )}
                                                helperText={
                                                    edited !== undefined
                                                        ? validateSpotlightDisplayName(
                                                              edited,
                                                          )
                                                        : null
                                                }
                                                inputProps={{
                                                    maxLength: 50,
                                                    'aria-label': `Display name for ${field.name}`,
                                                }}
                                            />
                                            {edited !== undefined &&
                                                edited !==
                                                    field.display_name && (
                                                    <Button
                                                        size="small"
                                                        disabled={
                                                            loading ||
                                                            Boolean(
                                                                validateSpotlightDisplayName(
                                                                    edited,
                                                                ),
                                                            )
                                                        }
                                                        onClick={() =>
                                                            updateField(
                                                                field.name,
                                                                {
                                                                    display_name: edited.trim(),
                                                                },
                                                            )
                                                        }
                                                    >
                                                        Save
                                                    </Button>
                                                )}
                                        </TableCell>
                                        <TableCell>
                                            <code>{field.name}</code>
                                        </TableCell>
                                        <TableCell>
                                            {getSpotlightFieldTypeLabel(
                                                summary.field_types,
                                                field.field_type,
                                            )}
                                        </TableCell>
                                        <TableCell>
                                            {getSpotlightFieldStatus(field)}
                                        </TableCell>
                                        <TableCell>
                                            <Switch
                                                checked={field.active}
                                                disabled={
                                                    loading ||
                                                    !field.approved ||
                                                    blockedByDate
                                                }
                                                onChange={e =>
                                                    updateField(field.name, {
                                                        active:
                                                            e.target.checked,
                                                    })
                                                }
                                                inputProps={{
                                                    'aria-label': `Active: ${field.name}`,
                                                }}
                                            />
                                        </TableCell>
                                    </TableRow>
                                );
                            })}
                        </TableBody>
                    </Table>
                )}
                <Typography variant="caption" style={{ marginTop: 8 }}>
                    Fields cannot be deleted. Switch a field off to hide it
                    everywhere on OS Hub.
                </Typography>
            </div>

            {summary.can_control_visibility && (
                <div style={sectionStyle}>
                    <Typography variant="title" gutterBottom>
                        Where your fields appear
                    </Typography>
                    <FormControlLabel
                        control={
                            <Switch
                                checked={summary.available_in_api}
                                disabled={loading}
                                onChange={e =>
                                    updateVisibility({
                                        available_in_api: e.target.checked,
                                    })
                                }
                            />
                        }
                        label="Show in the API"
                    />
                    <FormControlLabel
                        control={
                            <Switch
                                checked={summary.available_in_data_downloads}
                                disabled={loading}
                                onChange={e =>
                                    updateVisibility({
                                        available_in_data_downloads:
                                            e.target.checked,
                                    })
                                }
                            />
                        }
                        label="Show in data downloads"
                    />
                </div>
            )}
        </AppGrid>
    );
}

export default SpotlightFieldsSettings;
